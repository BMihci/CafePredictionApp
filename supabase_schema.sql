-- ============================================================
-- KINGFOOL INC. SUPABASE ŞEMASI (Sadeleştirilmiş & Hatasız)
-- ============================================================

-- UYARI: Bu şema bir demo kurulumu içindir.
--  * Aşağıdaki başlangıç şifreleri örnektir; kendi projenizde mutlaka değiştirin.
--  * RLS politikaları anonim role tam okuma/yazma izni verir. Gerçek kullanımda
--    politikaları daraltın ve şifreleri düz metin olarak saklamayın.

-- 1. KULLANICILAR TABLOSU
CREATE TABLE IF NOT EXISTS public.kullanicilar (
    id BIGSERIAL PRIMARY KEY,
    kullanici_adi TEXT UNIQUE NOT NULL,
    sifre TEXT NOT NULL,
    rol TEXT DEFAULT 'user',
    kurulum_tamam BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. URUNLER TABLOSU
CREATE TABLE IF NOT EXISTS public.urunler (
    id BIGSERIAL PRIMARY KEY,
    kullanici_adi TEXT NOT NULL,
    urun_adi TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(kullanici_adi, urun_adi)
);

-- 3. SATISLAR TABLOSU
CREATE TABLE IF NOT EXISTS public.satislar (
    id BIGSERIAL PRIMARY KEY,
    kullanici_adi TEXT NOT NULL,
    urun_adi TEXT NOT NULL,
    tarih DATE NOT NULL,
    satis_adedi NUMERIC NOT NULL,
    sicaklik NUMERIC DEFAULT 25.0,
    haftasonu_mu INTEGER DEFAULT 0,
    promosyon_var_mi INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(kullanici_adi, urun_adi, tarih)
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_satislar_kullanici_urun_tarih ON public.satislar(kullanici_adi, urun_adi, tarih);
CREATE INDEX IF NOT EXISTS idx_urunler_kullanici ON public.urunler(kullanici_adi);

-- Row Level Security (RLS) Politikaları
ALTER TABLE public.kullanicilar ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.urunler ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.satislar ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "kullanicilar_anon_policy" ON public.kullanicilar;
DROP POLICY IF EXISTS "urunler_anon_policy" ON public.urunler;
DROP POLICY IF EXISTS "satislar_anon_policy" ON public.satislar;

CREATE POLICY "kullanicilar_anon_policy" ON public.kullanicilar FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "urunler_anon_policy" ON public.urunler FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "satislar_anon_policy" ON public.satislar FOR ALL USING (true) WITH CHECK (true);

-- Başlangıç Kullanıcıları
INSERT INTO public.kullanicilar (kullanici_adi, sifre, rol, kurulum_tamam) VALUES
('admin', 'admin1234', 'admin', true),
('ornekkafe', 'kafe1234', 'user', false),
('limon', 'limon1234', 'user', true)
ON CONFLICT (kullanici_adi) DO NOTHING;

-- Başlangıç Ürünleri
INSERT INTO public.urunler (kullanici_adi, urun_adi) VALUES
('admin', 'Cold Brew'),
('admin', 'Iced Americano'),
('admin', 'Iced Latte'),
('admin', 'Brownie'),
('limon', 'Cold Brew'),
('limon', 'Limonata'),
('limon', 'Çay'),
('limon', 'Brownie')
ON CONFLICT (kullanici_adi, urun_adi) DO NOTHING;

-- Admin için 45 Günlük Simülasyon Satış Verisi (generate_series ile temiz ve tek sorguda)
INSERT INTO public.satislar (kullanici_adi, urun_adi, tarih, satis_adedi, sicaklik, haftasonu_mu, promosyon_var_mi)
SELECT 
    'admin',
    'Cold Brew',
    (CURRENT_DATE - (45 - s.i) * INTERVAL '1 day')::date,
    ROUND(45.0 + (random() * 30.0)),
    ROUND((20.0 + (random() * 12.0))::NUMERIC, 1),
    CASE WHEN EXTRACT(DOW FROM (CURRENT_DATE - (45 - s.i) * INTERVAL '1 day')) IN (0, 6) THEN 1 ELSE 0 END,
    CASE WHEN random() < 0.25 THEN 1 ELSE 0 END
FROM generate_series(0, 44) AS s(i)
ON CONFLICT (kullanici_adi, urun_adi, tarih) DO NOTHING;
