# -*- coding: utf-8 -*-
"""
Kingfool Inc. | v1.5 Uluslararası Çoklu Ülke, Gerçek Kafe Verileri ve Dinamik Menü Test Paketi
"""
import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import locations
import calendar_events
import inventory_manager
import menu_engineering
import ml_ops
import llm_coaching
from api.main import (
    app, get_countries, get_cities, get_districts, geocode_location,
    login, get_products, get_daily_coaching_report, LoginRequest
)

class TestKingfoolV15MultiCountry(unittest.TestCase):

    def test_locations_rules(self):
        """Türkiye için ilçe seçimi aktif, diğer tüm ülkelerde kapalı olmalıdır."""
        self.assertTrue(locations.ilce_secimi_aktif_mi("Türkiye"))
        self.assertTrue(locations.ilce_secimi_aktif_mi("turkey"))
        self.assertFalse(locations.ilce_secimi_aktif_mi("Amerika Birleşik Devletleri"))
        self.assertFalse(locations.ilce_secimi_aktif_mi("Birleşik Krallık"))
        self.assertFalse(locations.ilce_secimi_aktif_mi("Almanya"))
        self.assertFalse(locations.ilce_secimi_aktif_mi("Fransa"))
        self.assertFalse(locations.ilce_secimi_aktif_mi("Japonya"))

        # İlçe listesi testi
        tr_districts = locations.ilce_listesi_getir("Türkiye", "İstanbul")
        self.assertGreater(len(tr_districts), 20)
        self.assertTrue(any("kad" in d.lower() for d in tr_districts))

        us_districts = locations.ilce_listesi_getir("Amerika Birleşik Devletleri", "New York")
        self.assertEqual(us_districts, [])

        # Şehir listesi testi
        us_cities = locations.sehir_listesi_getir("Amerika Birleşik Devletleri")
        self.assertIn("New York", us_cities)
        self.assertIn("Los Angeles", us_cities)

        # Koordinat bulma
        lat, lon, label = locations.konum_koordinat_bul("Amerika Birleşik Devletleri", "New York")
        self.assertEqual(round(lat, 2), 40.71)
        self.assertEqual(round(lon, 2), -74.01)

    def test_calendar_events_international(self):
        """Farklı ülkelerin resmi tatil ve bayramlarını doğru çeker."""
        # ABD: New Year's Day (2023-01-01)
        us_holiday = calendar_events.tarih_tatil_veya_etkinlik_mi("2023-01-01", ulke="Amerika Birleşik Devletleri")
        self.assertEqual(us_holiday["tatil_mi"], 1)
        self.assertIn("New Year", us_holiday["aciklama"])

        # Birleşik Krallık: New Year's Day (observed) (2017-01-02)
        uk_holiday = calendar_events.tarih_tatil_veya_etkinlik_mi("2017-01-02", ulke="Birleşik Krallık")
        self.assertEqual(uk_holiday["tatil_mi"], 1)
        self.assertIn("New Year", uk_holiday["aciklama"])

        # Türkiye: Cumhuriyet Bayramı (2026-10-29)
        tr_holiday = calendar_events.tarih_tatil_veya_etkinlik_mi("2026-10-29", ulke="Türkiye")
        self.assertEqual(tr_holiday["tatil_mi"], 1)
        self.assertIn("Cumhuriyet", tr_holiday["aciklama"])

        # Normal gün
        norm = calendar_events.tarih_tatil_veya_etkinlik_mi("2026-11-04", ulke="Türkiye")
        self.assertEqual(norm["tatil_mi"], 0)

    def test_inventory_and_recipes(self):
        """Maven Roasters ve Bread Basket ürünlerinin reçeteleri ve dinamik hesaplama."""
        recete_espresso = inventory_manager.urun_recetesi_getir("Barista Espresso")
        self.assertGreaterEqual(len(recete_espresso), 2)
        self.assertTrue(any(x["hammadde"] == "Kahve Çekirdeği" for x in recete_espresso))

        recete_bread = inventory_manager.urun_recetesi_getir("Bread")
        self.assertTrue(any("Ekmek" in x["hammadde"] for x in recete_bread))

        # Dinamik ürün reçete fallback'i
        recete_pasta = inventory_manager.urun_recetesi_getir("Çikolatalı Pasta")
        self.assertTrue(any("Porsiyon" in x["hammadde"] for x in recete_pasta))

        # Hammadde sarfiyat hesabı
        ihtiyaclar = inventory_manager.hammadde_ihtiyaci_hesapla({
            "Barista Espresso": 100,
            "Bread": 50
        })
        self.assertGreaterEqual(len(ihtiyaclar), 2)

    def test_real_cafes_models_and_inferences(self):
        """Maven Roasters ve Bread Basket modellerinin çıkarım yapabilmesi."""
        # Maven Roasters - Barista Espresso
        pred_nyc, met_nyc = ml_ops.tahmin_yap(
            kullanici_adi="mavenroasters",
            urun_adi="Barista Espresso",
            yarin_sicaklik=22.0,
            yarin_haftasonu=1,
            ulke="Amerika Birleşik Devletleri"
        )
        self.assertIsNotNone(pred_nyc)
        self.assertGreater(pred_nyc, 0)
        self.assertGreater(met_nyc["r2_score"], 0.70)

        # Bread Basket - Coffee
        pred_uk, met_uk = ml_ops.tahmin_yap(
            kullanici_adi="breadbasket",
            urun_adi="Coffee",
            yarin_sicaklik=12.0,
            yarin_haftasonu=0,
            ulke="Birleşik Krallık"
        )
        self.assertIsNotNone(pred_uk)
        self.assertGreater(pred_uk, 0)

    def test_api_locations_and_auth(self):
        """FastAPI konum ve oturum açma fonksiyonları."""
        # 1. Countries
        res_c = get_countries()
        self.assertTrue(res_c["success"])
        self.assertGreaterEqual(len(res_c["countries"]), 10)
        tr = next(c for c in res_c["countries"] if c["code"] == "TR")
        self.assertTrue(tr["has_districts"])
        us = next(c for c in res_c["countries"] if c["code"] == "US")
        self.assertFalse(us["has_districts"])

        # 2. Cities
        res_cities = get_cities(country="Birleşik Krallık")
        self.assertTrue(res_cities["success"])
        self.assertIn("Edinburgh", res_cities["cities"])

        # 3. Districts (Only for TR)
        res_d_tr = get_districts(country="Türkiye", city="İzmir")
        self.assertTrue(res_d_tr["districts_enabled"])
        self.assertIn("Konak", res_d_tr["districts"])

        res_d_us = get_districts(country="Amerika Birleşik Devletleri", city="New York")
        self.assertFalse(res_d_us["districts_enabled"])
        self.assertEqual(res_d_us["districts"], [])

        # 4. Login Maven Roasters
        res_login = login(LoginRequest(username="mavenroasters", password="MavenNYC2023!"))
        self.assertTrue(res_login["success"])
        self.assertEqual(res_login["username"], "mavenroasters")
        self.assertEqual(res_login["country"], "Amerika Birleşik Devletleri")
        self.assertEqual(res_login["city"], "New York")
        self.assertEqual(len(res_login["products"]), 6)

        # 5. Login Bread Basket
        res_login_bb = login(LoginRequest(username="breadbasket", password="Bread2017!"))
        self.assertTrue(res_login_bb["success"])
        self.assertEqual(res_login_bb["country"], "Birleşik Krallık")
        self.assertEqual(len(res_login_bb["products"]), 7)

    def test_api_daily_coaching_report(self):
        """Uluslararası kafe için Günlük Koçluk Bülteni üretimi."""
        data = get_daily_coaching_report(username="mavenroasters")
        self.assertTrue(data["success"])
        self.assertEqual(data["country"], "Amerika Birleşik Devletleri")
        self.assertIn("Barista Espresso", data["predictions"])
        self.assertGreater(len(data["inventory"]), 0)
        self.assertIn("Akıllı İşletme Koçu Günlük Bülteni", data["report_markdown"])

if __name__ == "__main__":
    unittest.main()
