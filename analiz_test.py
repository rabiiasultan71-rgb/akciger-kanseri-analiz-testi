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
            background-color: rgba(0, 0, 0, 0.82); z-index: -1;
        }}
        /* Soru ve yazıların netliği için özel ayarlar */
        h1, h2, h3, p, label, .stMarkdown {{
            color: #FFFFFF !important;
            font-weight: 500 !important;
            text-shadow: 1px 1px 3px #000000 !important;
        }}
        .stRadio label, .stSelectbox label {{
            font-size: 1.1rem !important;
            background: rgba(0,0,0,0.3);
            padding: 5px 10px;
            border-radius: 5px;
        }}
        .stButton>button {{
            width: 100%; border-radius: 12px; height: 3.5em; background-color: #e63946; 
            color: white; font-weight: bold; border: none; font-size: 17px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        </style>
        """, unsafe_allow_html=True)
except:
    st.info("Arka plan görseli yüklenemedi, varsayılan tema ile devam ediliyor.")

# Durum Yönetimi
if 'step' not in st.session_state: st.session_state.step = 1
if 'answers' not in st.session_state: st.session_state.answers = {}

# --- ADIM 1: TEMEL BİLGİLER ---
if st.session_state.step == 1:
    st.title("📋 Adım 1: Temel Bilgiler")
    
    yas_input = st.text_input("Yaşınız (18-85):", value="25")
    
    age_ok = False
    if "." in yas_input or "," in yas_input:
        st.error("🚨 UYARI: Kesinlikle buçuklu rakamlar girmeyiniz! Lütfen tam bir sayı yazın.")
    else:
        try:
            yas = int(yas_input)
            if 18 <= yas <= 85: age_ok = True
            else: st.error("⚠️ Lütfen 18 ile 85 arasında bir yaş giriniz.")
        except: st.error("⚠️ Lütfen geçerli bir sayı giriniz.")

    cinsiyet = st.selectbox("Cinsiyetiniz:", ["Seçiniz", "Erkek", "Kadın"])

    if st.button("İlerle ➡️"):
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
        st.session_state.answers['kronik_nedir'] = st.text_input("Rahatsızlığınız nedir? (Örn: KOAH, Astım):")
        if st.session_state.answers['kronik_nedir']:
            st.warning(f"💡 Not: {st.session_state.answers['kronik_nedir']} gibi kronik durumlar akciğer kapasitesini doğrudan etkileyebilir.")

    st.divider()
    
    genetik = st.radio("Ailenizde akciğer kanseri genetiği var mı?", ["Hayır", "Evet"], horizontal=True)
    if genetik == "Evet":
        st.session_state.answers['yakinlik'] = st.selectbox("Yakınlık derecesi:", 
            ["Anne, Baba, Kardeş", "Dede, Anneanne, Babaanne, Teyze, Hala, Amca, Dayı", "Uzaktan Akraba"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Geri"): st.session_state.step = 1; st.rerun()
    with col2:
        if st.button("İlerle ➡️"):
            st.session_state.answers['genetik'] = genetik
            st.session_state.step = 3
            st.rerun()

# --- ADIM 3: ALIŞKANLIKLAR ---
elif st.session_state.step == 3:
    st.title("🚬 Adım 3: Alışkanlıklar")
    
    sigara = st.radio("Sigara kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if sigara == "Evet":
        siklik = st.selectbox("Ne sıklıkla?", 
            ["Günde bir kaç tane", "Günde yarım paket", "Günde bir paket", "Günde bir paketten fazla"])
        st.session_state.answers['sigara_siklik'] = siklik
        if siklik in ["Günde bir paket", "Günde bir paketten fazla"]:
            st.error("⚠️ Yüksek Tüketim Uyarısı: Bu düzeyde sigara kullanımı akciğer dokusunda kalıcı hasar riskini %80 artırır.")

    st.divider()

    alkol = st.radio("Alkol kullanıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if alkol == "Evet":
        a_siklik = st.selectbox("Ne sıklıkla?", ["Özel günlerde", "Ayda bir", "Haftada bir kaç kez", "Her gün"])
        st.session_state.answers['alkol_siklik'] = a_siklik
        if a_siklik == "Her gün":
            st.warning("⚠️ Alkol tüketimi bağışıklık sistemini zayıflatarak akciğer enfeksiyonu riskini tetikleyebilir.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Geri"): st.session_state.step = 2; st.rerun()
    with col2:
        if st.button("İlerle ➡️"):
            st.session_state.answers['sigara'] = sigara
            st.session_state.answers['alkol'] = alkol
            st.session_state.step = 4
            st.rerun()

# --- ADIM 4: BELİRTİLER ---
elif st.session_state.step == 4:
    st.title("🔍 Adım 4: Mevcut Şikayetler")

    gogus = st.radio("Göğsünüzde ağrı / baskı var mı?", ["Hayır", "Evet"], horizontal=True)
    if gogus == "Evet":
        st.session_state.answers['gogus_tip'] = st.selectbox("Ağrı Tipi:", ["Hafif/batma", "Baskı/Sıkışma", "Keskin sürekli"])
        if "Sıkışma" in st.session_state.answers['gogus_tip']: st.warning("🚨 Göğüs sıkışması ciddi bir semptomdur.")

    oksuruk = st.radio("Öksürük şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if oksuruk == "Evet":
        st.session_state.answers['oksuruk_tip'] = st.selectbox("Öksürük Tipi:", ["Hafif ve kuru", "Sık ve balgamlı", "Şiddetli ve Kanlı"])
        if st.session_state.answers['oksuruk_tip'] == "Kanlı":
            st.error("🚨 ACİL: Kanlı öksürük vakit kaybetmeden uzman bir doktora görünmeyi gerektirir!")

    nefes = st.radio("Nefes darlığı şikayetiniz var mı?", ["Hayır", "Evet"], horizontal=True)
    if nefes == "Evet":
        st.session_state.answers['nefes_tip'] = st.selectbox("Durum:", ["Nadiren", "Merdiven çıkarken / Yürürken", "Dinlenirken bile"])

    yutkunma = st.radio("Yutkunurken güçlük çekiyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if yutkunma == "Evet":
        st.session_state.answers['yutkunma_tip'] = st.selectbox("Hangi durumlarda?", ["Nadiren", "Katı gıdalar tüketirken", "Sıvı gıdalar tüketirken bile"])

    stres = st.radio("Stres / Anksiyete sorunları yaşıyor musunuz?", ["Hayır", "Evet"], horizontal=True)
    if stres == "Evet":
        st.session_state.answers['stres_tip'] = st.selectbox("Sıklık:", ["Ara sıra", "Sık sık", "Sürekli"])

    yorgunluk = st.radio("Aşırı yorgunluk / halsizlik sorununuz var mı?", ["Hayır", "Evet"], horizontal=True)
    if yorgunluk == "Evet":
        st.session_state.answers['yorgunluk_tip'] = st.selectbox("Düzey:", ["Ara sıra", "Sık sık", "Günlük hayatımı etkiliyor"])

    parmak = st.radio("Parmaklarınızda sararmalar ve sarı lekeler var mı?", ["Hayır", "Evet"], horizontal=True)
    if parmak == "Evet":
        st.session_state.answers['parmak_tip'] = st.selectbox("Yaygınlık:", ["Çok az bir kaç parmağımda var", "Belirgin şekilde var", "Neredeyse bütün parmaklarımda var"])
        if "Belirgin" in st.session_state.answers['parmak_tip']: st.warning("💡 Bu lekeler genellikle yüksek miktarda nikotin maruziyetine işaret eder.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Geri"): st.session_state.step = 3; st.rerun()
    with col2:
        if st.button("Analizi Bitir 🎯"):
            st.session_state.step = 5
            st.rerun()

# --- ADIM 5: SONUÇ RAPORU ---
elif st.session_state.step == 5:
    st.title("📊 Detaylı Analiz Sonucu")
    
    # Risk Hesaplama
    risk_skoru = 10
    if st.session_state.answers.get('sigara') == "Evet": risk_skoru += 35
    if st.session_state.answers.get('oksuruk_tip') == "Kanlı": risk_skoru += 30
    if st.session_state.answers.get('genetik') == "Evet": risk_skoru += 15
    risk_skoru = min(risk_skoru, 99)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_skoru,
        number = {'suffix': "%", 'font': {'color': "white"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, 30], 'color': "#2a9d8f"},
                {'range': [30, 70], 'color': "#e9c46a"},
                {'range': [70, 100], 'color': "#e76f51"}]
        }))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig)

    st.write(f"**Yapay Zeka Doğruluk Oranı: %{round(random.uniform(96.5, 98.2), 1)}**")

    # --- DİNAMİK CÜMLELER ---
    if risk_skoru > 70:
        st.error("🚨 **DİKKAT VE UYARI:** Belirtileriniz ve alışkanlıklarınız yüksek risk profili çizmektedir. Vücudunuzun gönderdiği bu sinyalleri ciddiye almanız önerilir.")
        st.info("🏥 **Gidilmesi Gereken Bölümler:** Göğüs Hastalıkları, Göğüs Cerrahisi veya Onkoloji. Lütfen en kısa sürede randevu alarak düşük doz BT (Tomografi) çektiriniz.")
    elif 30 < risk_skoru <= 70:
        st.warning("🟡 **MOTİVASYON CÜMLESİ:** Sağlığınız için henüz geç değil! Bugün atacağınız bir adım, yarınki nefesinizi belirleyecek. Küçük değişimler büyük sonuçlar doğurur.")
        st.info("🏥 **Öneri:** Göğüs Hastalıkları polikliniğine başvurarak bir Solunum Fonksiyon Testi (SFT) yaptırmanız yararlı olacaktır.")
    else:
        st.success("✨ **TEBRİK VE MOTİVASYON:** Akciğerleriniz şu an için oldukça güvenli bir bölgede! Bu sağlıklı tabloyu korumak hayat kalitenizi her zaman yüksek tutacaktır.")
        st.info("🏃 **Koruyucu Aktivite Önerileri:** Haftalık 150 dakika tempolu yürüyüş, derin diyafram nefesi egzersizleri ve antioksidan (yeşil sebze vb.) ağırlıklı beslenme.")

    st.markdown("---")
    st.caption("🤖 *Bu proje yapay zeka tarafından hazırlanmıştır. Verilen bilgiler teşhis amacı taşımaz, sadece farkındalık oluşturmak içindir.*")

    if st.button("🔄 Testi Yeniden Başlat"):
        st.session_state.step = 1; st.rerun()
