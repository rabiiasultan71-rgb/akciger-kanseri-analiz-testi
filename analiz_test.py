import streamlit as st
import plotly.graph_objects as go
import base64
import os
import time

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="LUNG AI | Akciğer Risk Analizi", layout="centered")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Render ve GitHub için görsel yolu
image_path = "arkaplan (2).jpg" 

if os.path.exists(image_path):
    bin_str = get_base64(image_path)
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover; background-attachment: fixed;
    }}
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.88); z-index: -1;
    }}
    /* Form Alanları */
    div[data-baseweb="select"], div[data-baseweb="input"], .stRadio {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(0, 242, 255, 0.4) !important;
        border-radius: 12px !important;
        color: white !important;
    }}
    h1, h2, h3, label, p {{ color: white !important; font-weight: 300 !important; }}
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

# --- ADIM 2: SAĞLIK GEÇMİŞİ ---
elif st.session_state.step == 2:
    st.title("🧬 Adım 2: Sağlık ve Genetik")
    kronik = st.radio("Kronik bir rahatsızlığınız var mı?", ["Hayır", "Evet"], horizontal=True)
    if kronik == "Evet":
        st.session_state.data['kronik_tip'] = st.selectbox("Nedir?", ["KOAH", "Astım", "Bronşit", "Diğer"])
    
    genetik = st.radio("Ailenizde akciğer kanseri genetiği var mı?", ["Hayır", "Evet"], horizontal=True)
    if genetik == "Evet":
        st.session_state.data['yakinlik'] = st.selectbox("Yakınlık derecesi:", ["Anne-Baba-Kardeş", "Dede-Anane-Babaanne", "Teyze-Hala-Amca-Dayı", "Uzak akraba"])
    
    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 1; st.rerun()
    if col2.button("İlerle"): 
        st.session_state.data['kronik'] = kronik
        st.session_state.data['genetik'] = genetik
        st.session_state.step = 3; st.rerun()

