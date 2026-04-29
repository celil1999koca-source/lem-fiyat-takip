import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Sayfa Ayarları
st.set_page_config(page_title="LME & Kur Takibi", layout="wide")

st.title("📊 LME Metal ve Döviz Takip Paneli")

# Kontrol Paneli
guncelleme_hizi = st.sidebar.slider("Güncelleme Hızı (Saniye)", 30, 300, 60)

@st.cache_data(ttl=guncelleme_hizi)
def veri_cek(sembol):
    try:
        data = yf.Ticker(sembol)
        df = data.history(period="2d") # Kur için son 2 gün yeterli
        guncel = round(df['Close'].iloc[-1], 2)
        degisim = round(guncel - df['Close'].iloc[-2], 2)
        return guncel, degisim, df['Close']
    except:
        return 0.0, 0.0, pd.Series()

# Verileri Çekelim
bakir_fiyat, bakir_fark, _ = veri_cek('HG=F')
alu_fiyat, alu_fark, _ = veri_cek('ALI=F')
dolar_fiyat, dolar_fark, _ = veri_cek('USDTRY=X') # Dolar kurunu çeken satır

# Metrikleri Gösterelim
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Bakır (USD)", f"{bakir_fiyat}$", f"{bakir_fark}")

with col2:
    st.metric("Alüminyum (USD)", f"{alu_fiyat}$", f"{alu_fark}")

with col3:
    # Dolar kurunu burada gösteriyoruz
    st.metric("USD / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")

with col4:
    st.write(f"⏱️ Son Güncelleme:  \n{time.strftime('%H:%M:%S')}")

# Hesaplama Alanı (Bonus)
st.divider()
st.subheader("🧮 Hızlı Hesaplama (TL Karşılığı)")
secilen_metal = st.radio("Hesaplanacak Metali Seçin:", ["Bakır", "Alüminyum"], horizontal=True)

fiyat = bakir_fiyat if secilen_metal == "Bakır" else alu_fiyat
toplam_tl = round(fiyat * dolar_fiyat, 2)

st.info(f"1 Birim **{secilen_metal}** şu an yaklaşık **{toplam_tl} ₺** ediyor.")

# Sayfayı tazele
time.sleep(guncelleme_hizi)
st.rerun()
