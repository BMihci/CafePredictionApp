# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Örnek veriyle hızlı deneme

Arayüz, API ya da bulut veritabanı kurmadan tahmin motorunu dener:
ornek_veri/ornek_satislar.csv dosyasındaki uydurma satış verisiyle her ürün için
bir Random Forest modeli eğitir ve yarın için satış adedi tahmini yazdırır.

Kullanım:  python ornek_tahmin.py
"""
import os
import pandas as pd

import ml_ops

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERI = os.path.join(BASE_DIR, "ornek_veri", "ornek_satislar.csv")
KULLANICI = "ornek"
YARIN_SICAKLIK = 18.0   # °C
YARIN_HAFTASONU = 0     # 1 = hafta sonu
YARIN_PROMOSYON = 0     # 1 = promosyon var


def main():
    df = pd.read_csv(VERI)
    sabit = ["Tarih", "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi"]
    urunler = [c for c in df.columns if c not in sabit]
    print(f"Veri: {len(df)} gün, {len(urunler)} ürün ({df['Tarih'].min()} - {df['Tarih'].max()})")
    print(f"Yarın varsayımı: {YARIN_SICAKLIK} °C, hafta sonu={YARIN_HAFTASONU}, promosyon={YARIN_PROMOSYON}\n")
    print(f"{'Ürün':<16}{'Tahmin':>8}{'MAE':>8}{'R2':>8}   En önemli öznitelikler")
    for urun in urunler:
        model, metrik = ml_ops.egit_ve_kaydet_model(KULLANICI, urun, df[sabit + [urun]].copy(), ulke="Türkiye")
        if model is None:
            print(f"{urun:<16} eğitilemedi: {metrik}")
            continue
        tahmin, _ = ml_ops.tahmin_yap(KULLANICI, urun, YARIN_SICAKLIK, YARIN_HAFTASONU, YARIN_PROMOSYON, ulke="Türkiye")
        onemli = ", ".join(metrik["en_onemli_oznitelikler"].keys())
        print(f"{urun:<16}{tahmin:>8}{metrik['mae']:>8}{metrik['r2_score']:>8}   {onemli}")
    print("\nNot: MAE ve R2 eğitim verisi üzerinde ölçülür; gerçek başarıyı olduğundan iyi gösterir.")


if __name__ == "__main__":
    main()
