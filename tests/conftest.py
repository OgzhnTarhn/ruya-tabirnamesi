import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def jsonl_oku(yol: Path) -> list[dict]:
    with yol.open(encoding="utf-8") as dosya:
        return [json.loads(satir) for satir in dosya if satir.strip()]


@pytest.fixture
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture
def ornek_maddeler() -> list[dict]:
    return jsonl_oku(FIXTURES / "maddeler_ornek.jsonl")
