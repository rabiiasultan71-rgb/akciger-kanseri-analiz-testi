import streamlit as st
import plotly.graph_objects as go
import random
import base64
import os
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="LUNG AI | Profesyonel Analiz", layout="centered")

# --- ARKA PLAN VE GLASSMORPHISM TASARIMI ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Senin bilgisayarındaki özel yol
image_path = r"C:\Users\rabia\Downloads\arkaplan (2).jpg"

try:
    bin_str = get_base64(image_path)
    bg_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
    }}
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.85); /* Karartma efekti */
        z-index: -1;
    }}
    
    /* CAM EFEKTİ (Glassmorphism) KUTULARI */
    .stSelectbox, .stRadio, .stTextInput {{
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        backdrop-filter: blur(5px);
    }}

    /* İNCE BEYAZ YAZILAR */
    h1, h2, h3 {{
        color: #FFFFFF !important;
        font-weight: 200 !important;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    p, label, .stMarkdown {{
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 200 !important;
    }}

    /* SADE VE KÜÇÜK BUTONLAR */
    .stButton>button {{
        background: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 4px !important;
        font-weight: 200 !important;
        padding: 4px 20px !important;
        font-size: 13px !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        border-color: #00f2ff !important;
        background: rgba(0, 242, 255, 0.05) !important;
    }}
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)
except:
    st.warning("Arka plan dosyası bulunamadı, lütfen dosya yolunu kontrol edin.")

# --- DURUM YÖNETİMİ ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'answers' not in st.session_state: st.session_state.answers = {}

# --- 1. ADIM: GİRİŞ EKRANI ---
if st.session_state.step == 1:
    st.title("Kişisel Bilgiler")
    
    yas_raw = st.text_input("Yaşınız (18-85):", value="25")
    
    # Yaş Kontrolleri
    age_valid = False
    if not yas_raw.isdigit():
        st.error("🚨 Harf veya ondalıklı sayı girilemez.")
    else:
        yas = int(yas_raw)
        if yas > 85:
            st.error("🚨 Yaş 85’ten büyük olamaz.")
        elif yas < 18:
            st.error("🚨 Lütfen geçerli bir yaş giriniz (18+).")
        else:
            age_valid = True

    cinsiyet = st.selectbox("Cinsiyetiniz:", ["Seçiniz", "Erkek", "Kadın"])

    if st.button("İlerle"):
        if age_valid and cinsiyet != "Seçiniz":
            st.session_state.answers['yas'] = yas
            st.session_state.answers['cinsiyet'] = cinsiyet
            st.session_state.step = 2
            st.rerun()

# --- 2. ADIM: SAĞLIK GEÇMİŞİ ---
elif st.session_state.step == 2:
    st.title("Sağlık Geçmişi")
    
    kronik = st.radio("Kronik bir rahatsızlığınız var mı?", ["Hayır", "Evet"], horizontal=True)
    if kronik == "Evet":
        st.session_state.answers['kronik_tip'] = st.selectbox("Rahatsızlığınız nedir?", 
            ["KOAH", "Astım", "Bronşit", "Akciğer enfeksiyonu", "Diğer"])
    
    st.divider()
    
    genetik = st.radio("Ailenizde akciğer kanseri geçmişi var mı?", ["Hayır", "Evet"], horizontal=True)
    if genetik == "Evet":
        st.session_state.answers['yakinlik'] = st.selectbox("Yakınlık derecesi:", 
            ["Anne / Baba / Kardeş", "Dede / Anneanne / Babaanne", "Teyze / Hala / Amca / Dayı", "Uzak akraba"])

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Geri"): st.session_state.step = 1; st.rerun()
    with col2:
        if st.button("İlerle"):
            st.session_state.answers['genetik'] = genetik
            st.session_state.step = 3
            st.rerun()

# --- 3. ADIM: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("Alışkanlıklar")
    
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if sigara == "Evet":
        st.session_state.answers['sigara_siklik'] = st.selectbox("Ne sıklıkla?", 
            ["Günde birkaç tane", "Günde yarım paket", "Günde bir paket", "Günde bir paketten fazla"])

    st.divider()
    
    alkol = st.radio("Alkol kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if alkol == "Evet":
        st.session_state.answers['alkol_siklik'] = st.selectbox("Sıklık:", 
            ["Özel günlerde", "Ayda bir", "Haftada birkaç kez", "Her gün"])

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Geri"): st.session_state.step = 2; st.rerun()
    with col2:
        if st.button("İlerle"):
            st.session_state.answers['sigara'] = sigara
            st.session_state.answers['alkol'] = alkol
            st.session_state.step = 4
            st.rerun()

# --- 4. ADIM: BELİRTİ VE ŞİKAYETLER ---
elif st.session_state.step == 4:
    st.title("Belirtiler")
    
    with st.expander("Ağrı ve Öksürük", expanded=True):
        gogus = st.radio("Göğüs ağrısı/baskı var mı?", ["Hayır", "Evet"], horizontal=True)
        oksuruk = st.radio("Sürekli öksürük var mı?", ["Hayır", "Evet"], horizontal=True)
        if oksuruk == "Evet":
            st.session_state.answers['oksuruk_tip'] = st.selectbox("Öksürük Tipi:", ["Hafif kuru", "Sık balgamlı", "Şiddetli", "Kanlı"])

    with st.expander("Solunum ve Fiziksel"):
        nefes = st.radio("Nefes darlığı var mı?", ["Hayır", "Evet"], horizontal=True)
        yutkunma = st.radio("Yutkunma güçlüğü var mı?", ["Hayır", "Evet"], horizontal=True)
        parmak = st.radio("Parmaklarda sararma var mı?", ["Hayır", "Evet"], horizontal=True)

    with st.expander("Genel Durum"):
        stres = st.radio("Yoğun stres/anksiyete?", ["Hayır", "Evet"], horizontal=True)
        halsizlik = st.radio("Aşırı yorgunluk/halsizlik?", ["Hayır", "Evet"], horizontal=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Geri"): st.session_state.step = 3; st.rerun()
    with col2:
        if st.button("Analiz Et"):
            st.session_state.step = 5
            st.rerun()

# --- 5. ADIM: ANALİZ SONUÇLARI ---
elif st.session_state.step == 5:
    # LOADING ANİMASYONU
    with st.status("AI Analiz Yapılıyor...", expanded=True) as status:
        st.write("Veriler işleniyor...")
        time.sleep(1)
        st.write("Risk faktörleri taranıyor...")
        time.sleep(1)
        status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)

    st.title("Analiz Raporu")
    
    # RİSK HESAPLAMA MANTIĞI
    score = 10
    if st.session_state.answers.get('sigara') == "Evet": score += 30
    if st.session_state.answers.get('oksuruk_tip') == "Kanlı": score += 35
    if st.session_state.answers.get('genetik') == "Evet": score += 15
    score = min(score, 99)

    # İNCE GRAFİK SİSTEMİ
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        number = {'suffix': "%", 'font': {'color': "#FFFFFF", 'weight': 'lighter'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00f2ff", 'thickness': 0.05}, # İNCE ÇİZGİ
            'bgcolor': "rgba(255,255,255,0.05)",
            'steps': [
                {'range': [0, 30], 'color': "#00ff88"},
                {'range': [30, 70], 'color': "#ffcc00"},
                {'range': [70, 100], 'color': "#ff4444"}]
        }))
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

    # RADAR CHART (Faktör Etkisi)
    categories = ['Sigara', 'Genetik', 'Semptom', 'Yaş', 'Kronik']
    fig_radar = go.Figure(data=go.Scatterpolar(
      r=[40 if st.session_state.answers.get('sigara')=="Evet" else 10, 
         30 if st.session_state.answers.get('genetik')=="Evet" else 5,
         50 if score > 50 else 20,
         score/2,
         25 if 'kronik_tip' in st.session_state.answers else 0],
      theta=categories,
      fill='toself',
      line_color='#00f2ff'
    ))
    fig_radar.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)), 
                            paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
    st.plotly_chart(fig_radar)

    # AI YORUM VE ÖNERİLER
    if score > 70:
        st.error("⚠️ YÜKSEK RİSK: Belirtileriniz ve alışkanlıklarınız ciddi bir tablo çiziyor.")
        st.info("🏥 Gidilmesi Gereken Bölümler: Göğüs Hastalıkları, Onkoloji.")
    else:
        st.success("✨ DÜŞÜK RİSK: Akciğer sağlığınız şu an için stabil görünüyor.")
        st.info("🏃 Öneri: Düzenli yürüyüş ve nefes egzersizlerine devam edin.")

    st.markdown("---")
    st.caption("🤖 Bu analiz yapay zekâ destekli tahmini bir değerlendirmedir. Kesin teşhis yerine geçmez.")
    
    if st.button("Tekrar Başlat"):
        st.session_state.step = 1; st.rerun()
