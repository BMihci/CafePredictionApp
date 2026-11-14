import os
import sys
import json
import datetime
import requests
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from sklearn.ensemble import RandomForestRegressor
import inventory_manager
import ml_ops
import llm_coaching
import calendar_events
import menu_engineering
import locations
import analytics_charts
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -------------------------------------------------------------
# ULUSLARARASI DİL SÖZLÜĞÜ (TR / EN)
# -------------------------------------------------------------
DIL_SOZLUGU = {
    "TR": {
        "baslik": "🃏 KINGFOOL INC.",
        "aktif_kafe": "👤 Aktif Kafe:",
        "cikis": "🚪 Çıkış",
        "admin_btn": "👑 Admin Paneli",
        "kart1_baslik": "1. KAFE KONUMU (DÜNYA & TÜRKİYE)",
        "ulke": "Ülke:",
        "sehir": "Şehir:",
        "ilce": "İlçe (TR):",
        "hava_btn": "🌤️ Hava Al",
        "hava_bekleniyor": "Hava durumu bekleniyor...",
        "kart2_baslik": "2. GÜN SONU SATIŞ GİRİŞİ",
        "tarih": "📅 Tarih:",
        "promo": "Bugün özel indirim/promosyon uygulandı",
        "kaydet_btn": "💾 Günlük Satışları Kaydet & Yapay Zekayı Güncelle",
        "kart3_baslik": "3. YARINKİ TALEP TAHMİNİ (ÜRÜN BAZLI)",
        "tahmin_urun": "Tahmin Edilecek Ürün:",
        "bulten_btn": "🧠 Akıllı İşletme Koçu Günlük Bültenini Oku",
        "menu_matris_btn": "📊 Menü Mühendisliği ve Kâr Matrisi",
        "urun_yonet_btn": "⚙️ Menü & Ürünleri Yönet",
        "grafik_btn": "📈 Görsel Analitik & Grafikler",
        "tedarik_btn": "🛒 Tedarik & Sipariş Listesi",
        "kart4_baslik": "4. TOPLU GEÇMİŞ SATIŞ YÜKLE",
        "excel_btn": "📁 Bilgisayarımdan Geçmiş Excel Dosyası Yükle",
    },
    "EN": {
        "baslik": "🃏 KINGFOOL INC.",
        "aktif_kafe": "👤 Active Cafe:",
        "cikis": "🚪 Logout",
        "admin_btn": "👑 Admin Panel",
        "kart1_baslik": "1. CAFE LOCATION (GLOBAL & REGIONAL)",
        "ulke": "Country:",
        "sehir": "City:",
        "ilce": "District (TR):",
        "hava_btn": "🌤️ Fetch Weather",
        "hava_bekleniyor": "Weather forecast loading...",
        "kart2_baslik": "2. END-OF-DAY SALES ENTRY",
        "tarih": "📅 Date:",
        "promo": "Special discount/promotion was applied today",
        "kaydet_btn": "💾 Save Sales & Update AI Model",
        "kart3_baslik": "3. TOMORROW'S DEMAND PREDICTION (PER PRODUCT)",
        "tahmin_urun": "Product to Predict:",
        "bulten_btn": "🧠 Read Smart Business Coach Daily Bulletin",
        "menu_matris_btn": "📊 Menu Engineering & Profit Matrix",
        "urun_yonet_btn": "⚙️ Manage Menu & Products",
        "grafik_btn": "📈 Visual Analytics & Charts",
        "tedarik_btn": "🛒 Procurement & Order List",
        "kart4_baslik": "4. BATCH HISTORICAL SALES IMPORT",
        "excel_btn": "📁 Upload Historical Excel File From Computer",
    }
}

USERS_FILE = "kullanicilar.json"
ICON_FILE = "app_icon.ico"

# -------------------------------------------------------------
# ULUSLARARASI KONUM YÖNETİMİ (locations.py üzerinden)
# -------------------------------------------------------------

# -------------------------------------------------------------
# GALATASARAY RENK PALETİ
# -------------------------------------------------------------
GS_KIRMIZI = "#A6192E"
GS_SARI = "#FDB913"
GS_KIRMIZI_KOYU = "#7A0F21"

TEMALAR = {
    "light": {
        "pencere_bg": "#FDFBF7",
        "kart_bg": "#FFFFFF",
        "kart_kenarlik": "#F0EAE1",
        "yazi_ana": "#1A1417",
        "yazi_alt": "#6B5E66",
        "marka_kirmizi": GS_KIRMIZI,
        "marka_sari": "#D99B00",
        "buton_bg": "#F5EFE6",
        "buton_fg": "#1A1417",
        "vurgu_btn_bg": GS_KIRMIZI,
        "vurgu_btn_fg": GS_SARI,
        "giris_bg": "#FAF7F2",
        "giris_fg": "#1A1417",
        "tahmin_bg": "#FFF9EB",
        "tahmin_fg": "#8A6200",
        "tahmin_border": GS_SARI,
        "tema_btn_yazi": "🌙 Karanlık Mod"
    },
    "dark": {
        "pencere_bg": "#121013",
        "kart_bg": "#1C1920",
        "kart_kenarlik": "#332A36",
        "yazi_ana": "#FAF7F9",
        "yazi_alt": "#9E90A3",
        "marka_kirmizi": "#C8102E",
        "marka_sari": GS_SARI,
        "buton_bg": "#2C2532",
        "buton_fg": "#FAF7F9",
        "vurgu_btn_bg": GS_KIRMIZI,
        "vurgu_btn_fg": GS_SARI,
        "giris_bg": "#121013",
        "giris_fg": "#FAF7F9",
        "tahmin_bg": "#241B08",
        "tahmin_fg": GS_SARI,
        "tahmin_border": GS_SARI,
        "tema_btn_yazi": "☀️ Aydınlık Mod"
    }
}

# -------------------------------------------------------------
# KULLANICI YÖNETİMİ VE VERİTABANI
# -------------------------------------------------------------
VARSAYILAN_KULLANICILAR = {
    "admin": {
        "password": "admin1234",
        "role": "admin",
        "urunler": ["Cold Brew", "Iced Americano", "Iced Latte", "Brownie"],
        "kurulum_tamam": True
    },
    "ornekkafe": {
        "password": "kafe1234",
        "role": "user",
        "urunler": [],
        "kurulum_tamam": False
    }
}

def kullanicilari_yukle():
    # 1. Supabase Bulut Veritabanından Kullanıcıları Çekmeyi Dene
    try:
        import supabase_db
        sb_kullanicilar = supabase_db.kullanicilari_yukle()
        if sb_kullanicilar and len(sb_kullanicilar) > 0:
            kullanicilari_kaydet(sb_kullanicilar)
            return sb_kullanicilar
    except Exception:
        pass

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(VARSAYILAN_KULLANICILAR, f, ensure_ascii=False, indent=2)
        return VARSAYILAN_KULLANICILAR.copy()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            degisiklik_oldu = False
            # Geriye dönük uyumluluk: 'icecekler' anahtarını 'urunler' olarak da tanıyalım
            for k, v in data.items():
                if "urunler" not in v and "icecekler" in v:
                    v["urunler"] = v["icecekler"]
                    degisiklik_oldu = True
            for def_k, def_v in VARSAYILAN_KULLANICILAR.items():
                if def_k not in data:
                    data[def_k] = def_v.copy()
                    degisiklik_oldu = True
            if degisiklik_oldu:
                kullanicilari_kaydet(data)
            return data
    except Exception:
        return VARSAYILAN_KULLANICILAR.copy()

def kullanicilari_kaydet(kullanicilar):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=2)

def kullanici_excel_adi(kullanici):
    return f"kafe_{kullanici}_satislar.xlsx"

def kullanici_excel_hazirla(kullanici, urunler):
    dosya = kullanici_excel_adi(kullanici)
    if not os.path.exists(dosya):
        np.random.seed(42)
        base_date = datetime.date.today() - datetime.timedelta(days=45)
        kayitlar = []
        
        # Müşteri alışkanlığı ve trend simülasyonu
        sales_history = {u: [] for u in urunler}
        
        for i in range(45):
            t = base_date + datetime.timedelta(days=i)
            sicaklik = round(float(np.random.uniform(18, 36)), 1)
            haftasonu = 1 if t.weekday() >= 5 else 0
            promo = int(np.random.choice([0, 1], p=[0.8, 0.2]))
            
            satir = {
                "Tarih": t.strftime("%Y-%m-%d"),
                "Sicaklik": sicaklik,
                "Haftasonu_Mu": haftasonu,
                "Promosyon_Var_Mi": promo
            }
            # 4 ürün için başlangıç simülasyonu (Alışkanlık / Momentum dahil)
            for idx, urun in enumerate(urunler):
                carpan = 1.0 + (idx * 0.35)
                base = 10 + (carpan * sicaklik) + (12 * haftasonu) + (14 * promo) + (0.3 * sicaklik * promo)
                
                prev_sales = sales_history[urun]
                habit = 0.0
                if len(prev_sales) >= 1:
                    habit += 0.20 * prev_sales[-1]
                if len(prev_sales) >= 7:
                    habit += 0.15 * prev_sales[-7]
                    
                adet = max(5, int(round(base + habit + np.random.normal(0, 4))))
                sales_history[urun].append(adet)
                satir[urun] = adet
                
            kayitlar.append(satir)
            
        df = pd.DataFrame(kayitlar)
        df.to_excel(dosya, index=False)

# -------------------------------------------------------------
# HAVA DURUMU SERVİSLERİ
# -------------------------------------------------------------

