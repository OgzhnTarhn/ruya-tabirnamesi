# Test seti

`ruyalar_v1.jsonl`: her satır bir rüya. Şema: [docs/06, bölüm 1](../../docs/06-degerlendirme.md)
· kod: `ruya.schemas.TestOrnegi`.

- Yalnızca kendi rüyaların, LLM'e ürettirip elle düzelttiğin rüyalar ve lisansına uygun
  atıfla DreamBank raporları girer. Başkalarının rüyaları **izinsiz** girmez (docs/07, KVKK).
- Kendi rüyaların bulunduğu için repo özel kalmalı (TK-11).
- Hedef boyut: Aşama 1'de 20, Aşama 3 sonunda 40–50 rüya.
- Şu anki `ruyalar_v1.jsonl` tamamen sentetiktir; kullanıcının gözden geçirmesi ve
  `beklenen_maddeler` alanının doldurulması bekleniyor.
