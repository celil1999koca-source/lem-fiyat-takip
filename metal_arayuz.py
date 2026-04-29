import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="LME Canlı Takip", layout="wide")

st.title("📊 LME Metal Borsası - Canlı Takip Paneli")

# Sol menü ayarları
st.sidebar.header("Kontrol Paneli")
guncelleme = st.sidebar.slider("Güncelleme Hızı (Sn)", 5, 30, 10)

# Verileri tutmak için ana yerleşim
ust_alan = st.empty() # Metrikler (Kartlar) burada güncellenecek
grafik_alani = st.empty() # Grafik burada güncellenecek

def veri_cek(sembol):
    data = yf.Ticker(sembol)
    # Son 5 günlük veriyi çekelim ki grafik oluşsun
    df = data.history(period="50d")
    güncel_fiyat = round(df['Close'].iloc[-1], 2)
    degisim = round(güncel_fiyat - df['Close'].iloc[-2], 2)
    return güncel_fiyat, degisim, df['Close']

while True:
    # Verileri çekiyoruz
    bakir_fiyat, bakir_fark, bakir_liste = veri_cek('HG=F')
    alu_fiyat, alu_fark, alu_liste = veri_cek('ALI=F')

    # 1. KARTLARI GÜNCELLE (Üst Alan)
    with ust_alan.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Bakır (USD)", f"{bakir_fiyat}", f"{bakir_fark}")
        col2.metric("Alüminyum (USD)", f"{alu_fiyat}", f"{alu_fark}")
        col3.write(f"⏱️ Son Güncelleme: {time.strftime('%H:%M:%S')}")

    # 2. GRAFİĞİ GÜNCELLE (Grafik Alanı)
    with grafik_alani.container():
        st.subheader("Fiyat Trendi (Son 50 Gün)")
        grafik_data = pd.DataFrame({
            "Bakır": bakir_liste,
            "Alüminyum": alu_liste
        })
        st.line_chart(grafik_data)

    time.sleep(guncelleme)