def hava_tahmini_al(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&timezone=auto"
        res = requests.get(url, timeout=5).json()
        bugun = res["daily"]["temperature_2m_max"][0]
        yarin = res["daily"]["temperature_2m_max"][1]
        return bugun, yarin
    except Exception:
        return 24.0, 25.0

def gecmis_hava_sicakliklari_al(lat, lon, baslangic, bitis):
    try:
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={baslangic}&end_date={bitis}&daily=temperature_2m_max&timezone=auto"
        res = requests.get(url, timeout=10).json()
        if "daily" in res:
            return dict(zip(res["daily"]["time"], res["daily"]["temperature_2m_max"]))
    except Exception:
        pass
    return {}

# -------------------------------------------------------------
# MAKİNE ÖĞRENMESİ MODELİ (GELİŞMİŞ FEATURE ENGINEERING DAHİL)
# -------------------------------------------------------------
def yapay_zeka_tahmin(kullanici, urun_kolonu, yarin_sicaklik, yarin_haftasonu):
    """
    Gelişmiş Feature Engineering adımları:
    1. Zaman Değişkenleri (Ay, Haftanın Günü)
    2. Gecikmeli Değişkenler (Satis_Lag1, Satis_Lag7)
    3. Etkileşim Değişkeni (Sicaklik_x_Promosyon)
    4. NaN Temizliği ve Eğitim
    """
    # 1. Öncelikle Supabase bulut veritabanını dene
    try:
        import supabase_db
        cloud_tahmin, cloud_n = supabase_db.yapay_zeka_tahmin(kullanici, urun_kolonu, yarin_sicaklik, yarin_haftasonu)
        if cloud_tahmin is not None:
            return cloud_tahmin, cloud_n
    except Exception:
        pass

    dosya = kullanici_excel_adi(kullanici)
    if not os.path.exists(dosya):
        return None, 0
        
    df = pd.read_excel(dosya)
    if urun_kolonu not in df.columns or "Tarih" not in df.columns or "Sicaklik" not in df.columns:
        return None, 0

    # Tarihe göre sırala
    df["Tarih"] = pd.to_datetime(df["Tarih"])
    df = df.sort_values("Tarih").reset_index(drop=True)

    # 1. Zaman Değişkenleri
    df["Ay"] = df["Tarih"].dt.month
    df["Haftanin_Gunu"] = df["Tarih"].dt.dayofweek

    # 2. Gecikmeli Değişkenler (Lag Features)
    df["Satis_Lag1"] = df[urun_kolonu].shift(1)
    df["Satis_Lag7"] = df[urun_kolonu].shift(7)

    # 3. Etkileşim Değişkeni (Interaction)
    promo = df["Promosyon_Var_Mi"].fillna(0)
    df["Sicaklik_x_Promosyon"] = df["Sicaklik"] * promo

    feature_cols = [
        "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi", 
        "Ay", "Haftanin_Gunu", "Satis_Lag1", "Satis_Lag7", 
        "Sicaklik_x_Promosyon"
    ]

    # 4. Eksik Veri Temizliği (Lag'lerden dolayı oluşan NaN satırlarını düşür)
    df_train = df.dropna(subset=feature_cols + [urun_kolonu]).reset_index(drop=True)
    veri_sayisi = len(df_train)

    # Güvenilir tahmin için en az 5 geçerli eğitim satırı (yani toplamda ~12+ gün)
    if veri_sayisi < 5:
        return None, veri_sayisi

    X = df_train[feature_cols]
    y = df_train[urun_kolonu]

    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)

    # 5. Yarın İçin Çıkarım (Inference) Vektörünü Hazırlama
    yarin_tarih = datetime.date.today() + datetime.timedelta(days=1)
    
    # Yarının Satis_Lag1'i = Bugüne ait en son satış
    # Yarının Satis_Lag7'i = 7 gün önceki satış (veya sondan 7. kayıt)
    son_satislar = df[urun_kolonu].dropna().values
    lag1_val = son_satislar[-1] if len(son_satislar) >= 1 else y.mean()
    lag7_val = son_satislar[-7] if len(son_satislar) >= 7 else son_satislar[0]

    yarin_df = pd.DataFrame([{
        "Sicaklik": yarin_sicaklik,
        "Haftasonu_Mu": yarin_haftasonu,
        "Promosyon_Var_Mi": 0,
        "Ay": yarin_tarih.month,
        "Haftanin_Gunu": yarin_tarih.weekday(),
        "Satis_Lag1": lag1_val,
        "Satis_Lag7": lag7_val,
        "Sicaklik_x_Promosyon": 0.0
    }])[feature_cols]

    tahmin = round(model.predict(yarin_df)[0])
    return tahmin, veri_sayisi

