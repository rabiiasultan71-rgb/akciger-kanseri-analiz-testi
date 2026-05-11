import streamlit as st
import plotly.graph_objects as go
import base64
import os
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="LUNG AI | Profesyonel Akciğer Risk Analizi", layout="centered")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Resim Yolu (GitHub'daki isimle birebir aynı olmalı)
image_path = "arkaplan.jpg" 

if os.path.exists(image_path):
    bin_str = get_base64(image_path)
    # --- YENİLENMİŞ, KOYU VE FORM ALANLARI BELİRGİN STİL CSS (iOS Dostu) ---
    st.markdown(f"""
    <style>
    /* Temel Arka Plan */
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover; background-attachment: fixed; background-position: center;
    }}
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.88); z-index: -1;
    }}
    
    /* Form Alanları (Cam Paneller - Glassmorphism) */
    div[data-baseweb="select"], div[data-baseweb="input"], .stRadio, div.stChatMessage, div.stAlert {{
        background: rgba(255, 255, 255, 0.08) !important;
        border: 2px solid rgba(0, 242, 255, 0.4) !important; /* Form alanlarını daha belirgin yapar */
        border-radius: 12px !important;
        color: white !important;
        -webkit-backdrop-filter: blur(10px); /* iOS için bulanıklık */
        backdrop-filter: blur(10px);
    }}
    
    /* Input Metin Rengi ve Netlik */
    input, select, .stRadio label {{
        color: white !important; font-size: 16px !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }}
    
    /* BAŞLIK VE YAZI DÜZELTMELERİ - Okunabilirlik garantili */
    h1, h2, h3, label, p, .stMarkdown, .stCaption {{ 
        color: white !important; 
        font-weight: 300 !important; 
        text-shadow: 1px 1px 5px rgba(0,0,0,1); /* Yazıları her koşulda okunur yapar */
    }}
    
    /* MAVİ OLAN BAŞLIĞI BEYAZ YAPMA */
    h3 {{
        color: white !important; 
        font-weight: 400 !important;
    }}

    /* BUTON STİLLERİ (iOS'ta düzgün görünmesi için native streamlit yapısı) */
    .stButton>button {{
        width: 100%;
        background: linear-gradient(135deg, rgba(0, 242, 255, 0.1), rgba(0, 242, 255, 0.05)) !important;
        color: #00FFFF !important; /* Canlı firuze */
        border: 2px solid #00FFFF !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
        -webkit-appearance: none; /* iOS native buton görünümünü kaldırır */
    }}
    .stButton>button:hover {{
        background: #00FFFF !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00FFFF;
    }}
    
    /* Grafik ve Alert Panellerini Özelleştirme */
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
        if not yas_val:
            st.error("🚨 Lütfen bir yaş giriniz.")
        elif "." in yas_val or "," in yas_val:
            st.error("🚨 Lütfen 0-85 arasında tam sayı giriniz. Ondalıklı sayı yasak.")
        elif not yas_val.strip().isdigit():
            st.error("🚨 Negatif sayı veya harf yasak. Lütfen 0-85 arasında tam sayı giriniz.")
        elif int(yas_val) > 85 or int(yas_val) < 0:
            st.error("🚨 Lütfen 0-85 arasında tam sayı giriniz.")
        elif cinsiyet == "Seçiniz":
            st.error("🚨 Lütfen cinsiyet seçiniz.")
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
        st.session_state.data['yakinlik'] = st.selectbox("Yakınlık derecesi:", [" Anne-Baba-Kardeş", "Dede-Anane-Babaanne", "Teyze-Hala-Amca-Dayı", "Uzak akraba"])
    
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
    if col2.button("Analiz Et"): st.session_state.step = 5; st.rerun()

# --- ADIM 5: AKILLI VE GERÇEKÇİ ANALİZ SİSTEMİ ---
elif st.session_state.step == 5:
    st.title("📊 Akıllı Risk Analiz Raporu")
    
    # GERÇEKÇİ RİSK ALGORİTMASI
    risk = 10 # Temel risk (0-85 yaş ve ondalık sayı kontrolleri yapıldı)
    
    if st.session_state.data.get('yas') > 40: risk += 5
    if st.session_state.data.get('yas') > 60: risk += 5
    
    if st.session_state.data.get('sigara') == "Evet":
        risk += 25
        if st.session_state.data.get('sigara_siklik') in ["Günde bir paket", "Günde bir paketten fazla"]: risk += 20
        
    if st.session_state.data.get('genetik') == "Evet": risk += 10
    if st.session_state.data.get('kronik') == "Evet": risk += 10
    
    if st.session_state.data.get('oksuruk_tip') == "Kanlı öksürük": risk += 40
    if st.session_state.data.get('nefes_tip') == "Dinlenirken bile": risk += 20
    
    risk = min(risk, 99) # Maksimum sınır kontrolü

    # CANLI VE İNCE GRAFİK (Turkuaz dolgu ve ince çizgi)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = risk,
        number = {'suffix': "%", 'font': {'color': "#00FFFF", 'size': 50}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#00FFFF", 'thickness': 0.1}, # İnce çizgi halinde
            'steps': [
                {'range': [0, 30], 'color': "#00ff88"},
                {'range': [30, 70], 'color': "#ffcc00"},
                {'range': [70, 100], 'color': "#ff4444"}]
        }))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

    # AKILLI RİSK YORUMLAMA
    st.subheader("🤖 AI Risk Analiz Yorumu")
    
    # Alkol Uyarıları (Gelişmiş)
    if st.session_state.data.get('alkol_siklik') in ["Haftada birkaç kez", "Her gün"]:
        st.warning("⚠️ Yoğun alkol kullanımı bağışıklık ve solunum sistemi üzerinde olumsuz etkilere neden olabilir.")
        if risk > 60:
            st.write("*Sigara ve yoğun alkol kullanımı birlikte değerlendirildiğinde akciğer hastalıkları riski artmış olabilir.*")

    # Genetik Faktör Analizi (1. Derece ve Puan Birleşimi)
    is_first_degree = st.session_state.data.get('yakinlik') == " Anne-Baba-Kardeş"
    if st.session_state.data.get('genetik') == "Evet":
        if risk > 70 and is_first_degree:
            st.error("⚠️ Birinci derece aile bireylerinde akciğer kanseri öyküsü bulunması genetik risk faktörünü artırabilir. Uzman doktora başvurmanız önerilir.")
        elif risk >= 40 and is_first_degree:
            st.warning("⚠️ Aile geçmişiniz nedeniyle düzenli kontrol yaptırmanız önerilir.")

    # Sigara Uyarıları (Yoğun Kullanım)
    if st.session_state.data.get('sigara_siklik') in ["Günde bir paket", "Günde bir paketten fazla"]:
        st.error("⚠️ Uzun süreli yoğun sigara kullanımı akciğer kanseri riskini ciddi oranda artırabilir.")

    # GENEL ÖNERİLER VE MOTİVASYON
    if risk > 60:
        st.markdown("### 🛑 Dikkat: Yüksek Risk")
        st.write("Motivasyon: Sağlığınız için adım atmak asla geç değildir. Belirtileriniz tıbbi profesyonel denetimi gerektiriyor.")
        # Doktor Önerileri (Oncology, Internal Medicine)
        st.info("🏥 **Önerilen Bölümler (Oncology & Internal Medicine):** Göğüs Hastalıkları, Onkoloji, Dahiliye")
    else:
        st.markdown("### ✨ Düşük Risk Önerileri")
        st.write("Sağlığınızı korumak için şu adımları izleyin:")
        st.success("✅ Düzenli yürüyüş, Nefes egzersizi, Sigaradan uzak durma, Düzenli uyku ve Sağlıklı beslenme.")

    st.markdown("---")
    # Sayfa Altı Bilgilendirme Notu
    st.caption("“Bu analiz yapay zekâ tarafından oluşturulmuştur. Kesin teşhis yerine geçmez. Sağlık durumunuz için uzman doktora başvurunuz.”")
    
    if st.button("Yeniden Başlat"): 
        st.session_state.step = 1
        st.rerun()
