import streamlit as st
import yfinance as yf
import pandas as pd
import time
import base64 # Görseli yüklemek için gerekli

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alüminyum Profesyonel Takip", layout="wide")
# --- ARKA PLAN GÖRSELİ AYARLARI ---
# Görseli base64 formatına çeviren fonksiyon
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Arka plan görselini ve overlay'i uygulayan CSS
def set_png_as_page_bg(png_file):
    try:
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* İçeriğin okunabilirliği için hafif bir overlay (karartma) */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.4); /* Karartma oranı: 0.4 */
            z-index: -1;

        }}
        
        /* Metinleri ve kartları daha okunaklı yapmak için stil ayarı */
        .stMarkdown, .stMetric, .stDataFrame, .stTable, p, h1, h2, h3 {{
            color: white !important; /* Tüm metinleri beyaz yap */
        }}
        
        /* Kutucukların içindeki siyah yazıları beyaz yap */
        .stTextInput input, .stNumberInput input, .stSelectbox div {{
            color: black !important; /* Giriş metinleri siyah kalsın (okunabilirlik için) */
        }}
        
        /* Kartların arka planını hafif şeffaf yap */
        div[data-testid="metric-container"] {{
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ Arka plan görseli bulunamadı. Lütfen '{png_file}' dosyasının proje klasöründe olduğundan emin olun.")



# 2. Başlık
st.markdown("<h2 style='text-align: center; color: black;'>💼 Alüminyum Ticari Takip Paneli</h2>", unsafe_allow_html=True)

# 3. Ayarlar (Sidebar)
guncelleme_hizi = st.sidebar.slider("Güncelleme Hızı (Saniye)", 30, 300, 60)

# 4. Veri Çekme Fonksiyonu
@st.cache_data(ttl=guncelleme_hizi)
def veri_cek(sembol):
    try:
        ticker = yf.Ticker(sembol)
        df = ticker.history(period="1y") 
        if df.empty: return 0.0, 0.0, pd.Series()
        guncel = round(df['Close'].iloc[-1], 2)
        degisim = round(guncel - df['Close'].iloc[-2], 2)
        return guncel, degisim, df['Close']
    except:
        return 0.0, 0.0, pd.Series()

alu_fiyat, alu_fark, alu_liste = veri_cek('ALI=F')
dolar_fiyat, dolar_fark, _ = veri_cek('USDTRY=X')

# 5. Miktar Giriş Alanı
st.divider()
st.markdown("### 📥 Veri Girişi", unsafe_allow_html=True)
miktar = st.number_input("Eldeki Miktar (Ton)", min_value=0.0, value=1.0, step=0.1)

# 6. Hesaplama ve Değer Tablosu
st.write("---")
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

# 9. Grafik (Yıllık Görünüm)
st.subheader("📈 1 Yıllık Fiyat Grafiği")
if not alu_liste.empty:
    st.line_chart(alu_liste)
else:
    st.error("Veri çekilemedi.")

# 10. Otomatik Yenileme
time.sleep(guncelleme_hizi)
st.rerun()
