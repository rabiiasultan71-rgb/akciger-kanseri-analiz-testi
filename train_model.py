import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Dataset yükle
df = pd.read_csv("dataset.csv")
df.columns = df.columns.str.strip()

# 2. Veri Temizleme ve Dönüştürme
df["GENDER"] = df["GENDER"].map({"M": 1, "F": 0})
df["LUNG_CANCER"] = df["LUNG_CANCER"].map({"YES": 1, "NO": 0})

# --- 🌟 MANTIKSAL VERİ SETİ GÜÇLENDİRME ---
# Orijinal veri çok küçük ve dengesiz olduğu için kurallı ve geniş bir evren yaratıyoruz
ek_veriler = []

for _ in range(800):
    # Senaryo A: Ağır Belirtiler ve Risk Faktörleri olanlar (Kesinlikle Kanser: 1)
    # Yaş yüksek, sigara var, öksürük ve nefes darlığı var
    ek_veriler.append({
        "GENDER": np.random.choice([0, 1]), "AGE": np.random.randint(50, 85), "SMOKING": 2, 
        "YELLOW_FINGERS": np.random.choice([1, 2]), "ANXIETY": np.random.choice([1, 2]), "PEER_PRESSURE": np.random.choice([1, 2]), 
        "CHRONIC_DISEASE": 2, "FATIGUE": 2, "ALLERGY": np.random.choice([1, 2]), "WHEEZING": 2, 
        "ALCOHOL_CONSUMING": 2, "COUGHING": 2, "SHORTNESS_OF_BREATH": 2, "SWALLOWING_DIFFICULTY": 2, 
        "CHEST_PAIN": 2, "LUNG_CANCER": 1
    })
    
    # Senaryo B: Tamamen Temiz ve Sağlıklı Profiller (Kesinlikle Sağlıklı: 0)
    ek_veriler.append({
        "GENDER": np.random.choice([0, 1]), "AGE": np.random.randint(18, 35), "SMOKING": 1, 
        "YELLOW_FINGERS": 1, "ANXIETY": 1, "PEER_PRESSURE": 1, "CHRONIC_DISEASE": 1, 
        "FATIGUE": 1, "ALLERGY": 1, "WHEEZING": 1, "ALCOHOL_CONSUMING": 1, "COUGHING": 1, 
        "SHORTNESS_OF_BREATH": 1, "SWALLOWING_DIFFICULTY": 1, "CHEST_PAIN": 1, "LUNG_CANCER": 0
    })

df_ek = pd.DataFrame(ek_veriler)
df_son = pd.concat([df, df_ek], ignore_index=True)

X = df_son.drop("LUNG_CANCER", axis=1)
y = df_son["LUNG_CANCER"]

# Eğitim ve test ayırma
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# RandomForest model ayarları
model = RandomForestClassifier(
    n_estimators=100, 
    max_depth=10, 
    min_samples_split=2,
    class_weight="balanced", 
    random_state=42
)

model.fit(X_train, y_train)

train_score = model.score(X_train, y_train)
test_score = accuracy_score(y_test, model.predict(X_test))

print(f"📈 Yeni Model Eğitim Doğruluğu: %{train_score*100:.2f}")
print(f"📉 Yeni Model Test Doğruluğu (Genel Skor): %{test_score*100:.2f}")

# Kaydet
joblib.dump(model, "akciger_modeli.pkl")
print("✅ Yeni model başarıyla eğitildi ve kaydedildi!")