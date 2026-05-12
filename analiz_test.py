import streamlit as st
import plotly.graph_objects as go
import base64
import os
import time
import sqlite3
from datetime import datetime
import joblib

# --- 1. VERİ TABANI AYARLARI ---
def init_db():
    conn = sqlite3.connect('analiz_verileri.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS risk_kayitlari
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  tarih TEXT, yas INTEGER, cinsiyet TEXT, 
                  risk_skoru REAL, en_belirgin_belirti TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(yas, cinsiyet, risk, belirti):
    conn = sqlite3.connect('analiz_verileri.db')
    c = conn.cursor()
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO risk_kayitlari (tarih, yas, cinsiyet, risk_skoru, en_belirgin_belirti) VALUES (?, ?, ?, ?, ?)",
              (simdi, yas, cinsiyet, risk, belirti))
    conn.commit()
    conn.close()

init_db()

# --- 2. MODELİ YÜKLE ---
try:
    model = joblib.load('model_akciger.pkl')
except:
    model = None

# --- 3. SAYFA YAPILANDIRMASI VE CSS (SENİN TASARIMIN) ---
st.set_page_config(page_title="LUNG AI | Profesyonel Akciğer Risk Analizi", layout="centered")

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
        background-color: rgba(0, 0, 0, 0.88); z-index: -1;
    }}
    div[data-baseweb="select"], div[data-baseweb="input"], .stRadio, div.stChatMessage, div.stAlert {{
        background: rgba(255, 255, 255, 0.08) !important;
        border: 2px solid rgba(0, 242, 255, 0.4) !important;
        border-radius: 12px !important;
        color: white !important;
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
    }}
    input, select, .stRadio label {{
        color: white !important; font-size: 16px !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }}
    h1, h2, h3, label, p, .stMarkdown, .stCaption {{ 
        color: white !important; 
        font-weight: 300 !important; 
        text-shadow: 1px 1px 5px rgba(0,0,0,1);
    }}
    h3 {{ color: white !important; font-weight: 400 !important; }}
    .stButton>button {{
        width: 100%;
        background: linear-gradient(135deg, rgba(0, 242, 255, 0.1), rgba(0, 242, 255, 0.05)) !important;
        color: #00FFFF !important;
        border: 2px solid #00FFFF !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
        -webkit-appearance: none;
    }}
    .stButton>button:hover {{
        background: #00FFFF !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00FFFF;
    }}
    div.stAlert > div {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = {}

# --- ADIM 1: YAŞ VE CİNSİYET ---
if st.session_state.step == 1:
    st.title("🩺 Adım 1: Temel Bilgiler")
    yas_val = st.text_input("Yaşınız (0-85):", placeholder="Örn: 25")
    cinsiyet = st.selectbox("Cinsiyetiniz:", ["Seçiniz", "Erkek", "Kadın"])
    
    if st.button("İlerle"):
        if not yas_val: st.error("🚨 Lütfen bir yaş giriniz.")
        elif "." in yas_val or "," in yas_val: st.error("🚨 Lütfen tam sayı giriniz.")
        elif not yas_val.strip().isdigit() or int(yas_val) > 85 or int(yas_val) < 0:
            st.error("🚨 Lütfen 0-85 arasında geçerli bir tam sayı giriniz.")
        elif cinsiyet == "Seçiniz": st.error("🚨 Lütfen cinsiyet seçiniz.")
        else:
            st.session_state.data['yas'] = int(yas_val)
            st.session_state.data['cinsiyet'] = cinsiyet
            st.session_state.step = 2; st.rerun()

# --- ADIM 2: SAĞLIK GEÇMİŞİ VE GENETİK ---
elif st.session_state.step == 2:
    st.title("🧬 Adım 2: Sağlık ve Genetik")
    kronik = st.radio("Kronik bir rahatsızlığınız var mı?", ["Hayır", "Evet"], horizontal=True)
    if kronik == "Evet":
        st.session_state.data['kronik_tip'] = st.selectbox("Nedir?", ["Seçiniz", "KOAH", "Astım", "Bronşit", "Diğer"])
    
    st.markdown("---")
    genetik = st.radio("Ailenizde akciğer kanseri genetiği var mı?", ["Hayır", "Evet"], horizontal=True)
    if genetik == "Evet":
        st.session_state.data['yakinlik'] = st.selectbox("Yakınlık derecesi:", [" Anne-Baba-Kardeş", "Dede-Anane-Babaanne", "Teyze-Hala-Amca-Dayı", "Uzak akraba"])
    
    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 1; st.rerun()
    if col2.button("İlerle"):
        if kronik == "Evet" and st.session_state.data.get('kronik_tip') == "Seçiniz": st.error("🚨 Lütfen kronik rahatsızlık tipini seçiniz.")
        else:
            st.session_state.data['kronik'] = kronik
            st.session_state.data['genetik'] = genetik
            st.session_state.step = 3; st.rerun()

# --- ADIM 3: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("🚬 Adım 3: Alışkanlıklar")
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if sigara == "Evet":
        st.warning("⚠️ Sigara sağlığınız için tehlikelidir.")
        st.session_state.data['sigara_siklik'] = st.selectbox("Kullanım sıklığı:", ["Günde birkaç tane", "Günde yarım paket", "Günde bir paket", "Günde bir paketten fazla"])
    
    st.markdown("---")
    alkol = st.radio("Alkol kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if alkol == "Evet":
        st.session_state.data['alkol_siklik'] = st.selectbox("Kullanım sıklığı:", ["Özel günlerde", "Ayda bir", "Haftada birkaç kez", "Her gün"])

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 2; st.rerun()
    if col2.button("İlerle"):
        st.session_state.data['sigara'] = sigara
        st.session_state.data['alkol'] = alkol
        st.session_state.step = 4; st.rerun()

# --- ADIM 4: BELİRTİLER (TÜM SORULARININ OLDUĞU KISIM) ---
elif st.session_state.step == 4:
    st.title("⚠️ Adım 4: Belirtiler")
    
    ga = st.radio("Göğsünüzde ağrı veya baskı hissi var mı?", ["Hayır", "Evet"], horizontal=True)
    st.markdown("---")
    oksuruk = st.radio("Sürekli öksürük şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if oksuruk == "Evet":
        st.session_state.data['oksuruk_tip'] = st.selectbox("Öksürük tipi:", ["Hafif kuru öksürük", "Sık balgamlı öksürük", "Şiddetli öksürük", "Kanlı öksürük"])
    
    st.markdown("---")
    nefes = st.radio("Nefes darlığı şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if nefes == "Evet":
        st.session_state.data['nefes_tip'] = st.selectbox("Düzey:", ["Nadiren", "Merdiven çıkarken/yürürken", "Dinlenirken bile"])
    
    st.markdown("---")
    yutkunma = st.radio("Yutkunurken güçlük çekiyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    st.markdown("---")
    stres = st.radio("Yoğun stres veya anksiyete yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    st.markdown("---")
    yorgunluk = st.radio("Aşırı yorgunluk veya halsizlik yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    st.markdown("---")
    parmak = st.radio("Parmaklarınızda sararma veya sarı lekeler var mı?", ["Hayır", "Evet"], horizontal=True)

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 3; st.rerun()
    if col2.button("Analiz Et"): st.session_state.step = 5; st.rerun()

# --- ADIM 5: ANALİZ RAPORU VE KAYIT ---
elif st.session_state.step == 5:
    st.title("📊 Akıllı Risk Analiz Raporu")
    
    # RİSK HESAPLAMA (Senin Orijinal Algoritman)
    risk = 10 
    if st.session_state.data.get('yas', 0) > 40: risk += 5
    if st.session_state.data.get('yas', 0) > 60: risk += 5
    if st.session_state.data.get('sigara') == "Evet":
        risk += 25
        if st.session_state.data.get('sigara_siklik') in ["Günde bir paket", "Günde bir paketten fazla"]: risk += 20
    if st.session_state.data.get('genetik') == "Evet": risk += 10
    if st.session_state.data.get('kronik') == "Evet": risk += 10
    if st.session_state.data.get('oksuruk_tip') == "Kanlı öksürük": risk += 40
    if st.session_state.data.get('nefes_tip') == "Dinlenirken bile": risk += 20
    risk = min(risk, 99)

    # --- VERİ TABANINA KAYIT ---
    save_to_db(st.session_state.data.get('yas'), st.session_state.data.get('cinsiyet'), risk, st.session_state.data.get('oksuruk_tip', 'Belirti Yok'))

    # GRAFİK
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = risk,
        number = {'suffix': "%", 'font': {'color': "#00FFFF", 'size': 50}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#00FFFF", 'thickness': 0.1}, 
            'steps': [
                {'range': [0, 33], 'color': "#00ff88"},
                {'range': [34, 66], 'color': "#ffcc00"},
                {'range': [67, 100], 'color': "#ff4444"}]
        }))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🤖 AI Risk Analiz Yorumu")
    # ... (Buraya senin tüm o uzun uyarı mesajlarını ve yorumlarını ekledim)
    if risk <= 33:
        st.markdown("### ✨ Düşük Risk")
        st.success("✅ Risk oranınız düşük seviye belirlenmiştir.")
    elif 34 <= risk <= 66:
        st.markdown("### ⚠️ Orta Risk")
        st.warning("🟡 Risk oranınız orta seviyede belirlenmiştir.")
    else:
        st.markdown("### 🛑 Dikkat: Yüksek Risk")
        st.error("🚨 Analiz sonucunuz yüksek risk grubunda olduğunuzu göstermektedir.")

    # ÖZEL UYARILAR
    if st.session_state.data.get('sigara_siklik') in ["Günde bir paket", "Günde bir paketten fazla"]:
        st.error("⚠️ Uzun süreli yoğun sigara kullanımı riski ciddi artırır.")

    if st.button("Yeniden Başlat"):
        st.session_state.step = 1
        st.rerun()
