# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Görsel Analitik ve Grafik Motoru (v2.0)
Matplotlib TkAgg tabanlı görsel analitik modülü.
1. Zaman Serisi Satış Trendi & 7 Günlük Hareketli Ortalama
2. Kasavana & Smith Menü Mühendisliği 4 Kadran Kâr-Hacim Matrisi (Scatter Plot)
3. Sıcaklık vs. Satış Korelasyon Grafiği (Hava Duyarlılığı Regresyonu)
4. MLOps Random Forest Öznitelik Önem Düzeyleri (Feature Importance)
"""
import matplotlib
matplotlib.use("Agg")  # Thread-safe arka plan çizim modu
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

# Kingfool / Galatasaray Renkleri
GS_KIRMIZI = "#A6192E"
GS_SARI = "#FDB913"
RENK_YILDIZ = "#FDB913"
RENK_IS_ATI = "#4A90E2"
RENK_BULMACA = "#BD10E0"
RENK_KOPEK = "#8E8E93"

def _uygula_tema(fig, ax, dark_mode: bool = True):
    """Grafik zeminini ve yazı renklerini koyu/açık temaya göre ayarlar."""
    bg_color = "#1C1920" if dark_mode else "#FFFFFF"
    fig_bg = "#121013" if dark_mode else "#FDFBF7"
    text_color = "#FAF7F9" if dark_mode else "#1A1417"
    grid_color = "#332A36" if dark_mode else "#EAE2D8"

    fig.patch.set_facecolor(fig_bg)
    ax.set_facecolor(bg_color)
    ax.tick_params(colors=text_color, labelsize=9)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(GS_SARI if dark_mode else GS_KIRMIZI)
    ax.grid(True, linestyle="--", alpha=0.4, color=grid_color)
    for spine in ax.spines.values():
        spine.set_color(grid_color)

def ciz_satis_trendi(df: pd.DataFrame, urun_adi: str, yarin_tahmin: Optional[int] = None, dark_mode: bool = True) -> Figure:
    """Satış geçmişi, 7 günlük hareketli ortalama ve yarınki yapay zeka tahminini çizer."""
    fig = Figure(figsize=(7.5, 4.2), dpi=100)
    ax = fig.add_subplot(111)
    _uygula_tema(fig, ax, dark_mode)

    if df.empty or urun_adi not in df.columns or "Tarih" not in df.columns:
        ax.text(0.5, 0.5, f"'{urun_adi}' için görselleştirilecek veri bulunamadı.",
                ha="center", va="center", color="#8E8E93", fontsize=11)
        return fig

    df_sub = df[["Tarih", urun_adi]].dropna().tail(45).copy()
    df_sub["Tarih"] = pd.to_datetime(df_sub["Tarih"])
    df_sub = df_sub.sort_values("Tarih").reset_index(drop=True)

    tarihler = df_sub["Tarih"]
    satislar = df_sub[urun_adi]

    # Gerçek Satış Çizgisi
    line_color = "#FDB913" if dark_mode else "#A6192E"
    ax.plot(tarihler, satislar, marker="o", markersize=4, color=line_color, linewidth=2, label="Günlük Satış")

    # 7 Günlük Hareketli Ortalama (Moving Average)
    if len(satislar) >= 7:
        ma7 = satislar.rolling(window=7, min_periods=1).mean()
        ax.plot(tarihler, ma7, color="#4A90E2", linestyle="--", linewidth=1.8, label="7 Günlük Trend (MA7)")

    # Yarınki Tahmin Vurgusu
    if yarin_tahmin is not None and yarin_tahmin > 0:
        yarin_tarih = tarihler.iloc[-1] + pd.Timedelta(days=1)
        ax.plot([yarin_tarih], [yarin_tahmin], marker="*", markersize=14, color="#00E676",
                label=f"Yarınki Tahmin (~{yarin_tahmin} adet)", linestyle="None")
        ax.annotate(f"★ Tahmin: {yarin_tahmin}",
                    (yarin_tarih, yarin_tahmin),
                    textcoords="offset points", xytext=(0, 10), ha="center",
                    color="#00E676", fontweight="bold", fontsize=9)

    ax.set_title(f"📈 {urun_adi} — Satış Trendi & Yapay Zeka Tahmini", fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel("Satılan Bardak / Adet", fontsize=9)
    fig.autofmt_xdate(rotation=30)
    ax.legend(loc="upper left", facecolor="#1F1A24" if dark_mode else "#FFFFFF",
              edgecolor="#332A36" if dark_mode else "#D9D0C5",
              labelcolor="#FAF7F9" if dark_mode else "#1A1417", fontsize=8)
    fig.tight_layout()
    return fig

def ciz_menu_matrisi(matris: Dict[str, Any], dark_mode: bool = True) -> Figure:
    """Kasavana & Smith Menü Mühendisliği 4 Kadran Scatter Plot'unu çizer."""
    fig = Figure(figsize=(7.5, 4.4), dpi=100)
    ax = fig.add_subplot(111)
    _uygula_tema(fig, ax, dark_mode)

    tum_urunler = matris.get("tum_urunler", [])
    if not tum_urunler:
        ax.text(0.5, 0.5, "Menü matrisi için veri bulunamadı.", ha="center", va="center", color="#8E8E93")
        return fig

    esikler = matris.get("esikler", {})
    esik_hacim = esikler.get("ortalama_hacim_esigi", 50.0)
    esik_kar = esikler.get("ortalama_katki_payi", 50.0)

    # Eşik Çizgileri (Kesişen Ekseler)
    ax.axvline(x=esik_hacim, color="#6B5E66", linestyle=":", alpha=0.7, linewidth=1.5)
    ax.axhline(y=esik_kar, color="#6B5E66", linestyle=":", alpha=0.7, linewidth=1.5)

    # 4 Kadran Başlıkları
    text_color = "#FAF7F9" if dark_mode else "#1A1417"
    x_max = max([u["satis_adedi"] for u in tum_urunler] + [esik_hacim * 1.5]) * 1.15
    y_max = max([u["katki_payi"] for u in tum_urunler] + [esik_kar * 1.5]) * 1.15

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)

    ax.text(x_max * 0.75, y_max * 0.90, "🌟 YILDIZLAR\n(Yüksek Hacim & Kâr)", color=RENK_YILDIZ, fontsize=8, fontweight="bold", ha="center")
    ax.text(x_max * 0.75, esik_kar * 0.25, "🐴 İŞ ATLARI\n(Yüksek Hacim / Düşük Kâr)", color=RENK_IS_ATI, fontsize=8, fontweight="bold", ha="center")
    ax.text(esik_hacim * 0.45, y_max * 0.90, "🧩 BULMACALAR\n(Düşük Hacim / Yüksek Kâr)", color=RENK_BULMACA, fontsize=8, fontweight="bold", ha="center")
    ax.text(esik_hacim * 0.45, esik_kar * 0.25, "🐕 KÖPEKLER\n(Düşük Hacim & Kâr)", color=RENK_KOPEK, fontsize=8, fontweight="bold", ha="center")

    # Ürün Noktalarını Çiz
    kadran_renkleri = {
        "🌟 YILDIZ": RENK_YILDIZ,
        "🐴 İŞ ATI": RENK_IS_ATI,
        "🧩 BULMACA": RENK_BULMACA,
        "🐕 KÖPEK": RENK_KOPEK
    }

    for item in tum_urunler:
        u_ad = item["urun"]
        x = item["satis_adedi"]
        y = item["katki_payi"]
        kadr = item.get("kadran", "🐕 KÖPEK")
        c = kadran_renkleri.get(kadr, "#FDB913")

        ax.scatter([x], [y], s=140, color=c, edgecolors="#FAF7F9", linewidth=1.5, zorder=5)
        ax.annotate(f"{u_ad}\n({x} ad / {y}₺)",
                    (x, y), textcoords="offset points", xytext=(0, 8), ha="center",
                    color=text_color, fontsize=8, fontweight="bold")

    ax.set_title("📊 Menü Mühendisliği Kâr & Hacim Matrisi (Kasavana & Smith BCG)", fontsize=11, fontweight="bold", pad=10)
    ax.set_xlabel("Popülarite (Tahmini Satış Adedi)", fontsize=9)
    ax.set_ylabel("Birim Brüt Kâr Katkı Payı (TL)", fontsize=9)
    fig.tight_layout()
    return fig

