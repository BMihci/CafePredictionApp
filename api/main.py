# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Kafe Satış & Talep Tahmin REST API (v1.3 - AI Coach & Inventory Edition)
Mobil (Android) ve Web/Masaüstü için merkezi yapay zeka, MLOps, envanter ve koçluk backend servisi.
"""
import sys
import os
import datetime
import json
from typing import List, Optional, Dict, Any
import requests
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Proje ana dizinini import yoluna ekleyelim
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import supabase_db
import inventory_manager
import ml_ops
import llm_coaching
import calendar_events
import menu_engineering
import locations

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _kullanicilari_birlestir() -> Dict[str, Any]:
    """Supabase ve yerel kullanicilar.json'ı birleştirir (kesintisiz erişim)."""
    users = {}
    try:
        users = supabase_db.kullanicilari_yukle()
    except Exception:
        pass
    
    yerel_dosya = os.path.join(BASE_DIR, "kullanicilar.json")
    if os.path.exists(yerel_dosya):
        try:
            with open(yerel_dosya, "r", encoding="utf-8") as f:
                yerel = json.load(f)
                for k, v in yerel.items():
                    if k not in users:
                        users[k] = v
        except Exception:
            pass
    return users

app = FastAPI(
    title="Kingfool Inc. AI, Global Locations, Inventory & Coaching API",
    description="Kafe satış yönetimi, uluslararası MLOps pipeline, hammadde optimizasyonu, Menü Mühendisliği ve LLM İşletme Koçu bülteni servisi.",
    version="1.5.0"
)

# CORS (Mobil ve Web istemcileri için tam erişim)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# PYDANTIC MODELLERİ
# -------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

class ProductsUpdateRequest(BaseModel):
    username: str
    products: List[str]

class SaleRecordRequest(BaseModel):
    username: str
    product: str
    date: str
    amount: float
    temperature: float = 25.0
    is_weekend: int = 0
    has_promotion: int = 0

class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

class PriceUpdateRequest(BaseModel):
    product: str
    price: float

class CustomEventRequest(BaseModel):
    date: str
    event_name: str

