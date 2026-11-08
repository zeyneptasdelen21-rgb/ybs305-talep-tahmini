"""Compare two regressors using a chronological holdout on daily retail unit demand."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data" / "mart_daily_demand.csv"
RETAIL_FEATURES = ["lag_1", "lag_7", "rolling_mean_7", "rolling_mean_28", "day_of_week", "month", "day_of_year"]
ARMUT_FEATURES = ["armut_lag_1", "armut_lag_7"]

def features(frame: pd.DataFrame) -> pd.DataFrame:
    x = frame.copy().sort_values("demand_date")
    x["demand_date"] = pd.to_datetime(x["demand_date"])
    y = x["retail_units_sold"].astype(float)
    x["lag_1"] = y.shift(1)
    x["lag_7"] = y.shift(7)
    x["rolling_mean_7"] = y.shift(1).rolling(7).mean()
    x["rolling_mean_28"] = y.shift(1).rolling(28).mean()
    x["day_of_week"] = x["demand_date"].dt.dayofweek
    x["month"] = x["demand_date"].dt.month
    x["day_of_year"] = x["demand_date"].dt.dayofyear
    armut = x["armut_service_requests"].astype(float)
    x["armut_lag_1"] = armut.shift(1)
    x["armut_lag_7"] = armut.shift(7)
    x["target"] = y
    return x.dropna(subset=RETAIL_FEATURES + ARMUT_FEATURES + ["target"]).reset_index(drop=True)

def evaluate_models(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict, str]:
    data = features(frame)
    if len(data) < 80:
        raise ValueError("At least 80 daily rows are required for a chronological evaluation.")
    cutoff = int(len(data) * 0.8)
    train, test = data.iloc[:cutoff], data.iloc[cutoff:]
    algorithms = {
        "Random Forest": RandomForestRegressor(n_estimators=300, max_depth=6, min_samples_leaf=3, random_state=42, n_jobs=-1),
        "HistGradientBoosting": HistGradientBoostingRegressor(max_iter=150, max_leaf_nodes=15, l2_regularization=1.0, random_state=42),
    }
    report = {}
    for name, estimator in algorithms.items():
        for feature_set_name, feature_set in [("retail-only", RETAIL_FEATURES), ("plus-lagged-Armut", RETAIL_FEATURES + ARMUT_FEATURES)]:
            label = f"{name} ({feature_set_name})"
            estimator.fit(train[feature_set], train["target"])
            pred = np.maximum(0, estimator.predict(test[feature_set]))
            mae = float(mean_absolute_error(test["target"], pred))
            rmse = float(np.sqrt(mean_squared_error(test["target"], pred)))
            denominator = max(float(test["target"].sum()), 1.0)
            report[label] = {"MAE": round(mae, 3), "RMSE": round(rmse, 3), "WAPE": round(float(np.abs(test["target"].to_numpy() - pred).sum() / denominator), 4)}
    retail_only = {name: metrics for name, metrics in report.items() if "retail-only" in name}
    winner = min(retail_only, key=lambda n: retail_only[n]["MAE"])
    return data, report, winner

def forecast_next_seven(frame: pd.DataFrame, model_name: str) -> pd.DataFrame:
    data, _, _ = evaluate_models(frame)
    estimator = {
        "Random Forest": RandomForestRegressor(n_estimators=300, max_depth=6, min_samples_leaf=3, random_state=42, n_jobs=-1),
        "HistGradientBoosting": HistGradientBoostingRegressor(max_iter=150, max_leaf_nodes=15, l2_regularization=1.0, random_state=42),
    }[model_name.split(" (")[0]]
    estimator.fit(data[RETAIL_FEATURES], data["target"])
    hist = frame.copy().sort_values("demand_date")
    hist["demand_date"] = pd.to_datetime(hist["demand_date"])
    values = hist["retail_units_sold"].astype(float).tolist()
    last = hist["demand_date"].max()
    rows = []
    for offset in range(1, 8):
        d = last + pd.Timedelta(days=offset)
        row = pd.DataFrame([{
            "lag_1": values[-1], "lag_7": values[-7],
            "rolling_mean_7": float(np.mean(values[-7:])),
            "rolling_mean_28": float(np.mean(values[-28:])),
            "day_of_week": d.dayofweek, "month": d.month, "day_of_year": d.dayofyear,
        }])
        value = max(0.0, float(estimator.predict(row[RETAIL_FEATURES])[0]))
        rows.append({"demand_date": d.date().isoformat(), "forecast_units": round(value, 2)})
        values.append(value)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = pd.read_csv(DATA)
    _, results, best = evaluate_models(df)
    print(json.dumps({"evaluation": results, "selected_model_by_mae": best}, indent=2))
    out = ROOT / "model" / "artifacts"
    out.mkdir(exist_ok=True)
    (out / "evaluation.json").write_text(json.dumps({"evaluation": results, "selected_model_by_mae": best}, indent=2), encoding="utf-8")
    forecast_next_seven(df, best).to_csv(out / "forecast_next_7_days.csv", index=False)
