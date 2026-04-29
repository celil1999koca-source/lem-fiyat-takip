# Başlık kısmını mobil için daha kompakt yapalım
st.markdown("<h2 style='text-align: center;'>📱 Metal Takip Mobil</h2>", unsafe_allow_html=True)

# Metrikleri mobil ekranda alt alta gelmesi için 2'li sütunlara bölelim
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.metric("Bakır", f"{bakir_fiyat}$", f"{bakir_fark}")
with col2:
    st.metric("Alüminyum", f"{alu_fiyat}$", f"{alu_fark}")
with col3:
    st.metric("Dolar/TL", f"{dolar_fiyat}₺", f"{dolar_fark}")
with col4:
    # Mobil için daha küçük bir saat gösterimi
    st.caption(f"Güncelleme: {time.strftime('%H:%M')}")
