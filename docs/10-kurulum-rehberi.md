# 10 · Kurulum Rehberi (Hafta 0)

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026
> Bu adımların çoğunu **senin** yapman gerekiyor: hesap açma, ödeme bilgisi, API anahtarı. Kodlu kısımları birlikte yapacağız.

## 1. Claude API hesabı [ZORUNLU]

1. **platform.claude.com** adresine git ve bir hesap aç. (Eski adresi console.anthropic.com idi. Yönlendirme ya da arayüz değişmiş olabilir.)
2. Faturalandırma (Billing) bölümünden bir ödeme yöntemi ekle ve küçük bir kredi yükle. 5–10 $ başlangıç için yeterli.
3. **Harcama limiti koy:** Limitler (Limits) bölümünden aylık bir tavan belirle. Önerim 10 $. Menünün yeri değişmiş olabilir; bulamazsan bana yaz.
4. API Keys bölümünden yeni bir anahtar oluştur. Adı `ruya-tabirnamesi` olsun.
5. **Anahtarı hiçbir yere yapıştırma:** sohbete, koda, GitHub'a. Yalnızca proje klasöründeki `.env` dosyasına yazacaksın (aşağıda).

## 2. GitHub özel repo [ÖNERİLEN]

1. github.com'da yeni bir repo oluştur: ad `ruya-tabirnamesi`, görünürlük **Private**. README, .gitignore ya da lisans ekleme; onları biz hazırlıyoruz.
2. Bağlantı adresini bana söylersen yerel repoyu ona bağlarım. Uzak repoya push yalnızca sen istediğinde yapılır.

## 3. uv ve Python 3.12

PowerShell'de uv'yi kur (resmî kurulum betiği):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Alternatif olarak `winget install --id=astral-sh.uv -e` de kullanılabilir. Kurulumdan sonra terminali kapatıp açman ve şu komutla kontrol etmen gerekiyor:

```powershell
uv --version
```

Python 3.12'yi ayrıca kurmana gerek yok. Projeyi başlatırken uv onu kendisi indirecek (`uv python install 3.12`).

## 4. `.env` dosyası

Proje kökünde `.env.example` dosyası olacak. Onu `.env` adıyla kopyalayıp doldur:

```
ANTHROPIC_API_KEY=buraya-anahtarin
HF_HOME=C:\ruya-tabirnamesi\.cache\hf
RUYA_LLM_CACHE=on
RUYA_GECMIS=off
```

`.env` git'e eklenmez, çünkü `.gitignore` dosyasında yer alıyor.

## 5. Elle doğrulanacaklar (10 dakika)

- [ ] [Zenodo'daki OpenITI kaydını](https://zenodo.org/records/17767721) aç ve lisansın CC BY-NC-SA 4.0 olduğunu gör. Atıf künyesi sonra `docs/KAYNAKLAR.md` dosyasına eklenecek.
- [ ] Ekran kartını kontrol et: Görev Yöneticisi'nde Performans sekmesini aç, GPU bölümüne bak. Model adını ve "Ayrılmış GPU belleği" değerini bana yaz (açık soru S2).

## 6. Pip ile kurulum (uv sorun çıkarırsa)

```powershell
py -3.12 -m venv .venv
```

Sonra `.venv\Scripts\Activate.ps1` ile ortamı etkinleştir ve `pip install -e .` ile kur. Ayrıntıları kodlama başladığında ekleyeceğiz.
