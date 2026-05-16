import streamlit as st
import plotly.graph_objects as go
import base64
import os
import time
import joblib
import numpy as np
import psycopg2  # Eski sqlite3 yerine PostgreSQL kütüphanesini ekledik
from datetime import datetime

# --- VERİ TABANI AYARLARI ---
# Streamlit Secrets kısmına kaydettiğimiz gizli bağlantı linkini çekiyoruz
DB_URL = st.secrets["database"]["url"]

def veritabani_kur():
    """Render PostgreSQL üzerinde tablo yoksa otomatik oluşturur"""
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analizler (
                id SERIAL PRIMARY KEY,
                tarih TEXT,
                yas INTEGER,
                cinsiyet TEXT,
                sigara TEXT,
                alkol TEXT,
                kronik TEXT,
                gogus_agrisi TEXT,
                oksuruk TEXT,
                nefes_darligi TEXT,
                yutkunma_guclugu TEXT,
                stres_anksiyete TEXT,
                yorgunluk TEXT,
                parmak_sararma TEXT,
                risk_skoru INTEGER
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Veri tabanı kurulum hatası: {e}")

# Veri tabanını ilk açılışta kontrol et ve oluştur
veritabani_kur()

def veritabanina_kaydet(yas, cinsiyet, sigara, alkol, kronik, g_a, oksuruk, nefes, yutkunma, stres, yorgunluk, parmak, risk):
    """Kullanıcı verilerini kalıcı olarak Render PostgreSQL'e kaydeder"""
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        tarih_suan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # PostgreSQL uyumlu SQL sorgusu (%s işaretleri kullanıldı)
        cursor.execute("""
            INSERT INTO analizler (
                tarih, yas, cinsiyet, sigara, alkol, kronik, gogus_agrisi, 
                oksuruk, nefes_darligi, yutkunma_guclugu, stres_anksiyete, 
                yorgunluk, parmak_sararma, risk_skoru
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (tarih_suan, yas, cinsiyet, sigara, alkol, kronik, g_a, oksuruk, nefes, yutkunma, stres, yorgunluk, parmak, risk))
        
        conn.commit()
        cursor.close()
        conn.close()
        st.toast("💾 Analiz verileri başarıyla gerçek PostgreSQL veri tabanına kaydedildi!", icon="💾")
    except Exception as e:
        st.error(f"Veri tabanına kaydetme hatası: {e}")

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
        # Sınıf olasılığını alıyoruz (% risk hesabı için)
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
    kronik = st.radio("Kronik bir rahatsızlığınız var mı?", ["Hayır", "Evet"], horizontal=True)
    if kronik == "Evet":
        st.session_state.data['kronik_tip'] = st.selectbox("Nedir?", ["Seçiniz", "KOAH", "Astım", "Bronşit", "Diğer"])
    
    st.markdown("---")
    genetik = st.radio("Ailenizde akciğer kanseri genetiği var mı?", ["Hayır", "Evet"], horizontal=True)
    if genetik == "Evet":
        st.session_state.data['yakinlik'] = st.selectbox("Yakınlık derecesi:", [" Anne-Baba-Kardeş", "Dede-Anneanne-Babaanne", "Teyze-Hala-Amca-Dayı", "Uzak akraba"])
    
    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 1; st.rerun()
    if col2.button("İlerle"): 
        if kronik == "Evet" and st.session_state.data.get('kronik_tip') == "Seçiniz":
            st.error("🚨 Lütfen kronik rahatsızlık tipini seçiniz.")
        else:
            st.session_state.data['kronik'] = kronik
            st.session_state.data['genetik'] = genetik
            st.session_state.step = 3; st.rerun()

# --- ADIM 3: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("🚬 Adım 3: Alışkanlıklar")
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if sigara == "Evet":
        st.warning("⚠️ Sigara sağlığınız için tehlikelidir, bırakmanız tavsiye edilir.")
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

# --- ADIM 4: BELİRTİLER ---
elif st.session_state.step == 4:
    st.title("⚠️ Adım 4: Belirtiler")
    
    g_a = st.radio("Göğsünüzde ağrı veya baskı hissi var mı?", ["Hayır", "Evet"], horizontal=True)
    if g_a == "Evet": st.selectbox("Ağrı tipi:", ["Hafif batma", "Baskı hissi", "Sıkışma", "Keskin ağrı"])
    
    st.markdown("---")
    oksuruk = st.radio("Sürekli öksürük şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if oksuruk == "Evet":
        st.session_state.data['oksuruk_tip'] = st.selectbox("Öksürük tipi:", ["Hafif kuru öksürük", "Sık balgamlı öksürük", "Şiddetli öksürük", "Kanlı öksürük"])
        if st.session_state.data['oksuruk_tip'] == "Kanlı öksürük":
            st.markdown("### 🚨 CİDDİ UYARI: Kanlı öksürük acil tıbbi değerlendirme gerektiren kritik bir belirtidir!")

    st.markdown("---")
    nefes = st.radio("Nefes darlığı şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if nefes == "Evet":
        st.session_state.data['nefes_tip'] = st.selectbox("Düzey:", ["Nadiren", "Merdiven çıkarken/yürürken", "Dinlenirken bile"])
        if st.session_state.data['nefes_tip'] == "Dinlenirken bile":
            st.warning("⚠️ UYARI: Dinlenme sırasında nefes darlığı yaşanması ileri düzey solunum problemlerinin belirtisi olabilir.")

    st.markdown("---")
    yutkunma = st.radio("Yutkunurken güçlük çekiyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if yutkunma == "Evet": st.selectbox("Durum:", ["Nadiren", "Katı gıdalar tüketirken", "Sıvı tüketirken bile"])
    
    st.markdown("---")
    stres = st.radio("Yoğun stres veya anksiyete yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if stres == "Evet": st.selectbox("Sıklık:", ["Ara sıra", "Sık sık", "Sürekli"])
    
    st.markdown("---")
    yorgunluk = st.radio("Aşırı yorgunluk veya halsizlik yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if yorgunluk == "Evet": st.selectbox("Derece:", ["Ara sıra", "Sık sık", "Günlük hayatımı etkiliyor"])
    
    st.markdown("---")
    parmak = st.radio("Parmaklarınızda sararma veya sarı lekeler var mı?", ["Hayır", "Evet"], horizontal=True)
    if parmak == "Evet": st.selectbox("Miktar:", ["Çok az/birkaç parmağımda var", "Belirgin şekilde var", "Neredeyse bütün parmaklarımda var"])

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 3; st.rerun()
    if col2.button("Analiz Et"):
        st.session_state.data['g_a'] = g_a
        st.session_state.data['oksuruk'] = oksuruk
        st.session_state.data['nefes'] = nefes
        st.session_state.data['yutkunma'] = yutkunma
        st.session_state.data['stres'] = stres
        st.session_state.data['yorgunluk'] = yorgunluk
        st.session_state.data['parmak'] = parmak
        st.session_state.step = 5
        st.rerun()

# --- ADIM 5: GERÇEKÇİ AI ANALİZ VE VERİ TABANI KAYDI ---
elif st.session_state.step == 5:
    st.title("📊 Akıllı Risk Analiz Raporu")
    
    d = st.session_state.data 

    # --- MODELİN SÜTUN SIRALAMASINA GÖRE BİREBİR EŞLEME ---
    veriler = [
        1 if d.get('cinsiyet') == "Erkek" else 0,                               # GENDER
        d.get('yas', 45),                                                       # AGE
        2 if d.get('sigara') == "Evet" else 1,                                 # SMOKING
        2 if d.get('parmak') == "Evet" else 1,                                 # YELLOW_FINGERS
        2 if d.get('stres') == "Evet" else 1,                                  # ANXIETY
        2 if d.get('sigara') == "Evet" or d.get('alkol') == "Evet" else 1, # PEER_PRESSURE
        2 if d.get('kronik') == "Evet" else 1,                                 # CHRONIC_DISEASE
        2 if d.get('yorgunluk') == "Evet" else 1,                              # FATIGUE
        2 if d.get('genetik') == "Evet" or d.get('kronik') == "Evet" else 1, # ALLERGY
        2 if d.get('nefes') == "Evet" else 1,                                  # WHEEZING
        2 if d.get('alkol') == "Evet" else 1,                                  # ALCOHOL_CONSUMING
        2 if d.get('oksuruk') == "Evet" else 1,                                # COUGHING
        2 if d.get('nefes') == "Evet" else 1,                                  # SHORTNESS_OF_BREATH
        2 if d.get('yutkunma') == "Evet" else 1,                               # SWALLOWING_DIFFICULTY
        2 if d.get('g_a') == "Evet" else 1                                     # CHEST_PAIN
    ]
    
    # Modelden saf olasılık sonucunu alıyoruz
    tahmin_orani = yapay_zekadan_tahmin_al(veriler)
    risk = int(tahmin_orani * 100)
    
    # 🌟 KLİNİK HİBRİT FORMÜL (Her şeye Evet diyen profil düzeltmesi)
    evet_sayisi = sum([1 for v in veriler[2:] if v == 2]) 
    
    if evet_sayisi >= 10:
        risk = max(risk, 95) # Neredeyse tüm belirtiler varsa %95-99 arası yüksek risk yap
    elif evet_sayisi >= 6:
        risk = max(risk, 70) # Belirtilerin yarısından profesyonelce fazlası varsa en az %70 yüksek risk yap
    elif evet_sayisi <= 1:
        risk = min(risk, 20) # Neredeyse hiç belirti yoksa en fazla %20 düşük risk yap

    # %5 ile %99 arasında sınırla
    risk = max(5, min(risk, 99))
    
    # --- VERİ TABANINA KAYDETME ---
    if 'kaydedildi' not in st.session_state:
        veritabanina_kaydet(
            d.get('yas'), d.get('cinsiyet'), d.get('sigara'), d.get('alkol'), d.get('kronik'),
            d.get('g_a'), d.get('oksuruk'), d.get('nefes'), d.get('yutkunma'), d.get('stres'),
            d.get('yorgunluk'), d.get('parmak'), risk
        )
        st.session_state.kaydedildi = True

    # GRAFİK GÖSTERİMİ
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
        st.success("✅ Risk oranınız düşük seviye belirlenmiştir. Sağlığınızı korumak için şu adımları izleyin:")
        st.write("Düzenli yürüyüş, Nefes egzersizi, Sigaradan uzak durma, Düzenli uyku ve Sağlıklı beslenme.")
    elif 34 <= risk <= 66:
        st.markdown("### ⚠️ Orta Risk")
        st.warning("🟡 Risk oranınız orta seviyede belirlenmiştir. Yaşam alışkanlıklarınızı gözden geçirmeniz önerilir.")
        st.write("Motivasyon: Sağlığınız için küçük değişiklikler büyük farklar yaratabilir.")
    else:
        st.markdown("### 🛑 Dikkat: Yüksek Risk")
        st.error("🚨 Analiz sonucunuz yüksek risk grubunda olduğunuzu göstermektedir.")
        st.write("Motivasyon: Sağlığınız için adım atmak asla geç değildir. Belirtileriniz tıbbi profesyonel denetimi gerektir")