import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Uygulama Ayarları
st.set_page_config(page_title="LGS Profesyonel Koçluk", layout="wide")

# Veritabanı Dosyası (CSV)
DB_FILE = "lgs_veritabani.csv"

# Veri Yükleme Fonksiyonu
def veri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["Tarih", "Ogrenci", "Deneme", "Ders", "Konu", "Doğru", "Yanlış", "Net"])

# 1. ÖĞRENCİ LİSTESİ VE YÖNETİMİ
if 'ogrenci_listesi' not in st.session_state:
    st.session_state['ogrenci_listesi'] = [
        "NBA8", "ÇNY8", "ÇBA8", "ÇAA8", "30BB8", "NZEY8", 
        "ÇYSD7", "ÇERE7", "NEBŞ6", "NEB6", "ÇYK5", "ÇEEÇ5"
    ]

with st.sidebar:
    st.title("👥 Koçluk Paneli")
    secilen_ogrenci = st.selectbox("Öğrenci Seçiniz", st.session_state['ogrenci_listesi'])
    
    st.divider()
    st.subheader("➕ Yeni Öğrenci Tanımla")
    yeni_isim = st.text_input("Öğrenci Kodu/Adı")
    if st.button("Sisteme Ekle"):
        if yeni_isim and yeni_isim not in st.session_state['ogrenci_listesi']:
            st.session_state['ogrenci_listesi'].append(yeni_isim)
            st.success(f"{yeni_isim} eklendi!")
            st.rerun()

# --- ANA EKRAN ---
st.title(f"📊 {secilen_ogrenci} - Başarı Analiz Üssü")

tab1, tab2, tab3 = st.tabs(["📝 Veri Girişi", "📈 Gelişim İzleme", "🖼️ Soru Kumbarası"])

# --- TAB 1: ÖĞRENCİ VERİ GİRİŞİ ---
with tab1:
    with st.form("veri_giris_formu"):
        col1, col2 = st.columns(2)
        with col1:
            deneme = st.text_input("Deneme Adı / Yayın", placeholder="Örn: Bilfen-1")
            ders = st.selectbox("Ders", ["Matematik", "Fen Bilimleri", "Türkçe", "Sosyal", "Din", "İngilizce"])
            konu = st.text_input("Hatalı Konu")
        with col2:
            d = st.number_input("Doğru", 0, 20, 15)
            y = st.number_input("Yanlış", 0, 20, 0)
            tarih = st.date_input("Deneme Tarihi", datetime.now())
        
        kaydet = st.form_submit_button("Analiz Et ve Veritabanına Yaz")
        
        if kaydet:
            net = d - (y * 0.33)
            df = veri_yukle()
            yeni_veri = pd.DataFrame([[tarih, secilen_ogrenci, deneme, ders, konu, d, y, net]], columns=df.columns)
            df = pd.concat([df, yeni_veri], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.balloons()
            st.success(f"Tebrikler {secilen_ogrenci}! Verilerin başarıyla arşive eklendi.")

# --- TAB 2: KOÇ ANALİZ EKRANI ---
with tab2:
    df = veri_yukle()
    # Filtreleme
    ogrenci_df = df[df["Ogrenci"] == secilen_ogrenci]
    
    if not ogrenci_df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Genel Net Ortalaması", f"{ogrenci_df['Net'].mean():.2f}")
        c2.metric("Son Deneme Neti", f"{ogrenci_df['Net'].iloc[-1]:.2f}")
        c3.metric("Toplam Girilen Kayıt", len(ogrenci_df))

        st.divider()
        st.subheader("📈 Net Değişim Grafiği")
        st.line_chart(ogrenci_df.set_index("Tarih")["Net"])

        st.subheader("📋 Son Kayıtlar")
        st.dataframe(ogrenci_df.tail(5), use_container_width=True)
    else:
        st.info("Bu öğrenci için henüz veri girişi yapılmamış. İlk veriyi 'Veri Girişi' sekmesinden ekleyebilirsiniz.")

# --- TAB 3: SORU KUMBARASI ---
with tab3:
    st.subheader("📸 Kritik Soru Arşivi")
    st.write("Öğrencinin yapamadığı veya senin 'mutlaka tekrar etmelisin' dediğin soruları buraya ekleyin.")
    uploaded_file = st.file_uploader("Soru Fotoğrafı (Kamerayı açmak için dokunun)", type=['jpg', 'png', 'jpeg'])
    if uploaded_file:
        st.image(uploaded_file, caption=f"{secilen_ogrenci} - Hatalı Soru Notu", use_container_width=True)