# --- ADIM 3: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("🚬 Adım 3: Alışkanlıklar")
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if sigara == "Evet":
        st.session_state.data['sigara_siklik'] = st.selectbox("Kullanım sıklığı:", ["Günde birkaç tane", "Günde yarım paket", "Günde bir paket", "Günde bir paketten fazla"])
    
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
    
    oksuruk = st.radio("Sürekli öksürük şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if oksuruk == "Evet":
        st.session_state.data['oksuruk_tip'] = st.selectbox("Öksürük tipi:", ["Hafif kuru öksürük", "Sık balgamlı öksürük", "Şiddetli öksürük", "Kanlı öksürük"])
        if st.session_state.data['oksuruk_tip'] == "Kanlı öksürük":
            st.error("⚠️ CİDDİ UYARI: Kanlı öksürük acil tıbbi değerlendirme gerektiren kritik bir belirtidir!")

    nefes = st.radio("Nefes darlığı şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if nefes == "Evet":
        st.session_state.data['nefes_tip'] = st.selectbox("Düzey:", ["Nadiren", "Merdiven çıkarken/yürürken", "Dinlenirken bile"])
        if st.session_state.data['nefes_tip'] == "Dinlenirken bile":
            st.warning("⚠️ UYARI: Dinlenme sırasında nefes darlığı yaşanması ileri düzey solunum problemlerinin belirtisi olabilir.")

    yutkunma = st.radio("Yutkunurken güçlük çekiyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if yutkunma == "Evet": st.selectbox("Durum:", ["Nadiren", "Katı gıdalar tüketirken", "Sıvı tüketirken bile"])
    
    stres = st.radio("Yoğun stres veya anksiyete yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if stres == "Evet": st.selectbox("Sıklık:", ["Ara sıra", "Sık sık", "Sürekli"])
    
    yorgunluk = st.radio("Aşırı yorgunluk veya halsizlik yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if yorgunluk == "Evet": st.selectbox("Derece:", ["Ara sıra", "Sık sık", "Günlük hayatımı etkiliyor"])
    
    parmak = st.radio("Parmaklarınızda sararma veya sarı lekeler var mı?", ["Hayır", "Evet"], horizontal=True)
    if parmak == "Evet": st.selectbox("Miktar:", ["Çok az/birkaç parmağımda var", "Belirgin şekilde var", "Neredeyse bütün parmaklarımda var"])

    col1, col2 = st.columns(2)
    if col1.button("Geri"): st.session_state.step = 3; st.rerun()
    if col2.button("Analiz Et"): st.session_state.step = 5; st.rerun()

# --- ADIM 5: AKILLI ANALİZ SİSTEMİ ---
elif st.session_state.step == 5:
    st.title("📊 Akıllı Risk Analiz Raporu")
    
    # RİSK ALGORİTMASI
    risk = 10
    if st.session_state.data.get('sigara') == "Evet": risk += 25
    if st.session_state.data.get('sigara_siklik') in ["Günde bir paket", "Günde bir paketten fazla"]: risk += 20
    if st.session_state.data.get('oksuruk_tip') == "Kanlı öksürük": risk += 40
    if st.session_state.data.get('genetik') == "Evet": risk += 10
    risk = min(risk, 99)

    # GRAFİK
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = risk,
        number = {'suffix': "%", 'font': {'color': "#00f2ff", 'size': 50}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#00f2ff", 'thickness': 0.1},
            'steps': [
                {'range': [0, 30], 'color': "#00ff88"},
                {'range': [30, 70], 'color': "#ffcc00"},
                {'range': [70, 100], 'color': "#ff4444"}]
        }))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

    # AKILLI RİSK YORUMLAMA
    st.subheader("🤖 AI Risk Analiz Yorumu")
    
    # Alkol Uyarıları
    if st.session_state.data.get('alkol_siklik') in ["Haftada birkaç kez", "Her gün"]:
        st.warning("⚠️ Yoğun alkol kullanımı bağışıklık ve solunum sistemi üzerinde olumsuz etkilere neden olabilir.")
        if risk > 60:
            st.write("*Sigara ve yoğun alkol kullanımı birlikte değerlendirildiğinde akciğer hastalıkları riski artmış olabilir.*")

    # Genetik Faktör Analizi
    is_first_degree = st.session_state.data.get('yakinlik') == "Anne-Baba-Kardeş"
    if st.session_state.data.get('genetik') == "Evet":
        if risk > 70 and is_first_degree:
            st.error("⚠️ Birinci derece aile bireylerinde akciğer kanseri öyküsü bulunması genetik risk faktörünü artırabilir. Uzman doktora başvurmanız önerilir.")
        elif risk >= 40 and is_first_degree:
            st.warning("⚠️ Aile geçmişiniz nedeniyle düzenli kontrol yaptırmanız önerilir.")

    # Sigara Uyarıları
    if st.session_state.data.get('sigara_siklik') in ["Günde bir paket", "Günde bir paketten fazla"]:
        st.error("⚠️ Uzun süreli yoğun sigara kullanımı akciğer kanseri riskini ciddi oranda artırabilir.")

    # GENEL ÖNERİLER
    if risk > 60:
        st.markdown("### 🛑 Dikkat: Yüksek Risk")
        st.write("Motivasyon: Sağlığınız için adım atmak asla geç değildir. Belirtileriniz tıbbi profesyonel denetimi gerektiriyor.")
        st.info("🏥 **Önerilen Bölümler (Oncology & Internal Medicine):** Göğüs Hastalıkları, Onkoloji, Dahiliye")
    else:
        st.markdown("### ✨ Düşük Risk Önerileri")
        st.write("Sağlığınızı korumak için şu adımları izleyin:")
        st.success("✅ Düzenli yürüyüş, Nefes egzersizi, Sigaradan uzak durma, Düzenli uyku ve Sağlıklı beslenme.")

    st.markdown("---")
    st.caption("“Bu analiz yapay zekâ tarafından oluşturulmuştur. Kesin teşhis yerine geçmez. Sağlık durumunuz için uzman doktora başvurunuz.”")
    
    if st.button("Yeniden Başlat"): st.session_state.step = 1; st.rerun()