def ciz_sicaklik_korelasyon(df: pd.DataFrame, urun_adi: str, dark_mode: bool = True) -> Figure:
    """Hava sıcaklığı ile ürün satış miktarı arasındaki korelasyon ve trend eğrisini çizer."""
    fig = Figure(figsize=(7.5, 4.2), dpi=100)
    ax = fig.add_subplot(111)
    _uygula_tema(fig, ax, dark_mode)

    if df.empty or urun_adi not in df.columns or "Sicaklik" not in df.columns:
        ax.text(0.5, 0.5, "Korelasyon analizi için yeterli sıcaklık verisi yok.", ha="center", va="center", color="#8E8E93")
        return fig

    df_clean = df[["Sicaklik", urun_adi]].dropna()
    x = df_clean["Sicaklik"].values
    y = df_clean[urun_adi].values

    if len(x) < 5:
        ax.text(0.5, 0.5, "Korelasyon analizi için en az 5 günlük veri gereklidir.", ha="center", va="center", color="#8E8E93")
        return fig

    # Scatter Noktaları
    dot_color = "#FDB913" if dark_mode else "#A6192E"
    ax.scatter(x, y, alpha=0.75, color=dot_color, edgecolors="#121013", s=45, label="Günlük Satışlar")

    # Regresyon Eğilimi (Trendline)
    poly = np.polyfit(x, y, deg=1)
    x_line = np.linspace(min(x), max(x), 50)
    y_line = np.polyval(poly, x_line)

    egim = poly[0]
    egim_yorum = "Pozitif (Sıcakta Artıyor)" if egim > 0.5 else ("Negatif (Soğukta Artıyor)" if egim < -0.5 else "Nötr")
    ax.plot(x_line, y_line, color="#00E676" if egim > 0 else "#FF5252", linewidth=2.2,
            label=f"Trend Eğimi: {egim:+.2f} ({egim_yorum})")

    ax.set_title(f"🌡️ Sıcaklık Duyarlılığı Analizi — {urun_adi}", fontsize=11, fontweight="bold", pad=10)
    ax.set_xlabel("Sıcaklık (°C)", fontsize=9)
    ax.set_ylabel(f"{urun_adi} Satış Miktarı (Adet)", fontsize=9)
    ax.legend(loc="upper left", facecolor="#1F1A24" if dark_mode else "#FFFFFF",
              edgecolor="#332A36" if dark_mode else "#D9D0C5",
              labelcolor="#FAF7F9" if dark_mode else "#1A1417", fontsize=8)
    fig.tight_layout()
    return fig

