import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alüminyum Profesyonel Terminal", layout="wide")

# 2. Başlık
st.markdown("<h2 style='text-align: center;'>📊 Alüminyum Canlı Takip & Alarm</h2>", unsafe_allow_html=True)

# 3. Ayarlar (Sidebar'da sadece yenileme kalsın)
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

# 5. Ana Giriş Alanı (Miktar ve Hedef Yan Yana)
st.divider()
col_inp1, col_inp2 = st.columns(2)

with col_inp1:
    miktar = st.number_input("Eldeki Miktar (Ton)", min_value=0.0, value=1.0, step=0.1)

with col_inp2:
    hedef_fiyat = st.number_input("Satış Hedef Fiyatı (USD)", min_value=0.0, value=2600.0, step=10.0)

# 6. GÖRSEL ALARM (Hedef Kontrolü)
if alu_fiyat >= hedef_fiyat and hedef_fiyat > 0:
    st.balloons()
    st.markdown(f"""
        <div style="background-color:#155724; border: 2px solid #d4edda; padding:20px; border-radius:10px; text-align:center; margin-bottom:20px;">
            <h1 style="color:#d4edda; margin:0;">🚀 HEDEF GÖRÜLDÜ!</h1>
            <p style="color:#d4edda; font-size:22px; margin:10px 0;">Güncel: {alu_fiyat}$ | Hedefin: {hedef_fiyat}$</p>
            <strong style="color:white; font-size:25px;">SATIŞ İÇİN UYGUN SEVİYE!</strong>
        </div>
    """, unsafe_allow_html=True)
else:
    kalan = round(hedef_fiyat - alu_fiyat, 2)
    st.info(f"🎯 Hedefe Kalan: **{kalan}$** | Mevcut Fiyatın Hedefe Oranı: **%{(alu_fiyat/hedef_fiyat)*100:.1f}**")

# 7. Canlı Göstergeler (Metrikler)
st.write("---")
m1, m2, m3 = st.columns(3)
m1.metric("LME Alüminyum", f"{alu_fiyat}$", f"{alu_fark}")
m2.metric("Dolar / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")
m3.metric("Toplam Değer (TL)", f"{round(miktar * alu_fiyat * dolar_fiyat, 2):,} ₺")

# 8. Kâr / Zarar Genişletici
with st.expander("📉 Kâr/Zarar Hesaplama Detayları"):
    c_a, c_b = st.columns(2)
    alis_fiyati = c_a.number_input("Alış Fiyatın (USD)", value=2200.0)
    alis_kuru = c_b.number_input("Alış Kurun (₺)", value=dolar_fiyat)
    fark_tl = (miktar * alu_fiyat * dolar_fiyat) - (miktar * alis_fiyati * alis_kuru)
    
    if fark_tl >= 0:
        st.success(f"💰 Toplam Kâr: {fark_tl:,.2f} ₺")
    else:
        st.error(f"🚨 Toplam Zarar: {fark_tl:,.2f} ₺")

# 9. Grafik
st.subheader("📈 Fiyat Trendi (Son 5 Gün)")
st.line_chart(alu_liste)

# 10. Otomatik Yenileme
time.sleep(guncelleme_hizi)
st.rerun()
