import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alüminyum Ticari Terminal", layout="wide")

# 2. Mobil Uyumlu Başlık
st.markdown("<h2 style='text-align: center;'>📈 Alüminyum Kâr/Zarar Takibi</h2>", unsafe_allow_html=True)

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

# 6. Üst Metrik Kartları
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Alüminyum (LME/USD)", f"{alu_fiyat}$", f"{alu_fark}")
with col2:
    st.metric("Dolar / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")
with col3:
    st.write(f"⏱️ Son Güncelleme:  \n{time.strftime('%H:%M:%S')}")

# 7. Kâr / Zarar Analiz Alanı
st.divider()
st.subheader("📊 Ticari Senaryo Analizi")

c1, c2, c3 = st.columns(3)

with c1:
    miktar = st.number_input("Eldeki Miktar (Ton)", min_value=0.0, value=1.0, step=0.1)
with c2:
    alis_fiyati = st.number_input("Alış Fiyatın (USD/Ton)", min_value=0.0, value=2200.0, step=10.0)
with c3:
    alis_kuru = st.number_input("Alırkenki Dolar Kuru (₺)", min_value=0.0, value=dolar_fiyat, step=0.1)

# Hesaplamalar
toplam_maliyet_usd = miktar * alis_fiyati
toplam_maliyet_tl = miktar * alis_fiyati * alis_kuru

guncel_deger_usd = miktar * alu_fiyat
guncel_deger_tl = guncel_deger_usd * dolar_fiyat

kar_zarar_usd = guncel_deger_usd - toplam_maliyet_usd
kar_zarar_tl = guncel_deger_tl - toplam_maliyet_tl

# Sonuçları Göster
st.write("---")
res1, res2 = st.columns(2)

with res1:
    if kar_zarar_usd >= 0:
        st.success(f"💰 **USD Bazında Kâr:** \n{kar_zarar_usd:,.2f} $")
    else:
        st.error(f"📉 **USD Bazında Zarar:** \n{kar_zarar_usd:,.2f} $")

with res2:
    if kar_zarar_tl >= 0:
        st.success(f"🇹🇷 **TL Bazında Kâr:** \n{kar_zarar_tl:,.2f} ₺")
    else:
        st.error(f"📉 **TL Bazında Zarar:** \n{kar_zarar_tl:,.2f} ₺")

# 8. Grafik Alanı
st.divider()
st.subheader("📈 Fiyat Trendi")
if not alu_liste.empty:
    st.line_chart(alu_liste)