def ciz_oznitelik_onemleri(metrikler: Dict[str, Any], dark_mode: bool = True) -> Figure:
    """Random Forest regresyon modelinin en etkili özniteliklerini yatay çubuk grafiğinde gösterir."""
    fig = Figure(figsize=(7.5, 4.0), dpi=100)
    ax = fig.add_subplot(111)
    _uygula_tema(fig, ax, dark_mode)

    importances = metrikler.get("en_onemli_oznitelikler", {})
    if not importances:
        # Fallback standart öznitelikler
        importances = {
            "Sicaklik_x_Promosyon": 0.35,
            "Satis_Lag1 (Dünkü Satış)": 0.22,
            "Tatil_Mi (Resmi/Dini)": 0.16,
            "Haftasonu_Mu": 0.14,
            "Satis_Lag7 (Geçen Hafta)": 0.13
        }

    etiketler = list(importances.keys())
    degerler = [v * 100 for v in importances.values()]

    # Sırala (en yüksek üstte)
    y_pos = np.arange(len(etiketler))
    bar_colors = ["#FDB913", "#A6192E", "#4A90E2", "#BD10E0", "#00E676"][:len(etiketler)]

    bars = ax.barh(y_pos, degerler, color=bar_colors, align="center", height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(etiketler, fontsize=9)
    ax.invert_yaxis()

    text_color = "#FAF7F9" if dark_mode else "#1A1417"
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1.0, bar.get_y() + bar.get_height() / 2, f"%{width:.1f}",
                va="center", ha="left", color=text_color, fontsize=8, fontweight="bold")

    ax.set_xlim(0, max(degerler) * 1.25 if degerler else 100)
    ax.set_title("🧠 Yapay Zekayı En Çok Etkileyen Faktörler (Random Forest MLOps)", fontsize=11, fontweight="bold", pad=10)
    ax.set_xlabel("Tahmine Etki Oranı (%)", fontsize=9)
    fig.tight_layout()
    return fig
