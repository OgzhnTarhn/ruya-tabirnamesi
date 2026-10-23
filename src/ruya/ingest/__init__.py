"""Kaynak ayrıştırıcıları: ham dosya → ``Madde`` kayıtları (data/interim/<kaynak>.jsonl).

Her ayrıştırıcı aynı arayüzü uygular::

    def ayristir(ham_dosya: Path) -> Iterator[Madde]

Ayrıştırıcılar deterministiktir ve LLM çağırmaz. Sembol atama ve çeviri ``enrich/`` işidir.
"""
