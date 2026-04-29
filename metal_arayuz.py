import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Sayfa Ayarları (En üstte olmalı)
st.set_page_config(page_title="LME & Kur Takibi", layout="wide")

# 2. Mobil Uyumlu Başlık
st.markdown("<h2 style='text-align: center;'>📱 Metal Takip Mobil</h2>", unsafe_allow_html=True)

# 3. Kontrol Paneli (Sol Menü)
st.sidebar.header("Ayarlar")
guncelleme_hizi = st.sidebar.slider("Güncelleme Hızı (Saniye)", 30, 300, 60)

# 4. Veri Çekme Fonksiyonu (Hata kontrolü eklenmiş)
@st.cache_data(ttl=guncelleme_hizi)
def veri_cek(sembol):
    try:
        ticker = yf.Ticker(sembol)
        df = ticker.history(period="5d")
        if df.empty:
            return 0.0, 0.0, pd.Series()
        guncel = round(df['Close'].iloc[-1], 2)
        degisim = round(guncel - df['Close'].iloc[-2], 2)
        return guncel, degisim, df['Close']
    except Exception:
        return 0.0, 0.0, pd.Series()

# 5. Verileri Çek
bakir_fiyat, bakir_fark, bakir_liste = veri_cek('HG=F')
alu_fiyat, alu_fark, alu_liste = veri_cek('ALI=F')
dolar_fiyat, dolar_fark, _ = veri_cek('USDTRY=X')

# 6. Metrik Kartları (Mobil için 2 sütunlu düzen)
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.metric("Bakır (USD)", f"{bakir_fiyat}$", f"{bakir_fark}")

with col2:
    st.metric("Alüminyum (USD)", f"{alu_fiyat}$", f"{alu_fark}")

with col3:
    st.metric("Dolar / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")

with col4:
    st.write(f"⏱️ Güncelleme:  \n{time.strftime('%H:%M:%S')}")

# 7. Grafik Alanı
st.divider()
st.subheader("📈 Fiyat Trendi (Son 5 Gün)")
if not bakir_liste.empty:
    grafik_data = pd.DataFrame({
        "Bakır": bakir_liste,
        "Alüminyum": alu_liste
    })
    st.line_chart(grafik_data)

# 8. Hızlı TL Hesaplama
st.divider()
st.subheader("🧮 TL Karşılığı")
secilen_metal = st.radio("Metal Seçin:", ["Bakır", "Alüminyum"], horizontal=True)
fiyat = bakir_fiyat if secilen_metal == "Bakır" else alu_fiyat
toplam_tl = round(fiyat * dolar_fiyat, 2)
st.success(f"1 Birim **{secilen_metal}** şu an yaklaşık **{toplam_tl} ₺** ediyor.")

# 9. Sayfayı Yenileme Mekanizması
time.sleep(guncelleme_hizi)
st.rerun()
