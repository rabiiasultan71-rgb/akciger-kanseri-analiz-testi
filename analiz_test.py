import streamlit as st
import plotly.graph_objects as go
import base64
import os

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="LUNG AI | Akıllı Analiz", layout="centered")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_path = "arkaplan.jpg" 

if os.path.exists(image_path):
    bin_str = get_base64(image_path)
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover; background-attachment: fixed; background-position: center;
    }}
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.82); z-index: -1;
    }}
    /* Yazı Panelleri ve Okunabilirlik */
    div[data-baseweb="select"], div[data-baseweb="input"], .stRadio {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(0, 255, 255, 0.4) !important;
        border-radius: 12px !important;
        padding: 5px;
        backdrop-filter: blur(8px);
    }}
    h1, h2, h3, label, p {{ 
        color: white !important; 
        text-shadow: 2px 2px 5px rgba(0,0,0,1) !important; 
    }}
    /* Butonlar */
    .stButton>button {{
        width: 100%; border-radius: 25px !important;
        background: rgba(0, 255, 255, 0.15) !important;
        color: #00FFFF !important; border: 1px solid #00FFFF !important;
        font-weight: bold !important;
        -webkit-appearance: none;
    }}
    </style>
    """, unsafe_allow_html=True)

if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = {}

# --- ADIM 1: TEMEL BİLGİLER ---
if st.session_state.step == 1:
    st.title("🩺 Adım 1: Temel Bilgiler")
    yas = st.text_input("Yaşınız:", placeholder="Örn: 40")
    cinsiyet = st.selectbox("Cinsiyetiniz:", ["Seçiniz", "Erkek", "Kadın"])
    if st.button("İlerle"):
        if yas.isdigit() and cinsiyet != "Seçiniz":
            st.session_state.data['yas'] = int(yas)
            st.session_state.data['cinsiyet'] = cinsiyet
            st.session_state.step = 2; st.rerun()
        else: st.error("Lütfen bilgileri eksiksiz girin.")

# --- ADIM 2: RİSK FAKTÖRLERİ ---
elif st.session_state.step == 2:
    st.title("🧬 Adım 2: Risk Faktörleri")
    genetik = st.radio("Ailede akciğer kanseri öyküsü?", ["Hayır", "Evet"], horizontal=True)
    sigara = st.radio("Sigara içiyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if sigara == "Evet":
        paket = st.selectbox("Sıklık:", ["Günde yarım paket", "Günde 1 paket", "Günde 1 paketten fazla"])
        st.session_state.data['paket'] = paket
    
    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 1; st.rerun()
    if col2.button("İlerle"):
        st.session_state.data['genetik'] = genetik
        st.session_state.data['sigara'] = sigara
        st.session_state.step = 3; st.rerun()

# --- ADIM 3: BELİRTİLER ---
elif st.session_state.step == 3:
    st.title("⚠️ Adım 3: Belirtiler")
    oksuruk = st.selectbox("Öksürük durumu:", ["Yok", "Hafif", "Şiddetli", "Kanlı"])
    nefes = st.selectbox("Nefes darlığı:", ["Yok", "Yürürken", "Dinlenirken bile"])
    
    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 2; st.rerun()
    if col2.button("Analiz Et"):
        st.session_state.data['oksuruk'] = oksuruk
        st.session_state.data['nefes'] = nefes
        st.session_state.step = 4; st.rerun()

# --- ADIM 4: GERÇEKÇİ SONUÇ ---
elif st.session_state.step == 4:
    st.title("📊 Analiz Sonucu")
    
    # HESAPLAMA MANTIĞI
    puan = 5
    if st.session_state.data['sigara'] == "Evet":
        puan += 25
        if st.session_state.data.get('paket') == "Günde 1 paket": puan += 10
        if st.session_state.data.get('paket') == "Günde 1 paketten fazla": puan += 20
    
    if st.session_state.data['genetik'] == "Evet": puan += 15
    if st.session_state.data['oksuruk'] == "Kanlı": puan += 35
    elif st.session_state.data['oksuruk'] == "Şiddetli": puan += 10
    if st.session_state.data['nefes'] == "Dinlenirken bile": puan += 15
    
    puan = min(puan, 99)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = puan,
        number = {'suffix': "%", 'font': {'color': "#00FFFF"}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"},
                 'steps': [{'range': [0, 30], 'color': "green"},
                           {'range': [30, 70], 'color': "orange"},
                           {'range': [70, 100], 'color': "red"}]}))
    st.plotly_chart(fig, use_container_width=True)

    if puan < 30: st.success("Düşük Risk: Sağlıklı görünüyorsunuz.")
    elif puan < 70: st.warning("Orta Risk: Yaşam tarzınıza dikkat etmelisiniz.")
    else: st.error("Yüksek Risk: Lütfen bir doktora görünün.")

    if st.button("Yeniden Başla"): st.session_state.step = 1; st.rerun()