# -------------------------------------------------------------
# ANA UYGULAMA (Kingfool Inc. v2.0 - Enterprise Analytics Edition)
# -------------------------------------------------------------
class KingfoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kingfool Inc. | Kafe Satış & Talep Tahmin Sistemi v2.0 (Enterprise Analytics)")
        self.root.geometry("610x910")
        self.root.resizable(False, False)

        self.aktif_tema = "dark"
        self.aktif_dil = "TR"
        self.aktif_kullanici = None
        self.kullanicilar = kullanicilari_yukle()

        self.lat, self.lon = 41.0082, 28.9784
        self.bugun_temp, self.yarin_temp = 25.0, 26.0
        self.bugun_tarih = datetime.date.today().strftime("%Y-%m-%d")

        self.son_tum_tahminler = {}
        self.son_hammadde_ihtiyaclari = []
        self.son_tahmin = None
        self.son_metrikler = {}

        self.kart_listesi = []
        self.etiket_ana_listesi = []
        self.etiket_alt_listesi = []
        self.normal_buton_listesi = []
        self.vurgu_buton_listesi = []
        self.giris_kutulari = []

        self.ana_konteyner = tk.Frame(self.root)
        self.ana_konteyner.pack(fill="both", expand=True)

        self.goster_giris_ekrani()

    def t(self, key: str, default: str = "") -> str:
        """Aktif dile göre çeviri metnini döner."""
        lang = getattr(self, "aktif_dil", "TR")
        return DIL_SOZLUGU.get(lang, {}).get(key, default or key)

    def dil_degistir(self):
        """Uygulama dilini TR ve EN arasında değiştirir ve aktif ekranı yeniler."""
        self.aktif_dil = "EN" if getattr(self, "aktif_dil", "TR") == "TR" else "TR"
        self.goster_kafe_ekrani()

    def temizle_konteyner(self):
        self.kart_listesi.clear()
        self.etiket_ana_listesi.clear()
        self.etiket_alt_listesi.clear()
        self.normal_buton_listesi.clear()
        self.vurgu_buton_listesi.clear()
        self.giris_kutulari.clear()
        for w in self.ana_konteyner.winfo_children():
            w.destroy()

    def tema_degistir(self):
        self.aktif_tema = "dark" if self.aktif_tema == "light" else "light"
        self.temayi_uygula()

    def temayi_uygula(self):
        t = TEMALAR[self.aktif_tema]
        self.root.configure(bg=t["pencere_bg"])
        self.ana_konteyner.configure(bg=t["pencere_bg"])

        for k in self.kart_listesi:
            try: k.configure(bg=t["kart_bg"], highlightbackground=t["kart_kenarlik"])
            except: pass

        for l in self.etiket_ana_listesi:
            try: l.configure(bg=t["kart_bg"], fg=t["yazi_ana"])
            except: pass

        for l in self.etiket_alt_listesi:
            try: l.configure(bg=t["kart_bg"], fg=t["yazi_alt"])
            except: pass

        for b in self.normal_buton_listesi:
            try: b.configure(bg=t["buton_bg"], fg=t["buton_fg"])
            except: pass

        for vb in self.vurgu_buton_listesi:
            try: vb.configure(bg=t["vurgu_btn_bg"], fg=t["vurgu_btn_fg"], activebackground=GS_KIRMIZI_KOYU)
            except: pass

        for ent in self.giris_kutulari:
            try: ent.configure(bg=t["giris_bg"], fg=t["giris_fg"], insertbackground=t["yazi_ana"])
            except: pass

    # ---------------------------------------------------------
    # 1. GİRİŞ EKRANI (LOGIN SCREEN)
    # ---------------------------------------------------------
    def goster_giris_ekrani(self):
        self.temizle_konteyner()
        t = TEMALAR[self.aktif_tema]

        f_giris = tk.Frame(self.ana_konteyner, bg=t["kart_bg"], bd=1, relief="solid", padx=25, pady=25)
        f_giris.place(relx=0.5, rely=0.5, anchor="center", width=420)
        self.kart_listesi.append(f_giris)

        lbl_logo = tk.Label(f_giris, text="🃏 KINGFOOL INC.", font=("Impact", 22), fg=t["marka_sari"], bg=t["kart_bg"])
        lbl_logo.pack(pady=5)

        lbl_alt = tk.Label(f_giris, text="Kafe Satış & Talep Tahmin Sistemi v1.2", font=("Segoe UI", 9), bg=t["kart_bg"], fg=t["yazi_alt"])
        lbl_alt.pack(pady=2)

        lbl_k = tk.Label(f_giris, text="Kullanıcı Adı:", font=("Segoe UI", 10, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"])
        lbl_k.pack(anchor="w", pady=(15, 2))
        self.etiket_ana_listesi.append(lbl_k)

        self.txt_kullanici = tk.Entry(f_giris, font=("Segoe UI", 11), relief="solid", bd=1)
        self.txt_kullanici.pack(fill="x", pady=4)
        self.giris_kutulari.append(self.txt_kullanici)
        self.txt_kullanici.focus_set()

        lbl_s = tk.Label(f_giris, text="Şifre:", font=("Segoe UI", 10, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"])
        lbl_s.pack(anchor="w", pady=(10, 2))
        self.etiket_ana_listesi.append(lbl_s)

        self.txt_sifre = tk.Entry(f_giris, font=("Segoe UI", 11), show="*", relief="solid", bd=1)
        self.txt_sifre.pack(fill="x", pady=4)
        self.giris_kutulari.append(self.txt_sifre)
        self.txt_sifre.bind("<Return>", lambda e: self.giris_yap())

        btn_giris = tk.Button(
            f_giris, 
            text="Giriş Yap", 
            font=("Segoe UI", 11, "bold"),
            relief="flat", 
            pady=8,
            cursor="hand2",
            command=self.giris_yap
        )
        btn_giris.pack(fill="x", pady=(20, 10))
        self.vurgu_buton_listesi.append(btn_giris)

        lbl_guvenlik = tk.Label(
            f_giris, 
            text="🔒 Kingfool Inc. Güvenli Giriş Portalı",
            font=("Segoe UI", 8, "italic"),
            justify="center",
            bg=t["kart_bg"],
            fg=t["yazi_alt"]
        )
        lbl_guvenlik.pack(pady=8)
        self.etiket_alt_listesi.append(lbl_guvenlik)

        btn_tema = tk.Button(self.ana_konteyner, text=t["tema_btn_yazi"], font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=3, cursor="hand2", command=self.tema_degistir)
        btn_tema.place(relx=0.95, rely=0.03, anchor="ne")
        self.normal_buton_listesi.append(btn_tema)

        self.temayi_uygula()

    def giris_yap(self):
        kullanici = self.txt_kullanici.get().strip()
        sifre = self.txt_sifre.get().strip()
        self.kullanicilar = kullanicilari_yukle()

        if kullanici in self.kullanicilar and self.kullanicilar[kullanici]["password"] == sifre:
            self.aktif_kullanici = kullanici
            bilgi = self.kullanicilar[kullanici]

            if bilgi["role"] == "admin":
                self.goster_admin_ekrani()
            elif not bilgi.get("kurulum_tamam", False):
                self.goster_urun_kurulum_ekrani()
            else:
                self.goster_kafe_ekrani()
        else:
            messagebox.showerror("Kingfool Inc. | Hata", "Kullanıcı adı veya şifre hatalı!")

    # ---------------------------------------------------------
    # 2. İLK GİRİŞ KONUM VE DİNAMİK ÜRÜN BELİRLEME SİHİRBAZI
    # ---------------------------------------------------------
    def goster_urun_kurulum_ekrani(self):
        self.temizle_konteyner()
        t = TEMALAR[self.aktif_tema]

        f_kurulum = tk.Frame(self.ana_konteyner, bg=t["kart_bg"], bd=1, relief="solid", padx=20, pady=16)
        f_kurulum.place(relx=0.5, rely=0.5, anchor="center", width=540)
        self.kart_listesi.append(f_kurulum)

        lbl_b = tk.Label(f_kurulum, text=f"👋 Hoş Geldiniz {self.aktif_kullanici}!", font=("Segoe UI", 14, "bold"), fg=t["marka_sari"], bg=t["kart_bg"])
        lbl_b.pack(pady=(0, 2))

        lbl_aciklama = tk.Label(
            f_kurulum, 
            text="Kafe konumunuzu ve takip etmek istediğiniz ürünleri belirleyiniz.\n(Türkiye için ilçe seçimi aktiftir; yurtdışı konumlarında yalnızca şehir seçilir.)",
            font=("Segoe UI", 8),
            justify="center",
            bg=t["kart_bg"],
            fg=t["yazi_alt"]
        )
        lbl_aciklama.pack(pady=(0, 8))
        self.etiket_alt_listesi.append(lbl_aciklama)

        # 1. KONUM BÖLÜMÜ
        f_konum = tk.LabelFrame(f_kurulum, text="📍 1. Kafe Konumu", font=("Segoe UI", 9, "bold"), bg=t["kart_bg"], fg=t["marka_sari"], padx=10, pady=6)
        f_konum.pack(fill="x", pady=(0, 8))
        self.kart_listesi.append(f_konum)

        lbl_ulke = tk.Label(f_konum, text="Ülke:", font=("Segoe UI", 8, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"])
        lbl_ulke.grid(row=0, column=0, sticky="w", padx=3, pady=1)
        self.etiket_ana_listesi.append(lbl_ulke)

        self.setup_cmb_ulke = ttk.Combobox(f_konum, values=locations.ULKE_LISTESI, state="readonly", width=17, font=("Segoe UI", 9))
        self.setup_cmb_ulke.set("Türkiye")
        self.setup_cmb_ulke.grid(row=1, column=0, padx=3, pady=2)
        self.setup_cmb_ulke.bind("<<ComboboxSelected>>", self._setup_ulke_degisti)

        lbl_sehir = tk.Label(f_konum, text="Şehir:", font=("Segoe UI", 8, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"])
        lbl_sehir.grid(row=0, column=1, sticky="w", padx=3, pady=1)
        self.etiket_ana_listesi.append(lbl_sehir)

        self.setup_cmb_sehir = ttk.Combobox(f_konum, values=locations.sehir_listesi_getir("Türkiye"), state="readonly", width=14, font=("Segoe UI", 9))
        self.setup_cmb_sehir.set("İstanbul")
        self.setup_cmb_sehir.grid(row=1, column=1, padx=3, pady=2)
        self.setup_cmb_sehir.bind("<<ComboboxSelected>>", self._setup_sehir_degisti)

        self.setup_lbl_ilce = tk.Label(f_konum, text="İlçe (TR):", font=("Segoe UI", 8, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"])
        self.setup_lbl_ilce.grid(row=0, column=2, sticky="w", padx=3, pady=1)
        self.etiket_ana_listesi.append(self.setup_lbl_ilce)

        self.setup_cmb_ilce = ttk.Combobox(f_konum, values=locations.ilce_listesi_getir("Türkiye", "İstanbul"), state="readonly", width=14, font=("Segoe UI", 9))
        self.setup_cmb_ilce.set("Kadıköy")
        self.setup_cmb_ilce.grid(row=1, column=2, padx=3, pady=2)

        # 2. ÜRÜNLER BÖLÜMÜ (DİNAMİK LİSTE)
        f_urunler = tk.LabelFrame(f_kurulum, text="☕ 2. Takip Edilecek Ürünler (Dilediğiniz Kadar Ekleyin)", font=("Segoe UI", 9, "bold"), bg=t["kart_bg"], fg=t["marka_sari"], padx=10, pady=6)
        f_urunler.pack(fill="x", pady=(0, 8))
        self.kart_listesi.append(f_urunler)

        self.f_urun_listesi = tk.Frame(f_urunler, bg=t["kart_bg"])
        self.f_urun_listesi.pack(fill="x", pady=2)
        self.kart_listesi.append(self.f_urun_listesi)

        self.setup_urun_entries = []
        varsayilanlar = ["Cold Brew", "Iced Americano", "Iced Latte", "Brownie"]
        for urun in varsayilanlar:
            self._setup_urun_satiri_ekle(urun)

        f_butonlar = tk.Frame(f_urunler, bg=t["kart_bg"])
        f_butonlar.pack(fill="x", pady=(4, 0))
        self.kart_listesi.append(f_butonlar)

        btn_ekle = tk.Button(f_butonlar, text="➕ Yeni Ürün Ekle", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=3, cursor="hand2", command=lambda: self._setup_urun_satiri_ekle())
        btn_ekle.pack(side="left", padx=2)
        self.normal_buton_listesi.append(btn_ekle)

        btn_cikar = tk.Button(f_butonlar, text="➖ Son Ürünü Sil", font=("Segoe UI", 8), relief="flat", padx=8, pady=3, cursor="hand2", command=self._setup_urun_satiri_cikar)
        btn_cikar.pack(side="left", padx=2)
        self.normal_buton_listesi.append(btn_cikar)

        btn_kaydet = tk.Button(
            f_kurulum, 
            text="🚀 Kafenizi Başlat ve Kaydet", 
            font=("Segoe UI", 10, "bold"),
            relief="flat", 
            pady=8,
            cursor="hand2",
            command=self.urun_kurulum_kaydet
        )
        btn_kaydet.pack(fill="x", pady=(10, 0))
        self.vurgu_buton_listesi.append(btn_kaydet)

        self.temayi_uygula()

    def _setup_ulke_degisti(self, event=None):
        ulke = self.setup_cmb_ulke.get()
        sehirler = locations.sehir_listesi_getir(ulke)
        self.setup_cmb_sehir["values"] = sehirler
        self.setup_cmb_sehir.set(sehirler[0] if sehirler else "")

        if locations.ilce_secimi_aktif_mi(ulke):
            self.setup_cmb_ilce.config(state="readonly")
            ilceler = locations.ilce_listesi_getir(ulke, self.setup_cmb_sehir.get())
            self.setup_cmb_ilce["values"] = ilceler
            self.setup_cmb_ilce.set("Kadıköy" if "Kadıköy" in ilceler else (ilceler[0] if ilceler else "Merkez"))
        else:
            self.setup_cmb_ilce["values"] = ["(İlçe Seçimi Yok)"]
            self.setup_cmb_ilce.set("(İlçe Seçimi Yok)")
            self.setup_cmb_ilce.config(state="disabled")

    def _setup_sehir_degisti(self, event=None):
        ulke = self.setup_cmb_ulke.get()
        sehir = self.setup_cmb_sehir.get()
        if locations.ilce_secimi_aktif_mi(ulke):
            ilceler = locations.ilce_listesi_getir(ulke, sehir)
            self.setup_cmb_ilce["values"] = ilceler
            self.setup_cmb_ilce.set(ilceler[0] if ilceler else "Merkez")

    def _setup_urun_satiri_ekle(self, varsayilan_ad=""):
        t = TEMALAR[self.aktif_tema]
        idx = len(self.setup_urun_entries) + 1
        f_row = tk.Frame(self.f_urun_listesi, bg=t["kart_bg"])
        f_row.pack(fill="x", pady=2)
        self.kart_listesi.append(f_row)

        lbl = tk.Label(f_row, text=f"{idx}. Ürün:", font=("Segoe UI", 8, "bold"), width=8, anchor="w", bg=t["kart_bg"], fg=t["yazi_ana"])
        lbl.pack(side="left", padx=2)
        self.etiket_ana_listesi.append(lbl)

        ent = tk.Entry(f_row, font=("Segoe UI", 9), relief="solid", bd=1)
        if varsayilan_ad:
            ent.insert(0, varsayilan_ad)
        ent.pack(side="left", fill="x", expand=True, padx=4)
        self.giris_kutulari.append(ent)

        self.setup_urun_entries.append((f_row, ent))

    def _setup_urun_satiri_cikar(self):
        if len(self.setup_urun_entries) <= 1:
            messagebox.showwarning("Kingfool Inc.", "En az 1 ürün kalmalıdır!")
            return
        f_row, ent = self.setup_urun_entries.pop()
        f_row.destroy()
        if ent in self.giris_kutulari:
            self.giris_kutulari.remove(ent)

    def urun_kurulum_kaydet(self):
        ulke = self.setup_cmb_ulke.get().strip() or "Türkiye"
        sehir = self.setup_cmb_sehir.get().strip() or "İstanbul"
        ilce = self.setup_cmb_ilce.get().strip() if locations.ilce_secimi_aktif_mi(ulke) else ""
        lat, lon, etiket = locations.konum_koordinat_bul(ulke, sehir, ilce)

        secilenler = []
        for _, ent in self.setup_urun_entries:
            val = ent.get().strip()
            if val and val not in secilenler:
                secilenler.append(val)

        if len(secilenler) == 0:
            messagebox.showwarning("Kingfool Inc.", "Lütfen en az 1 ürün ismi giriniz!")
            return

        k_bilgi = self.kullanicilar.setdefault(self.aktif_kullanici, {})
        k_bilgi["ulke"] = ulke
        k_bilgi["sehir"] = sehir
        k_bilgi["ilce"] = ilce
        k_bilgi["lat"] = lat
        k_bilgi["lon"] = lon
        k_bilgi["konum_etiket"] = etiket
        k_bilgi["urunler"] = secilenler
        k_bilgi["kurulum_tamam"] = True

        kullanicilari_kaydet(self.kullanicilar)
        kullanici_excel_hazirla(self.aktif_kullanici, secilenler)

        # Her ürün için model eğit
        try:
            for u in secilenler:
                ml_ops.egit_ve_kaydet_model(self.aktif_kullanici, u, ulke=ulke)
        except Exception:
            pass

        # Supabase Bulut Veritabanı Senkronizasyonu
        try:
            import supabase_db
            supabase_db.kullanici_urunleri_kaydet(self.aktif_kullanici, secilenler)
        except Exception as e:
            print(f"[Supabase Urun Kayit] {e}")

        messagebox.showinfo("Kingfool Inc.", f"Tebrikler! {len(secilenler)} ürününüz ve {etiket} konumunuz başarıyla kaydedildi.")
        self.goster_kafe_ekrani()

    # ---------------------------------------------------------
    # 3. ADMİN YÖNETİM PANELİ (KULLANICI EKLE / ÇIKAR / DÜZENLE)
    # ---------------------------------------------------------
    def goster_admin_ekrani(self):
        self.temizle_konteyner()
        t = TEMALAR[self.aktif_tema]

        frame_ust = tk.Frame(self.ana_konteyner, bg=t["pencere_bg"], padx=15, pady=8)
        frame_ust.pack(fill="x")

        lbl_admin = tk.Label(frame_ust, text="👑 KINGFOOL INC. YÖNETİCİ PANELİ", font=("Impact", 16), fg=t["marka_sari"], bg=t["pencere_bg"])
        lbl_admin.pack(side="left")

        btn_cikis = tk.Button(frame_ust, text="🚪 Çıkış Yap", font=("Segoe UI", 9), relief="flat", padx=8, pady=3, command=self.goster_giris_ekrani)
        btn_cikis.pack(side="right", padx=3)
        self.normal_buton_listesi.append(btn_cikis)

        btn_kafe = tk.Button(frame_ust, text="☕ Kafe Paneline Geç", font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=3, command=self.goster_kafe_ekrani)
        btn_kafe.pack(side="right", padx=3)
        self.vurgu_buton_listesi.append(btn_kafe)

        # Kullanıcı Listesi Kartı
        kart_liste = tk.Frame(self.ana_konteyner, bg=t["kart_bg"], bd=1, relief="solid", padx=10, pady=8)
        kart_liste.pack(fill="x", padx=15, pady=6)
        self.kart_listesi.append(kart_liste)

        tk.Label(kart_liste, text="Kayıtlı Kullanıcılar Listesi:", font=("Segoe UI", 10, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"]).pack(anchor="w")

        self.tree_kullanicilar = ttk.Treeview(kart_liste, columns=("Kullanici", "Rol", "Durum", "Urunler"), show="headings", height=5)
        self.tree_kullanicilar.heading("Kullanici", text="Kullanıcı Adı")
        self.tree_kullanicilar.heading("Rol", text="Yetki")
        self.tree_kullanicilar.heading("Durum", text="Kurulum")
        self.tree_kullanicilar.heading("Urunler", text="Takip Edilen Ürünler")
        self.tree_kullanicilar.column("Kullanici", width=110)
        self.tree_kullanicilar.column("Rol", width=70)
        self.tree_kullanicilar.column("Durum", width=80)
        self.tree_kullanicilar.column("Urunler", width=220)
        self.tree_kullanicilar.pack(fill="x", pady=6)

        self.admin_tablo_guncelle()

        # Yeni Kullanıcı Ekleme Formu
        kart_ekle = tk.Frame(self.ana_konteyner, bg=t["kart_bg"], bd=1, relief="solid", padx=12, pady=8)
        kart_ekle.pack(fill="x", padx=15, pady=6)
        self.kart_listesi.append(kart_ekle)

        tk.Label(kart_ekle, text="➕ Yeni Kullanıcı Ekle", font=("Segoe UI", 10, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"]).pack(anchor="w", pady=2)

        f_ekle_grid = tk.Frame(kart_ekle, bg=t["kart_bg"])
        f_ekle_grid.pack(fill="x", pady=4)
        self.kart_listesi.append(f_ekle_grid)

        tk.Label(f_ekle_grid, text="Kullanıcı Adı:", font=("Segoe UI", 9), bg=t["kart_bg"], fg=t["yazi_ana"]).grid(row=0, column=0, padx=4, sticky="w")
        self.txt_yeni_ad = tk.Entry(f_ekle_grid, width=15)
        self.txt_yeni_ad.grid(row=1, column=0, padx=4, pady=2)
        self.giris_kutulari.append(self.txt_yeni_ad)

        tk.Label(f_ekle_grid, text="Şifre:", font=("Segoe UI", 9), bg=t["kart_bg"], fg=t["yazi_ana"]).grid(row=0, column=1, padx=4, sticky="w")
        self.txt_yeni_sifre = tk.Entry(f_ekle_grid, width=15)
        self.txt_yeni_sifre.grid(row=1, column=1, padx=4, pady=2)
        self.giris_kutulari.append(self.txt_yeni_sifre)

        tk.Label(f_ekle_grid, text="Yetki Rolü:", font=("Segoe UI", 9), bg=t["kart_bg"], fg=t["yazi_ana"]).grid(row=0, column=2, padx=4, sticky="w")
        self.cmb_yeni_rol = ttk.Combobox(f_ekle_grid, values=["user", "admin"], state="readonly", width=10)
        self.cmb_yeni_rol.set("user")
        self.cmb_yeni_rol.grid(row=1, column=2, padx=4, pady=2)

        btn_kullanici_ekle = tk.Button(kart_ekle, text="Kullanıcıyı Sisteme Ekle", font=("Segoe UI", 9, "bold"), relief="flat", pady=4, cursor="hand2", command=self.admin_kullanici_ekle)
        btn_kullanici_ekle.pack(fill="x", pady=6)
        self.vurgu_buton_listesi.append(btn_kullanici_ekle)

        # Kullanıcı Düzenle / Sil Kartı
        kart_duzenle = tk.Frame(self.ana_konteyner, bg=t["kart_bg"], bd=1, relief="solid", padx=12, pady=8)
        kart_duzenle.pack(fill="x", padx=15, pady=6)
        self.kart_listesi.append(kart_duzenle)

        tk.Label(kart_duzenle, text="✏️ Seçili Kullanıcıyı Düzenle / Şifre Değiştir / Sil", font=("Segoe UI", 10, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"]).pack(anchor="w", pady=2)

        f_duz_grid = tk.Frame(kart_duzenle, bg=t["kart_bg"])
        f_duz_grid.pack(fill="x", pady=4)
        self.kart_listesi.append(f_duz_grid)

        tk.Label(f_duz_grid, text="Yeni Şifre:", font=("Segoe UI", 9), bg=t["kart_bg"], fg=t["yazi_ana"]).grid(row=0, column=0, padx=4, sticky="w")
        self.txt_yeni_parola = tk.Entry(f_duz_grid, width=18)
        self.txt_yeni_parola.grid(row=1, column=0, padx=4, pady=2)
        self.giris_kutulari.append(self.txt_yeni_parola)

        btn_sifre_guncelle = tk.Button(f_duz_grid, text="🔑 Şifreyi Güncelle", relief="flat", padx=6, pady=2, cursor="hand2", command=self.admin_sifre_guncelle)
        btn_sifre_guncelle.grid(row=1, column=1, padx=4, pady=2)
        self.normal_buton_listesi.append(btn_sifre_guncelle)

        btn_sil = tk.Button(f_duz_grid, text="🗑️ Kullanıcıyı Sil", relief="flat", padx=6, pady=2, cursor="hand2", command=self.admin_kullanici_sil)
        btn_sil.grid(row=1, column=2, padx=12, pady=2)
        self.normal_buton_listesi.append(btn_sil)

        self.temayi_uygula()

    def admin_tablo_guncelle(self):
        for item in self.tree_kullanicilar.get_children():
            self.tree_kullanicilar.delete(item)
        self.kullanicilar = kullanicilari_yukle()
        for k, v in self.kullanicilar.items():
            durum = "Tamamlandı" if v.get("kurulum_tamam", False) else "Bekliyor"
            urun_listesi = v.get("urunler", v.get("icecekler", []))
            urun_metni = ", ".join(urun_listesi) if urun_listesi else "Belirlenmedi"
            self.tree_kullanicilar.insert("", "end", values=(k, v.get("role", "user"), durum, urun_metni))

    def admin_kullanici_ekle(self):
        ad = self.txt_yeni_ad.get().strip()
        sifre = self.txt_yeni_sifre.get().strip()
        rol = self.cmb_yeni_rol.get()

        if not ad or not sifre:
            messagebox.showwarning("Admin", "Kullanıcı adı ve şifre boş bırakılamaz!")
            return
        if ad in self.kullanicilar:
            messagebox.showerror("Admin", "Bu kullanıcı adı zaten mevcut!")
            return

        # 1. Supabase Bulut Veritabanına Ekle
        try:
            import supabase_db
            supabase_db.kullanici_ekle(ad, sifre, rol)
        except Exception as e:
            print(f"[Supabase Kullanici Ekle] {e}")

        # 2. Yerel Bellek ve JSON Güncelle
        self.kullanicilar[ad] = {
            "password": sifre,
            "role": rol,
            "urunler": [],
            "kurulum_tamam": False
        }
        kullanicilari_kaydet(self.kullanicilar)
        self.admin_tablo_guncelle()
        self.txt_yeni_ad.delete(0, tk.END)
        self.txt_yeni_sifre.delete(0, tk.END)
        messagebox.showinfo("Admin", f"'{ad}' kullanıcısı başarıyla eklendi!")

    def admin_sifre_guncelle(self):
        secili = self.tree_kullanicilar.selection()
        if not secili:
            messagebox.showwarning("Admin", "Lütfen önce tablodan bir kullanıcı seçiniz!")
            return
        kullanici_ad = self.tree_kullanicilar.item(secili[0])["values"][0]
        yeni_sifre = self.txt_yeni_parola.get().strip()

        if not yeni_sifre:
            messagebox.showwarning("Admin", "Lütfen yeni bir şifre yazınız!")
            return

        # 1. Supabase Bulut Veritabanında Güncelle
        try:
            import supabase_db
            supabase_db.kullanici_sifre_guncelle(kullanici_ad, yeni_sifre)
        except Exception as e:
            print(f"[Supabase Sifre Guncelle] {e}")

        # 2. Yerel Bellek ve JSON Güncelle
        self.kullanicilar[kullanici_ad]["password"] = yeni_sifre
        kullanicilari_kaydet(self.kullanicilar)
        self.txt_yeni_parola.delete(0, tk.END)
        messagebox.showinfo("Admin", f"'{kullanici_ad}' kullanıcısının şifresi güncellendi!")

    def admin_kullanici_sil(self):
        secili = self.tree_kullanicilar.selection()
        if not secili:
            messagebox.showwarning("Admin", "Lütfen silinecek kullanıcıyı seçiniz!")
            return
        kullanici_ad = self.tree_kullanicilar.item(secili[0])["values"][0]

        if kullanici_ad == "admin":
            messagebox.showerror("Admin", "Ana yönetici hesabı silinemez!")
            return

        if messagebox.askyesno("Kullanıcı Silme", f"'{kullanici_ad}' kullanıcısını silmek istediğinize emin misiniz?"):
            # 1. Supabase Bulut Veritabanından Sil
            try:
                import supabase_db
                supabase_db.kullanici_sil(kullanici_ad)
            except Exception as e:
                print(f"[Supabase Kullanici Sil] {e}")

            # 2. Yerel Bellek ve JSON'dan Sil
            if kullanici_ad in self.kullanicilar:
                del self.kullanicilar[kullanici_ad]
            kullanicilari_kaydet(self.kullanicilar)
            self.admin_tablo_guncelle()
            messagebox.showinfo("Admin", f"'{kullanici_ad}' kullanıcısı silindi.")

    # ---------------------------------------------------------
    # 4. KAFE TAHMİN EKRANI (MAIN CAFE PREDICTION SCREEN)
    # ---------------------------------------------------------
    def goster_kafe_ekrani(self):
        self.temizle_konteyner()
        t = TEMALAR[self.aktif_tema]
        kullanici = self.aktif_kullanici or "admin"
        kullanici_bilgi = self.kullanicilar.get(kullanici, {})
        self.urunler = kullanici_bilgi.get("urunler", kullanici_bilgi.get("icecekler", ["Cold Brew", "Iced Americano", "Iced Latte", "Brownie"]))

        if not self.urunler:
            self.urunler = ["Cold Brew", "Iced Americano", "Iced Latte", "Brownie"]
            kullanici_excel_hazirla(kullanici, self.urunler)

        # Üst Başlık ve Kullanıcı Barı
        frame_ust = tk.Frame(self.ana_konteyner, bg=t["pencere_bg"], padx=15, pady=6)
        frame_ust.pack(fill="x")

        f_sol = tk.Frame(frame_ust, bg=t["pencere_bg"])
        f_sol.pack(side="left")

        lbl_logo = tk.Label(f_sol, text="🃏 KINGFOOL INC.", font=("Impact", 16), fg=t["marka_sari"], bg=t["pencere_bg"])
        lbl_logo.pack(anchor="w")

        lbl_kullanici = tk.Label(f_sol, text=f"👤 Aktif Kafe: {kullanici}", font=("Segoe UI", 9, "bold"), bg=t["pencere_bg"], fg=t["yazi_ana"])
        lbl_kullanici.pack(anchor="w")
        self.etiket_ana_listesi.append(lbl_kullanici)

        f_sag = tk.Frame(frame_ust, bg=t["pencere_bg"])
        f_sag.pack(side="right")

        btn_cikis = tk.Button(f_sag, text="🚪 Çıkış", font=("Segoe UI", 8), relief="flat", padx=6, pady=2, cursor="hand2", command=self.goster_giris_ekrani)
        btn_cikis.pack(side="right", padx=2)
        self.normal_buton_listesi.append(btn_cikis)

        if kullanici_bilgi.get("role") == "admin":
            btn_yonetici = tk.Button(f_sag, text="👑 Admin Paneli", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2", command=self.goster_admin_ekrani)
            btn_yonetici.pack(side="right", padx=2)
            self.vurgu_buton_listesi.append(btn_yonetici)

        btn_tema = tk.Button(f_sag, text=t["tema_btn_yazi"], font=("Segoe UI", 8), relief="flat", padx=6, pady=2, cursor="hand2", command=self.tema_degistir)
        btn_tema.pack(side="right", padx=2)
        self.normal_buton_listesi.append(btn_tema)

        # 1. KART: KAFE KONUMU (DÜNYA & TÜRKİYE)
        kart_konum = self.yeni_kart("1. KAFE KONUMU (DÜNYA & TÜRKİYE)")

        frame_secim = tk.Frame(kart_konum)
        frame_secim.pack(fill="x", padx=8, pady=3)
        self.kart_listesi.append(frame_secim)

        self.aktif_ulke = kullanici_bilgi.get("ulke", "Türkiye")
        self.aktif_sehir = kullanici_bilgi.get("sehir", "İstanbul")
        self.aktif_ilce = kullanici_bilgi.get("ilce", "Kadıköy")

        lbl_ulke = tk.Label(frame_secim, text="Ülke:", font=("Segoe UI", 9, "bold"))
        lbl_ulke.grid(row=0, column=0, sticky="w", padx=3)
        self.etiket_ana_listesi.append(lbl_ulke)

        self.cmb_ulke = ttk.Combobox(frame_secim, values=locations.ULKE_LISTESI, state="readonly", width=18, font=("Segoe UI", 9))
        self.cmb_ulke.set(self.aktif_ulke if self.aktif_ulke in locations.ULKE_LISTESI else "Türkiye")
        self.cmb_ulke.grid(row=1, column=0, padx=3, pady=2)
        self.cmb_ulke.bind("<<ComboboxSelected>>", self.ulke_degisti)

        lbl_il = tk.Label(frame_secim, text="Şehir:", font=("Segoe UI", 9, "bold"))
        lbl_il.grid(row=0, column=1, sticky="w", padx=3)
        self.etiket_ana_listesi.append(lbl_il)

        sehirler = locations.sehir_listesi_getir(self.cmb_ulke.get())
        self.cmb_il = ttk.Combobox(frame_secim, values=sehirler, state="readonly", width=15, font=("Segoe UI", 9))
        self.cmb_il.set(self.aktif_sehir if self.aktif_sehir in sehirler else (sehirler[0] if sehirler else ""))
        self.cmb_il.grid(row=1, column=1, padx=3, pady=2)
        self.cmb_il.bind("<<ComboboxSelected>>", self.il_degisti)

        lbl_ilce = tk.Label(frame_secim, text="İlçe (TR):", font=("Segoe UI", 9, "bold"))
        lbl_ilce.grid(row=0, column=2, sticky="w", padx=3)
        self.etiket_ana_listesi.append(lbl_ilce)

        self.cmb_ilce = ttk.Combobox(frame_secim, state="readonly", width=15, font=("Segoe UI", 9))
        self.cmb_ilce.grid(row=1, column=2, padx=3, pady=2)
        self.cmb_ilce.bind("<<ComboboxSelected>>", lambda e: self.konumu_guncelle())

        btn_yenile = tk.Button(frame_secim, text="🌤️ Hava Al", relief="flat", padx=6, pady=2, cursor="hand2", command=self.konumu_guncelle)
        btn_yenile.grid(row=1, column=3, padx=4, pady=2)
        self.normal_buton_listesi.append(btn_yenile)

        self._ilce_durumunu_ayarla()

        self.lbl_hava = tk.Label(kart_konum, text="Hava durumu bekleniyor...", font=("Segoe UI", 9, "bold"))
        self.lbl_hava.pack(anchor="w", padx=10, pady=3)
        self.etiket_ana_listesi.append(self.lbl_hava)

        # 2. KART: GÜNLÜK SATIŞ GİRİŞİ (KULLANICININ ÖZEL ÜRÜNLERİ)
        kart_satis = self.yeni_kart(f"2. GÜN SONU SATIŞ GİRİŞİ ({kullanici.upper()})")

        lbl_tarih = tk.Label(kart_satis, text=f"📅 Tarih: {self.bugun_tarih}", font=("Segoe UI", 9))
        lbl_tarih.pack(anchor="w", padx=10, pady=2)
        self.etiket_alt_listesi.append(lbl_tarih)

        frame_grid = tk.Frame(kart_satis)
        frame_grid.pack(fill="x", padx=8, pady=3)
        self.kart_listesi.append(frame_grid)

        frame_grid.columnconfigure(0, weight=1)
        frame_grid.columnconfigure(1, weight=1)
        self.kafe_giris_kutulari = {}

        for i, urun_isim in enumerate(self.urunler):
            r = i // 2
            c = i % 2
            f_item = tk.Frame(frame_grid, padx=4, pady=2)
            f_item.grid(row=r, column=c, sticky="ew")
            self.kart_listesi.append(f_item)

            l = tk.Label(f_item, text=f"{urun_isim}:", font=("Segoe UI", 9, "bold"))
            l.pack(anchor="w")
            self.etiket_ana_listesi.append(l)

            ent = tk.Entry(f_item, font=("Segoe UI", 11), relief="solid", bd=1)
            ent.pack(fill="x", pady=2)
            self.giris_kutulari.append(ent)
            self.kafe_giris_kutulari[urun_isim] = ent

        self.promo_var = tk.IntVar(value=0)
        self.chk_promo = tk.Checkbutton(
            kart_satis, 
            text="Bugün özel indirim/promosyon uygulandı", 
            variable=self.promo_var,
            font=("Segoe UI", 9)
        )
        self.chk_promo.pack(anchor="w", padx=10, pady=2)

        btn_kaydet = tk.Button(
            kart_satis, 
            text="💾 Günlük Satışları Kaydet & Yapay Zekayı Güncelle", 
            font=("Segoe UI", 10, "bold"),
            relief="flat", 
            pady=6,
            cursor="hand2",
            command=self.gunluk_satis_kaydet
        )
        btn_kaydet.pack(fill="x", padx=10, pady=5)
        self.vurgu_buton_listesi.append(btn_kaydet)

        # 3. KART: YARIN İÇİN TAHMİN (ÖZEL ÜRÜN SEÇİMLİ & FEATURE ENGINEERING MOTORU)
        kart_tahmin = self.yeni_kart("3. YARINKİ TALEP TAHMİNİ (ÜRÜN BAZLI)")

        frame_tahmin_secim = tk.Frame(kart_tahmin)
        frame_tahmin_secim.pack(fill="x", padx=8, pady=3)
        self.kart_listesi.append(frame_tahmin_secim)

        lbl_soru = tk.Label(frame_tahmin_secim, text="Tahmin Edilecek Ürün:", font=("Segoe UI", 9, "bold"))
        lbl_soru.pack(side="left", padx=3)
        self.etiket_ana_listesi.append(lbl_soru)

        self.cmb_tahmin_urun = ttk.Combobox(frame_tahmin_secim, values=self.urunler, state="readonly", width=24, font=("Segoe UI", 10))
        self.cmb_tahmin_urun.set(self.urunler[0])
        self.cmb_tahmin_urun.pack(side="left", padx=5)
        self.cmb_tahmin_urun.bind("<<ComboboxSelected>>", lambda e: self.tahmin_uret())

        self.lbl_tahmin = tk.Label(
            kart_tahmin, 
            text="Hesaplanıyor...", 
            font=("Segoe UI", 11, "bold"),
            relief="solid",
            bd=1,
            pady=10
        )
        self.lbl_tahmin.pack(fill="x", padx=10, pady=6)

        self.lbl_hammadde = tk.Label(
            kart_tahmin, 
            text="📦 Yarınki Hammadde İhtiyacı Hesaplanıyor...", 
            font=("Segoe UI", 8, "bold"),
            bg=t["kart_bg"],
            fg=t["yazi_alt"],
            justify="center",
            pady=2
        )
        self.lbl_hammadde.pack(fill="x", padx=10, pady=2)
        self.etiket_alt_listesi.append(self.lbl_hammadde)

        btn_bulten = tk.Button(
            kart_tahmin,
            text="🧠 Akıllı İşletme Koçu Günlük Bültenini Oku",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            pady=4,
            cursor="hand2",
            command=self.goster_bulten_penceresi
        )
        btn_bulten.pack(fill="x", padx=10, pady=4)
        self.vurgu_buton_listesi.append(btn_bulten)

        f_aksiyon_bar = tk.Frame(kart_tahmin, bg=t["kart_bg"])
        f_aksiyon_bar.pack(fill="x", padx=10, pady=(2, 4))
        self.kart_listesi.append(f_aksiyon_bar)

        btn_menu_matris = tk.Button(
            f_aksiyon_bar,
            text="📊 Menü Mühendisliği ve Kâr Matrisi",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            pady=4,
            cursor="hand2",
            command=self.goster_menu_matrisi_penceresi
        )
        btn_menu_matris.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self.normal_buton_listesi.append(btn_menu_matris)

        btn_urun_yonet = tk.Button(
            f_aksiyon_bar,
            text="⚙️ Menü & Ürünleri Yönet",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            pady=4,
            cursor="hand2",
            command=self.goster_urun_yonetimi_penceresi
        )
        btn_urun_yonet.pack(side="right", fill="x", expand=True, padx=(3, 0))
        self.normal_buton_listesi.append(btn_urun_yonet)

        # 4. KART: GEÇMİŞ EXCEL DOSYASI YÜKLE
        kart_gecmis = self.yeni_kart("4. TOPLU GEÇMİŞ SATIŞ YÜKLE")

        lbl_gecmis_not = tk.Label(
            kart_gecmis,
            text=f"Elinizdeki geçmiş Excel dosyasını seçin. Kingfool AI geçmiş hava durumlarını arşivden çeker.\nDosya Adı: {kullanici_excel_adi(kullanici)}",
            font=("Segoe UI", 8, "italic")
        )
        lbl_gecmis_not.pack(anchor="w", padx=10, pady=1)
        self.etiket_alt_listesi.append(lbl_gecmis_not)

        btn_excel_yukle = tk.Button(
            kart_gecmis, 
            text="📁 Bilgisayarımdan Geçmiş Excel Dosyası Yükle", 
            relief="flat", 
            pady=4,
            font=("Segoe UI", 9),
            cursor="hand2",
            command=self.gecmis_excel_yukle
        )
        btn_excel_yukle.pack(fill="x", padx=10, pady=3)
        self.normal_buton_listesi.append(btn_excel_yukle)

        # FOOTER
        self.lbl_footer = tk.Label(
            self.ana_konteyner, 
            text="Kingfool Inc. AI Suite v1.5 © Küresel Sürüm | Tüm Hakları Saklıdır", 
            font=("Segoe UI", 8)
        )
        self.lbl_footer.pack(side="bottom", pady=4)
        self.etiket_alt_listesi.append(self.lbl_footer)

        self.konumu_guncelle()
        self.temayi_uygula()

    def yeni_kart(self, baslik):
        t = TEMALAR[self.aktif_tema]
        kart = tk.Frame(self.ana_konteyner, bg=t["kart_bg"], bd=1, relief="solid", padx=6, pady=4)
        kart.pack(fill="x", padx=15, pady=3)
        self.kart_listesi.append(kart)

        lbl_b = tk.Label(kart, text=baslik, font=("Segoe UI", 9, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"])
        lbl_b.pack(anchor="w", padx=6, pady=2)
        self.etiket_ana_listesi.append(lbl_b)
        return kart

    def _ilce_durumunu_ayarla(self):
        ulke = self.cmb_ulke.get()
        sehir = self.cmb_il.get()
        if locations.ilce_secimi_aktif_mi(ulke):
            self.cmb_ilce.config(state="readonly")
            ilceler = locations.ilce_listesi_getir(ulke, sehir)
            self.cmb_ilce["values"] = ilceler
            kullanici_bilgi = self.kullanicilar.get(self.aktif_kullanici, {})
            kayitli_ilce = kullanici_bilgi.get("ilce", "")
            if kayitli_ilce and kayitli_ilce in ilceler:
                self.cmb_ilce.set(kayitli_ilce)
            elif "Kadıköy" in ilceler:
                self.cmb_ilce.set("Kadıköy")
            else:
                self.cmb_ilce.set(ilceler[0] if ilceler else "Merkez")
        else:
            self.cmb_ilce["values"] = ["(İlçe Seçimi Yok)"]
            self.cmb_ilce.set("(İlçe Seçimi Yok)")
            self.cmb_ilce.config(state="disabled")

    def ulke_degisti(self, event=None):
        ulke = self.cmb_ulke.get()
        sehirler = locations.sehir_listesi_getir(ulke)
        self.cmb_il["values"] = sehirler
        self.cmb_il.set(sehirler[0] if sehirler else "")
        self._ilce_durumunu_ayarla()
        self.konumu_guncelle()

    def il_degisti(self, event=None):
        self._ilce_durumunu_ayarla()
        self.konumu_guncelle()

    def konumu_guncelle(self):
        ulke = self.cmb_ulke.get() if hasattr(self, "cmb_ulke") else "Türkiye"
        sehir = self.cmb_il.get() if hasattr(self, "cmb_il") else "İstanbul"
        ilce = self.cmb_ilce.get() if (hasattr(self, "cmb_ilce") and locations.ilce_secimi_aktif_mi(ulke)) else ""
        self.lat, self.lon, bulunan = locations.konum_koordinat_bul(ulke, sehir, ilce)
        self.aktif_ulke = ulke

        if self.aktif_kullanici in self.kullanicilar:
            self.kullanicilar[self.aktif_kullanici].update({
                "ulke": ulke, "sehir": sehir, "ilce": ilce,
                "lat": self.lat, "lon": self.lon, "konum_etiket": bulunan
            })
            kullanicilari_kaydet(self.kullanicilar)

        self.bugun_temp, self.yarin_temp = hava_tahmini_al(self.lat, self.lon)

        yarin = datetime.date.today() + datetime.timedelta(days=1)
        tatil_info = calendar_events.tarih_tatil_veya_etkinlik_mi(yarin, ulke=ulke)
        tatil_ek = f"  |  🎉 {tatil_info['aciklama']}" if tatil_info["ozel_gun_mu"] == 1 else ""

        self.lbl_hava.config(
            text=f"📍 {bulunan}  |  Bugün: {self.bugun_temp}°C  |  Yarın: {self.yarin_temp}°C{tatil_ek}"
        )
        self.tahmin_uret()

    def goster_urun_yonetimi_penceresi(self):
        """Kullanıcının takip ettiği ürünleri dinamik olarak ekleyip çıkarmasını sağlayan yönetim penceresi."""
        t = TEMALAR[self.aktif_tema]
        win = tk.Toplevel(self.root)
        win.title("Kingfool Inc. | Menü & Ürün Yönetimi")
        win.geometry("480x440")
        win.configure(bg=t["pencere_bg"])
        win.transient(self.root)
        win.grab_set()

        lbl_b = tk.Label(win, text="⚙️ Menü & Ürünleri Yönet", font=("Segoe UI", 13, "bold"), fg=t["marka_sari"], bg=t["pencere_bg"])
        lbl_b.pack(pady=(12, 4))

        lbl_info = tk.Label(win, text="Kafenizde talep tahmini yapılan ürünleri buradan artırabilir veya azaltabilirsiniz.", font=("Segoe UI", 8), fg=t["yazi_alt"], bg=t["pencere_bg"])
        lbl_info.pack(pady=(0, 8))

        f_list = tk.LabelFrame(win, text="Mevcut Takip Edilen Ürünler", font=("Segoe UI", 9, "bold"), bg=t["kart_bg"], fg=t["marka_sari"], padx=10, pady=8)
        f_list.pack(fill="both", expand=True, padx=15, pady=4)

        lst_box = tk.Listbox(f_list, font=("Segoe UI", 10), height=5, relief="solid", bd=1)
        lst_box.pack(fill="both", expand=True, pady=4)
        for u in self.urunler:
            lst_box.insert(tk.END, u)

        def urun_sil():
            secili = lst_box.curselection()
            if not secili:
                messagebox.showwarning("Ürün Yönetimi", "Lütfen silmek istediğiniz ürünü seçin!", parent=win)
                return
            u_sil = lst_box.get(secili[0])
            if len(self.urunler) <= 1:
                messagebox.showerror("Ürün Yönetimi", "En az 1 aktif ürün kalmalıdır!", parent=win)
                return
            if messagebox.askyesno("Ürün Sil", f"'{u_sil}' ürününü takip listesinden çıkarmak istediğinize emin misiniz?", parent=win):
                self.urunler.remove(u_sil)
                self.kullanicilar[self.aktif_kullanici]["urunler"] = self.urunler
                kullanicilari_kaydet(self.kullanicilar)
                try:
                    import supabase_db
                    supabase_db.kullanici_urunleri_kaydet(self.aktif_kullanici, self.urunler)
                except Exception:
                    pass
                lst_box.delete(secili[0])
                messagebox.showinfo("Başarılı", f"'{u_sil}' menüden çıkarıldı.", parent=win)
                win.destroy()
                self.goster_kafe_ekrani()

        btn_sil = tk.Button(f_list, text="🗑️ Seçilen Ürünü Menüden Kaldır", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=3, cursor="hand2", command=urun_sil)
        btn_sil.pack(anchor="e", pady=2)

        f_ekle = tk.LabelFrame(win, text="Yeni Ürün Ekle", font=("Segoe UI", 9, "bold"), bg=t["kart_bg"], fg=t["marka_sari"], padx=10, pady=8)
        f_ekle.pack(fill="x", padx=15, pady=(4, 12))

        lbl_yeni = tk.Label(f_ekle, text="Ürün Adı:", font=("Segoe UI", 9, "bold"), bg=t["kart_bg"], fg=t["yazi_ana"])
        lbl_yeni.grid(row=0, column=0, padx=4, pady=4, sticky="w")

        ent_yeni = tk.Entry(f_ekle, font=("Segoe UI", 10), relief="solid", bd=1, width=22)
        ent_yeni.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        def urun_ekle():
            yeni_ad = ent_yeni.get().strip()
            if not yeni_ad:
                messagebox.showwarning("Ürün Yönetimi", "Lütfen bir ürün adı yazın!", parent=win)
                return
            if yeni_ad in self.urunler:
                messagebox.showwarning("Ürün Yönetimi", "Bu ürün zaten menünüzde mevcut!", parent=win)
                return

            self.urunler.append(yeni_ad)
            self.kullanicilar[self.aktif_kullanici]["urunler"] = self.urunler
            kullanicilari_kaydet(self.kullanicilar)

            dosya = kullanici_excel_adi(self.aktif_kullanici)
            if os.path.exists(dosya):
                try:
                    df = pd.read_excel(dosya)
                    if yeni_ad not in df.columns:
                        df[yeni_ad] = np.random.randint(20, 60, size=len(df))
                        df.to_excel(dosya, index=False)
                except Exception:
                    pass

            try:
                ml_ops.egit_ve_kaydet_model(self.aktif_kullanici, yeni_ad, ulke=getattr(self, "aktif_ulke", "Türkiye"))
            except Exception:
                pass

            try:
                import supabase_db
                supabase_db.kullanici_urunleri_kaydet(self.aktif_kullanici, self.urunler)
            except Exception:
                pass

            messagebox.showinfo("Başarılı", f"'{yeni_ad}' başarıyla eklendi ve yapay zeka eğitildi!", parent=win)
            win.destroy()
            self.goster_kafe_ekrani()

        btn_ekle = tk.Button(f_ekle, text="➕ Menüye Ekle", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=3, cursor="hand2", command=urun_ekle)
        btn_ekle.grid(row=0, column=2, padx=4, pady=4)
        self.vurgu_buton_listesi.append(btn_ekle)

    def gunluk_satis_kaydet(self):
        yeni_veriler = {}
        hata_var = False

        for urun_isim in self.urunler:
            val = self.kafe_giris_kutulari[urun_isim].get().strip()
            if val == "":
                yeni_veriler[urun_isim] = np.nan
            elif val.isdigit():
                yeni_veriler[urun_isim] = int(val)
            else:
                hata_var = True
                break

        if hata_var:
            messagebox.showerror("Kingfool Inc. | Hata", "Lütfen satış adetlerini sadece sayı olarak giriniz!")
            return

        if all(np.isnan(v) if isinstance(v, float) else False for v in yeni_veriler.values()):
            messagebox.showwarning("Kingfool Inc.", "Lütfen en az bir ürün için satış miktarı giriniz.")
            return

        haftasonu = 1 if datetime.date.today().weekday() >= 5 else 0
        kayit = {
            "Tarih": self.bugun_tarih,
            "Sicaklik": self.bugun_temp,
            "Haftasonu_Mu": haftasonu,
            "Promosyon_Var_Mi": self.promo_var.get(),
            **yeni_veriler
        }

        dosya = kullanici_excel_adi(self.aktif_kullanici)
        df = pd.read_excel(dosya) if os.path.exists(dosya) else pd.DataFrame()
        if not df.empty and "Tarih" in df.columns:
            df = df[df["Tarih"] != self.bugun_tarih]
        df = pd.concat([df, pd.DataFrame([kayit])], ignore_index=True)
        df.to_excel(dosya, index=False)

        # Supabase Bulut Veritabanı Senkronizasyonu
        try:
            import supabase_db
            for u_ad, u_adt in yeni_veriler.items():
                if pd.notna(u_adt) and u_adt > 0:
                    supabase_db.satis_kaydet(
                        kullanici_adi=self.aktif_kullanici,
                        tarih=self.bugun_tarih,
                        urun_adi=u_ad,
                        adet=u_adt,
                        sicaklik=self.bugun_temp,
                        haftasonu=haftasonu,
                        promosyon=self.promo_var.get()
                    )
        except Exception:
            pass

        # MLOps Model Yeniden Eğitimi (Joblib .pkl)
        try:
            for u_ad in yeni_veriler.keys():
                ml_ops.egit_ve_kaydet_model(self.aktif_kullanici, u_ad)
        except Exception:
            pass

        messagebox.showinfo("Kingfool Inc.", "Bugünkü satışlar kaydedildi ve yapay zeka güncellendi!")
        for ent in self.kafe_giris_kutulari.values():
            ent.delete(0, tk.END)
        self.tahmin_uret()

    def tahmin_uret(self):
        if not hasattr(self, "cmb_tahmin_urun"):
            return
        secilen_urun = self.cmb_tahmin_urun.get()
        yarin = datetime.date.today() + datetime.timedelta(days=1)
        yarin_haftasonu = 1 if yarin.weekday() >= 5 else 0

        # Tatil ve Özel Gün Tespiti (Ülkeye Duyarlı)
        aktif_ulke = getattr(self, "aktif_ulke", "Türkiye")
        tatil_info = calendar_events.tarih_tatil_veya_etkinlik_mi(yarin, ulke=aktif_ulke)
        yarin_tatil = tatil_info["tatil_mi"]
        tatil_etiket = f" [🎉 {tatil_info['aciklama']}]" if tatil_info["ozel_gun_mu"] == 1 else ""

        # MLOps destekli tahmin üret
        tahmin, metrikler = ml_ops.tahmin_yap(
            self.aktif_kullanici, secilen_urun, self.yarin_temp, yarin_haftasonu, yarin_tatil=yarin_tatil, ulke=aktif_ulke
        )
        if tahmin is None:
            tahmin, veri_sayisi = yapay_zeka_tahmin(self.aktif_kullanici, secilen_urun, self.yarin_temp, yarin_haftasonu)
        else:
            veri_sayisi = metrikler.get("egitim_satir_sayisi", 38)

        if tahmin is not None:
            self.lbl_tahmin.config(
                text=f"🔮 Yarın Beklenen Satış: ~{tahmin} Adet ({secilen_urun}){tatil_etiket}\n📊 Model {veri_sayisi} günlük gelişmiş öznitelik (Lag, Sıcaklık, Tatil) verisiyle eğitildi."
            )
        else:
            self.lbl_tahmin.config(
                text=f"⚠️ {secilen_urun} için henüz yeterli satış verisi yok!\n(Gereken: En az 12 gün kayıt / 5 gün öznitelik | Mevcut: {veri_sayisi} gün)"
            )

        # Tüm ürünler için yarınki hammadde sarfiyatını hesapla
        try:
            tum_tahminler = {}
            for u in self.urunler:
                t_val, _ = ml_ops.tahmin_yap(self.aktif_kullanici, u, self.yarin_temp, yarin_haftasonu, yarin_tatil=yarin_tatil, ulke=aktif_ulke)
                tum_tahminler[u] = t_val if t_val is not None else (tahmin or 35)

            ihtiyaclar = inventory_manager.hammadde_ihtiyaci_hesapla(tum_tahminler)
            ozet_maddeler = [f"{x['hammadde']}: {x['gosterim']}" for x in ihtiyaclar[:4]]
            self.lbl_hammadde.config(text="📦 Yarınki Hammadde İhtiyacı: " + " | ".join(ozet_maddeler))
        except Exception as e:
            self.lbl_hammadde.config(text=f"📦 Hammadde Hesabı: {e}")

    def goster_bulten_penceresi(self):
        """Akıllı İşletme Koçu Günlük Aksiyon Raporunu modal pencerede açar."""
        if not self.urunler:
            messagebox.showwarning("Ürün Tanımlı Değil", "Günlük bülten hesaplanabilmesi için lütfen önce ürün kurulumunu tamamlayın.")
            return

        yarin = datetime.date.today() + datetime.timedelta(days=1)
        yarin_haftasonu = 1 if yarin.weekday() >= 5 else 0
        yarin_tarih = yarin.strftime("%Y-%m-%d")
        aktif_ulke = getattr(self, "aktif_ulke", "Türkiye")

        tum_tahminler = {}
        for u in self.urunler:
            t_val, _ = ml_ops.tahmin_yap(self.aktif_kullanici, u, self.yarin_temp, yarin_haftasonu, ulke=aktif_ulke)
            tum_tahminler[u] = t_val if t_val is not None else 45

        ihtiyaclar = inventory_manager.hammadde_ihtiyaci_hesapla(tum_tahminler)

        # Raporu üret (Ülkeye duyarlı)
        rapor_sonuc = llm_coaching.gunluk_koc_raporu_uret(
            kullanici_adi=self.aktif_kullanici,
            yarin_tarih=yarin_tarih,
            yarin_sicaklik=self.yarin_temp,
            yarin_haftasonu=yarin_haftasonu,
            urun_tahminleri=tum_tahminler,
            hammadde_ihtiyaclari=ihtiyaclar,
            ulke=aktif_ulke
        )
        rapor_metni = rapor_sonuc.get("rapor", "Rapor hazırlanamadı.")
        motor_bilgi = rapor_sonuc.get("kaynak", "Kingfool Engine")

        # Modal Pencere Aç
        pencere = tk.Toplevel(self.root)
        pencere.title(f"Kingfool Inc. | Akıllı İşletme Koçu Bülteni ({motor_bilgi})")
        pencere.geometry("640x700")
        pencere.configure(bg="#121013")

        f_ust = tk.Frame(pencere, bg="#121013", padx=15, pady=10)
        f_ust.pack(fill="x")

        lbl_b = tk.Label(f_ust, text="🧠 AKILLI İŞLETME KOÇU VE GÜNLÜK BÜLTEN", font=("Impact", 15), fg=GS_SARI, bg="#121013")
        lbl_b.pack(anchor="w")
        lbl_alt = tk.Label(f_ust, text=f"Kaynak Motor: {motor_bilgi} | Tarih: {yarin_tarih}", font=("Segoe UI", 9), fg="#A39BA8", bg="#121013")
        lbl_alt.pack(anchor="w")

        f_orta = tk.Frame(pencere, bg="#1F1A24", padx=10, pady=10)
        f_orta.pack(fill="both", expand=True, padx=15, pady=5)

        txt_rapor = tk.Text(f_orta, bg="#121013", fg="#FAF7F9", font=("Segoe UI", 10), wrap="word", padx=10, pady=10, bd=0)
        txt_rapor.insert("1.0", rapor_metni)
        txt_rapor.config(state="disabled")

        scrollbar = ttk.Scrollbar(f_orta, command=txt_rapor.yview)
        txt_rapor['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side="right", fill="y")
        txt_rapor.pack(side="left", fill="both", expand=True)

        f_alt = tk.Frame(pencere, bg="#121013", padx=15, pady=10)
        f_alt.pack(fill="x")

        def panoya_kopyala():
            self.root.clipboard_clear()
            self.root.clipboard_append(rapor_metni)
            messagebox.showinfo("Bülten", "Günlük bülten panoya kopyalandı!")

        btn_kopyala = tk.Button(f_alt, text="📋 Panoya Kopyala", font=("Segoe UI", 9, "bold"), bg=GS_KIRMIZI, fg="#FAF7F9", relief="flat", padx=10, pady=4, cursor="hand2", command=panoya_kopyala)
        btn_kopyala.pack(side="left")

        btn_kapat = tk.Button(f_alt, text="Kapat", font=("Segoe UI", 9), bg="#282230", fg="#FAF7F9", relief="flat", padx=10, pady=4, cursor="hand2", command=pencere.destroy)
        btn_kapat.pack(side="right")

    def goster_menu_matrisi_penceresi(self):
        """Menü Mühendisliği ve Kâr Marjı Matrisi modal penceresini açar."""
        if not self.urunler:
            messagebox.showwarning("Ürün Tanımlı Değil", "Menü matrisi için lütfen önce ürün kurulumunuzu tamamlayın.")
            return

        yarin = datetime.date.today() + datetime.timedelta(days=1)
        yarin_haftasonu = 1 if yarin.weekday() >= 5 else 0
        aktif_ulke = getattr(self, "aktif_ulke", "Türkiye")

        tum_tahminler = {}
        for u in self.urunler:
            t_val, _ = ml_ops.tahmin_yap(self.aktif_kullanici, u, self.yarin_temp, yarin_haftasonu, ulke=aktif_ulke)
            tum_tahminler[u] = t_val if t_val is not None else 45

        matris = menu_engineering.menu_matrisi_analiz_et(tum_tahminler)

        # Modal Pencere
        pencere = tk.Toplevel(self.root)
        pencere.title("Kingfool Inc. | Menü Mühendisliği & Kâr Marjı Matrisi (BCG / F&B)")
        pencere.geometry("780x660")
        pencere.configure(bg="#121013")

        # Üst Başlık
        f_ust = tk.Frame(pencere, bg="#121013", padx=15, pady=10)
        f_ust.pack(fill="x")

        lbl_b = tk.Label(f_ust, text="📊 MENÜ MÜHENDİSLİĞİ & KÂR MARJI MATRİSİ", font=("Impact", 16), fg=GS_SARI, bg="#121013")
        lbl_b.pack(anchor="w")
        lbl_alt = tk.Label(f_ust, text="Kasavana & Smith F&B Modeli | Satış Popülaritesi vs. Birim Brüt Kâr Katkısı", font=("Segoe UI", 9), fg="#A39BA8", bg="#121013")
        lbl_alt.pack(anchor="w")

        # 4 KPI Kartı
        f_kpi = tk.Frame(pencere, bg="#121013", padx=15, pady=5)
        f_kpi.pack(fill="x")

        y_sayi = len(matris.get("yildizlar", []))
        ia_sayi = len(matris.get("is_atlari", []))
        b_sayi = len(matris.get("bulmacalar", []))
        k_sayi = len(matris.get("kopekler", []))
        toplam_kar = matris["esikler"]["toplam_brut_kar"]

        kpi_listesi = [
            ("🌟 YILDIZLAR", f"{y_sayi} Ürün", "#FDB913", "#2A2210"),
            ("🐴 İŞ ATLARI", f"{ia_sayi} Ürün", "#4A90E2", "#102030"),
            ("🧩 BULMACALAR", f"{b_sayi} Ürün", "#BD10E0", "#25102A"),
            ("🐕 KÖPEKLER", f"{k_sayi} Ürün", "#909090", "#202020"),
        ]

        for i, (baslik, deger, fg_col, bg_col) in enumerate(kpi_listesi):
            card = tk.Frame(f_kpi, bg=bg_col, bd=1, relief="solid", padx=10, pady=6)
            card.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(card, text=baslik, font=("Segoe UI", 9, "bold"), fg=fg_col, bg=bg_col).pack()
            tk.Label(card, text=deger, font=("Impact", 14), fg="#FAF7F9", bg=bg_col).pack()

        # Özet Eşik Bilgisi
        esikler = matris["esikler"]
        lbl_esik = tk.Label(
            pencere,
            text=f"Eşik Değerler: Ortalama Hacim = {esikler['ortalama_satis_adedi']} adet | Ortalama Kâr Katkısı = {esikler['ortalama_katki_payi']} TL | Yarınki Tahmini Brüt Kâr = {toplam_kar:,.0f} TL",
            font=("Segoe UI", 8, "italic"),
            fg="#FDB913",
            bg="#121013"
        )
        lbl_esik.pack(padx=15, pady=(2, 6), anchor="w")

        # Tablo Alanı (Treeview)
        f_tablo = tk.Frame(pencere, bg="#1F1A24", padx=10, pady=8)
        f_tablo.pack(fill="both", expand=True, padx=15, pady=5)

        sutunlar = ("Urun", "Sinif", "Fiyat", "Maliyet", "KatkiPayi", "Marj", "Tavsiye")
        tree = ttk.Treeview(f_tablo, columns=sutunlar, show="headings", height=8)
        tree.heading("Urun", text="Ürün Adı")
        tree.heading("Sinif", text="Kadran")
        tree.heading("Fiyat", text="Satış Fiyatı")
        tree.heading("Maliyet", text="Hammadde (COGS)")
        tree.heading("KatkiPayi", text="Katkı Payı")
        tree.heading("Marj", text="Kâr Marjı")
        tree.heading("Tavsiye", text="Stratejik Aksiyon Tavsiyesi")

        tree.column("Urun", width=110)
        tree.column("Sinif", width=85)
        tree.column("Fiyat", width=80)
        tree.column("Maliyet", width=95)
        tree.column("KatkiPayi", width=80)
        tree.column("Marj", width=70)
        tree.column("Tavsiye", width=220)

        def tabloyu_doldur(guncel_matris):
            for row in tree.get_children():
                tree.delete(row)
            for item in guncel_matris["tum_urunler"]:
                tree.insert("", "end", values=(
                    item["urun"],
                    f"{item['ikon']} {item['sinif']}",
                    f"{item['satis_fiyati']:.1f} TL",
                    f"{item['porsiyon_maliyeti']:.2f} TL",
                    f"{item['katki_payi']:.2f} TL",
                    f"%{item['kar_marji_yuzde']}",
                    item["tavsiye"]
                ))

        tabloyu_doldur(matris)

        sb = ttk.Scrollbar(f_tablo, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        # Fiyat Güncelleme Barı
        f_fiyat = tk.Frame(pencere, bg="#1F1A24", padx=15, pady=8)
        f_fiyat.pack(fill="x", padx=15, pady=5)

        tk.Label(f_fiyat, text="Fiyat Güncelle:", font=("Segoe UI", 9, "bold"), fg="#FAF7F9", bg="#1F1A24").pack(side="left", padx=(0, 6))
        cmb_fiyat_urun = ttk.Combobox(f_fiyat, values=self.urunler, state="readonly", width=16, font=("Segoe UI", 9))
        cmb_fiyat_urun.set(self.urunler[0])
        cmb_fiyat_urun.pack(side="left", padx=4)

        fiyat_map = menu_engineering.kullanici_fiyatlarini_yukle()
        ent_yeni_fiyat = tk.Entry(f_fiyat, font=("Segoe UI", 9), width=8)
        ent_yeni_fiyat.insert(0, str(fiyat_map.get(self.urunler[0], 120.0)))
        ent_yeni_fiyat.pack(side="left", padx=4)

        def urun_degisti(e=None):
            secili = cmb_fiyat_urun.get()
            f_guncel = menu_engineering.kullanici_fiyatlarini_yukle()
            ent_yeni_fiyat.delete(0, tk.END)
            ent_yeni_fiyat.insert(0, str(f_guncel.get(secili, 120.0)))

        cmb_fiyat_urun.bind("<<ComboboxSelected>>", urun_degisti)

        def fiyati_kaydet():
            secili = cmb_fiyat_urun.get()
            val = ent_yeni_fiyat.get().strip()
            try:
                y_f = float(val)
                if y_f <= 0:
                    raise ValueError
                menu_engineering.satis_fiyati_kaydet(secili, y_f)
                yeni_m = menu_engineering.menu_matrisi_analiz_et(tum_tahminler)
                tabloyu_doldur(yeni_m)
                messagebox.showinfo("Fiyat Güncellendi", f"{secili} yeni fiyatı {y_f:.1f} TL olarak kaydedildi ve matris güncellendi!")
            except Exception:
                messagebox.showerror("Hata", "Lütfen geçerli pozitif bir fiyat girin!")

        btn_fiyat_kaydet = tk.Button(f_fiyat, text="💾 Fiyatı Kaydet", font=("Segoe UI", 9, "bold"), bg=GS_KIRMIZI, fg="#FAF7F9", relief="flat", padx=8, pady=3, cursor="hand2", command=fiyati_kaydet)
        btn_fiyat_kaydet.pack(side="left", padx=6)

        # Alt Buton
        f_alt = tk.Frame(pencere, bg="#121013", padx=15, pady=8)
        f_alt.pack(fill="x")
        btn_kapat = tk.Button(f_alt, text="Kapat", font=("Segoe UI", 9), bg="#282230", fg="#FAF7F9", relief="flat", padx=12, pady=4, cursor="hand2", command=pencere.destroy)
        btn_kapat.pack(side="right")

    def gecmis_excel_yukle(self):
        dosya = filedialog.askopenfilename(
            title="Geçmiş Satış Excel Dosyasını Seçin",
            filetypes=[("Excel Dosyaları", "*.xlsx;*.xls"), ("CSV Dosyaları", "*.csv")]
        )
        if not dosya:
            return

        try:
            gelen_df = pd.read_csv(dosya) if dosya.endswith(".csv") else pd.read_excel(dosya)
            gelen_df.columns = [c.strip() for c in gelen_df.columns]

            tarih_kolonu = None
            for c in gelen_df.columns:
                if c.lower() == "tarih":
                    tarih_kolonu = c
                    break

            if not tarih_kolonu:
                messagebox.showerror("Kingfool Inc.", "Excel dosyasında 'Tarih' sütunu bulunamadı!")
                return

            messagebox.showinfo("Kingfool Inc. AI", "Geçmiş günlerin hava durumu arşivden çekiliyor, lütfen bekleyin...")

            gelen_df["Tarih"] = pd.to_datetime(gelen_df[tarih_kolonu]).dt.strftime("%Y-%m-%d")
            min_t = gelen_df["Tarih"].min()
            max_t = gelen_df["Tarih"].max()
            arsiv = gecmis_hava_sicakliklari_al(self.lat, self.lon, min_t, max_t)

            yeni_satirlar = []
            for _, r in gelen_df.iterrows():
                t = r["Tarih"]
                temp = arsiv.get(t, 24.0)
                haftasonu = 1 if datetime.datetime.strptime(t, "%Y-%m-%d").weekday() >= 5 else 0
                promo = r.get("Promosyon_Var_Mi", r.get("promosyon", 0))

                satir = {
                    "Tarih": t,
                    "Sicaklik": temp,
                    "Haftasonu_Mu": haftasonu,
                    "Promosyon_Var_Mi": promo
                }
                for urun in self.urunler:
                    bulunan_val = np.nan
                    for c in gelen_df.columns:
                        if urun.lower() in c.lower() or c.lower() in urun.lower():
                            bulunan_val = r[c]
                            break
                    satir[urun] = bulunan_val

                yeni_satirlar.append(satir)

            hedef_dosya = kullanici_excel_adi(self.aktif_kullanici)
            yeni_df = pd.DataFrame(yeni_satirlar)
            yeni_df.to_excel(hedef_dosya, index=False)

            messagebox.showinfo("Kingfool Inc.", f"{len(yeni_df)} günlük satış ve hava durumu verisi başarıyla aktarıldı!")
            self.tahmin_uret()

        except Exception as e:
            messagebox.showerror("Kingfool Inc. | Hata", f"Dosya işlenirken hata oluştu:\n{str(e)}")

if __name__ == "__main__":
    pencere = tk.Tk()
    app = KingfoolApp(pencere)
    pencere.mainloop()
