# Görev

Bir rüya tabiri sisteminin getirme adımını değerlendiriyorsun. Sana bir rüya metni, o rüyadaki
**bir sembol** ve tabirnamelerden numaralı aday maddeler verilir. Her maddenin, bu sembolü
rüyadaki anlamıyla **yorumlamak için işe yarayıp yaramadığına** karar verirsin.

Rüyayı yorumlamazsın; yalnız hangi maddelerin ilgili olduğunu seçersin.

# Ölçüt

Bir madde şu durumda **ilgilidir**:

- Sembolün kendisini anlatıyor: "Rüyada balık görmek…" maddesi `balık` için ilgilidir.
- Sembolün rüyadaki hâline yakın bir durumu anlatıyor (ör. rüyada "berrak su" varsa suyun
  berraklığından söz eden madde).
- Madde uzun ve birçok konuyu karıştırıyor olsa bile, bu sembolü yorumlayan bir cümle içeriyor.

Şu durumda **ilgili değildir**:

- Başka bir şeyi anlatıyor ve sembolün adı yalnız geçerken anılıyor.
- Sözcük benzerliğinden gelmiş, anlamı başka (`bilek` için `bilezik`, `yüz` (surat) için
  `yüz` (sayı)).
- Sembolün rüyadaki rolüyle ilgisiz, çok özel bir durumu anlatıyor ve sembolün genel
  anlamını hiç vermiyor.

Emin değilsen ilgili sayma. Hiçbiri ilgili değilse boş liste dön.

# Çıktı

Yalnız şu şemaya uyan JSON yaz:

```json
{"ilgili": [1, 4]}
```

`ilgili`: ilgili maddelerin numaraları, artan sırada.
