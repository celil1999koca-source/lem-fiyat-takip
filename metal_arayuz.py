import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alüminyum Profesyonel Terminal", layout="wide")

# 2. Başlık
st.markdown("<h2 style='text-align: center;'>💼 Alüminyum Ticari Takip Merkezi</h2>", unsafe_allow_html=True)

# 3. Ayarlar
guncelleme_hizi = st.sidebar.slider("Güncelleme Hızı (Saniye)", 30, 300, 60)

# 4. Veri Çekme
@st.cache_data(ttl=guncelleme_hizi)
def veri_cek(sembol):
    try:
        ticker = yf.Ticker(sembol)
        df = ticker.history(period="5d")
        if df.empty: return 0.0, 0.0, pd.Series()
        guncel = round(df['Close'].iloc[-1], 2)
        degisim = round(guncel - df['Close'].iloc[-2], 2)
        return guncel, degisim, df['Close']
    except:
        return 0.0, 0.0, pd.Series()

alu_fiyat, alu_fark, alu_liste = veri_cek('ALI=F')
dolar_fiyat, dolar_fark, _ = veri_cek('USDTRY=X')

# 5. Canlı Göstergeler
col1, col2, col3 = st.columns(3)
col1.metric("LME Alüminyum (USD)", f"{alu_fiyat}$", f"{alu_fark}")
col2.metric("Dolar / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")
col3.write(f"⏱️ Güncelleme: {time.strftime('%H:%M:%S')}")

st.divider()

# 6. Miktar Girişi ve Hızlı Hesaplama (İstediğin Kutu)
st.subheader("🧮 Miktar ve Değer Hesaplama")
miktar = st.number_input("Toplam Alüminyum Miktarı (Ton)", min_value=0.0, value=1.0, step=0.1)

hizli_usd = miktar * alu_fiyat
hizli_tl = hizli_usd * dolar_fiyat

c1, c2 = st.columns(2)
c1.info(f"💰 **Mevcut Dolar Değeri:** {hizli_usd:,.2f} $")
c2.info(f"₺ **Mevcut TL Değeri:** {hizli_tl:,.2f} ₺")

st.divider()

# 7. Kâr / Zarar Analizi (Ekstra Detaylar)
with st.expander("📉 Kâr/Zarar Detaylarını Gör/Düzenle"):
    st.write("Maliyetlerinizi girerek kâr durumunuzu görün:")
    ca, cb = st.columns(2)
    alis_fiyati = ca.number_input("Alış Fiyatın (USD/Ton)", min_value=0.0, value=2200.0)
    alis_kuru = cb.number_input("Alış Dolar Kuru (₺)", min_value=0.0, value=dolar_fiyat)

    maliyet_tl = miktar * alis_fiyati * alis_kuru
    guncel_tl = miktar * alu_fiyat * dolar_fiyat
    fark_tl = guncel_tl - maliyet_tl
    
    if fark_tl >= 0:
        st.success(f"✅ Toplam Kârınız: {fark_tl:,.2f} ₺")
    else:
        st.error(f"🚨 Toplam Zararınız: {fark_tl:,.2f} ₺")

# 8. Grafik
st.subheader("📈 5 Günlük Fiyat Seyri")
st.line_chart(alu_liste)

# 9. Yenileme
time.sleep(guncelleme_hizi)
st.rerun()
