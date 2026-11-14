# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Uluslararası Konum ve Koordinat Yönetimi (v1.5)
Türkiye (81 il ve tüm ilçeleri) ile birlikte uluslararası ülkeleri (ABD, Birleşik Krallık, vb.) destekler.
Kural: Sadece Türkiye için ilçe seçimi aktiftir; diğer ülkelerde ilçe seçimi kapalıdır.
"""
import json
import requests
from typing import Dict, List, Tuple, Optional

# Türkiye 81 İl ve İlçeleri
TURKIYE_DATA_RAW = r'''{"list":[{"name":"Adana","districts":["ALADAĞ","CEYHAN","ÇUKUROVA","FEKE","İMAMOĞLU","KARAİSALI","KARATAŞ","KOZAN","POZANTI","SAİMBEYLİ","SARIÇAM","SEYHAN","TUFANBEYLİ","YUMURTALIK","YÜREĞİR"]},{"name":"Adıyaman","districts":["MERKEZ","BESNİ","ÇELİKHAN","GERGER","GÖLBAŞI","KAHTA","SAMSAT","SİNCİK","TUT"]},{"name":"Afyonkarahisar","districts":["MERKEZ","BAŞMAKÇI","BAYAT","BOLVADİN","ÇAY","ÇOBANLAR","DAZKIRI","DİNAR","EMİRDAĞ","EVCİLER","HOCALAR","İHSANİYE","İSCEHİSAR","KIZILÖREN","SANDIKLI","SİNANPAŞA","SULTANDAĞI","ŞUHUT"]},{"name":"Ağrı","districts":["MERKEZ","DİYADİN","DOĞUBAYAZIT","ELEŞKİRT","HAMUR","PATNOS","TAŞLIÇAY","TUTAK"]},{"name":"Amasya","districts":["MERKEZ","GÖYNÜCEK","GÜMÜŞHACIKÖY","HAMAMÖZÜ","MERZİFON","SULUOVA","TAŞOVA"]},{"name":"Ankara","districts":["AKYURT","ALTINDAĞ","AYAŞ","BALA","BEYPAZARI","ÇAMLIDERE","ÇANKAYA","ÇUBUK","ELMADAĞ","ETİMESGUT","EVREN","GÖLBAŞI","GÜDÜL","HAYMANA","KAHRAMANKAZAN","KALECİK","KEÇİÖREN","KIZILCAHAMAM","MAMAK","NALLIHAN","POLATLI","PURSAKLAR","SİNCAN","ŞEREFLİKOÇHİSAR","YENİMAHALLE"]},{"name":"Antalya","districts":["AKSEKİ","AKSU","ALANYA","DEMRE","DÖŞEMEALTI","ELMALI","FİNİKE","GAZİPAŞA","GÜNDOĞMUŞ","İBRADI","KAŞ","KEMER","KEPEZ","KONYAALTI","KORKUTELİ","KUMLUCA","MANAVGAT","MURATPAŞA","SERİK"]},{"name":"Artvin","districts":["MERKEZ","ARDANUÇ","ARHAVİ","BORÇKA","HOPA","KEMALPAŞA","MURGUL","ŞAVŞAT","YUSUFELİ"]},{"name":"Aydın","districts":["BOZDOĞAN","BUHARKENT","ÇİNE","DİDİM","EFELER","GERMENCİK","İNCİRLİOVA","KARACASU","KARPUZLU","KOÇARLI","KÖŞK","KUŞADASI","KUYUCAK","NAZİLLİ","SÖKE","SULTANHİSAR","YENİPAZAR"]},{"name":"Balıkesir","districts":["ALTIEYLÜL","AYVALIK","BALYA","BANDIRMA","BİGADİÇ","BURHANİYE","DURSUNBEY","EDREMİT","ERDEK","GÖMEÇ","GÖNEN","HAVRAN","İVRİNDİ","KARESİ","KEPSUT","MANYAS","MARMARA","SAVAŞTEPE","SINDIRGI","SUSURLUK"]},{"name":"Bilecik","districts":["MERKEZ","BOZÜYÜK","GÖLPAZARI","İNHİSAR","OSMANELİ","PAZARYERİ","SÖĞÜT","YENİPAZAR"]},{"name":"Bingöl","districts":["MERKEZ","ADAKLI","GENÇ","KARLIOVA","KİĞI","SOLHAN","YAYLADERE","YEDİSU"]},{"name":"Bitlis","districts":["MERKEZ","ADİLCEVAZ","AHLAT","GÜROYMAK","HİZAN","MUTKİ","TATVAN"]},{"name":"Bolu","districts":["MERKEZ","DÖRTDİVAN","GEREDE","GÖYNÜK","KIBRISCIK","MENGEN","MUDURNU","SEBEN","YENİÇAĞA"]},{"name":"Burdur","districts":["MERKEZ","AĞLASUN","ALTINYAYLA","BUCAK","ÇAVDIR","ÇELTİKÇİ","GÖLHİSAR","KARAMANLI","KEMER","TEFENNİ","YEŞİLOVA"]},{"name":"Bursa","districts":["BÜYÜKORHAN","GEMLİK","GÜRSU","HARMANCIK","İNEGÖL","İZNİK","KARACABEY","KELES","KESTEL","MUDANYA","MUSTAFAKEMALPAŞA","NİLÜFER","ORHANELİ","ORHANGAZİ","OSMANGAZİ","YENİŞEHİR","YILDIRIM"]},{"name":"Çanakkale","districts":["MERKEZ","AYVACIK","BAYRAMİÇ","BİGA","BOZCAADA","ÇAN","ECEABAT","EZİNE","GELİBOLU","GÖKÇEADA","LAPSEKİ","YENİCE"]},{"name":"Çankırı","districts":["MERKEZ","ATKARACALAR","BAYRAMÖREN","ÇERKEŞ","ELDİVAN","ILGAZ","KIZILIRMAK","KORGUN","KURŞUNLU","ORTA","ŞABANÖZÜ","YAPRAKLI"]},{"name":"Çorum","districts":["MERKEZ","ALACA","BAYAT","BOĞAZKALE","DODURGA","İSKİLİP","KARGI","LAÇİN","MECİTÖZÜ","OĞUZLAR","ORTAKÖY","OSMANCIK","SUNGURLU","UĞURLUDAĞ"]},{"name":"Denizli","districts":["ACIPAYAM","BABADAĞ","BAKLAN","BEKİLLİ","BEYAĞAÇ","BOZKURT","BULDAN","ÇAL","ÇAMELİ","ÇARDAK","ÇİVRİL","GÜNEY","HONAZ","KALE","MERKEZEFENDİ","PAMUKKALE","SARAYKÖY","SERİNHİSAR","TAVAS"]},{"name":"Diyarbakır","districts":["BAĞLAR","BİSMİL","ÇERMİK","ÇINAR","ÇÜNGÜŞ","DİCLE","EĞİL","ERGANİ","HANİ","HAZRO","KAYAPINAR","KOCAKÖY","KULP","LİCE","SİLVAN","SUR","YENİŞEHİR"]},{"name":"Edirne","districts":["MERKEZ","ENEZ","HAVSA","İPSALA","KEŞAN","LALAPAŞA","MERİÇ","SÜLOĞLU","UZUNKÖPRÜ"]},{"name":"Elazığ","districts":["MERKEZ","AĞIN","ALACAKAYA","ARICAK","BASKİL","KARAKOÇAN","KEBAN","KOVANCILAR","MADEN","PALU","SİVRİCE"]},{"name":"Erzincan","districts":["MERKEZ","ÇAYIRLI","İLİÇ","KEMAH","KEMALİYE","OTLUKBELİ","REFAHİYE","TERCAN","ÜZÜMLÜ"]},{"name":"Erzurum","districts":["AŞKALE","AZİZİYE","ÇAT","HINIS","HORASAN","İSPİR","KARAÇOBAN","KARAYAZI","KÖPRÜKÖY","NARMAN","OLTU","OLUR","PALANDÖKEN","PASİNLER","PAZARYOLU","ŞENKAYA","TEKMAN","TORTUM","UZUNDERE","YAKUTİYE"]},{"name":"Eskişehir","districts":["ALPU","BEYLİKOVA","ÇİFTELER","GÜNYÜZÜ","HAN","İNÖNÜ","MAHMUDİYE","MİHALGAZİ","MİHALIÇÇIK","ODUNPAZARI","SARICAKAYA","SEYİTGAZİ","SİVRİHİSAR","TEPEBAŞI"]},{"name":"Gaziantep","districts":["ARABAN","İSLAHİYE","KARKAMIŞ","NİZİP","NURDAĞI","OĞUZELİ","ŞAHİNBEY","ŞEHİTKAMİL","YAVUZELİ"]},{"name":"Giresun","districts":["MERKEZ","ALUCRA","BULANCAK","ÇAMOLUK","ÇANAKÇI","DERELİ","DOĞANKENT","ESPİYE","EYNESİL","GÖRELE","GÜCE","KEŞAP","PİRAZİZ","ŞEBİNKARAHİSAR","TİREBOLU","YAĞLIDERE"]},{"name":"Gümüşhane","districts":["MERKEZ","KELKİT","KÖSE","KÜRTÜN","ŞİRAN","TORUL"]},{"name":"Hakkari","districts":["MERKEZ","ÇUKURCA","DERECİK","ŞEMDİNLİ","YÜKSEKOVA"]},{"name":"Hatay","districts":["ALTINÖZÜ","ANTAKYA","ARSUZ","BELEN","DEFNE","DÖRTYOL","ERZİN","HASSA","İSKENDERUN","KIRIKHAN","KUMLU","PAYAS","REYHANLI","SAMANDAĞ","YAYLADAĞI"]},{"name":"Isparta","districts":["MERKEZ","AKSU","ATABEY","EĞİRDİR","GELENDOST","GÖNEN","KEÇİBORLU","SENİRKENT","SÜTÇÜLER","ŞARKİKARAAĞAÇ","ULUBORLU","YALVAÇ","YENİŞARBADEMLİ"]},{"name":"Mersin","districts":["AKDENİZ","ANAMUR","AYDINCIK","BOZYAZI","ÇAMLIYAYLA","ERDEMLİ","GÜLNAR","MEZİTLİ","MUT","SİLİFKE","TARSUS","TOROSLAR","YENİŞEHİR"]},{"name":"İstanbul","districts":["ADALAR","ARNAVUTKÖY","ATAŞEHİR","AVCILAR","BAĞCILAR","BAHÇELİEVLER","BAKIRKÖY","BAŞAKŞEHİR","BAYRAMPAŞA","BEŞİKTAŞ","BEYKOZ","BEYLİKDÜZÜ","BEYOĞLU","BÜYÜKÇEKMECE","ÇATALCA","ÇEKMEKÖY","ESENLER","ESENYURT","EYÜPSULTAN","FATİH","GAZİOSMANPAŞA","GÜNGÖREN","KADIKÖY","KAĞITHANE","KARTAL","KÜÇÜKÇEKMECE","MALTEPE","PENDİK","SANCAKTEPE","SARIYER","SİLİVRİ","SULTANBEYLİ","SULTANGAZİ","ŞİLE","ŞİŞLİ","TUZLA","ÜMRANİYE","ÜSKÜDAR","ZEYTİNBURNU"]},{"name":"İzmir","districts":["ALİAĞA","BALÇOVA","BAYINDIR","BAYRAKLI","BERGAMA","BEYDAĞ","BORNOVA","BUCA","ÇEŞME","ÇİĞLİ","DİKİLİ","FOÇA","GAZİEMİR","GÜZELBAHÇE","KARABAĞLAR","KARABURUN","KARŞIYAKA","KEMALPAŞA","KINIK","KİRAZ","KONAK","MENDERES","MENEMEN","NARLIDERE","ÖDEMİŞ","SEFERİHİSAR","SELÇUK","TİRE","TORBALI","URLA"]},{"name":"Kars","districts":["MERKEZ","AKYAKA","ARPAÇAY","DİGOR","KAĞIZMAN","SARIKAMIŞ","SELİM","SUSUZ"]},{"name":"Kastamonu","districts":["MERKEZ","ABANA","AĞLI","ARAÇ","AZDAVAY","BOZKURT","CİDE","ÇATALZEYTİN","DADAY","DEVREKANİ","DOĞANYURT","HANÖNÜ","İHSANGAZİ","İNEBOLU","KÜRE","PINARBAŞI","SEYDİLER","ŞENPAZAR","TAŞKÖPRÜ","TOSYA"]},{"name":"Kayseri","districts":["AKKIŞLA","BÜNYAN","DEVELİ","FELAHİYE","HACILAR","İNCESU","KOCASİNAN","MELİKGAZİ","ÖZVATAN","PINARBAŞI","SARIOĞLAN","SARIZ","TALAS","TOMARZA","YAHYALI","YEŞİLHİSAR"]},{"name":"Kırklareli","districts":["MERKEZ","BABAESKİ","DEMİRKÖY","KOFÇAZ","LÜLEBURGAZ","PEHLİVANKÖY","PINARHİSAR","VİZE"]},{"name":"Kırşehir","districts":["MERKEZ","AKÇAKENT","AKPINAR","BOZTEPE","ÇİÇEKDAĞI","KAMAN","MUCUR"]},{"name":"Kocaeli","districts":["BAŞİSKELE","ÇAYIROVA","DARICA","DERİNCE","DİLOVASI","GEBZE","GÖLCÜK","İZMİT","KANDIRA","KARAMÜRSEL","KARTEPE","KÖRFEZ"]},{"name":"Konya","districts":["AHIRLI","AKÖREN","AKŞEHİR","ALTINEKİN","BEYŞEHİR","BOZKIR","CİHANBEYLİ","ÇELTİK","ÇUMRA","DERBENT","DEREBUCAK","DOĞANHİSAR","EMİRGAZİ","EREĞLİ","GÜNEYSINIR","HADİM","HALKAPINAR","HÜYÜK","ILGIN","KADINHANI","KARAPINAR","KARATAY","KULU","MERAM","SARAYÖNÜ","SELÇUKLU","SEYDİŞEHİR","TAŞKENT","TUZLUKÇU","YALIHÜYÜK","YUNAK"]},{"name":"Kütahya","districts":["MERKEZ","ALTINTAŞ","ASLANAPA","ÇAVDARHİSAR","DOMANİÇ","DUMLUPINAR","EMET","GEDİZ","HİSARCIK","PAZARLAR","SİMAV","ŞAPHANE","TAVŞANLI"]},{"name":"Malatya","districts":["AKÇADAĞ","ARAPGİR","ARGUVAN","BATTALGAZİ","DARENDE","DOĞANŞEHİR","DOĞANYOL","HEKİMHAN","KALE","KULUNCAK","PÜTÜRGE","YAZIHAN","YEŞİLYURT"]},{"name":"Manisa","districts":["AHMETLİ","AKHİSAR","ALAŞEHİR","DEMİRCİ","GÖLMARMARA","GÖRDES","KIRKAĞAÇ","KÖPRÜBAŞI","KULA","SALİHLİ","SARIGÖL","SARUHANLI","SELENDİ","SOMA","ŞEHZADELER","TURGUTLU","YUNUSEMRE"]},{"name":"Kahramanmaraş","districts":["AFŞİN","ANDIRIN","ÇAĞLAYANCERİT","DULKADİROĞLU","EKİNÖZÜ","ELBİSTAN","GÖKSUN","NURHAK","ONİKİŞUBAT","PAZARCIK","TÜRKOĞLU"]},{"name":"Mardin","districts":["ARTUKLU","DARGEÇİT","DERİK","KIZILTEPE","MAZIDAĞI","MİDYAT","NUSAYBİN","ÖMERLİ","SAVUR","YEŞİLLİ"]},{"name":"Muğla","districts":["BODRUM","DALAMAN","DATÇA","FETHİYE","KAVAKLIDERE","KÖYCEĞİZ","MARMARİS","MENTEŞE","MİLAS","ORTACA","SEYDİKEMER","ULA","YATAĞAN"]},{"name":"Muş","districts":["MERKEZ","BULANIK","HASKÖY","KORKUT","MALAZGİRT","VARTO"]},{"name":"Nevşehir","districts":["MERKEZ","ACIGÖL","AVANOS","DERİNKUYU","GÜLŞEHİR","HACIBEKTAŞ","KOZAKLI","ÜRGÜP"]},{"name":"Niğde","districts":["MERKEZ","ALTUNHİSAR","BOR","ÇAMARDI","ÇİFTLİK","ULUKIŞLA"]},{"name":"Ordu","districts":["AKKUŞ","ALTINORDU","AYBASTI","ÇAMAŞ","ÇATALPINAR","ÇAYBAŞI","FATSA","GÖLKÖY","GÜLYALI","GÜRGENTEPE","İKİZCE","KABADÜZ","KABATAŞ","KORGAN","KUMRU","MESUDİYE","PERŞEMBE","ULUBEY","ÜNYE"]},{"name":"Rize","districts":["MERKEZ","ARDEŞEN","ÇAMLIHEMŞİN","ÇAYELİ","DEREPAZARI","FINDIKLI","GÜNEYSU","HEMŞİN","İKİZDERE","İYİDERE","KALKANDERE","PAZAR"]},{"name":"Sakarya","districts":["ADAPAZARI","AKYAZI","ARİFİYE","ERENLER","FERİZLİ","GEYVE","HENDEK","KARAPÜRÇEK","KARASU","KAYNARCA","KOCAALİ","PAMUKOVA","SAPANCA","SERDİVAN","SÖĞÜTLÜ","TARAKLI"]},{"name":"Samsun","districts":["ALAÇAM","ASARCIK","ATAKUM","AYVACIK","BAFRA","CANİK","ÇARŞAMBA","HAVZA","İLKADIM","KAVAK","LADİK","19 MAYIS","SALIPAZARI","TEKKEKÖY","TERME","VEZİRKÖPRÜ","YAKAKENT"]},{"name":"Siirt","districts":["MERKEZ","BAYKAN","ERUH","KURTALAN","PERVARİ","ŞİRVAN","TİLLO"]},{"name":"Sinop","districts":["MERKEZ","AYANCIK","BOYABAT","DİKMEN","DURAĞAN","ERFELEK","GERZE","SARAYDÜZÜ","TÜRKELİ"]},{"name":"Sivas","districts":["MERKEZ","AKINCILAR","ALTINYAYLA","DİVRİĞİ","DOĞANŞAR","GEMEREK","GÖLOVA","GÜRÜN","HAFİK","İMRANLI","KANGAL","KOYULHİSAR","SUŞEHRİ","ŞARKIŞLA","ULAŞ","YILDIZELİ","ZARA"]},{"name":"Tekirdağ","districts":["ÇERKEZKÖY","ÇORLU","ERGENE","HAYRABOLU","KAPAKLI","MALKARA","MARMARAEREĞLİSİ","MURATLI","SARAY","SÜLEYMANPAŞA","ŞARKÖY"]},{"name":"Tokat","districts":["MERKEZ","ALMUS","ARTOVA","BAŞÇİFTLİK","ERBAA","NİKSAR","PAZAR","REŞADİYE","SULUSARAY","TURHAL","YEŞİLYURT","ZİLE"]},{"name":"Trabzon","districts":["AKÇAABAT","ARAKLI","ARSİN","BEŞİKDÜZÜ","ÇARŞIBAŞI","ÇAYKARA","DERNEKPAZARI","DÜZKÖY","HAYRAT","KÖPRÜBAŞI","MAÇKA","OF","ORTAHİSAR","SÜRMENE","ŞALPAZARI","TONYA","VAKFIKEBİR","YOMRA"]},{"name":"Tunceli","districts":["MERKEZ","ÇEMİŞGEZEK","HOZAT","MAZGİRT","NAZIMİYE","OVACIK","PERTEK","PÜLÜMÜR"]},{"name":"Şanlıurfa","districts":["AKÇAKALE","BİRECİK","BOZOVA","CEYLANPINAR","EYYÜBİYE","HALFETİ","HALİLİYE","HARRAN","HİLVAN","KARAKÖPRÜ","SİVEREK","SURUÇ","VİRANŞEHİR"]},{"name":"Uşak","districts":["MERKEZ","BANAZ","EŞME","KARAHALLI","SİVASLI","ULUBEY"]},{"name":"Van","districts":["BAHÇESARAY","BAŞKALE","ÇALDIRAN","ÇATAK","EDREMİT","ERCİŞ","GEVAŞ","GÜRPINAR","İPEKYOLU","MURADİYE","ÖZALP","SARAY","TUŞBA"]},{"name":"Yozgat","districts":["MERKEZ","AKDAĞMADENİ","AYDINCIK","BOĞAZLIYAN","ÇANDIR","ÇAYIRALAN","ÇEKEREK","KADIŞEHRİ","SARAYKENT","SARIKAYA","SORGUN","ŞEFAATLİ","YENİFAKILI","YERKÖY"]},{"name":"Zonguldak","districts":["MERKEZ","ALAPLI","ÇAYCUMA","DEVREK","EREĞLİ","GÖKÇEBEY","KİLİMLİ","KOZLU"]},{"name":"Aksaray","districts":["MERKEZ","AĞAÇÖREN","ESKİL","GÜLAĞAÇ","GÜZELYURT","ORTAKÖY","SARIYAHŞİ","SULTANHANI"]},{"name":"Bayburt","districts":["MERKEZ","AYDINTEPE","DEMİRÖZÜ"]},{"name":"Karaman","districts":["MERKEZ","AYRANCI","BAŞYAYLA","ERMENEK","KAZIMKARABEKİR","SARIVELİLER"]},{"name":"Kırıkkale","districts":["MERKEZ","BAHŞILI","BALIŞEYH","ÇELEBİ","DELİCE","KARAKEÇİLİ","KESKİN","SULAKYURT","YAHŞİHAN"]},{"name":"Batman","districts":["MERKEZ","BEŞİRİ","GERCÜŞ","HASANKEYF","KOZLUK","SASON"]},{"name":"Şırnak","districts":["MERKEZ","BEYTÜŞŞEBAP","CİZRE","GÜÇLÜKONAK","İDİL","SİLOPİ","ULUDERE"]},{"name":"Bartın","districts":["MERKEZ","AMASRA","KURUCAŞİLE","ULUS"]},{"name":"Ardahan","districts":["MERKEZ","ÇILDIR","DAMAL","GÖLE","HANAK","POSOF"]},{"name":"Iğdır","districts":["MERKEZ","ARALIK","KARAKOYUNLU","TUZLUCA"]},{"name":"Yalova","districts":["MERKEZ","ALTINOVA","ARMUTLU","ÇINARCIK","ÇİFTLİKKÖY","TERMAL"]},{"name":"Karabük","districts":["MERKEZ","EFLANİ","ESKİPAZAR","OVACIK","SAFRANBOLU","YENİCE"]},{"name":"Kilis","districts":["MERKEZ","ELBEYLİ","MUSABEYLİ","POLATELİ"]},{"name":"Osmaniye","districts":["MERKEZ","BAHÇE","DÜZİÇİ","HASANBEYLİ","KADİRLİ","SUMBAS","TOPRAKKALE"]},{"name":"Düzce","districts":["MERKEZ","AKÇAKOCA","CUMAYERİ","ÇİLİMLİ","GÖLYAKA","GÜMÜŞOVA","KAYNAŞLI","YIĞILCA"]}]}'''

TURKIYE_IL_ILCE: Dict[str, List[str]] = {
    item["name"]: [d.title() for d in item["districts"]]
    for item in json.loads(TURKIYE_DATA_RAW)["list"]
}

# Desteklenen Ülkeler ve Şehirleri + Sabit Koordinatları
DUNYA_ULKELERI = {
    "Türkiye": {
        "kod": "TR",
        "ilce_destegi": True,
        "sehirler": sorted(list(TURKIYE_IL_ILCE.keys()))
    },
    "Amerika Birleşik Devletleri": {
        "kod": "US",
        "ilce_destegi": False,
        "sehirler": ["New York", "Los Angeles", "Chicago", "Houston", "Seattle", "San Francisco", "Boston", "Miami"],
        "koordinatlar": {
            "New York": (40.7128, -74.0060),
            "Los Angeles": (34.0522, -118.2437),
            "Chicago": (41.8781, -87.6298),
            "Houston": (29.7604, -95.3698),
            "Seattle": (47.6062, -122.3321),
            "San Francisco": (37.7749, -122.4194),
            "Boston": (42.3601, -71.0589),
            "Miami": (25.7617, -80.1918)
        }
    },
    "Birleşik Krallık": {
        "kod": "GB",
        "ilce_destegi": False,
        "sehirler": ["Edinburgh", "Londra", "Manchester", "Birmingham", "Glasgow", "Liverpool"],
        "koordinatlar": {
            "Edinburgh": (55.9533, -3.1883),
            "Londra": (51.5074, -0.1278),
            "Manchester": (53.4808, -2.2426),
            "Birmingham": (52.4862, -1.8904),
            "Glasgow": (55.8642, -4.2518),
            "Liverpool": (53.4084, -2.9916)
        }
    },
    "Almanya": {
        "kod": "DE",
        "ilce_destegi": False,
        "sehirler": ["Berlin", "Münih", "Frankfurt", "Hamburg", "Köln"],
        "koordinatlar": {
            "Berlin": (52.5200, 13.4050),
            "Münih": (48.1351, 11.5820),
            "Frankfurt": (50.1109, 8.6821),
            "Hamburg": (53.5511, 9.9937),
            "Köln": (50.9375, 6.9603)
        }
    },
    "Fransa": {
        "kod": "FR",
        "ilce_destegi": False,
        "sehirler": ["Paris", "Lyon", "Marsilya", "Nice", "Bordeaux"],
        "koordinatlar": {
            "Paris": (48.8566, 2.3522),
            "Lyon": (45.7640, 4.8357),
            "Marsilya": (43.2965, 5.3698),
            "Nice": (43.7102, 7.2620),
            "Bordeaux": (44.8378, -0.5792)
        }
    },
    "İtalya": {
        "kod": "IT",
        "ilce_destegi": False,
        "sehirler": ["Roma", "Milano", "Floransa", "Napoli", "Venedik"],
        "koordinatlar": {
            "Roma": (41.9028, 12.4964),
            "Milano": (45.4642, 9.1900),
            "Floransa": (43.7696, 11.2558),
            "Napoli": (40.8518, 14.2681),
            "Venedik": (45.4408, 12.3155)
        }
    },
    "Karadağ": {
        "kod": "ME",
        "ilce_destegi": False,
        "sehirler": ["Podgorica", "Budva", "Bar", "Kotor", "Tivat", "Herceg Novi", "Ulcinj", "Cetinje", "Nikšić"],
        "koordinatlar": {
            "Podgorica": (42.4411, 19.2636),
            "Budva": (42.2868, 18.8400),
            "Bar": (42.0931, 19.1003),
            "Kotor": (42.4247, 18.7712),
            "Tivat": (42.4364, 18.6961),
            "Herceg Novi": (42.4531, 18.5375),
            "Ulcinj": (41.9294, 19.2056),
            "Cetinje": (42.3931, 18.9219),
            "Nikšić": (42.7731, 18.9444)
        }
    },
    "Hollanda": {
        "kod": "NL",
        "ilce_destegi": False,
        "sehirler": ["Amsterdam", "Rotterdam", "Utrecht", "Lahey"],
        "koordinatlar": {
            "Amsterdam": (52.3676, 4.9041),
            "Rotterdam": (51.9244, 4.4777),
            "Utrecht": (52.0907, 5.1214),
            "Lahey": (52.0705, 4.3007)
        }
    },
    "İspanya": {
        "kod": "ES",
        "ilce_destegi": False,
        "sehirler": ["Madrid", "Barselona", "Valensiya", "Sevilla"],
        "koordinatlar": {
            "Madrid": (40.4168, -3.7038),
            "Barselona": (41.3851, 2.1734),
            "Valensiya": (39.4699, -0.3763),
            "Sevilla": (37.3891, -5.9845)
        }
    },
    "Japonya": {
        "kod": "JP",
        "ilce_destegi": False,
        "sehirler": ["Tokyo", "Osaka", "Kyoto"],
        "koordinatlar": {
            "Tokyo": (35.6762, 139.6503),
            "Osaka": (34.6937, 135.5023),
            "Kyoto": (35.0116, 135.7681)
        }
    },
    "Avustralya": {
        "kod": "AU",
        "ilce_destegi": False,
        "sehirler": ["Sidney", "Melbourne", "Brisbane", "Perth"],
        "koordinatlar": {
            "Sidney": (-33.8688, 151.2093),
            "Melbourne": (-37.8136, 144.9631),
            "Brisbane": (-27.4698, 153.0251),
            "Perth": (-31.9505, 115.8605)
        }
    }
}

ULKE_LISTESI = list(DUNYA_ULKELERI.keys())

def ulke_kodu_bul(ulke: str) -> str:
    """Ülke adına göre ISO 3166-1 alpha-2 kodunu döndürür (varsayılan TR)."""
    if not ulke:
        return "TR"
    u = DUNYA_ULKELERI.get(ulke)
    if u and "kod" in u:
        return u["kod"]
    # İsim eşleştirmeleri
    eslesme = {
        "türkiye": "TR", "turkey": "TR", "tr": "TR",
        "abd": "US", "usa": "US", "amerika": "US", "amerika birleşik devletleri": "US", "united states": "US",
        "birleşik krallık": "GB", "uk": "GB", "ingiltere": "GB", "united kingdom": "GB", "scotland": "GB",
        "almanya": "DE", "germany": "DE",
        "fransa": "FR", "france": "FR",
        "italya": "IT", "italy": "IT", "i̇talya": "IT",
        "karadağ": "ME", "montenegro": "ME",
        "hollanda": "NL", "netherlands": "NL",
        "i̇spanya": "ES", "ispanya": "ES", "spain": "ES",
        "japonya": "JP", "japan": "JP",
        "avustralya": "AU", "australia": "AU"
    }
    return eslesme.get(ulke.strip().lower(), "TR")

def ilce_secimi_aktif_mi(ulke: str) -> bool:
    """Yalnızca Türkiye için ilçe seçimi aktiftir."""
    if not ulke:
        return True
    return ulke.strip().lower() in ("türkiye", "turkey", "tr")

def sehir_listesi_getir(ulke: str) -> List[str]:
    """Seçilen ülkenin şehir listesini döndürür."""
    if ulke in DUNYA_ULKELERI:
        return DUNYA_ULKELERI[ulke]["sehirler"]
    return sorted(list(TURKIYE_IL_ILCE.keys()))

def ilce_listesi_getir(ulke: str, sehir: str) -> List[str]:
    """Eğer Türkiye ise seçilen ilin ilçelerini, değilse boş liste döndürür."""
    if ilce_secimi_aktif_mi(ulke):
        return TURKIYE_IL_ILCE.get(sehir, ["Merkez"])
    return []

def konum_koordinat_bul(ulke: str, sehir: str, ilce: Optional[str] = None) -> Tuple[float, float, str]:
    """
    Ülke, şehir ve varsa ilçe bilgisine göre kesin coğrafi koordinatları (lat, lon) ve formatlı etiketi döner.
    """
    ulke = ulke or "Türkiye"
    sehir = sehir or "İstanbul"
    ilce = ilce or ""

    # 1. Türkiye İçi Arama
    if ilce_secimi_aktif_mi(ulke):
        etiket = f"{ilce} / {sehir}" if ilce and ilce != "Merkez" else f"{sehir} / Türkiye"
        arama = f"{ilce} {sehir}".strip()
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={arama}&count=5&language=tr&format=json"
            res = requests.get(url, timeout=5).json()
            if "results" in res and len(res["results"]) > 0:
                for r in res["results"]:
                    admin = r.get("admin1", "").lower()
                    if sehir.lower() in admin:
                        return r["latitude"], r["longitude"], etiket
                return res["results"][0]["latitude"], res["results"][0]["longitude"], etiket
        except Exception:
            pass
        return 41.0082, 28.9784, etiket

    # 2. Uluslararası Sabit Koordinatlar
    u_data = DUNYA_ULKELERI.get(ulke)
    if u_data and "koordinatlar" in u_data and sehir in u_data["koordinatlar"]:
        lat, lon = u_data["koordinatlar"][sehir]
        return lat, lon, f"{sehir} / {ulke}"

    # 3. Uluslararası Geocoding Fallback
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={sehir}&count=3&format=json"
        res = requests.get(url, timeout=5).json()
        if "results" in res and len(res["results"]) > 0:
            return res["results"][0]["latitude"], res["results"][0]["longitude"], f"{sehir} / {ulke}"
    except Exception:
        pass

    return 40.7128, -74.0060, f"{sehir} / {ulke}"
