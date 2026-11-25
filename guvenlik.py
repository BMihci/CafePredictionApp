# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Şifre güvenliği

Şifreler düz metin olarak değil, PBKDF2-SHA256 ile özetlenerek (hash) saklanır.
Yalnızca Python standart kütüphanesini kullanır; ek paket gerekmez.

Saklanan biçim:  pbkdf2_sha256$<tur_sayisi>$<tuz_hex>$<ozet_hex>

Eski sürümlerden kalan düz metin şifreler de doğrulanır; doğru girildiklerinde
`yukseltme_gerekli()` True döner ve çağıran kod şifreyi özetlenmiş haliyle
yeniden kaydeder. Böylece mevcut kullanıcılar şifre değiştirmeden geçiş yapar.
"""
import hashlib
import hmac
import secrets

ALGORITMA = "pbkdf2_sha256"
TUR_SAYISI = 260_000
TUZ_UZUNLUGU = 16  # bayt


def sifre_ozetle(sifre: str, tur: int = TUR_SAYISI) -> str:
    """Şifreyi rastgele tuzla özetler ve saklanacak metni döndürür."""
    if not isinstance(sifre, str) or not sifre:
        raise ValueError("Şifre boş olamaz.")
    tuz = secrets.token_bytes(TUZ_UZUNLUGU)
    ozet = hashlib.pbkdf2_hmac("sha256", sifre.encode("utf-8"), tuz, tur)
    return f"{ALGORITMA}${tur}${tuz.hex()}${ozet.hex()}"


def ozetli_mi(kayitli) -> bool:
    """Kayıtlı değer bu modülün ürettiği biçimde mi?"""
    if not isinstance(kayitli, str):
        return False
    parcalar = kayitli.split("$")
    return len(parcalar) == 4 and parcalar[0] == ALGORITMA and parcalar[1].isdigit()


def sifre_dogrula(sifre: str, kayitli) -> bool:
    """Girilen şifre kayıtlı değerle eşleşiyor mu? Düz metin eski kayıtları da tanır."""
    if not isinstance(sifre, str) or not isinstance(kayitli, str) or not kayitli:
        return False
    if ozetli_mi(kayitli):
        _, tur, tuz_hex, ozet_hex = kayitli.split("$")
        try:
            tuz = bytes.fromhex(tuz_hex)
            beklenen = bytes.fromhex(ozet_hex)
        except ValueError:
            return False
        hesaplanan = hashlib.pbkdf2_hmac("sha256", sifre.encode("utf-8"), tuz, int(tur))
        return hmac.compare_digest(hesaplanan, beklenen)
    # Eski sürüm: düz metin şifre (sabit süreli karşılaştırma)
    return hmac.compare_digest(sifre.encode("utf-8"), kayitli.encode("utf-8"))


def yukseltme_gerekli(kayitli) -> bool:
    """Kayıt düz metinse ya da eski tur sayısıyla özetlendiyse yeniden özetlenmeli."""
    if not ozetli_mi(kayitli):
        return True
    return int(kayitli.split("$")[1]) < TUR_SAYISI
