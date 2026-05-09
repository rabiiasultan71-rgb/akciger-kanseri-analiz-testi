import streamlit as st
import plotly.graph_objects as go
import base64
import os
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="LUNG AI | Profesyonel Analiz", layout="centered")

# --- ARKA PLAN VE GÖRSEL TASARIM (GLASSMORPHISM) ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Belirttiğin yerel dosya yolu
image_path = r"C:\Users\rabia\Downloads\arkaplan (2).jpg"

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
            background-color: rgba(0, 0, 0, 0.82); /* Profesyonel koyu katman */
            z-index: -1;
        }}
        /* Form Alanları ve Cam Efekti */
        div[data-baseweb="select"], div[data-baseweb="input"], .stRadio {{
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            padding: 5px !important;
            color: white !important;
        }}
        /* Yazı Okunabilirliği */
        h1, h2, h3, label, p {{
            color: #FFFFFF !important;
            font-weight: 300 !important;
            text-shadow: 1px 1px 2px black;
        }}
        .stButton>button {{
            background: #00f2ff33 !important;
            color: white !important;
            border: 1px solid #00f2ff !important;
            border-radius: 20px !important;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background: #00f2ff66 !important;
            box-shadow: 0 0 15px #00f2ff;
        }}
        </style>
        """, unsafe_allow_html=True)
except:
    st.info("Arka plan görseli yerel yolda bulunamadı. Lütfen Render için resmi GitHub'a yükleyin.")

# --- SESSION STATE YÖNETİMİ ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = {}

# --- ADIM 1: GİRİŞ ---
if st.session_state.step == 1:
    st.title("🩺 Kişisel Bilgiler")
    yas_val = st.text_input("Yaşınız:", placeholder="Örn: 25")
    cinsiyet = st.selectbox("Cinsiyetiniz:", ["Seçiniz", "Erkek", "Kadın"])
    
    error = False
    if yas_val:
        if "." in yas_val or "," in yas_val:
            st.error("🚨 Kesinlikle buçuklu veya ondalıklı sayı girilemez.")
            error = True
        elif not yas_val.isdigit():
            st.error("🚨 Lütfen sadece sayı giriniz.")
            error = True
        elif int(yas_val) > 85:
            st.error("🚨 Maksimum yaş sınırı 85'tir.")
            error = True
            
    if st.button("İlerle") and not error and yas_val and cinsiyet != "Seçiniz":
        st.session_state.data['yas'] = int(yas_val)
        st.session_state.data['cinsiyet'] = cinsiyet
        st.session_state.step = 2
        st.rerun()

# --- ADIM 2: SAĞLIK GEÇMİŞİ ---
elif st.session_state.step == 2:
    st.title("🧬 Sağlık Geçmişi")
    
    kronik = st.radio("Kronik bir rahatsızlığınız var mı?", ["Hayır", "Evet"], horizontal=True)
    if kronik == "Evet":
        st.session_state.data['kronik_detay'] = st.selectbox("Nedir?", ["Seçiniz", "KOAH", "Astım", "Bronşit", "Diğer"])
    
    st.markdown("---")
    genetik = st.radio("Ailenizde akciğer kanseri geçmişi var mı?", ["Hayır", "Evet"], horizontal=True)
    if genetik == "Evet":
        st.session_state.data['yakinlik'] = st.selectbox("Yakınlık Derecesi:", 
            ["Anne-Baba-Kardeş", "Dede-Anane-Babaanne", "Teyze-Hala-Amca-Dayı", "Uzak Akraba"])

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 1; st.rerun()
    if col2.button("İlerle"): st.session_state.step = 3; st.rerun()

# --- ADIM 3: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("🚬 Alışkanlıklar")
    
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if sigara == "Evet":
        st.session_state.data['sigara_siklik'] = st.selectbox("Kullanım sıklığı:", 
            ["Günde birkaç tane", "Günde yarım paket", "Günde bir paket", "Günde bir paketten fazla"])
    
    st.markdown("---")
    alkol = st.radio("Alkol kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if alkol == "Evet":
        st.session_state.data['alkol_siklik'] = st.selectbox("Kullanım sıklığı:", 
            ["Özel günlerde", "Ayda bir", "Haftada birkaç kez", "Her gün"])

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 2; st.rerun()
    if col2.button("İlerle"): st.session_state.step = 4; st.rerun()

# --- ADIM 4: BELİRTİLER ---
elif st.session_state.step == 4:
    st.title("⚠️ Belirtiler")
    
    # 1. Göğüs Ağrısı
    gogus = st.radio("Göğsünüzde ağrı veya baskı hissi var mı?", ["Hayır", "Evet"], horizontal=True)
    if gogus == "Evet":
        st.session_state.data['gogus_tip'] = st.selectbox("Ağrı Tipi:", ["Hafif batma", "Baskı hissi", "Sıkışma", "Keskin ağrı"])

    # 2. Öksürük
    oksuruk = st.radio("Sürekli öksürük şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if oksuruk == "Evet":
        st.session_state.data['oksuruk_tip'] = st.selectbox("Öksürük Tipi:", ["Hafif kuru öksürük", "Sık balgamlı öksürük", "Şiddetli öksürük", "Kanlı öksürük"])

    # 3. Nefes Darlığı
    nefes = st.radio("Nefes darlığı şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if nefes == "Evet":
        st.session_state.data['nefes_tip'] = st.selectbox("Düzey:", ["Nadiren", "Merdiven çıkarken/yürürken", "Dinlenirken bile"])

    # 4. Yutkunma
    yutkunma = st.radio("Yutkunurken güçlük çekiyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if yutkunma == "Evet":
        st.session_state.data['yutkunma_tip'] = st.selectbox("Zorluk Derecesi:", ["Nadiren", "Katı gıdalar tüketirken", "Sıvı tüketirken bile"])

    # 5. Stres
    stres = st.radio("Yoğun stres veya anksiyete yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if stres == "Evet":
        st.session_state.data['stres_tip'] = st.selectbox("Sıklık:", ["Ara sıra", "Sık sık", "Sürekli"])

    # 6. Yorgunluk
    yorgunluk = st.radio("Aşırı yorgunluk veya halsizlik yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if yorgunluk == "Evet":
        st.session_state.data['yorgunluk_tip'] = st.selectbox("Derece:", ["Ara sıra", "Sık sık", "Günlük hayatımı etkiliyor"])

    # 7. Parmak Sararması
    parmak = st.radio("Parmaklarınızda sararma veya sarı lekeler var mı?", ["Hayır", "Evet"], horizontal=True)
    if parmak == "Evet":
        st.session_state.data['parmak_tip'] = st.selectbox("Miktar:", ["Çok az/birkaç parmağımda var", "Belirgin şekilde var", "Neredeyse bütün parmaklarımda var"])

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 3; st.rerun()
    if col2.button("Analiz Et"): st.session_state.step = 5; st.rerun()

# --- ADIM 5: ANALİZ SONUCU ---
elif st.session_state.step == 5:
    st.title("📊 Analiz Sonucunuz")
    
    # Risk Puanlama (Basit AI Mantığı)
    risk_score = 10
    if st.session_state.data.get('sigara_siklik') == "Günde bir paketten fazla": risk_score += 40
    if st.session_state.data.get('oksuruk_tip') == "Kanlı öksürük": risk_score += 45
    if st.session_state.data.get('nefes_tip') == "Dinlenirken bile": risk_score += 25
    risk_score = min(risk_score, 99)

    # CANLI VE İNCE GRAFİK (Plotly Gauge)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_score,
        number = {'suffix': "%", 'font': {'color': "#00f2ff", 'size': 50}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#00f2ff", 'thickness': 0.1}, # İnce çizgi
            'steps': [
                {'range': [0, 30], 'color': "#00ff88"},
                {'range': [30, 70], 'color': "#ffcc00"},
                {'range': [70, 100], 'color': "#ff4444"}]
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Arial"}, height=350)
    st.plotly_chart(fig, use_container_width=True)

    # ANALİZ VE UYARI MESAJLARI
    st.subheader("📝 Değerlendirme")
    
    # Özel Kritik Uyarılar
    if st.session_state.data.get('oksuruk_tip') == "Kanlı öksürük":
        st.error("🚨 **KRİTİK UYARI:** Kanlı öksürük ciddi bir semptomdur. Lütfen vakit kaybetmeden muayene olunuz.")
    
    if st.session_state.data.get('sigara_siklik') in ["Günde bir paket", "Günde bir paketten fazla"]:
        st.warning("⚠️ **DİKKAT:** Yoğun sigara kullanımı akciğer dokusundaki riski doğrudan ve hızla artırmaktadır.")

    # Risk Seviyesine Göre Tavsiyeler
    if risk_score > 60:
        st.markdown("### 🔴 Yüksek Risk Saptandı")
        st.write("Motivasyon: Sağlığınız her şeyden değerlidir. Belirtileriniz bir uzman kontrolü gerektiriyor.")
        st.info("🏥 **Önerilen Bölümler:** Göğüs Hastalıkları, Onkoloji, Dahiliye")
    else:
        st.markdown("### 🟢 Düşük / Orta Risk Saptandı")
        st.write("Motivasyon: Sağlıklı alışkanlıklar kazanarak risk faktörlerini minimize edebilirsiniz.")
        st.success("✨ **Sağlıklı Yaşam Önerileri:** Düzenli yürüyüşler yapın, nefes egzersizlerini günlük rutininize ekleyin ve sigara dumanından uzak durun.")

    st.markdown("---")
    st.caption("ℹ️ *Bu analiz yapay zekâ tarafından hazırlanmıştır, kesin teşhis yerine geçmez. Lütfen profesyonel tıbbi destek alınız.*")

    if st.button("Yeni Analiz Başlat"):
        st.session_state.step = 1; st.rerun()
