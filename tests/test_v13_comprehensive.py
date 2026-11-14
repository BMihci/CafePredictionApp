# -*- coding: utf-8 -*-
"""
Kingfool Inc. v1.3 Comprehensive Bug & Regression Test Suite
Direct testing of:
1. inventory_manager (types, string conversions, unit scalers, edge cases)
2. ml_ops (training, caching, persistence, inference, edge cases)
3. llm_coaching (local generator, formatting, empty dicts, fallback)
4. supabase_db (credentials, connection, user loading)
5. api.main endpoints (root, health, login, products, weather, predict, inventory, coaching, ml_status, retrain)
"""
import sys
import os
import unittest
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import inventory_manager
import ml_ops
import llm_coaching
import supabase_db
from api.main import (
    root, health_check, login, get_products, get_weather,
    predict_sales, get_recipes, get_inventory_requirements,
    get_daily_coaching_report, get_ml_status, retrain_models,
    LoginRequest
)

class TestKingfoolV13(unittest.TestCase):

    # ---------------------------------------------------------
    # 1. INVENTORY MANAGER TESTS
    # ---------------------------------------------------------
    def test_inventory_recipes(self):
        recipes = inventory_manager.VARSAYILAN_RECETELER
        self.assertIn("Cold Brew", recipes)
        self.assertIn("Iced Latte", recipes)
        self.assertIn("Brownie", recipes)
        self.assertGreater(len(recipes), 4)

    def test_inventory_unknown_product(self):
        recete = inventory_manager.urun_recetesi_getir("Özel Ejder Meyveli Frappe")
        self.assertTrue(len(recete) >= 2)
        self.assertTrue(any("Kahve" in k["hammadde"] for k in recete))

    def test_inventory_calculation_normal(self):
        tahminler = {"Cold Brew": 50, "Iced Latte": 100}
        reqs = inventory_manager.hammadde_ihtiyaci_hesapla(tahminler)
        self.assertIsInstance(reqs, list)
        self.assertGreater(len(reqs), 0)

        # 50 * 50g + 100 * 20g = 4500g = 4.50 kg
        kahve = next((x for x in reqs if x["hammadde"] == "Kahve Çekirdeği"), None)
        self.assertIsNotNone(kahve)
        self.assertEqual(kahve["gosterim"], "4.50 kg")

        # Süt: 100 * 180ml = 18000ml = 18.00 Litre
        sut = next((x for x in reqs if x["hammadde"] == "Süt"), None)
        self.assertIsNotNone(sut)
        self.assertEqual(sut["gosterim"], "18.00 Litre")

    def test_inventory_calculation_robust_string_inputs(self):
        # String numbers from JSON
        tahminler = {"Cold Brew": "50", "Iced Latte": "100", "Bilinmeyen": "invalid"}
        reqs = inventory_manager.hammadde_ihtiyaci_hesapla(tahminler)
        self.assertGreater(len(reqs), 0)
        kahve = next((x for x in reqs if x["hammadde"] == "Kahve Çekirdeği"), None)
        self.assertEqual(kahve["gosterim"], "4.50 kg")

    def test_inventory_calculation_edge_cases(self):
        reqs_empty = inventory_manager.hammadde_ihtiyaci_hesapla({})
        self.assertEqual(reqs_empty, [])

        reqs_zeros = inventory_manager.hammadde_ihtiyaci_hesapla({"Cold Brew": 0, "Iced Latte": -10})
        self.assertEqual(reqs_zeros, [])

    def test_inventory_operational_alerts(self):
        tahminler = {"Cold Brew": 40, "Iced Latte": 60}
        reqs = inventory_manager.hammadde_ihtiyaci_hesapla(tahminler)
        alerts = inventory_manager.stok_kontrol_ve_uyarilar(reqs)
        self.assertIsInstance(alerts, list)
        self.assertTrue(any("Süt" in a for a in alerts))
        self.assertTrue(any("Çekirdek" in a for a in alerts))

    # ---------------------------------------------------------
    # 2. ML OPS TESTS
    # ---------------------------------------------------------
    def test_mlops_training_and_inference(self):
        model, metrikler = ml_ops.egit_ve_kaydet_model("admin", "Cold Brew")
        self.assertIsNotNone(model)
        self.assertIn("r2_score", metrikler)
        self.assertIn("mae", metrikler)
        self.assertGreater(metrikler["r2_score"], 0.5)

        path = ml_ops.model_dosya_yolu("admin", "Cold Brew")
        self.assertTrue(os.path.exists(path))

        # Normal inference
        tahmin, m = ml_ops.tahmin_yap("admin", "Cold Brew", yarin_sicaklik=28.0, yarin_haftasonu=1, yarin_promosyon=0)
        self.assertIsNotNone(tahmin)
        self.assertGreater(tahmin, 0)

        # Inference with promo
        tahmin_promo, _ = ml_ops.tahmin_yap("admin", "Cold Brew", yarin_sicaklik=28.0, yarin_haftasonu=1, yarin_promosyon=1)
        self.assertIsNotNone(tahmin_promo)
        self.assertGreater(tahmin_promo, 0)

    # ---------------------------------------------------------
    # 3. LLM COACHING TESTS
    # ---------------------------------------------------------
    def test_llm_coaching_local_generator(self):
        tahminler = {"Cold Brew": 45, "Iced Latte": 80, "Brownie": 25}
        reqs = inventory_manager.hammadde_ihtiyaci_hesapla(tahminler)
        res = llm_coaching.gunluk_koc_raporu_uret(
            kullanici_adi="admin",
            yarin_tarih="2026-10-21",
            yarin_sicaklik=27.5,
            yarin_haftasonu=1,
            urun_tahminleri=tahminler,
            hammadde_ihtiyaclari=reqs,
            gemini_api_key=None
        )
        self.assertTrue(res["success"])
        self.assertIn("Kingfool Heuristic Business Engine", res["kaynak"])
        self.assertIn("Günün Nabzı", res["rapor"])
        self.assertIn("Ciro Projeksiyonu", res["rapor"])
        self.assertIn("Cold Brew", res["rapor"])

    # ---------------------------------------------------------
    # 4. SUPABASE CONNECTION & USERS
    # ---------------------------------------------------------
    def test_supabase_users_and_connection(self):
        ok, msg = supabase_db.baglanti_kontrol()
        if not ok:
            self.skipTest(f"Supabase offline / DNS erişilemiyor: {msg}")

        self.assertTrue(ok, f"Supabase connection failed: {msg}")
        users = supabase_db.kullanicilari_yukle()
        self.assertIn("admin", users)
        self.assertIn("ornekkafe", users)

    # ---------------------------------------------------------
    # 5. FASTAPI REST API ENDPOINTS
    # ---------------------------------------------------------
    def test_api_root_and_health(self):
        res_root = root()
        self.assertIn("version", res_root)
        self.assertEqual(res_root["status"], "online")

        res_health = health_check()
        self.assertEqual(res_health["api_status"], "ok")
        self.assertIn("database_connected", res_health)

    def test_api_auth_login(self):
        req = LoginRequest(username="admin", password="admin1234")
        res = login(req)
        self.assertTrue(res["success"])
        self.assertEqual(res["username"], "admin")
        self.assertEqual(res["role"], "admin")

    def test_api_products(self):
        res = get_products(username="admin")
        self.assertEqual(res["username"], "admin")
        self.assertIsInstance(res["products"], list)
        self.assertGreater(len(res["products"]), 0)

    def test_api_weather(self):
        res = get_weather()
        self.assertIn("tomorrow_temp", res)
        self.assertIsInstance(res["tomorrow_temp"], (int, float))

    def test_api_predict(self):
        res = predict_sales(username="admin", product="Cold Brew", tomorrow_temp=27.0, tomorrow_is_weekend=1, tomorrow_has_promo=0)
        self.assertTrue(res["success"])
        self.assertGreater(res["prediction"], 0)
        self.assertIn("model_metrics", res)

    def test_api_inventory_recipes(self):
        res = get_recipes()
        self.assertTrue(res["success"])
        self.assertIn("Cold Brew", res["recipes"])

    def test_api_inventory_requirements(self):
        res = get_inventory_requirements(username="admin", tomorrow_temp=28.0, tomorrow_is_weekend=1)
        self.assertTrue(res["success"])
        self.assertIn("raw_materials_needed", res)
        self.assertIn("operational_alerts", res)
        self.assertGreater(len(res["raw_materials_needed"]), 0)

    def test_api_coaching_daily_report(self):
        res = get_daily_coaching_report(username="admin")
        self.assertTrue(res["success"])
        self.assertIn("report_markdown", res)
        self.assertIn("predictions", res)
        self.assertIn("inventory", res)

    def test_api_ml_status(self):
        res = get_ml_status(username="admin")
        self.assertEqual(res["username"], "admin")
        self.assertIn("models", res)
        self.assertGreater(len(res["models"]), 0)

    def test_api_retrain_models(self):
        res = retrain_models(username="admin", product="Cold Brew")
        self.assertTrue(res["success"])
        self.assertIn("metrics", res)
        self.assertEqual(res["metrics"]["kullanici"], "admin")

if __name__ == "__main__":
    unittest.main()
