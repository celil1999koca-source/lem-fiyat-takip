import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="LME Canlı Takip", layout="wide")

st.title("📊 LME Metal Borsası - Canlı Takip Paneli")

# --- YENİ ÖZELLİK: Otomatik Yenileme (Yahoo Engelini Aşmak İçin) ---
# Sayfanın kaç saniyede bir kendini tazeleyeceğini belirler
guncelleme_hizi = st.sidebar.slider("Güncelleme Hızı (Saniye)", 30, 300, 60)

# Veri çekme fonksiyonunu önbelleğe alıyoruz (Sürekli internete gitmemesi için)
@st.cache_data(ttl=guncelleme_hizi)
def veri_cek(sembol):
    try:
        data = yf.Ticker(sembol)
        df = data.history(period="5d")
        güncel_fiyat = round(df['Close'].iloc[-1], 2)
        degisim = round(güncel_fiyat - df['Close'].iloc[-2], 2)
        return güncel_fiyat, degisim, df['Close']
    except:
        return 0.0, 0.0, pd.Series()

# Verileri çek
bakir_fiyat, bakir_fark, bakir_liste = veri_cek('HG=F')
alu_fiyat, alu_fark, alu_liste = veri_cek('ALI=F')

# Üst Alan (Metrikler)
col1, col2, col3 = st.columns(3)
col1.metric("Bakır (USD/lb)", f"{bakir_fiyat}", f"{bakir_fark}")
col2.metric("Alüminyum (USD/ton)", f"{alu_fiyat}", f"{alu_fark}")
col3.info(f"⏱️ Son Senkronizasyon: {time.strftime('%H:%M:%S')}")

# Orta Alan (Grafik)
st.subheader("📈 Fiyat Trendi (Son 5 Gün)")
if not bakir_liste.empty:
    grafik_data = pd.DataFrame({
        "Bakır": bakir_liste,
        "Alüminyum": alu_liste
    })
    st.line_chart(grafik_data)
else:
    st.warning("Veri şu an çekilemiyor, lütfen biraz bekleyin.")

# --- SAYFAYI OTOMATİK YENİLE ---
time.sleep(guncelleme_hizi)
st.rerun()
