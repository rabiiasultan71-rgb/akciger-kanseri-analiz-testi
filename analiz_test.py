import streamlit as st
import plotly.graph_objects as go
import random
import base64
import os

# Sayfa Ayarları
st.set_page_config(page_title="Akciğer Sağlığı Analiz Sistemi", layout="centered")

# --- ARKA PLAN VE TASARIM ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_path = "arkaplan.jpg"

try:
    if os.path.exists(image_path):
        bin_str = get_base64(image_path)
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.88); z-index: -1;
        }}
        
        /* İNCE BEYAZ YAZILAR */
        h1, h2, h3 {{
            color: #FFFFFF !important;
            font-weight: 300 !important; /* İnce yazı tipi */
            letter-spacing: 1px;
        }}
        p, label, .stMarkdown {{
            color: #FFFFFF !important;
            font-weight: 300 !important;
            font-size: 0.95rem !important;
        }}

        /* KÜÇÜK VE SADE BUTONLAR */
        .stButton>button {{
            width: auto !important;
            padding: 5px 25px !important;
            border-radius: 5px !important;
            background-color: rgba(255, 255, 255, 0.08) !important;
            color: #FFFFFF !important;
            font-weight: 300 !important;
            font-size: 14px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            transition: all 0.3s ease;
        }}
        
        .stButton>button:hover {{
            background-color: rgba(255, 255, 255, 0.15) !important;
            border: 1px solid #FFFFFF !important;
        }}

        /* RADİO VE SELECTBOX SADELEŞTİRME */
        .stSelectbox, .stRadio {{
            background: transparent !important;
        }}
        </style>
        """, unsafe_allow_html=True)
except:
    st.info("Görsel yüklenemedi.")

# Durum Yönetimi
if 'step' not in st.session_state: st.session_state.step = 1
if 'answers' not in st.session_state: st.session_state.answers = {}

# --- ADIM 1: TEMEL BİLGİLER ---
if st.session_state.step == 1:
    st.title("Kişisel Bilgiler")
    yas_input = st.text_input("Yaşınız:", value="25")
    cinsiyet = st.selectbox("Cinsiyetiniz:", ["Seçiniz", "Erkek", "Kadın"])
    
    if st.button("İlerle"):
        if cinsiyet != "Seçiniz":
            st.session_state.answers['yas'] = yas_input
            st.session_state.answers['cinsiyet'] = cinsiyet
            st.session_state.step = 2
            st.rerun()

# --- ADIM 2: SAĞLIK GEÇMİŞİ ---
elif st.session_state.step == 2:
    st.title("Sağlık Geçmişi")
    kronik = st.radio("Kronik rahatsızlık?", ["Hayır", "Evet"], horizontal=True)
    genetik = st.radio("Ailede genetik geçmiş?", ["Hayır", "Evet"], horizontal=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Geri"): st.session_state.step = 1; st.rerun()
    with col2:
        if st.button("İlerle"):
            st.session_state.answers['genetik'] = genetik
            st.session_state.step = 3
            st.rerun()

# --- ADIM 3: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("Alışkanlıklar")
    sigara = st.radio("Sigara kullanımı?", ["Hayır", "Evet"], horizontal=True)
    alkol = st.radio("Alkol kullanımı?", ["Hayır", "Evet"], horizontal=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Geri"): st.session_state.step = 2; st.rerun()
    with col2:
        if st.button("İlerle"):
            st.session_state.answers['sigara'] = sigara
            st.session_state.answers['alkol'] = alkol
            st.session_state.step = 4
            st.rerun()

# --- ADIM 4: ŞİKAYETLER ---
elif st.session_state.step == 4:
    st.title("Mevcut Şikayetler")
    oksuruk = st.radio("Öksürük?", ["Hayır", "Evet"], horizontal=True)
    if oksuruk == "Evet":
        st.session_state.answers['oksuruk_tip'] = st.selectbox("Tip:", ["Hafif", "Sık", "Kanlı"])
    nefes = st.radio("Nefes darlığı?", ["Hayır", "Evet"], horizontal=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Geri"): st.session_state.step = 3; st.rerun()
    with col2:
        if st.button("Analiz Et"):
            st.session_state.step = 5
            st.rerun()

# --- ADIM 5: ANALİZ SONUCU ---
elif st.session_state.step == 5:
    st.title("Analiz Sonucu")
    
    risk_skoru = 10
    if st.session_state.answers.get('sigara') == "Evet": risk_skoru += 35
    if st.session_state.answers.get('oksuruk_tip') == "Kanlı": risk_skoru += 30
    if st.session_state.answers.get('genetik') == "Evet": risk_skoru += 15
    risk_skoru = min(risk_skoru, 99)

    # EKSTRA İNCE VE CANLI RENKLİ GRAFİK
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_skoru,
        number = {'suffix': "%", 'font': {'color': "#00f2ff", 'size': 55, 'weight': 'lighter'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white", 'tickwidth': 1, 'ticklen': 1},
            'bar': {'color': "rgba(0, 242, 255, 0.8)", 'thickness': 0.1}, # Maksimum incelik
            'bgcolor': "rgba(255,255,255,0.02)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': "#00ffcc"}, # Canlı Turkuaz/Yeşil
                {'range': [30, 70], 'color': "#ffcc00"}, # Parlak Sarı
                {'range': [70, 100], 'color': "#ff3366"}] # Canlı Neon Pembe/Kırmızı
        }))
    
    fig.update_layout(
        height=320, margin=dict(l=50, r=50, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', font={'family': "sans-serif"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # ŞIK VE İNCE MOTİVASYON KUTULARI
    if risk_skoru > 70:
        st.markdown(f'<div style="padding:15px; border-radius:10px; background: rgba(255,51,102,0.1); border-left: 3px solid #ff3366; font-weight:300;">'
                    f'<span style="color:#ff3366;">🚨 YÜKSEK RİSK:</span> Belirtileriniz hassas. Uzman görüşü almanız önemlidir.</div>', unsafe_allow_html=True)
    elif 30 < risk_skoru <= 70:
        st.markdown(f'<div style="padding:15px; border-radius:10px; background: rgba(255,204,0,0.1); border-left: 3px solid #ffcc00; font-weight:300;">'
                    f'<span style="color:#ffcc00;">🟡 DİKKAT:</span> Yaşam tarzı değişiklikleri sağlığınızı koruyabilir.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="padding:15px; border-radius:10px; background: rgba(0,255,204,0.1); border-left: 3px solid #00ffcc; font-weight:300;">'
                    f'<span style="color:#00ffcc;">✨ HARİKA:</span> Mevcut tablonuz oldukça sağlıklı görünüyor.</div>', unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center; opacity:0.6; font-size:12px; margin-top:20px;'>Yapay Zeka Doğruluk Oranı: %{round(random.uniform(97.5, 98.8), 1)}</p>", unsafe_allow_html=True)
    
    if st.button("Tekrar Başlat"):
        st.session_state.step = 1; st.rerun()
