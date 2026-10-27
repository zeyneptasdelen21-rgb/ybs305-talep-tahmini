from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.train import evaluate_models, forecast_next_seven

DATA = ROOT / "app" / "data" / "mart_daily_demand.csv"

st.set_page_config(page_title="Hizmet Talebi ve Perakende Talep Tahmini", layout="wide")
st.title("Armut Hizmet Talebi ve NovaPerakende Satışlarının Zaman Analizi ve Talep Tahmini")
st.caption("Armut hizmet talebi ile NovaPerakende ürün satışlarının günlük ilişkisini inceliyor, perakende talebini tahmin ederek stok planlamasına yönelik öneriler geliştiriyoruz. Kaynaklar müşteri veya kategori bazında eşleşmez.")
if not DATA.exists():
    st.error("Mart CSV bulunamadı. Önce dbt modellerini çalıştırıp `scripts/export_marts.py` adımını tamamlayın.")
    st.stop()
df = pd.read_csv(DATA, parse_dates=["demand_date"])
min_date, max_date = df.demand_date.min().date(), df.demand_date.max().date()
start, end = st.date_input("Tarih aralığı", (min_date, max_date), min_value=min_date, max_value=max_date)
view = df[(df.demand_date.dt.date >= start) & (df.demand_date.dt.date <= end)].copy()
if view.empty:
    st.warning("Seçilen tarihlerde kayıt yok.")
    st.stop()

k1, k2, k3 = st.columns(3)
k1.metric("Hizmet talebi", f"{int(view.armut_service_requests.sum()):,}")
k2.metric("Satılan ürün adedi", f"{int(view.retail_units_sold.sum()):,}")
k3.metric("Net satış", f"₺{view.retail_net_sales.sum():,.0f}")

left, right = st.columns(2)
with left:
    st.subheader("Günlük talep karşılaştırması")
    chart = view.melt(id_vars="demand_date", value_vars=["armut_service_requests", "retail_units_sold"], var_name="seri", value_name="adet")
    st.plotly_chart(px.line(chart, x="demand_date", y="adet", color="seri"), use_container_width=True)
with right:
    st.subheader("Perakende satış tutarı")
    st.plotly_chart(px.area(view, x="demand_date", y="retail_net_sales"), use_container_width=True)
st.subheader("Haftanın gününe göre ürün talebi")
weekday = view.assign(hafta_gunu=view.demand_date.dt.day_name()).groupby(["day_of_week", "hafta_gunu"], as_index=False).retail_units_sold.mean().sort_values("day_of_week")
st.plotly_chart(px.bar(weekday, x="hafta_gunu", y="retail_units_sold", labels={"hafta_gunu":"Haftanın günü", "retail_units_sold":"Ortalama adet"}), use_container_width=True)

st.subheader("7 günlük perakende talep tahmini")
st.caption(f"Son gözlem {df.demand_date.max():%d.%m.%Y}; bu dönem verisiyle hesaplanan tahmin geçmişe dönük bir ders demosudur, güncel tahmin değildir.")
try:
    _, scores, winner = evaluate_models(df)
    st.write(f"Tahmin için seçilen model: **{winner}** (yalnızca geçmiş perakende satışlarını kullanır; test MAE’si en düşük model).")
    st.caption("Ek deney: aynı algoritmalar, gecikmeli Armut sayımları eklenerek de ölçülür. Bu özelliklerin test hatasını düşürüp düşürmediğini karşılaştırın; yalnızca 2024 ve takvim günü eşleşmesi nedeniyle sonuç keşifseldir.")
    st.dataframe(pd.DataFrame(scores).T.rename_axis("Model"), use_container_width=True)
    forecast = forecast_next_seven(df, winner)
    st.plotly_chart(px.bar(forecast, x="demand_date", y="forecast_units", title="Gelecek 7 gün için tahmini satılan ürün adedi"), use_container_width=True)
except ValueError as exc:
    st.info(str(exc))

with st.expander("Yöntem ve sınırlılıklar"):
    pearson = view[["armut_service_requests", "retail_units_sold"]].corr(method="pearson").iloc[0, 1]
    spearman = view[["armut_service_requests", "retail_units_sold"]].corr(method="spearman").iloc[0, 1]
    st.write(f"Seçili aralıkta eşzamanlı günlük korelasyon: Pearson {pearson:.3f}, Spearman {spearman:.3f}. Bu istatistikler nedensellik göstermez ve trend/haftalık örüntülerden etkilenebilir.")
    st.markdown("""
    - İlişki analizi aynı takvim günündeki toplam hizmet kayıtları ve toplam perakende ürün adedini karşılaştırır.
    - Armut dosyasında şehir/bölge ve kategori adı; iki dosyada ortak müşteri anahtarı yoktur. Kategori eşleştirmesi veya nedensellik iddiası kurulmaz.
    - Perakende verisi 2024'te 2.000 satırla sınırlıdır. Sıfır görünen günler kaynakta işlem satırı bulunmayan günlerdir.
    - Tahmin hedefi Armut değil, günlük toplam perakende ürün adedidir. Son %20 zaman sıralı test kümesinde MAE, RMSE ve WAPE karşılaştırılır.
    - Pilot sonuç stok kararına doğrudan aktarılmadan önce daha uzun, gerçek ve temsil gücü doğrulanmış geçmiş veriyle yeniden değerlendirilmelidir.
    """)
