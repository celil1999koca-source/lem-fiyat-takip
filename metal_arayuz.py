import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alüminyum 1 Yıllık Analiz", layout="wide")

# 2. Başlık
st.markdown("<h2 style='text-align: center;'>📊 Alüminyum Yıllık Analiz Paneli</h2>", unsafe_allow_html=True)

# 3. Ayarlar (Sidebar)
guncelleme_hizi = st.sidebar.slider("Güncelleme Hızı (Saniye)", 30, 300, 60)

# 4. Veri Çekme Fonksiyonu (1 Yıllık Veri Aktif)
@st.cache_data(ttl=guncelleme_hizi)
def veri_cek(sembol):
    try:
        ticker = yf.Ticker(sembol)
        # Veri periyodu 1 yıla çıkarıldı
        df = ticker.history(period="1y") 
        if df.empty: return 0.0, 0.0, pd.Series()
        guncel = round(df['Close'].iloc[-1], 2)
        # Değişim hala son iş gününe göre hesaplanıyor
        degisim = round(guncel - df['Close'].iloc[-2], 2)
        return guncel, degisim, df['Close']
    except:
        return 0.0, 0.0, pd.Series()

alu_fiyat, alu_fark, alu_liste = veri_cek('ALI=F')
dolar_fiyat, dolar_fark, _ = veri_cek('USDTRY=X')

# 5. Miktar Giriş Alanı
st.divider()
miktar = st.number_input("Eldeki Miktar (Ton)", min_value=0.0, value=1.0, step=0.1)

# 6. Hesaplama ve Değer Tablosu
st.subheader("🧮 Güncel Değer Hesaplamaları")
toplam_usd = miktar * alu_fiyat
toplam_tl = toplam_usd * dolar_fiyat

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"**1 Ton Fiyatı:** \n\n💵 {alu_fiyat:,} $  \n\n₺ {round(alu_fiyat * dolar_fiyat, 2):,} ₺")
with c2:
    st.markdown(f"**Toplam Tutar (USD):** \n### {toplam_usd:,.2f} $")
with c3:
    st.markdown(f"**Toplam Tutar (TL):** \n### {toplam_tl:,.2f} ₺")

# 7. Canlı Gösterge Kartları
st.write("---")
m1, m2, m3 = st.columns(3)
m1.metric("LME Alüminyum", f"{alu_fiyat}$", f"{alu_fark}")
m2.metric("Dolar / TRY", f"{dolar_fiyat} ₺", f"{dolar_fark}")
m3.metric("Yıllık Seyir", "Analiz Modu")

# 8. Kâr / Zarar Analizi
with st.expander("📉 Kâr/Zarar Detaylarını Gör"):
    ca, cb = st.columns(2)
    alis_fiyati = ca.number_input("Alış Fiyatın (USD)", value=2200.0)
    alis_kuru = cb.number_input("Alış Kurun (₺)", value=dolar_fiyat)
    fark_tl = (miktar * alu_fiyat * dolar_fiyat) - (miktar * alis_fiyati * alis_kuru)
    
    if fark_tl >= 0:
        st.success(f"💰 Toplam Kâr: {fark_tl:,.2f} ₺")
    else:
        st.error(f"🚨 Toplam Zarar: {fark_tl:,.2f} ₺")

# 9. Grafik (1 Yıllık Görünüm)
st.subheader("📈 1 Yıllık Fiyat Grafiği")
if not alu_liste.empty:
    # Grafiği daha detaylı görmek için line_chart kullanıyoruz
    st.line_chart(alu_liste)
else:
    st.error("Veri çekilemedi, lütfen internet bağlantınızı kontrol edin.")

# 10. Otomatik Yenileme
time.sleep(guncelleme_hizi)
st.rerun()
