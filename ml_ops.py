# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Automated MLOps Pipeline (v1.3)
Random Forest modellerini eğitir, joblib ile .pkl formatında kalıcı kılar ve hot-reload ile servis eder.
"""
import os
import sys
import json
import datetime
from typing import Optional
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import calendar_events

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Bellek içi model önbelleği: { "kullanici_urun": (model, egitim_zamani, metrikler) }
_MODEL_CACHE = {}

FEATURE_COLS = [
    "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi",
    "Ay", "Haftanin_Gunu", "Satis_Lag1", "Satis_Lag7",
    "Sicaklik_x_Promosyon", "Tatil_Mi"
]

def _kullanici_ulkesi_bul(kullanici_adi: str) -> str:
    """Kullanıcının kayıtlı ülkesini kullanicilar.json veya supabase'den çeker."""
    try:
        users_file = os.path.join(BASE_DIR, "kullanicilar.json")
        if os.path.exists(users_file):
            with open(users_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if kullanici_adi in data and "ulke" in data[kullanici_adi]:
                    return data[kullanici_adi]["ulke"]
    except Exception:
        pass
    return "Türkiye"

def model_dosya_yolu(kullanici_adi: str, urun_adi: str) -> str:
    temiz_urun = urun_adi.replace(" ", "_").replace("/", "_").replace("\\", "_")
    return os.path.join(MODELS_DIR, f"{kullanici_adi}_{temiz_urun}_rf.pkl")

def egit_ve_kaydet_model(kullanici_adi: str, urun_adi: str, df: pd.DataFrame = None, ulke: Optional[str] = None):
    """
    Belirtilen kullanıcı ve ürün için RandomForestRegressor modelini eğitir,
    joblib ile .pkl olarak kaydeder ve bellek önbelleğine alır.
    Ülkeye özel resmi tatil ve bayramları otomatik uygular.
    """
    if ulke is None:
        ulke = _kullanici_ulkesi_bul(kullanici_adi)

    if df is None or df.empty:
        import supabase_db
        df = supabase_db.satis_gecmisi_df(kullanici_adi, urun_adi)
        if df.empty:
            # Yerel Excel fallback dene
            yerel_excel = os.path.join(BASE_DIR, f"kafe_{kullanici_adi}_satislar.xlsx")
            if os.path.exists(yerel_excel):
                df_raw = pd.read_excel(yerel_excel)
                if urun_adi in df_raw.columns:
                    df = df_raw[["Tarih", "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi", urun_adi]].copy()

    if df.empty or urun_adi not in df.columns or len(df) < 8:
        return None, {"hata": "Yetersiz veri", "satir_sayisi": len(df)}

    # Tarihe göre sırala
    df["Tarih"] = pd.to_datetime(df["Tarih"])
    df = df.sort_values("Tarih").reset_index(drop=True)

    # 1. Feature Engineering
    df["Ay"] = df["Tarih"].dt.month
    df["Haftanin_Gunu"] = df["Tarih"].dt.dayofweek
    df["Satis_Lag1"] = df[urun_adi].shift(1)
    df["Satis_Lag7"] = df[urun_adi].shift(7)
    promo = df["Promosyon_Var_Mi"].fillna(0)
    df["Sicaklik_x_Promosyon"] = df["Sicaklik"] * promo
    # Ülkeye Özel Resmi Tatil ve Bayram Özniteliği
    df["Tatil_Mi"] = df["Tarih"].apply(lambda t: calendar_events.tarih_tatil_veya_etkinlik_mi(t, ulke=ulke)["tatil_mi"])

    # 2. NaN Temizliği
    df_train = df.dropna(subset=FEATURE_COLS + [urun_adi]).reset_index(drop=True)
    veri_sayisi = len(df_train)

    if veri_sayisi < 5:
        return None, {"hata": "Eğitim için en az 5 geçerli lag satırı gerekli", "satir_sayisi": veri_sayisi}

    X = df_train[FEATURE_COLS]
    y = df_train[urun_adi]

    # 3. Model Eğitimi (RandomForestRegressor)
    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)

    # 4. Metrikler
    y_pred = model.predict(X)
    mae = float(round(mean_absolute_error(y, y_pred), 2))
    r2 = float(round(r2_score(y, y_pred), 3)) if len(y) > 1 else 1.0
    importances = {col: float(round(imp, 3)) for col, imp in zip(FEATURE_COLS, model.feature_importances_)}

    metrikler = {
        "kullanici": kullanici_adi,
        "urun": urun_adi,
        "egitim_tarihi": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "egitim_satir_sayisi": veri_sayisi,
        "mae": mae,
        "r2_score": r2,
        "en_onemli_oznitelikler": dict(sorted(importances.items(), key=lambda x: x[1], reverse=True)[:3])
    }

    # 5. Kalıcılık (Joblib .pkl)
    dosya_yolu = model_dosya_yolu(kullanici_adi, urun_adi)
    joblib.dump({"model": model, "metrikler": metrikler, "son_satislar": df[urun_adi].dropna().values.tolist()}, dosya_yolu)

    # 6. Belleğe Önbellekleme
    cache_key = f"{kullanici_adi}_{urun_adi}"
    _MODEL_CACHE[cache_key] = (model, metrikler, df[urun_adi].dropna().values)

    return model, metrikler

