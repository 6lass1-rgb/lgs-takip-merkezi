import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Uygulama Ayarları
st.set_page_config(page_title="LGS Profesyonel Koçluk", layout="wide")

# Veritabanı Dosyası
DB_FILE = "lgs_veritabani.csv"

def veri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["Tarih", "Ogrenci", "Deneme", "Ders", "Konu", "Doğru", "Yanlış", "Net"])

# ÖĞRENCİ LİSTESİ (Session State ile yönetilir)
if 'ogrenci_listesi' not in st.session_state:
    st.session_state['ogrenci_listesi'] = [
        "NBA8", "ÇNY8", "ÇBA8", "ÇAA8", "30BB8", "NZEY8", 
        "ÇYSD7", "ÇERE7", "NEBŞ6", "NEB6", "ÇYK5", "ÇEEÇ5"
    ]

# --- YAN PANEL ---
with st.sidebar:
    st.title("👥 Koçluk Paneli")
    secilen_ogrenci = st.selectbox("Öğrenci Seçiniz", st.session_state['ogrenci_listesi'])
    st.divider()
    yeni_isim = st.text_input("Yeni Öğrenci Ekle")
    if st.button("Listeye Ekle"):
        if yeni_isim and yeni_isim not in st.session_state['ogrenci_listesi']:
            st.session_state['ogrenci_listesi'].append(yeni_isim)
            st.rerun()

# --- ANA EKRAN ---
st.title(f"📊 {secilen_ogrenci} - Takip Paneli")
tab1, tab2, tab3 = st.tabs(["📝 Veri Girişi", "📈 Gelişim", "🖼️ Hata Kumbarası"])

with tab1:
    with st.form("giris"):
        c1, c2 = st.columns(2)
        deneme = c1.text_input("Deneme Adı")
        ders = c1.selectbox("Ders", ["Matematik", "Fen", "Türkçe", "Sosyal", "Din", "İngilizce"])
        d = c2.number_input("Doğru", 0, 20, 15)
        y = c2.number_input("Yanlış", 0, 20, 0)
        tarih = st.date_input("Tarih", datetime.now())
        if st.form_submit_button("Kaydet"):
            net = d - (y * 0.33)
            df = veri_yukle()
            yeni = pd.DataFrame([[tarih, secilen_ogrenci, deneme, ders, "Konu", d, y, net]], columns=df.columns)
            pd.concat([df, yeni]).to_csv(DB_FILE, index=False)
            st.success("Kaydedildi!")

with tab2:
    df = veri_yukle()
    o_df = df[df["Ogrenci"] == secilen_ogrenci]
    if not o_df.empty:
        st.line_chart(o_df.set_index("Tarih")["Net"])
        st.dataframe(o_df)
    else: st.info("Veri yok.")

# --- ⚙️ YÖNETİCİ PANELİ (SİLME İŞLEMLERİ) ---
st.divider()
with st.expander("⚙️ Yönetici Ayarları (Silme İşlemleri)"):
    sifre = st.text_input("Yönetici Şifresi", type="password")
    if sifre == "koc123": # <--- Şifren bu!
        st.subheader("🗑️ Veri/Öğrenci Yönetimi")
        
        # Öğrenci Silme
        sil_isim = st.selectbox("Listeden Silinecek Öğrenci", st.session_state['ogrenci_listesi'])
        if st.button(f"{sil_isim} İsimli Öğrenciyi Listeden Kaldır"):
            st.session_state['ogrenci_listesi'].remove(sil_isim)
            st.error("Öğrenci silindi.")
            st.rerun()
            
        # Son Veriyi Silme
        df = veri_yukle()
        if not df.empty:
            st.divider()
            st.write("Son Girilen Kayıtlar (Yanlışsa Silin):")
            st.dataframe(df.tail(5))
            if st.button("En Son Girilen Kaydı Sil"):
                df[:-1].to_csv(DB_FILE, index=False)
                st.warning("Son kayıt silindi.")
                st.rerun()
    elif sifre != "":
        st.error("Hatalı şifre!")
