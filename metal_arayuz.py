import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alüminyum Ticari Terminal", layout="wide")

# 2. Başlık
st.markdown("<h2 style='text-align: center;'>💼 Alüminyum Profesyonel Takip Sistemi</h2>", unsafe_allow_html=True)

# 3. Ayarlar (Sidebar)
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





# 7. HESAPLAMA VE DEĞER TABLOSU (İstediğin Kısım)
st.write("---")
st.subheader("🧮 Güncel Değer Hesaplamaları")

# Hesaplamalar
toplam_usd = miktar * alu_fiyat
toplam_tl = toplam_usd * dolar_fiyat

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"**1 Ton Fiyatı:** \n💵 {alu_fiyat:,} $  \n₺ {round(alu_fiyat * dolar_fiyat, 2):,} ₺")
with c2:
    st.markdown(f"**Toplam Tutar (USD):** \n### {toplam_usd:,.2f} $")
with c3:
    st.markdown(f"**Toplam Tutar (TL):** \n### {toplam_tl:,.2f} ₺")

# 8. Canlı Göstergeler (Metrikler)
st.write("---")
m1, m2, m3 = st.columns(3)
m1.metric("LME Alüminyum", f"{alu_fiyat}$", f"{alu_fark}")
m2.metric("Dolar / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")
m3.metric("Günlük Değişim", f"{alu_fark}$", delta_color="normal")

# 9. Kâr / Zarar Genişletici
with st.expander("📉 Kâr/Zarar Hesaplama Detayları"):
    ca, cb = st.columns(2)
    alis_fiyati = ca.number_input("Alış Fiyatın (USD)", value=2200.0)
    alis_kuru = cb.number_input("Alış Kurun (₺)", value=dolar_fiyat)
    fark_tl = (miktar * alu_fiyat * dolar_fiyat) - (miktar * alis_fiyati * alis_kuru)
    
    if fark_tl >= 0:
        st.success(f"💰 Toplam Kâr: {fark_tl:,.2f} ₺")
    else:
        st.error(f"🚨 Toplam Zarar: {fark_tl:,.2f} ₺")

# 10. Grafik
st.subheader("📈 Fiyat Trendi (Son 5 Gün)")
st.line_chart(alu_liste)

# 11. Otomatik Yenileme
time.sleep(guncelleme_hizi)
st.rerun()
