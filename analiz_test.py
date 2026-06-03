import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- 1. VERİTABANI AYARLARI ---
def veritabani_kur():
    conn = sqlite3.connect("akciger_analiz.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analizler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT, ad TEXT, yas INTEGER, cinsiyet TEXT, 
            genetik TEXT, kronik TEXT, sigara TEXT, alkol TEXT, 
            gogus_agrisi TEXT, g_a_detay TEXT, oksuruk TEXT, oksuruk_detay TEXT, 
            nefes_darligi TEXT, nefes_detay TEXT, yutkunma_guclugu TEXT, 
            yutkunma_detay TEXT, stres TEXT, yorgunluk TEXT, parmak TEXT, risk_skoru INTEGER
        )
    """)
    conn.commit()
    conn.close()

veritabani_kur()

def veritabanina_kaydet(d, risk):
    conn = sqlite3.connect("akciger_analiz.db")
    cursor = conn.cursor()
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO analizler (tarih, ad, yas, cinsiyet, genetik, kronik, sigara, alkol, 
        gogus_agrisi, g_a_detay, oksuruk, oksuruk_detay, nefes_darligi, nefes_detay, 
        yutkunma_guclugu, yutkunma_detay, stres, yorgunluk, parmak, risk_skoru)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (tarih, d['ad'], d['yas'], d['cinsiyet'], d['genetik'], d['kronik'], d['sigara'], d['alkol'],
          d['g_a'], d['g_a_d'], d['oksuruk'], d['oks_d'], d['nefes'], d['nef_d'], 
          d['yutkunma'], d['yut_d'], d['stres'], d['yorgunluk'], d['parmak'], risk))
    conn.commit()
    conn.close()

# --- 2. ARAYÜZ YÖNETİMİ ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = {}

# ADIM 1: TEMEL BİLGİLER
if st.session_state.step == 1:
    st.title("🩺 Adım 1: Temel Bilgiler")
    ad = st.text_input("Ad Soyad:")
    yas = st.text_input("Yaş (15-90):")
    cinsiyet = st.selectbox("Cinsiyet:", ["Erkek", "Kadın"])
    if st.button("İlerle"):
        if not ad or not yas: st.error("Lütfen tüm alanları doldurun!"); st.stop()
        if not yas.isdigit() or not (15 <= int(yas) <= 90): st.error("Yaş 15-90 arası sayı olmalı!"); st.stop()
        if any(char.isdigit() for char in ad): st.error("İsimde sayı olmaz!"); st.stop()
        st.session_state.data.update({'ad': ad, 'yas': int(yas), 'cinsiyet': cinsiyet})
        st.session_state.step = 2; st.rerun()

# ADIM 2: GEÇMİŞ
elif st.session_state.step == 2:
    st.title("🧬 Adım 2: Sağlık Geçmişi")
    genetik = st.radio("Ailede kanser var mı?", ["Hayır", "Evet"], horizontal=True)
    g_detay = st.selectbox("Derece:", ["1. Derece", "2. Derece"]) if genetik == "Evet" else "Yok"
    kronik = st.radio("Kronik hastalık var mı?", ["Hayır", "Evet"], horizontal=True)
    k_detay = st.selectbox("Tür:", ["Astım", "KOAH", "Diğer"]) if kronik == "Evet" else "Yok"
    if st.button("İlerle"):
        st.session_state.data.update({'genetik': f"{genetik} ({g_detay})", 'kronik': f"{kronik} ({k_detay})"})
        st.session_state.step = 3; st.rerun()

# ADIM 3: ALIŞKANLIKLAR
elif st.session_state.step == 3:
    st.title("🚬 Adım 3: Alışkanlıklar")
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    s_sik = st.selectbox("Sıklık:", ["Günde 1-5", "Günde yarım paket", "Günde 1+ paket"]) if sigara == "Evet" else "Yok"
    if sigara == "Evet": st.warning("⚠️ Sigara sağlığa zararlıdır, bırakmanızı öneririz.")
    alkol = st.radio("Alkol kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    a_sik = st.selectbox("Sıklık:", ["Özel günlerde", "Haftada 1-2", "Her gün"]) if alkol == "Evet" else "Yok"
    if st.button("İlerle"):
        st.session_state.data.update({'sigara': f"{sigara} ({s_sik})", 'alkol': f"{alkol} ({a_sik})"})
        st.session_state.step = 4; st.rerun()

# ADIM 4: BELİRTİLER
elif st.session_state.step == 4:
    st.title("⚠️ Adım 4: Belirtiler")
    def semptom(soru, seçenekler):
        cvp = st.radio(soru, ["Hayır", "Evet"], horizontal=True)
        detay = st.selectbox(f"{soru} Detayı:", seçenekler) if cvp == "Evet" else "Yok"
        return cvp, detay

    g_a, g_a_d = semptom("Göğüs ağrısı?", ["Batma", "Baskı", "Sürekli"])
    oksuruk, oks_d = semptom("Öksürük?", ["1-2 Hafta", "1 Ay", "3 Ay+"])
    nefes, nef_d = semptom("Nefes darlığı?", ["Hareket halinde", "İstirahat halinde"])
    yutkunma, yut_d = semptom("Yutkunma güçlüğü?", ["Katı gıdalar", "Sıvılar"])
    stres = st.radio("Stres/Anksiyete var mı?", ["Hayır", "Evet"], horizontal=True)
    yorgunluk = st.radio("Aşırı yorgunluk var mı?", ["Hayır", "Evet"], horizontal=True)
    parmak = st.radio("Parmaklarda sararma var mı?", ["Hayır", "Evet"], horizontal=True)

    if st.button("Analiz Et"):
        st.session_state.data.update({'g_a': g_a, 'g_a_d': g_a_d, 'oksuruk': oksuruk, 'oks_d': oks_d, 'nefes': nefes, 'nef_d': nef_d, 'yutkunma': yutkunma, 'yut_d': yut_d, 'stres': stres, 'yorgunluk': yorgunluk, 'parmak': parmak})
        st.session_state.step = 5; st.rerun()

# ADIM 5: ANALİZ
elif st.session_state.step == 5:
    st.title("📊 Analiz Sonucu")
    risk = 50 # Yapay zeka skorun buraya gelecek
    veritabanina_kaydet(st.session_state.data, risk)
    if risk < 35: st.success(f"Düşük Risk: %{risk}")
    elif risk < 70: st.warning(f"Orta Risk: %{risk}")
    else: st.error(f"Yüksek Risk: %{risk} - Lütfen bir uzmana danışın!")
    if st.button("Yeni Analiz"): st.session_state.clear(); st.rerun()

# --- HOCA İÇİN GİZLİ PANEL ---
with st.expander("🎓 Eğitmen Kontrol Paneli"):
    if st.button("Tüm Geçmişi Göster"):
        conn = sqlite3.connect("akciger_analiz.db")
        st.dataframe(pd.read_sql("SELECT * FROM analizler", conn))
        conn.close()
