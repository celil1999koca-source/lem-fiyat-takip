import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alüminyum Alarm Terminali", layout="wide")

# 2. Başlık ve Stil
st.markdown("<h2 style='text-align: center;'>🔔 Alüminyum Alarm & Takip Sistemi</h2>", unsafe_allow_html=True)

# 3. Ayarlar (Sidebar)
st.sidebar.header("⚙️ Ayarlar")
guncelleme_hizi = st.sidebar.slider("Güncelleme Hızı (Saniye)", 30, 300, 60)
hedef_fiyat = st.sidebar.number_input("Hedef Satış Fiyatı (USD)", min_value=0.0, value=2600.0, step=10.0)

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

# 5. GÖRSEL UYARI SİSTEMİ (Yeni Özellik)
if alu_fiyat >= hedef_fiyat:
    st.balloons() # Ekranda balonlar uçar
    st.error(f"🚀 HEDEFE ULAŞILDI! Güncel Fiyat: {alu_fiyat}$ | Hedefin: {hedef_fiyat}$")
    st.markdown(f"""
        <div style="background-color:#ff4b4b; padding:20px; border-radius:10px; text-align:center;">
            <h1 style="color:white;">⚠️ SATIŞ ZAMANI GELDİ! ⚠️</h1>
            <p style="color:white; font-size:20px;">Alüminyum fiyatı hedeflediğin {hedef_fiyat}$ seviyesini geçti.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning(f"🎯 Hedef Bekleniyor... (Kalan: {round(hedef_fiyat - alu_fiyat, 2)}$)")

st.write("---")

# 6. Canlı Göstergeler
col1, col2, col3 = st.columns(3)
col1.metric("LME Alüminyum (USD)", f"{alu_fiyat}$", f"{alu_fark}")
col2.metric("Dolar / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")
col3.write(f"⏱️ Son Senkronizasyon: {time.strftime('%H:%M:%S')}")

# 7. Miktar ve Hesaplama
st.divider()
st.subheader("🧮 Hesaplama ve Maliyet")
miktar = st.number_input("Toplam Alüminyum (Ton)", min_value=0.0, value=1.0, step=0.1)

hizli_usd = miktar * alu_fiyat
hizli_tl = hizli_usd * dolar_fiyat

c1, c2 = st.columns(2)
c1.info(f"💰 Mevcut Dolar Değeri: **{hizli_usd:,.2f} $**")
c2.info(f"₺ Mevcut TL Değeri: **{hizli_tl:,.2f} ₺**")

# 8. Kâr / Zarar Genişletici
with st.expander("📉 Kâr/Zarar Analizini Düzenle"):
    alis_fiyati = st.number_input("Alış Fiyatın (USD/Ton)", value=2200.0)
    alis_kuru = st.number_input("Alış Dolar Kuru (₺)", value=dolar_fiyat)
    fark_tl = (miktar * alu_fiyat * dolar_fiyat) - (miktar * alis_fiyati * alis_kuru)
    
    if fark_tl >= 0:
        st.success(f"✅ Toplam Kârınız: {fark_tl:,.2f} ₺")
    else:
        st.error(f"🚨 Toplam Zararınız: {fark_tl:,.2f} ₺")

# 9. Grafik
st.subheader("📈 5 Günlük Trend")
