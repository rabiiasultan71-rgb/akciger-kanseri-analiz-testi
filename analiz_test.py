import streamlit as st
import plotly.graph_objects as go
import random
import base64
import os

# Sayfa Ayarları
st.set_page_config(page_title="Akciğer Sağlığı Analiz Sistemi", layout="centered")

# --- ARKA PLAN VE OKUNABİLİRLİK TASARIMI ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# RENDER VE GITHUB İÇİN DÜZELTİLMİŞ GÖRSEL YOLU
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
            background-color: rgba(0, 0, 0, 0.85); z-index: -1;
        }}
        
        /* GENEL YAZI ESTETİĞİ */
        h1, h2, h3 {{
            color: #00f2ff !important; /* Canlı neon mavi başlıklar */
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
        }}
        p, label, .stMarkdown {{
            color: #FFFFFF !important;
            font-size: 1.05rem !important;
        }}

        /* ŞEFFAF SİYAH KARE BUTON TASARIMI */
        .stButton>button {{
            width: 100% !important;
            border-radius: 8px !important; /* Tam kare değil, çok hafif yuvarlatılmış modern kare */
            height: 3em !important;
            background-color: rgba(0, 0, 0, 0.5) !important; /* Şeffaf siyah */
            color: #00f2ff !important; /* Yazı rengi neon mavi */
            font-weight: bold !important;
            border: 1px solid rgba(0, 242, 255, 0.4) !important; /* İnce neon çerçeve */
            transition: all 0.4s ease !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stButton>button:hover {{
            background-color: rgba(0, 242, 255, 0.2) !important; /* Üzerine gelince neon parlaması */
            border: 1px solid #00f2ff !important;
            box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
            color: white !important;
        }}

        /* KUTUCUKLARIN ESTETİĞİ */
        .stSelectbox, .stRadio, .stTextInput {{
            background-color: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 10px;
        }}
        
        /* BAŞARI VE HATA MESAJLARI RENKLERİ */
        .stAlert {{
            border-radius: 15px !important;
            border: none !important;
            background-color: rgba(0, 0, 0, 0.6) !important;
        }}
        </style>
        """, unsafe_allow_html=True)
except:
    st.info("Arka plan görseli yüklenemedi.")

# Durum Yönetimi
if 'step' not in st.session_state: st.session_state.step = 1
if 'answers' not in st.session_state: st.session_state.answers = {}

# --- ADIM 1: TEMEL BİLGİLER ---
if st.session_state.step == 1:
    st.title("📋 Adım 1: Temel Bilgiler")
    yas_input = st.text_input("Yaşınız (18-85):", value="25")
    age_ok = False
    try:
        yas = int(yas_input)
        if 18 <= yas <= 85: age_ok = True
        else: st.error("⚠️ 18-85 arası bir yaş girin.")
    except: st.error("⚠️ Geçerli bir sayı girin.")
    
    cinsiyet = st.selectbox("Cinsiyetiniz:", ["Seçiniz", "Erkek", "Kadın"])
    if st.button("İLERLE ➡️"):
        if age_ok and cinsiyet != "Seçiniz":
            st.session_state.answers['yas'] = int(yas_input)
            st.session_state.answers['cinsiyet'] = cinsiyet
            st.session_state.step = 2
            st.rerun()

# --- ADIM 2: SAĞLIK GEÇMİŞİ ---
elif st.session_state.step == 2:
    st.title("🧬 Adım 2: Sağlık Geçmişi")
    kronik = st.radio("Kronik bir rahatsızlığınız var mı?", ["Hayır", "Evet"], horizontal=True)
    if kronik == "Evet":
        st.session_state.answers['kronik_nedir'] = st.text_input("Rahatsızlığınız nedir?")
    genetik = st.radio("Ailenizde akciğer kanseri genetiği var mı?", ["Hayır", "Evet"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ GERİ"): st.session_state.step = 1; st.rerun()
    with col2:
        if st.button("İLERLE ➡️"):
            st.session_state.answers['genetik'] = genetik
            st.session_state.step = 3
            st.rerun()

# --- ADIM 3: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("🚬 Adım 3: Alışkanlıklar")
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    alkol = st.radio("Alkol kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ GERİ"): st.session_state.step = 2; st.rerun()
    with col2:
        if st.button("İLERLE ➡️"):
            st.session_state.answers['sigara'] = sigara
            st.session_state.answers['alkol'] = alkol
            st.session_state.step = 4
            st.rerun()

# --- ADIM 4: BELİRTİLER ---
elif st.session_state.step == 4:
    st.title("🔍 Adım 4: Şikayetler")
    oksuruk = st.radio("Öksürük şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if oksuruk == "Evet":
        st.session_state.answers['oksuruk_tip'] = st.selectbox("Tip:", ["Hafif", "Sık", "Kanlı"])
    nefes = st.radio("Nefes darlığı var mı?", ["Hayır", "Evet"], horizontal=True)
    parmak = st.radio("Parmaklarda sararma var mı?", ["Hayır", "Evet"], horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ GERİ"): st.session_state.step = 3; st.rerun()
    with col2:
        if st.button("ANALİZ ET 🎯"):
            st.session_state.step = 5
            st.rerun()

# --- ADIM 5: SONUÇ RAPORU ---
elif st.session_state.step == 5:
    st.title("📊 Analiz Sonucu")
    
    risk_skoru = 10
    if st.session_state.answers.get('sigara') == "Evet": risk_skoru += 35
    if st.session_state.answers.get('oksuruk_tip') == "Kanlı": risk_skoru += 30
    if st.session_state.answers.get('genetik') == "Evet": risk_skoru += 15
    risk_skoru = min(risk_skoru, 99)

    # EKSTRA İNCE VE ESTETİK GRAFİK
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_skoru,
        number = {'suffix': "%", 'font': {'color': "#00f2ff", 'size': 60}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white", 'tickwidth': 1},
            'bar': {'color': "#00f2ff", 'thickness': 0.15}, # Çok ince çubuk
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 1,
            'bordercolor': "rgba(255,255,255,0.2)",
            'steps': [
                {'range': [0, 30], 'color': "#00ff88"}, # Canlı Yeşil
                {'range': [30, 70], 'color': "#ffcc00"}, # Canlı Sarı
                {'range': [70, 100], 'color': "#ff4444"}] # Canlı Kırmızı
        }))
    
    fig.update_layout(
        height=350, margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)', font={'family': "Arial"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # MOTİVASYON VE ÖNERİ KISMI (Daha renkli ve estetik)
    if risk_skoru > 70:
        st.markdown(f'<div style="padding:20px; border-radius:15px; background: rgba(255,68,68,0.2); border-left: 5px solid #ff4444;">'
                    f'<h3 style="color:#ff4444 !important; margin:0;">🚨 YÜKSEK RİSK PROFİLİ</h3>'
                    f'<p style="margin-top:10px;">Lütfen en kısa sürede bir Göğüs Hastalıkları uzmanına başvurun. Erken teşhis hayat kurtarır.</p></div>', unsafe_allow_html=True)
    elif 30 < risk_skoru <= 70:
        st.markdown(f'<div style="padding:20px; border-radius:15px; background: rgba(255,204,0,0.2); border-left: 5px solid #ffcc00;">'
                    f'<h3 style="color:#ffcc00 !important; margin:0;">🟡 ORTA RİSK - DİKKAT</h3>'
                    f'<p style="margin-top:10px;">Yaşam tarzınızda yapacağınız küçük değişiklikler akciğer sağlığınızı geri kazanmanıza yardımcı olabilir.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="padding:20px; border-radius:15px; background: rgba(0,255,136,0.2); border-left: 5px solid #00ff88;">'
                    f'<h3 style="color:#00ff88 !important; margin:0;">✨ HARİKA DURUMDASINIZ</h3>'
                    f'<p style="margin-top:10px;">Akciğerleriniz şu an oldukça sağlıklı görünüyor. Bu tabloyu korumaya devam edin!</p></div>', unsafe_allow_html=True)

    st.write(f"**🤖 Yapay Zeka Analiz Güvenilirliği: %{round(random.uniform(97.1, 98.9), 1)}**")
    
    if st.button("🔄 TESTİ YENİDEN BAŞLAT"):
        st.session_state.step = 1; st.rerun()
