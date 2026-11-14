# -*- coding: utf-8 -*-
"""
Kingfool Inc. v1.4 Comprehensive Test Suite
Tests:
1. calendar_events (official holidays, religious feasts, custom events, normal days)
2. menu_engineering (COGS portion costs, 4-quadrant matrix, price updating)
3. inventory_manager (recipes, calculation, units, alerts)
4. ml_ops (training with Tatil_Mi, inference with holiday parameter, metrics)
5. llm_coaching (bulletin generation, holiday alerts, puzzle upselling)
6. supabase_db (credentials, connection, user data)
7. api.main endpoints (calendar, menu engineering, predictions, coaching, inventory)
"""
import sys
import os
import unittest
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import calendar_events
import menu_engineering
import inventory_manager
import ml_ops
import llm_coaching
import supabase_db
from api.main import (
    root, health_check, login, get_products, get_weather,
    predict_sales, get_recipes, get_inventory_requirements,
    get_daily_coaching_report, get_ml_status, retrain_models,
    get_holidays, check_calendar_date, add_custom_event,
    get_menu_matrix, get_product_cost, update_product_price,
    LoginRequest, CustomEventRequest, PriceUpdateRequest
)

class TestKingfoolV14(unittest.TestCase):

    # ---------------------------------------------------------
    # 1. CALENDAR & HOLIDAYS TESTS
    # ---------------------------------------------------------
    def test_fixed_holiday_detection(self):
        info_cumhuriyet = calendar_events.tarih_tatil_veya_etkinlik_mi("2026-10-29")
        self.assertEqual(info_cumhuriyet["tatil_mi"], 1)
        self.assertIn("Cumhuriyet", info_cumhuriyet["aciklama"])
        self.assertEqual(info_cumhuriyet["kategori"], "Resmi Tatil")

    def test_religious_holiday_detection(self):
        info_bayram = calendar_events.tarih_tatil_veya_etkinlik_mi("2026-03-20")
        self.assertEqual(info_bayram["tatil_mi"], 1)
        self.assertIn("Ramazan Bayramı", info_bayram["aciklama"])
        self.assertEqual(info_bayram["kategori"], "Dini Bayram")

    def test_normal_day_detection(self):
        info_normal = calendar_events.tarih_tatil_veya_etkinlik_mi("2026-10-20")
        self.assertEqual(info_normal["tatil_mi"], 0)
        self.assertEqual(info_normal["ozel_gun_mu"], 0)

    def test_custom_event_addition(self):
        date_str = "2026-11-20"
        ok = calendar_events.ozel_etkinlik_kaydet(date_str, "Kafe Akustik Konser Gecesi")
        self.assertTrue(ok)
        info_custom = calendar_events.tarih_tatil_veya_etkinlik_mi(date_str)
        self.assertEqual(info_custom["ozel_gun_mu"], 1)
        self.assertIn("Akustik Konser", info_custom["aciklama"])

    def test_annual_holiday_list(self):
        holidays = calendar_events.yillik_tatil_listesi(2026)
        self.assertGreater(len(holidays), 10)
        self.assertTrue(any("Cumhuriyet" in h["ad"] for h in holidays))

    # ---------------------------------------------------------
    # 2. MENU ENGINEERING & PROFIT MARGIN TESTS
    # ---------------------------------------------------------
    def test_portion_cost_cogs(self):
        cogs_coldbrew = menu_engineering.porsiyon_maliyeti_hesapla("Cold Brew")
        self.assertGreater(cogs_coldbrew["porsiyon_maliyeti"], 20.0)
        self.assertTrue(len(cogs_coldbrew["kalemler"]) >= 3)

        cogs_latte = menu_engineering.porsiyon_maliyeti_hesapla("Iced Latte")
        self.assertGreater(cogs_latte["porsiyon_maliyeti"], 15.0)

    def test_menu_matrix_classification(self):
        tahminler = {
            "Cold Brew": 90,
            "Iced Latte": 130,
            "Brownie": 30,
            "Iced Americano": 60
        }
        matrix = menu_engineering.menu_matrisi_analiz_et(tahminler)
        self.assertIn("yildizlar", matrix)
        self.assertIn("is_atlari", matrix)
        self.assertIn("bulmacalar", matrix)
        self.assertIn("kopekler", matrix)
        self.assertEqual(len(matrix["tum_urunler"]), 4)

        # Total gross profit must be positive
        self.assertGreater(matrix["esikler"]["toplam_brut_kar"], 1000)

    def test_price_updating(self):
        ok = menu_engineering.satis_fiyati_kaydet("Cold Brew", 130.0)
        self.assertTrue(ok)
        fiyatlar = menu_engineering.kullanici_fiyatlarini_yukle()
        self.assertEqual(fiyatlar["Cold Brew"], 130.0)

    # ---------------------------------------------------------
    # 3. INVENTORY MANAGER TESTS
    # ---------------------------------------------------------
    def test_inventory_calculation(self):
        tahminler = {"Cold Brew": 50, "Iced Latte": 100}
        reqs = inventory_manager.hammadde_ihtiyaci_hesapla(tahminler)
        self.assertIsInstance(reqs, list)
        self.assertGreater(len(reqs), 0)

        kahve = next((x for x in reqs if x["hammadde"] == "Kahve Çekirdeği"), None)
        self.assertIsNotNone(kahve)
        self.assertEqual(kahve["gosterim"], "4.50 kg")

    # ---------------------------------------------------------
    # 4. MLOPS PIPELINE WITH TATIL_MI FEATURE
    # ---------------------------------------------------------
    def test_mlops_training_and_inference(self):
        model, metrikler = ml_ops.egit_ve_kaydet_model("admin", "Cold Brew")
        self.assertIsNotNone(model)
        self.assertIn("Tatil_Mi", ml_ops.FEATURE_COLS)
        self.assertGreater(metrikler["r2_score"], 0.5)

        # Inference on a holiday
        tahmin_tatil, _ = ml_ops.tahmin_yap("admin", "Cold Brew", 28.0, 1, yarin_promosyon=0, yarin_tatil=1)
        self.assertIsNotNone(tahmin_tatil)
        self.assertGreater(tahmin_tatil, 0)

    # ---------------------------------------------------------
    # 5. LLM COACHING WITH HOLIDAY & MENU ENGINEERING
    # ---------------------------------------------------------
    def test_llm_coaching_report_features(self):
        tahminler = {"Cold Brew": 50, "Iced Latte": 90, "Brownie": 25}
        reqs = inventory_manager.hammadde_ihtiyaci_hesapla(tahminler)
        res = llm_coaching.gunluk_koc_raporu_uret(
            kullanici_adi="admin",
            yarin_tarih="2026-10-29",  # Cumhuriyet Bayramı
            yarin_sicaklik=27.0,
            yarin_haftasonu=1,
            urun_tahminleri=tahminler,
            hammadde_ihtiyaclari=reqs,
            gemini_api_key=None
        )
        self.assertTrue(res["success"])
        self.assertIn("Cumhuriyet Bayramı", res["rapor"])
        self.assertIn("Menü Mühendisliği", res["rapor"])
        self.assertIn("tatil_bilgisi", res)
        self.assertIn("menu_matrisi", res)

    # ---------------------------------------------------------
    # 6. SUPABASE CONNECTION & USERS
    # ---------------------------------------------------------
    def test_supabase_connection(self):
        ok, msg = supabase_db.baglanti_kontrol()
        self.assertIsInstance(ok, bool)
        self.assertIsInstance(msg, str)
        users = supabase_db.kullanicilari_yukle()
        if ok:
            self.assertIn("admin", users)

    # ---------------------------------------------------------
    # 7. FASTAPI API ENDPOINTS
    # ---------------------------------------------------------
    def test_api_root_and_health(self):
        self.assertIn(root()["version"], ["1.4.0", "1.5.0"])
        self.assertIn("database_connected", health_check())

    def test_api_predict_with_holiday(self):
        res = predict_sales("admin", "Cold Brew", 27.0, 1, 0, 1)
        self.assertTrue(res["success"])
        self.assertIn("holiday_info", res)
        self.assertEqual(res["tomorrow_is_holiday"], 1)

    def test_api_calendar_endpoints(self):
        res_hols = get_holidays(2026)
        self.assertTrue(res_hols["success"])
        self.assertGreater(len(res_hols["holidays"]), 5)

        res_check = check_calendar_date("2026-10-29")
        self.assertTrue(res_check["success"])
        self.assertEqual(res_check["info"]["tatil_mi"], 1)

        res_add_evt = add_custom_event(CustomEventRequest(date="2026-12-05", event_name="Derbi Maçı"))
        self.assertTrue(res_add_evt["success"])

    def test_api_menu_engineering_endpoints(self):
        res_matrix = get_menu_matrix("admin", 27.0, 1)
        self.assertTrue(res_matrix["success"])
        self.assertIn("matrix", res_matrix)
        self.assertIn("tum_urunler", res_matrix["matrix"])

        res_cost = get_product_cost("Cold Brew")
        self.assertTrue(res_cost["success"])
        self.assertGreater(res_cost["portion_cost"], 20.0)
        self.assertGreater(res_cost["profit_margin_percent"], 50.0)

        res_price = update_product_price(PriceUpdateRequest(product="Cold Brew", price=135.0))
        self.assertTrue(res_price["success"])
        self.assertEqual(res_price["new_price"], 135.0)

    def test_api_daily_coaching_report(self):
        res = get_daily_coaching_report("admin")
        self.assertTrue(res["success"])
        self.assertIn("holiday_info", res)
        self.assertIn("menu_matrix", res)
        self.assertIn("report_markdown", res)

if __name__ == "__main__":
    unittest.main()
