# -*- coding: utf-8 -*-
"""Şifre özetleme testleri.  Çalıştırma:  python -m unittest tests.test_guvenlik"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import guvenlik  # noqa: E402


class SifreOzetlemeTest(unittest.TestCase):
    def test_ozet_bicimi_ve_dogrulama(self):
        ozet = guvenlik.sifre_ozetle("kafe1234")
        self.assertTrue(ozet.startswith("pbkdf2_sha256$"))
        self.assertNotIn("kafe1234", ozet)
        self.assertTrue(guvenlik.ozetli_mi(ozet))
        self.assertTrue(guvenlik.sifre_dogrula("kafe1234", ozet))
        self.assertFalse(guvenlik.sifre_dogrula("kafe12345", ozet))
        self.assertFalse(guvenlik.sifre_dogrula("", ozet))

    def test_ayni_sifre_farkli_ozet(self):
        # Rastgele tuz: aynı şifre iki kez özetlenince farklı metin çıkar
        self.assertNotEqual(guvenlik.sifre_ozetle("admin1234"), guvenlik.sifre_ozetle("admin1234"))

    def test_turkce_karakterler(self):
        ozet = guvenlik.sifre_ozetle("Çağrı-şifre_ğüİ")
        self.assertTrue(guvenlik.sifre_dogrula("Çağrı-şifre_ğüİ", ozet))
        self.assertFalse(guvenlik.sifre_dogrula("Cagri-sifre_guI", ozet))

    def test_eski_duz_metin_kayitlar(self):
        self.assertTrue(guvenlik.sifre_dogrula("admin1234", "admin1234"))
        self.assertFalse(guvenlik.sifre_dogrula("admin123", "admin1234"))
        self.assertTrue(guvenlik.yukseltme_gerekli("admin1234"))
        self.assertFalse(guvenlik.yukseltme_gerekli(guvenlik.sifre_ozetle("admin1234")))

    def test_dusuk_tur_sayisi_yukseltilir(self):
        eski = guvenlik.sifre_ozetle("x1", tur=1000)
        self.assertTrue(guvenlik.sifre_dogrula("x1", eski))
        self.assertTrue(guvenlik.yukseltme_gerekli(eski))

    def test_bozuk_kayitlar(self):
        for kayit in (None, "", 123, "pbkdf2_sha256$abc$00$00", "pbkdf2_sha256$1000$zz$zz"):
            self.assertFalse(guvenlik.sifre_dogrula("x", kayit), kayit)
        with self.assertRaises(ValueError):
            guvenlik.sifre_ozetle("")


class SupabaseKayitTest(unittest.TestCase):
    """Buluta yalnızca özetin gittiğini, ağ çağrısını taklit ederek doğrular."""

    @classmethod
    def setUpClass(cls):
        import supabase_db
        cls.db = supabase_db

    def _yakala(self, yontem):
        cevap = mock.Mock(status_code=201)
        return mock.patch.object(self.db.requests, yontem, return_value=cevap)

    def test_kullanici_ekle_ozet_gonderir(self):
        with self._yakala("post") as post:
            self.assertTrue(self.db.kullanici_ekle("yeni", "gizli123", "user"))
        gonderilen = post.call_args.kwargs["json"]["sifre"]
        self.assertNotEqual(gonderilen, "gizli123")
        self.assertTrue(guvenlik.sifre_dogrula("gizli123", gonderilen))

    def test_sifre_guncelle_ozet_gonderir(self):
        with self._yakala("patch") as patch:
            self.db.kullanici_sifre_guncelle("yeni", "yeniSifre!")
        gonderilen = patch.call_args.kwargs["json"]["sifre"]
        self.assertTrue(guvenlik.sifre_dogrula("yeniSifre!", gonderilen))

    def test_hazir_ozet_iki_kez_ozetlenmez(self):
        ozet = guvenlik.sifre_ozetle("abc12345")
        with self._yakala("patch") as patch:
            self.db.kullanici_sifre_guncelle("yeni", ozet)
        self.assertEqual(patch.call_args.kwargs["json"]["sifre"], ozet)


if __name__ == "__main__":
    unittest.main()
