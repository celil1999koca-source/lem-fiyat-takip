import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alüminyum & Kur Takibi", layout="wide")

# 2. Mobil Uyumlu Başlık
st.markdown("<h2 style='text-align: center;'>📱 Alüminyum & Döviz Takip</h2>", unsafe_allow_html=True)

# 3. Kontrol Paneli
st.sidebar.header("Ayarlar")
guncelleme_hizi = st.sidebar.slider("Güncelleme Hızı (Saniye)", 30, 300, 60)

# 4. Veri Çekme Fonksiyonu
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
alu_fiyat, alu_fark, alu_liste = veri_cek('ALI=F')
dolar_fiyat, dolar_fark, _ = veri_cek('USDTRY=X')

# 6. Metrik Kartları
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Alüminyum (USD)", f"{alu_fiyat}$", f"{alu_fark}")
with col2:
    st.metric("Dolar / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")
with col3:
    st.write(f"⏱️ Güncelleme:  \n{time.strftime('%H:%M:%S')}")

# 7. Hesaplama Kutusu (İstediğin Özellik)
st.divider()
st.subheader("🧮 Alüminyum Hesaplama Aracı")

# Kullanıcının miktar gireceği kutucuk
miktar = st.number_input("Kaç Ton Alüminyum?", min_value=0.0, value=1.0, step=0.1)

# Hesaplama mantığı
toplam_dolar = miktar * alu_fiyat
toplam_tl = toplam_dolar * dolar_fiyat

# Sonuç Ekranı
c1, c2 = st.columns(2)
c1.info(f"💵 Toplam Dolar: **{toplam_dolar:,.2f} $**")
c2.success(f"₺ Toplam TL: **{toplam_tl:,.2f} ₺**")

# 8. Grafik Alanı
st.divider()
st.subheader("📈 Alüminyum Fiyat Trendi (Son 5 Gün)")
if not alu_liste.empty:
    st.line_chart(alu_liste)

# 9. Otomatik Yenileme
time.sleep(guncelleme_hizi)
st.rerun()