def model_getir(kullanici_adi: str, urun_adi: str):
    """Bellekten veya diskten modeli getirir, yoksa otomatik eğitir."""
    cache_key = f"{kullanici_adi}_{urun_adi}"
    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    dosya_yolu = model_dosya_yolu(kullanici_adi, urun_adi)
    if os.path.exists(dosya_yolu):
        try:
            paket = joblib.load(dosya_yolu)
            model = paket["model"]
            metrikler = paket["metrikler"]
            son_satislar = np.array(paket.get("son_satislar", []))
            _MODEL_CACHE[cache_key] = (model, metrikler, son_satislar)
            return model, metrikler, son_satislar
        except Exception:
            pass

    # Model yoksa sıfırdan eğit
    model, metrikler = egit_ve_kaydet_model(kullanici_adi, urun_adi)
    if model is not None:
        return _MODEL_CACHE.get(cache_key, (model, metrikler, []))
    return None, metrikler, []

def tahmin_yap(kullanici_adi: str, urun_adi: str, yarin_sicaklik: float, yarin_haftasonu: int, yarin_promosyon: int = 0, yarin_tatil: Optional[int] = None, ulke: Optional[str] = None):
    """
    MLOps modelini kullanarak yarın için satış adedi tahmini üretir.
    Tatil_Mi özniteliğini kullanıcı ülkesine göre otomatik tespit eder veya parametreden alır.
    """
    model, metrikler, son_satislar = model_getir(kullanici_adi, urun_adi)
    if model is None:
        return None, metrikler

    # Çıkarım (Inference) vektörünü oluştur
    yarin_tarih = datetime.date.today() + datetime.timedelta(days=1)
    
    if len(son_satislar) == 0:
        import supabase_db
        df = supabase_db.satis_gecmisi_df(kullanici_adi, urun_adi)
        if not df.empty and urun_adi in df.columns:
            son_satislar = df[urun_adi].dropna().values
            
    lag1_val = float(son_satislar[-1]) if len(son_satislar) >= 1 else 40.0
    lag7_val = float(son_satislar[-7]) if len(son_satislar) >= 7 else lag1_val

    promo_val = int(yarin_promosyon)
    
    # Tatil durumunu tespit et (ülkeye duyarlı)
    if yarin_tatil is None:
        if ulke is None:
            ulke = _kullanici_ulkesi_bul(kullanici_adi)
        tatil_info = calendar_events.tarih_tatil_veya_etkinlik_mi(yarin_tarih, ulke=ulke)
        tatil_val = int(tatil_info["tatil_mi"])
    else:
        tatil_val = int(yarin_tatil)

    yarin_df = pd.DataFrame([{
        "Sicaklik": float(yarin_sicaklik),
        "Haftasonu_Mu": int(yarin_haftasonu),
        "Promosyon_Var_Mi": promo_val,
        "Ay": yarin_tarih.month,
        "Haftanin_Gunu": yarin_tarih.weekday(),
        "Satis_Lag1": lag1_val,
        "Satis_Lag7": lag7_val,
        "Sicaklik_x_Promosyon": float(yarin_sicaklik * promo_val),
        "Tatil_Mi": tatil_val
    }])[FEATURE_COLS]

    tahmin = int(round(model.predict(yarin_df)[0]))
    return max(0, tahmin), metrikler

def tum_modelleri_yeniden_egit(kullanici_adi: str):
    """Kullanıcının tüm ürünleri için modelleri baştan eğitir ve sonuçları döner."""
    users = {}
    try:
        import supabase_db
        users = supabase_db.kullanicilari_yukle()
    except Exception:
        pass
    if kullanici_adi not in users:
        yerel_f = os.path.join(BASE_DIR, "kullanicilar.json")
        if os.path.exists(yerel_f):
            try:
                with open(yerel_f, "r", encoding="utf-8") as f:
                    users = json.load(f)
            except Exception:
                pass
    if kullanici_adi not in users:
        return {"hata": "Kullanıcı bulunamadı"}

    urunler = users[kullanici_adi].get("urunler", [])
    rapor = []
    for u in urunler:
        _, met = egit_ve_kaydet_model(kullanici_adi, u)
        rapor.append(met)
    return {"kullanici": kullanici_adi, "egitilen_modeller": rapor}
