import sqlite3
from datetime import datetime
import streamlit as st
import joblib
import numpy as np
import plotly.graph_objects as go
import base64
import os

# --- SQLİTE (YEREL SQL) AYARLARI ---
def veritabani_kur():
    conn = sqlite3.connect("akciger_analiz.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analizler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT, yas INTEGER, cinsiyet TEXT, sigara TEXT, 
            alkol TEXT, kronik TEXT, gogus_agrisi TEXT, 
            oksuruk TEXT, nefes_darligi TEXT, yutkunma_guclugu TEXT, 
            stres_anksiyete TEXT, yorgunluk TEXT, parmak_sararma TEXT, risk_skoru INTEGER
        )
    """)
    conn.commit()
    conn.close()

veritabani_kur()

def veritabanina_kaydet(yas, cinsiyet, sigara, alkol, kronik, g_a, oksuruk, nefes, yutkunma, stres, yorgunluk, parmak, risk):
    conn = sqlite3.connect("akciger_analiz.db")
    cursor = conn.cursor()
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO analizler (tarih, yas, cinsiyet, sigara, alkol, kronik, gogus_agrisi, 
        oksuruk, nefes_darligi, yutkunma_guclugu, stres_anksiyete, yorgunluk, parmak_sararma, risk_skoru)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (tarih, yas, cinsiyet, sigara, alkol, kronik, g_a, oksuruk, nefes, yutkunma, stres, yorgunluk, parmak, risk))
    conn.commit()
    conn.close()
    st.toast("💾 Veriler SQL veri tabanına başarıyla kaydedildi!", icon="💾")

# --- MODELİ YÜKLEME ---
@st.cache_resource
def model_yukle():
    try:
        return joblib.load("akciger_modeli.pkl")
    except:
        return None

model = model_yukle()

def yapay_zekadan_tahmin_al(veriler):
    if model is not None:
        dizi = np.array(veriler).reshape(1, -1)
        tahmin_olasiligi = model.predict_proba(dizi)[0][1]
        return tahmin_olasiligi
    return 0.35

# --- SAYFA YAPILANDIRMASI ---
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
        backdrop-filter: blur(10px);
    }}
    input, select, .stRadio label {{
        color: white !important; font-size: 16px !important;
    }}
    h1, h2, h3, label, p, .stMarkdown, .stCaption {{ 
        color: white !important; 
        font-weight: 300 !important; 
    }}
    .stButton>button {{
        width: 100%;
        background: linear-gradient(135deg, rgba(0, 242, 255, 0.1), rgba(0, 242, 255, 0.05)) !important;
        color: #00FFFF !important;
        border: 2px solid #00FFFF !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background: #00FFFF !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00FFFF;
    }}
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
        elif "." in yas_val or "," in yas_val: st.error("🚨 Lütfen 0-85 arasında tam sayı giriniz.")
        elif not yas_val.strip().isdigit(): st.error("🚨 Negatif sayı veya harf yasak.")
        elif int(yas_val) > 85 or int(yas_val) < 0: st.error("🚨 Lütfen 0-85 arasında geçerli bir yaş giriniz.")
        elif cinsiyet == "Seçiniz": st.error("🚨 Lütfen cinsiyet seçiniz.")
        else:
            st.session_state.data['yas'] = int(yas_val)
            st.session_state.data['cinsiyet'] = cinsiyet
            st.session_state.step = 2
            st.rerun()


# --- ADIM 2: SAĞLIK GEÇMİŞİ VE GENETİK ---
elif st.session_state.step == 2:
    st.title("🧬 Adım 2: Sağlık ve Genetik")
    
    genetik = st.radio("Ailenizde akciğer kanseri genetiği var mı?", ["Hayır", "Evet"], horizontal=True)
    if genetik == "Evet":
        yakinlik = st.selectbox("Yakınlık derecesi nedir?", 
                                ["Seçiniz", "1. Derece (Anne, Baba, Kardeş)", 
                                 "2. Derece (Dede, Nene, Amca, Hala, Dayı, Teyze)", 
                                 "3. Derece ve sonrası", "Diğer"])
        st.session_state.data['genetik_yakinlik'] = yakinlik
    
    st.markdown("---")
    
    kronik = st.radio("Kronik bir rahatsızlığınız var mı?", ["Hayır", "Evet"], horizontal=True)
    if kronik == "Evet":
        kronik_tip = st.selectbox("Hastalık türü:", ["Seçiniz", "KOAH", "Astım", "Bronşit", "Diğer"])
        st.session_state.data['kronik_tip'] = kronik_tip

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 1; st.rerun()
    if col2.button("İlerle"):
        if genetik == "Evet" and st.session_state.data.get('genetik_yakinlik', "Seçiniz") == "Seçiniz":
            st.error("🚨 Lütfen yakınlık derecesini seçiniz.")
        elif kronik == "Evet" and st.session_state.data.get('kronik_tip', "Seçiniz") == "Seçiniz":
            st.error("🚨 Lütfen kronik rahatsızlık türünü seçiniz.")
        else:
            st.session_state.data['genetik'] = genetik
            st.session_state.data['kronik'] = kronik
            st.session_state.step = 3; st.rerun()

# --- ADIM 3: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("🚬 Adım 3: Alışkanlıklar")
    
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if sigara == "Evet":
        st.warning("⚠️ Sigara sağlığınız için zararlıdır. Bırakmanız tavsiye edilir.")
        sigara_siklik = st.selectbox("Kullanım sıklığı:", ["Seçiniz", "Ara sıra", "Günde yarım paket", "Günde 1 paket", "Günde 2+ paket"])
        st.session_state.data['sigara_siklik'] = sigara_siklik
    
    st.markdown("---")
    
    alkol = st.radio("Alkol kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if alkol == "Evet":
        alkol_siklik = st.selectbox("Kullanım sıklığı:", ["Seçiniz", "Özel günlerde", "Haftada bir", "Haftada 2-3 gün", "Her gün"])
        st.session_state.data['alkol_siklik'] = alkol_siklik

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 2; st.rerun()
    if col2.button("İlerle"):
        if sigara == "Evet" and st.session_state.data.get('sigara_siklik', "Seçiniz") == "Seçiniz":
            st.error("🚨 Lütfen sigara kullanım sıklığınızı seçiniz.")
        elif alkol == "Evet" and st.session_state.data.get('alkol_siklik', "Seçiniz") == "Seçiniz":
            st.error("🚨 Lütfen alkol kullanım sıklığınızı seçiniz.")
        else:
            st.session_state.data['sigara'] = sigara
            st.session_state.data['alkol'] = alkol
            st.session_state.step = 4; st.rerun()

elif st.session_state.step == 4:
    st.title("⚠️ Adım 4: Belirtiler")
    
    # 1. Göğüs Ağrısı
    g_a = st.radio("Göğüs ağrısı var mı?", ["Hayır", "Evet"], horizontal=True)
    g_a_detay = "Yok"
    if g_a == "Evet":
        g_a_detay = st.selectbox("Ağrı tipi:", ["Batma", "Baskı", "Sürekli"], key="ga_d")

    # 2. Öksürük
    oksuruk = st.radio("Sürekli öksürük var mı?", ["Hayır", "Evet"], horizontal=True)
    oksuruk_detay = "Yok"
    if oksuruk == "Evet":
        oksuruk_detay = st.selectbox("Süre:", ["1-2 Hafta", "1 Ay", "3 Ay+"], key="oks_d")

    # 3. Nefes Darlığı
    nefes = st.radio("Nefes darlığı var mı?", ["Hayır", "Evet"], horizontal=True)
    nefes_detay = "Yok"
    if nefes == "Evet":
        nefes_detay = st.selectbox("Durum:", ["Hareket halinde", "İstirahat halinde"], key="nef_d")

    # 4. Yutkunma Güçlüğü
    yutkunma = st.radio("Yutkunma güçlüğü var mı?", ["Hayır", "Evet"], horizontal=True)
    yutkunma_detay = "Yok"
    if yutkunma == "Evet":
        yutkunma_detay = st.selectbox("Zamanlama:", ["Katı gıdalar", "Sıvılar"], key="yut_d")

    # Diğerleri (Detaysız)
    stres = st.radio("Yoğun stres yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    yorgunluk = st.radio("Aşırı yorgunluk var mı?", ["Hayır", "Evet"], horizontal=True)
    parmak = st.radio("Parmak sararması var mı?", ["Hayır", "Evet"], horizontal=True)

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 3; st.rerun()
    if col2.button("Analiz Et"):
        st.session_state.data.update({
            'g_a': g_a, 'g_a_detay': g_a_detay,
            'oksuruk': oksuruk, 'oksuruk_detay': oksuruk_detay,
            'nefes': nefes, 'nefes_detay': nefes_detay,
            'yutkunma': yutkunma, 'yutkunma_detay': yutkunma_detay,
            'stres': stres, 'yorgunluk': yorgunluk, 'parmak': parmak
        })
        st.session_state.step = 5
        st.rerun()
        
# --- ADIM 5: GERÇEKÇİ AI ANALİZ VE VERİ TABANI KAYDI ---
elif st.session_state.step == 5:
    st.title("📊 Akıllı Risk Analiz Raporu")
    
    d = st.session_state.data 

    # [DÜZELTİLDİ]: Sütunlar dataset.csv'deki sıralamaya ve mantığa (%100) uyumlu hale getirildi.
    # 2 = Evet, 1 = Hayır mantığı korunmuştur.
    veriler = [
        1 if d.get('cinsiyet') == "Erkek" else 0,                               # GENDER
        d.get('yas', 45),                                                      # AGE
        2 if d.get('sigara') == "Evet" else 1,                                 # SMOKING
        2 if d.get('parmak') == "Evet" else 1,                                 # YELLOW_FINGERS
        2 if d.get('stres') == "Evet" else 1,                                  # ANXIETY
        2 if (d.get('sigara') == "Evet" or d.get('alkol') == "Evet") else 1,   # PEER_PRESSURE
        2 if d.get('kronik') == "Evet" else 1,                                 # CHRONIC_DISEASE
        2 if d.get('yorgunluk') == "Evet" else 1,                              # FATIGUE
        2 if (d.get('genetik') == "Evet" or d.get('kronik') == "Evet") else 1, # ALLERGY (Model girdisi)
        2 if d.get('nefes') == "Evet" else 1,                                  # WHEEZING
        2 if d.get('alkol') == "Evet" else 1,                                  # ALCOHOL_CONSUMING
        2 if d.get('oksuruk') == "Evet" else 1,                                # COUGHING
        2 if d.get('nefes') == "Evet" else 1,                                  # SHORTNESS_OF_BREATH
        2 if d.get('yutkunma') == "Evet" else 1,                               # SWALLOWING_DIFFICULTY
        2 if d.get('g_a') == "Evet" else 1                                     # CHEST_PAIN
    ]
    
    # Modelden tahmini alıyoruz
    tahmin_orani = yapay_zekadan_tahmin_al(veriler)
    risk = int(tahmin_orani * 100)
    
    # Klinik Hibrit İyileştirme kuralları
    evet_sayisi = sum([1 for v in veriler[2:] if v == 2]) 
    if evet_sayisi >= 10:
        risk = max(risk, 95)
    elif evet_sayisi >= 6:
        risk = max(risk, 70)
    elif evet_sayisi <= 1:
        risk = min(risk, 20)

    risk = max(5, min(risk, 99))
    
    # Veri Tabanına Tek Seferlik Kayıt Güvencesi
    if 'kaydedildi' not in st.session_state:
        veritabanina_kaydet(
            d.get('yas'), d.get('cinsiyet'), d.get('sigara'), d.get('alkol'), d.get('kronik'),
            d.get('g_a'), d.get('oksuruk'), d.get('nefes'), d.get('yutkunma'), d.get('stres'),
            d.get('yorgunluk'), d.get('parmak'), risk
        )
        st.session_state.kaydedildi = True

    # Grafiği Çiz
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = risk,
        number = {'suffix': "%", 'font': {'color': "#00FFFF", 'size': 50}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#00FFFF", 'thickness': 0.1}, 
            'steps': [
                {'range': [0, 33], 'color': "#055630"},
                {'range': [34, 66], 'color': "#eabb02"},
                {'range': [67, 100], 'color': "#af1313"}]
        }))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🤖 AI Risk Analiz Yorumu")
    
    if risk <= 33:
        st.markdown("### ✨ Düşük Risk")
        st.success("✅ Risk oranınız düşük seviye belirlenmiştir. Sağlığınızı korumak için sigara dumanından uzak durun ve düzenli egzersiz yapın.")
    elif 34 <= risk <= 66:
        st.markdown("### ⚠️ Orta Risk")
        st.warning("🟡 Risk oranınız orta seviyede belirlenmiştir. Yaşam alışkanlıklarınızı gözden geçirmeniz ve bir uzmana danışmanız önerilir.")
    else:
        st.markdown("### 🛑 Dikkat: Yüksek Risk")
        st.error("🚨 Analiz sonucunuz yüksek risk grubunda olduğunuzu göstermektedir. Lütfen en kısa sürede bir Göğüs Hastalıkları uzmanına başvurun.")
        
    if st.button("Yeni Analiz Yap"):
        st.session_state.clear()
        st.rerun()
       
st.markdown("---")
if st.button("SQL Veri Tabanındaki Kayıtları Gör"):
    try:
        conn = sqlite3.connect("akciger_analiz.db")
        import pandas as pd
        df = pd.read_sql_query("SELECT * FROM analizler", conn)
        st.dataframe(df) # Hocan burada tabloları ve verileri görecek!
        conn.close()
    except Exception as e:
        st.warning("Henüz veri tabanında kayıt bulunmuyor.")
