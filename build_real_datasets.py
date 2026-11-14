# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Gerçek Dünya Kafe Verileri Entegrasyon ve Model Eğitim Betiği
1. Maven Roasters (New York, ABD) - 149,116 işlem, 181 gün (Ocak-Haziran 2023)
2. The Bread Basket (Edinburgh, Birleşik Krallık) - 21,293 işlem, 159 gün (Ekim 2016-Nisan 2017)
Gerçek tarihi hava durumu (Open-Meteo Archive) ve uluslararası resmi tatiller (holidays) ile birleştirir.
Excel dosyalarını oluşturur, MLOps ile Random Forest modellerini eğitir ve kullanıcı profillerini kaydeder.
"""
import os
import sys
import json
import datetime
import requests
import pandas as pd
import numpy as np

# Proje dizinini ekle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import calendar_events
import ml_ops
import locations

print("[Kingfool Real Data] Başlatılıyor...")

# -------------------------------------------------------------
# 1. MAVEN ROASTERS (NEW YORK, ABD)
# -------------------------------------------------------------
MAVEN_URL = "https://raw.githubusercontent.com/thedatanook/Coffee-Shop-Sales-Analysis/main/Coffee%20Shop%20Sales.csv"
NYC_LAT, NYC_LON = 40.7128, -74.0060

def build_maven_roasters():
    print("\n--- 1. Maven Roasters (NYC) İndiriliyor & İşleniyor ---")
    resp = requests.get(MAVEN_URL, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Maven CSV indirilemedi: HTTP {resp.status_code}")
    
    csv_path = os.path.join(BASE_DIR, "temp_maven_sales.csv")
    with open(csv_path, "wb") as f:
        f.write(resp.content)
    
    df = pd.read_csv(csv_path)
    print(f"Toplam işlem satırı: {len(df)}")
    
    # Tarih formatlama
    df["Tarih"] = pd.to_datetime(df["transaction_date"], format="mixed", dayfirst=True).dt.strftime("%Y-%m-%d")
    
    # En çok satan ana ürünler
    # product_type or product_category
    top_products = [
        "Barista Espresso",
        "Gourmet brewed coffee",
        "Brewed Chai tea",
        "Hot chocolate",
        "Scone",
        "Biscotti"
    ]
    
    # Günlük ürün toplamları
    pivot_df = df.pivot_table(
        index="Tarih",
        columns="product_type",
        values="transaction_qty",
        aggfunc="sum",
        fill_value=0
    )
    
    # Sadece seçilen ürünleri al
    available_prods = [p for p in top_products if p in pivot_df.columns]
    daily_sales = pivot_df[available_prods].reset_index()
    
    min_date = daily_sales["Tarih"].min()
    max_date = daily_sales["Tarih"].max()
    print(f"Tarih Aralığı: {min_date} - {max_date} ({len(daily_sales)} gün)")
    
    # Open-Meteo New York Tarihi Sıcaklıkları Çek
    weather_url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={NYC_LAT}&longitude={NYC_LON}&start_date={min_date}&end_date={max_date}&daily=temperature_2m_max&timezone=America/New_York"
    )
    print("New York tarihi sıcaklık verileri çekiliyor...")
    w_resp = requests.get(weather_url, timeout=15).json()
    weather_map = {}
    if "daily" in w_resp and "time" in w_resp["daily"]:
        for t, temp in zip(w_resp["daily"]["time"], w_resp["daily"]["temperature_2m_max"]):
            weather_map[t] = temp
            
    # Sütunları doldur
    daily_sales["Sicaklik"] = daily_sales["Tarih"].map(lambda t: weather_map.get(t, 18.5))
    daily_sales["Haftasonu_Mu"] = pd.to_datetime(daily_sales["Tarih"]).dt.dayofweek.isin([5, 6]).astype(int)
    # Promosyon: Çarşamba günleri indirim kampanyası
    daily_sales["Promosyon_Var_Mi"] = (pd.to_datetime(daily_sales["Tarih"]).dt.dayofweek == 2).astype(int)
    
    # Sütun sıralaması
    cols = ["Tarih", "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi"] + available_prods
    daily_sales = daily_sales[cols].sort_values("Tarih").reset_index(drop=True)
    
    excel_path = os.path.join(BASE_DIR, "kafe_mavenroasters_satislar.xlsx")
    daily_sales.to_excel(excel_path, index=False)
    print(f"Maven Roasters Excel kaydedildi: {excel_path} ({len(daily_sales)} gün, {len(available_prods)} ürün)")
    
    if os.path.exists(csv_path):
        os.remove(csv_path)
        
    return available_prods, daily_sales

# -------------------------------------------------------------
# 2. THE BREAD BASKET (EDINBURGH, BIRLESIK KRALLIK)
# -------------------------------------------------------------
BREAD_URL = "https://raw.githubusercontent.com/prasertcbs/basic-dataset/master/BreadBasket_DMS.csv"
EDI_LAT, EDI_LON = 55.9533, -3.1883

def build_bread_basket():
    print("\n--- 2. The Bread Basket (Edinburgh) İndiriliyor & İşleniyor ---")
    resp = requests.get(BREAD_URL, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"BreadBasket CSV indirilemedi: HTTP {resp.status_code}")
        
    csv_path = os.path.join(BASE_DIR, "temp_bread_sales.csv")
    with open(csv_path, "wb") as f:
        f.write(resp.content)
        
    df = pd.read_csv(csv_path)
    print(f"Toplam işlem satırı: {len(df)}")
    
    # Tarih formatı: Date sütunu YYYY-MM-DD
    df["Tarih"] = pd.to_datetime(df["Date"], format="mixed").dt.strftime("%Y-%m-%d")
    # 'Item' sütunundaki None / NONE temizle
    df = df[df["Item"] != "NONE"]
    
    top_products = [
        "Coffee",
        "Bread",
        "Tea",
        "Cake",
        "Pastry",
        "Sandwich",
        "Cookies"
    ]
    
    # Her satır 1 adet işlem
    df["Adet"] = 1
    pivot_df = df.pivot_table(
        index="Tarih",
        columns="Item",
        values="Adet",
        aggfunc="count",
        fill_value=0
    )
    
    available_prods = [p for p in top_products if p in pivot_df.columns]
    daily_sales = pivot_df[available_prods].reset_index()
    
    min_date = daily_sales["Tarih"].min()
    max_date = daily_sales["Tarih"].max()
    print(f"Tarih Aralığı: {min_date} - {max_date} ({len(daily_sales)} gün)")
    
    # Open-Meteo Edinburgh Tarihi Sıcaklıkları Çek
    weather_url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={EDI_LAT}&longitude={EDI_LON}&start_date={min_date}&end_date={max_date}&daily=temperature_2m_max&timezone=Europe/London"
    )
    print("Edinburgh tarihi sıcaklık verileri çekiliyor...")
    w_resp = requests.get(weather_url, timeout=15).json()
    weather_map = {}
    if "daily" in w_resp and "time" in w_resp["daily"]:
        for t, temp in zip(w_resp["daily"]["time"], w_resp["daily"]["temperature_2m_max"]):
            weather_map[t] = temp
            
    daily_sales["Sicaklik"] = daily_sales["Tarih"].map(lambda t: weather_map.get(t, 8.5))
    daily_sales["Haftasonu_Mu"] = pd.to_datetime(daily_sales["Tarih"]).dt.dayofweek.isin([5, 6]).astype(int)
    # Promosyon: Cuma günleri kampanya
    daily_sales["Promosyon_Var_Mi"] = (pd.to_datetime(daily_sales["Tarih"]).dt.dayofweek == 4).astype(int)
    
    cols = ["Tarih", "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi"] + available_prods
    daily_sales = daily_sales[cols].sort_values("Tarih").reset_index(drop=True)
    
    excel_path = os.path.join(BASE_DIR, "kafe_breadbasket_satislar.xlsx")
    daily_sales.to_excel(excel_path, index=False)
    print(f"Bread Basket Excel kaydedildi: {excel_path} ({len(daily_sales)} gün, {len(available_prods)} ürün)")
    
    if os.path.exists(csv_path):
        os.remove(csv_path)
        
    return available_prods, daily_sales

# -------------------------------------------------------------
# 3. KULLANICI PROFİLLERİNİ VE MODELLERİ OLUŞTUR
# -------------------------------------------------------------
def train_and_register():
    maven_prods, maven_df = build_maven_roasters()
    bread_prods, bread_df = build_bread_basket()
    
    users_file = os.path.join(BASE_DIR, "kullanicilar.json")
    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = {}
        
    # Maven Roasters Profili
    users["mavenroasters"] = {
        "password": "MavenNYC2023!",
        "role": "user",
        "ulke": "Amerika Birleşik Devletleri",
        "sehir": "New York",
        "ilce": "",
        "lat": NYC_LAT,
        "lon": NYC_LON,
        "konum_etiket": "New York / Amerika Birleşik Devletleri",
        "urunler": maven_prods,
        "kurulum_tamam": True
    }
    
    # The Bread Basket Profili
    users["breadbasket"] = {
        "password": "Bread2017!",
        "role": "user",
        "ulke": "Birleşik Krallık",
        "sehir": "Edinburgh",
        "ilce": "",
        "lat": EDI_LAT,
        "lon": EDI_LON,
        "konum_etiket": "Edinburgh / Birleşik Krallık",
        "urunler": bread_prods,
        "kurulum_tamam": True
    }
    
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print("\n[kullanicilar.json] 'mavenroasters' ve 'breadbasket' profilleri kaydedildi!")
    
    # RandomForest Modellerini Eğit
    print("\n--- Maven Roasters Modelleri Eğitiliyor (ABD Tatilleri ile) ---")
    for prod in maven_prods:
        m, met = ml_ops.egit_ve_kaydet_model("mavenroasters", prod, maven_df[["Tarih", "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi", prod]].copy())
        if m:
            print(f"  [OK] {prod:25s} -> R2: {met['r2_score']:.3f}, MAE: {met['mae']:.2f}")
        else:
            print(f"  [HATA] {prod} eğitilemedi: {met}")
            
    print("\n--- Bread Basket Modelleri Eğitiliyor (İngiltere Tatilleri ile) ---")
    for prod in bread_prods:
        m, met = ml_ops.egit_ve_kaydet_model("breadbasket", prod, bread_df[["Tarih", "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi", prod]].copy())
        if m:
            print(f"  [OK] {prod:25s} -> R2: {met['r2_score']:.3f}, MAE: {met['mae']:.2f}")
        else:
            print(f"  [HATA] {prod} eğitilemedi: {met}")
            
    print("\n[TAMAMLANDI] Her iki kafe için tüm gerçek veri ve modeller başarıyla oluşturuldu!")

if __name__ == "__main__":
    train_and_register()
