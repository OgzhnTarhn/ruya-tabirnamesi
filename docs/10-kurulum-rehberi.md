# 10 · Kurulum Rehberi (Hafta 0)

> Durum: Taslak v0.2 · Tarih: 22 Ekim 2026 (Colab ve Drive'a göre güncellendi)
> Bu adımların çoğunu **senin** yapman gerekiyor: hesap açma, ödeme bilgisi, API anahtarı, token. Kodlu kısımları birlikte yapacağız.
> Ortamın genel resmi: [11-calisma-ortami-colab-drive.md](11-calisma-ortami-colab-drive.md)

## 1. Claude API hesabı [ZORUNLU]

1. **platform.claude.com** adresinde bir hesap aç. Eski adresi console.anthropic.com idi; yönlendirme ya da arayüz değişmiş olabilir.
2. Faturalandırma (Billing) bölümünden bir ödeme yöntemi ekle ve küçük bir kredi yükle. 5–10 $ başlangıç için yeterli.
3. **Harcama limiti koy:** Limitler (Limits) bölümünden aylık bir tavan belirle. Önerim 10 $. Menünün yeri değişmiş olabilir; bulamazsan bana yaz.
4. API Keys bölümünden `ruya-tabirnamesi` adında yeni bir anahtar oluştur.
5. **Anahtarı hiçbir yere yapıştırma:** sohbete, koda, GitHub'a, notebook hücresine. Yalnızca Colab Secrets'a gireceksin (4. adım).

## 2. GitHub repo [ÖNERİLEN]

1. github.com'da `ruya-tabirnamesi` adında yeni bir repo oluştur. Görünürlüğü **Private** seç. README, .gitignore ve lisans ekleme; onlar hazır.
2. Bilgisayardaki repoyu ona bağlayıp push et. İstersen bağlantı komutlarını ben hazırlarım, push'u sen yaparsın.
3. **Repo özelse Colab için okuma tokenı:** GitHub → Settings → Developer settings → Fine-grained tokens yolunu izle. Yalnızca bu repoya erişimi olan, **Contents: Read-only** yetkili bir token oluştur. Token'ı da yalnızca Colab Secrets'a gireceksin.

## 3. Google Drive klasörü [ZORUNLU]

1. Drive'da, **Drive'ım** (My Drive) altında `ruya-tabirnamesi` adında bir klasör oluştur. Alt klasörleri ilk notebook kendisi açacak.
2. Bu klasörü **kimseyle paylaşma**. İçinde lisanslı veri ve ileride kendi rüyaların olacak.
3. Bilgisayarına Drive masaüstü uygulaması kurman gerekmez. Veri yalnızca Colab üzerinden okunup yazılacak.

## 4. Colab Secrets [ZORUNLU]

1. colab.research.google.com adresinden yeni bir notebook aç.
2. Sol kenar çubuğundaki **anahtar simgesine (Secrets)** tıkla ve şunları ekle:
   - `ANTHROPIC_API_KEY`: 1. adımdaki anahtar
   - `GITHUB_TOKEN`: 2. adımdaki token (yalnızca repo özelse)
3. Notebook'ların bu gizli bilgilere erişimini, ilk çalıştırmada açılan izin penceresinden onayla.

Secrets Google hesabına bağlıdır. Bütün notebook'larında kullanabilirsin ve notebook paylaşılsa bile değerleri görünmez.

## 5. Bilgisayarda (yalnızca kod yazmak için)

Bilgisayarda veri ya da ağır bir paket olmayacak. Kodu yazmak ve hafif testleri çalıştırmak için şunlar yeterli:

- **VS Code** ve **Git** (ikisi de kurulu).
- **İsteğe bağlı: uv.** Verisiz birim testlerini ve ruff denetimini bilgisayarda hızlıca çalıştırmak istersen kur:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

uv kurmazsan testleri yalnızca Colab'de çalıştırırsın, bu da sorun değil.

## 6. Elle doğrulanacaklar (10 dakika)

- [ ] [Zenodo'daki OpenITI kaydını](https://zenodo.org/records/17767721) aç ve lisansın CC BY-NC-SA 4.0 olduğunu gör. Atıf künyesi sonra `docs/KAYNAKLAR.md` dosyasına eklenecek.
- [ ] İlk Colab oturumunda bir hücrede `!python --version` ve `!nvidia-smi` komutlarını çalıştır. Python sürümünü ve GPU durumunu not et. GPU için: Çalışma zamanı → Çalışma zamanı türünü değiştir → T4 GPU.