# -------------------------------------------------------------
# UÇ NOKTALAR (ENDPOINTS)
# -------------------------------------------------------------
@app.get("/")
def root():
    return {
        "app": "Kingfool Inc. AI & Cafe Analytics API",
        "version": "1.4.0",
        "edition": "Menu Engineering, Calendar & AI Coach Edition",
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    db_ok, db_msg = supabase_db.baglanti_kontrol()
    return {
        "api_status": "ok",
        "version": "1.4.0",
        "database_connected": db_ok,
        "database_message": db_msg
    }

# --- KULLANICI & KİMLİK DOĞRULAMA ---
@app.post("/api/auth/login")
def login(req: LoginRequest):
    users = _kullanicilari_birlestir()
    if req.username not in users:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı!")
    
    user_data = users[req.username]
    if user_data["password"] != req.password:
        raise HTTPException(status_code=401, detail="Hatalı şifre!")
        
    return {
        "success": True,
        "username": req.username,
        "role": user_data.get("role", "user"),
        "country": user_data.get("ulke", "Türkiye"),
        "city": user_data.get("sehir", "İstanbul"),
        "district": user_data.get("ilce", ""),
        "products": user_data.get("urunler", []),
        "setup_completed": user_data.get("kurulum_tamam", False)
    }

# --- ÜRÜN YÖNETİMİ ---
@app.get("/api/products")
def get_products(username: str = Query(..., description="Kullanıcı Adı")):
    users = _kullanicilari_birlestir()
    if username not in users:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")
    return {
        "username": username,
        "country": users[username].get("ulke", "Türkiye"),
        "city": users[username].get("sehir", "İstanbul"),
        "district": users[username].get("ilce", ""),
        "products": users[username].get("urunler", []),
        "setup_completed": users[username].get("kurulum_tamam", False)
    }

@app.post("/api/products")
def update_products(req: ProductsUpdateRequest):
    success = supabase_db.kullanici_urunleri_kaydet(req.username, req.products)
    if not success:
        raise HTTPException(status_code=500, detail="Ürünler kaydedilemedi!")
    return {
        "success": True,
        "message": "Ürünler başarıyla güncellendi.",
        "products": req.products
    }

# --- SATIŞ YÖNETİMİ (OTOMATİK MLOps ENTEGRELİ) ---
@app.get("/api/sales")
def get_sales(username: str = Query(...), product: str = Query(...)):
    df = supabase_db.satis_gecmisi_df(username, product)
    if df.empty:
        return {"username": username, "product": product, "count": 0, "sales": []}
    
    records = df.to_dict(orient="records")
    return {
        "username": username,
        "product": product,
        "count": len(records),
        "sales": records
    }

@app.post("/api/sales")
def add_sale(req: SaleRecordRequest, background_tasks: BackgroundTasks):
    success = supabase_db.satis_kaydet(
        kullanici_adi=req.username,
        tarih=req.date,
        urun_adi=req.product,
        adet=req.amount,
        sicaklik=req.temperature,
        haftasonu=req.is_weekend,
        promosyon=req.has_promotion
    )
    if not success:
        raise HTTPException(status_code=500, detail="Satış kaydedilemedi!")

    # Arka planda MLOps modelini otomatik yeniden eğit (hot-reload)
    background_tasks.add_task(ml_ops.egit_ve_kaydet_model, req.username, req.product)

    return {
        "success": True,
        "message": f"{req.date} tarihli {req.product} satışı kaydedildi ve yapay zeka modeli arka planda güncelleniyor."
    }

# --- HAVA DURUMU (OPEN-METEO) ---
@app.get("/api/weather")
def get_weather(lat: float = 41.0082, lon: float = 28.9784):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&timezone=auto"
        res = requests.get(url, timeout=5).json()
        temps = res.get("daily", {}).get("temperature_2m_max", [])
        dates = res.get("daily", {}).get("time", [])
        
        today_temp = temps[0] if len(temps) > 0 else 25.0
        tomorrow_temp = temps[1] if len(temps) > 1 else 26.0
        
        return {
            "latitude": lat,
            "longitude": lon,
            "today_date": dates[0] if dates else str(datetime.date.today()),
            "today_temp": today_temp,
            "tomorrow_date": dates[1] if len(dates) > 1 else str(datetime.date.today() + datetime.timedelta(days=1)),
            "tomorrow_temp": tomorrow_temp
        }
    except Exception as e:
        return {
            "error": str(e),
            "today_temp": 25.0,
            "tomorrow_temp": 26.0
        }

# --- YAPAY ZEKA TAHMİNİ (MLOps DESTEKLİ) ---
@app.get("/api/predict")
def predict_sales(
    username: str = Query(..., description="Kullanıcı Adı"),
    product: str = Query(..., description="Ürün Adı"),
    tomorrow_temp: float = Query(26.0, description="Yarınki Sıcaklık (°C)"),
    tomorrow_is_weekend: int = Query(0, description="Yarın Hafta Sonu Mu (1/0)"),
    tomorrow_has_promo: int = Query(0, description="Yarın Promosyon Var Mı (1/0)"),
    tomorrow_is_holiday: Optional[int] = Query(None, description="Yarın Resmi Tatil Mi (1/0)")
):
    yarin_tarih = datetime.date.today() + datetime.timedelta(days=1)
    tatil_bilgisi = calendar_events.tarih_tatil_veya_etkinlik_mi(yarin_tarih)
    
    if isinstance(tomorrow_is_holiday, (int, float, bool)):
        tatil_val = int(tomorrow_is_holiday)
    else:
        tatil_val = tatil_bilgisi["tatil_mi"]

    tahmin, metrikler = ml_ops.tahmin_yap(
        kullanici_adi=username,
        urun_adi=product,
        yarin_sicaklik=float(tomorrow_temp) if isinstance(tomorrow_temp, (int, float)) else 26.0,
        yarin_haftasonu=int(tomorrow_is_weekend) if isinstance(tomorrow_is_weekend, (int, float)) else 0,
        yarin_promosyon=int(tomorrow_has_promo) if isinstance(tomorrow_has_promo, (int, float)) else 0,
        yarin_tatil=tatil_val
    )
    
    if tahmin is None:
        return {
            "success": False,
            "prediction": None,
            "metrics": metrikler,
            "message": "Model eğitimi için yeterli geçmiş veri bulunamadı."
        }
        
    return {
        "success": True,
        "username": username,
        "product": product,
        "prediction": int(tahmin),
        "tomorrow_temp": tomorrow_temp,
        "tomorrow_is_weekend": tomorrow_is_weekend,
        "tomorrow_is_holiday": tatil_val,
        "holiday_info": tatil_bilgisi,
        "model_metrics": metrikler,
        "engine": "Kingfool MLOps Pipeline (RandomForest with Lag1, Lag7, Month, DayOfWeek, TempXPromo, Tatil_Mi)"
    }

# --- REÇETE & ENVANTER OPTİMİZASYON MODÜLÜ ---
@app.get("/api/inventory/recipes")
def get_recipes():
    """Tüm ürün reçetelerini listeler."""
    return {
        "success": True,
        "recipes": inventory_manager.VARSAYILAN_RECETELER
    }

@app.get("/api/inventory/requirements")
def get_inventory_requirements(
    username: str = Query(..., description="Kullanıcı Adı"),
    tomorrow_temp: float = Query(26.0),
    tomorrow_is_weekend: int = Query(0)
):
    """
    Kullanıcının tanımlı tüm ürünleri için yarınki tahminleri üretir
    ve gereken toplam hammadde (çekirdek, süt, bardak vb.) listesini hesaplar.
    """
    users = _kullanicilari_birlestir()
    if username not in users:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")

    urunler = users[username].get("urunler", ["Cold Brew", "Iced Latte", "Iced Americano", "Brownie"])
    tahminler = {}
    for u in urunler:
        tahmin, _ = ml_ops.tahmin_yap(username, u, tomorrow_temp, tomorrow_is_weekend)
        if tahmin is not None:
            tahminler[u] = tahmin
        else:
            tahminler[u] = 40  # Güvenli varsayılan

    ihtiyaclar = inventory_manager.hammadde_ihtiyaci_hesapla(tahminler)
    uyarilar = inventory_manager.stok_kontrol_ve_uyarilar(ihtiyaclar)

    return {
        "success": True,
        "username": username,
        "product_predictions": tahminler,
        "total_items": sum(tahminler.values()),
        "raw_materials_needed": ihtiyaclar,
        "operational_alerts": uyarilar
    }

# --- RESMİ TATİL VE ETKİNLİK TAKVİMİ MODÜLÜ ---
@app.get("/api/calendar/holidays")
def get_holidays(year: int = Query(2026, description="Yıl")):
    """Belirtilen yılın resmi tatil ve bayramlarını listeler."""
    return {
        "success": True,
        "year": year,
        "holidays": calendar_events.yillik_tatil_listesi(year)
    }

@app.get("/api/calendar/check-date")
def check_calendar_date(date: Optional[str] = Query(None, description="Tarih YYYY-MM-DD")):
    """Belirli bir tarihin resmi tatil veya özel etkinlik olup olmadığını döner."""
    t_str = date or str(datetime.date.today())
    info = calendar_events.tarih_tatil_veya_etkinlik_mi(t_str)
    return {
        "success": True,
        "date": t_str,
        "info": info
    }

@app.post("/api/calendar/custom-events")
def add_custom_event(req: CustomEventRequest):
    """Yeni yerel kafe etkinliği (konser, derbi maçı vb.) tanımlar."""
    ok = calendar_events.ozel_etkinlik_kaydet(req.date, req.event_name)
    if not ok:
        raise HTTPException(status_code=500, detail="Özel etkinlik kaydedilemedi!")
    return {
        "success": True,
        "message": f"{req.date} tarihine '{req.event_name}' etkinliği eklendi."
    }

# --- MENÜ MÜHENDİSLİĞİ VE KÂR MARJI MATRİSİ ---
@app.get("/api/menu-engineering/matrix")
def get_menu_matrix(
    username: str = Query(..., description="Kullanıcı Adı"),
    tomorrow_temp: float = Query(26.0),
    tomorrow_is_weekend: int = Query(0)
):
    """
    Kasavana & Smith F&B Menü Mühendisliği analizi.
    Ürünleri 4 kadrana (Yıldızlar, İş Atları, Bulmacalar, Köpekler) ayırır.
    """
    users = _kullanicilari_birlestir()
    if username not in users:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")
    
    urunler = users[username].get("urunler", ["Cold Brew", "Iced Latte", "Iced Americano", "Brownie"])
    tahminler = {}
    for u in urunler:
        t, _ = ml_ops.tahmin_yap(username, u, tomorrow_temp, tomorrow_is_weekend)
        tahminler[u] = t if t is not None else 45

    matris = menu_engineering.menu_matrisi_analiz_et(tahminler)
    return {
        "success": True,
        "username": username,
        "matrix": matris
    }

@app.get("/api/menu-engineering/cost")
def get_product_cost(product: str = Query(..., description="Ürün Adı")):
    """Ürünün reçetesine göre porsiyon hammadde maliyetini (COGS) ve kalemlerini döner."""
    maliyet = menu_engineering.porsiyon_maliyeti_hesapla(product)
    fiyatlar = menu_engineering.kullanici_fiyatlarini_yukle()
    satis_fiyati = fiyatlar.get(product, 120.0)
    katki_payi = round(satis_fiyati - maliyet["porsiyon_maliyeti"], 2)
    kar_marji = round((katki_payi / satis_fiyati) * 100, 1) if satis_fiyati > 0 else 0.0

    return {
        "success": True,
        "product": product,
        "sale_price": satis_fiyati,
        "portion_cost": maliyet["porsiyon_maliyeti"],
        "contribution_margin": katki_payi,
        "profit_margin_percent": kar_marji,
        "ingredients": maliyet["kalemler"]
    }

@app.post("/api/menu-engineering/prices")
def update_product_price(req: PriceUpdateRequest):
    """Ürünün satış fiyatını günceller."""
    ok = menu_engineering.satis_fiyati_kaydet(req.product, req.price)
    if not ok:
        raise HTTPException(status_code=500, detail="Fiyat güncellenemedi!")
    return {
        "success": True,
        "product": req.product,
        "new_price": req.price,
        "message": f"{req.product} fiyatı {req.price} TL olarak güncellendi."
    }

# --- ULUSLARARASI KONUM YÖNETİMİ ---
@app.get("/api/locations/countries")
def get_countries():
    """Desteklenen tüm dünya ülkelerini ve ilçe seçim kurallarını döner."""
    return {
        "success": True,
        "countries": [
            {
                "name": c_name,
                "code": c_data["kod"],
                "has_districts": c_data["ilce_destegi"],
                "city_count": len(c_data["sehirler"])
            }
            for c_name, c_data in locations.DUNYA_ULKELERI.items()
        ]
    }

@app.get("/api/locations/cities")
def get_cities(country: str = Query("Türkiye", description="Ülke Adı")):
    """Seçilen ülkenin şehir listesini döner."""
    return {
        "success": True,
        "country": country,
        "cities": locations.sehir_listesi_getir(country),
        "has_districts": locations.ilce_secimi_aktif_mi(country)
    }

@app.get("/api/locations/districts")
def get_districts(country: str = Query("Türkiye", description="Ülke Adı"), city: str = Query("İstanbul", description="Şehir / İl")):
    """Seçilen şehrin ilçelerini döner (Yalnızca Türkiye için aktiftir; diğer ülkelerde boş liste döner)."""
    districts = locations.ilce_listesi_getir(country, city)
    return {
        "success": True,
        "country": country,
        "city": city,
        "districts_enabled": locations.ilce_secimi_aktif_mi(country),
        "districts": districts
    }

@app.get("/api/locations/geocode")
def geocode_location(country: str = Query("Türkiye"), city: str = Query("İstanbul"), district: Optional[str] = Query(None)):
    """Ülke, şehir ve varsa ilçe bilgisine göre kesin coğrafi koordinatları döner."""
    lat, lon, label = locations.konum_koordinat_bul(country, city, district)
    return {
        "success": True,
        "country": country,
        "city": city,
        "district": district or "",
        "latitude": lat,
        "longitude": lon,
        "label": label
    }

# --- LLM PROMPT MİMARİSİ: AKILLI İŞLETME KOÇU VE GÜNLÜK BÜLTEN ---
@app.get("/api/coaching/daily-report")
def get_daily_coaching_report(
    username: str = Query(..., description="Kullanıcı Adı"),
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    country: Optional[str] = None,
    gemini_key: Optional[str] = None
):
    """
    Kafe sahibine özel yarınki hava durumu, yapay zeka satış tahminleri, tatil takvimi,
    hammadde ihtiyaçları ve Menü Mühendisliği matrisine göre günlük bülten üretir.
    Uluslararası ülke resmi tatillerini ve yerel hava durumunu entegre eder.
    """
    users = _kullanicilari_birlestir()
    if username not in users:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")

    u_data = users[username]
    if country is None:
        country = u_data.get("ulke", "Türkiye")

    if lat is None or lon is None:
        lat = u_data.get("lat", 41.0082)
        lon = u_data.get("lon", 28.9784)

    # 1. Hava Durumu
    w = get_weather(lat, lon)
    yarin_temp = w.get("tomorrow_temp", 26.0)
    yarin_tarih = w.get("tomorrow_date") or str(datetime.date.today() + datetime.timedelta(days=1))
    
    try:
        t_obj = datetime.datetime.strptime(yarin_tarih, "%Y-%m-%d")
        yarin_haftasonu = 1 if t_obj.weekday() >= 5 else 0
    except Exception:
        yarin_haftasonu = 0

    # 2. Ürün Tahminleri
    urunler = u_data.get("urunler", ["Cold Brew", "Iced Latte", "Iced Americano", "Brownie"])
    tahminler = {}
    for u in urunler:
        tahmin, _ = ml_ops.tahmin_yap(username, u, yarin_temp, yarin_haftasonu, ulke=country)
        tahminler[u] = tahmin if tahmin is not None else 45

    # 3. Hammadde İhtiyaçları
    ihtiyaclar = inventory_manager.hammadde_ihtiyaci_hesapla(tahminler)

    # 4. LLM Koçluk Raporunu Üret (Ülkeye Duyarlı)
    rapor_sonuc = llm_coaching.gunluk_koc_raporu_uret(
        kullanici_adi=username,
        yarin_tarih=yarin_tarih,
        yarin_sicaklik=yarin_temp,
        yarin_haftasonu=yarin_haftasonu,
        urun_tahminleri=tahminler,
        hammadde_ihtiyaclari=ihtiyaclar,
        gemini_api_key=gemini_key,
        ulke=country
    )

    return {
        "success": True,
        "username": username,
        "country": country,
        "date": yarin_tarih,
        "temperature": yarin_temp,
        "is_weekend": yarin_haftasonu,
        "holiday_info": rapor_sonuc.get("tatil_bilgisi"),
        "predictions": tahminler,
        "inventory": ihtiyaclar,
        "menu_matrix": rapor_sonuc.get("menu_matrisi"),
        "engine": rapor_sonuc.get("kaynak"),
        "report_markdown": rapor_sonuc.get("rapor")
    }

# --- MLOps YENİDEN EĞİTİM (RETRAINING) UÇ NOKTALARI ---
@app.post("/api/ml/retrain")
def retrain_models(username: str = Query(...), product: Optional[str] = Query(None)):
    """Kullanıcının modelini/modellerini baştan eğitir ve güncel metrikleri döner."""
    if product:
        model, metrikler = ml_ops.egit_ve_kaydet_model(username, product)
        return {
            "success": model is not None,
            "metrics": metrikler
        }
    else:
        sonuc = ml_ops.tum_modelleri_yeniden_egit(username)
        return {
            "success": True,
            "result": sonuc
        }

@app.get("/api/ml/status")
def get_ml_status(username: str = Query(...)):
    """Kullanıcının eğitilmiş modellerinin durumunu listeler."""
    users = _kullanicilari_birlestir()
    if username not in users:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")
    
    urunler = users[username].get("urunler", [])
    durumlar = []
    for u in urunler:
        dosya = ml_ops.model_dosya_yolu(username, u)
        if os.path.exists(dosya):
            _, metrikler, _ = ml_ops.model_getir(username, u)
            durumlar.append({"product": u, "trained": True, "metrics": metrikler})
        else:
            durumlar.append({"product": u, "trained": False, "metrics": None})
            
    return {
        "username": username,
        "models": durumlar
    }

# --- ADMIN KULLANICI YÖNETİMİ ---
@app.post("/api/admin/users")
def admin_create_user(req: UserCreateRequest):
    ok = supabase_db.kullanici_ekle(req.username, req.password, req.role)
    if not ok:
        raise HTTPException(status_code=500, detail="Kullanıcı oluşturulamadı!")
    return {"success": True, "message": f"{req.username} kullanıcısı oluşturuldu."}

@app.delete("/api/admin/users/{username}")
def admin_delete_user(username: str):
    ok = supabase_db.kullanici_sil(username)
    if not ok:
        raise HTTPException(status_code=500, detail="Kullanıcı silinemedi!")
    return {"success": True, "message": f"{username} kullanıcısı silindi."}

if __name__ == "__main__":
    import uvicorn
    # Destek: Hem KafeProjesi kök dizininden hem de api/ içinden başlatılabilir
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    app_target = "api.main:app" if os.path.exists("api/main.py") else "main:app"
    uvicorn.run(app_target, host="0.0.0.0", port=8000, reload=True)
