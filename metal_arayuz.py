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

# 5. Sadece Gerekli Verileri Çek
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

# 7. Grafik Alanı
st.divider()
st.subheader("📈 Alüminyum Fiyat Trendi (Son 5 Gün)")
if not alu_liste.empty:
    st.line_chart(alu_liste)
else:
    st.warning("Veri şu an çekilemiyor.")

# 8. TL Hesaplama
st.divider()
st.subheader("🧮 Alüminyum TL Karşılığı")
toplam_tl = round(alu_fiyat * dolar_fiyat, 2)
st.success(f"1 Ton Alüminyum şu an yaklaşık **{toplam_tl:,} ₺** ediyor.")

# 9. Otomatik Yenileme
time.sleep(guncelleme_hizi)
st.rerun()
