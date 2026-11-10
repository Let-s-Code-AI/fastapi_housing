import os
import tempfile
from pathlib import Path

# Osobna baza dla testów – musi być ustawiona przed importem database/main
_tmp_dir = tempfile.mkdtemp(prefix="housing-api-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp_dir) / 'test.db'}"

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _fresh_db():
    """Pusta baza na start każdej sesji pytest.

    mutmut wywołuje pytest.main() wiele razy w jednym procesie, więc plik bazy
    z poprzedniego przebiegu by przetrwał i zepsuł asercje na liczbę wierszy.
    """
    from database import Base, engine
    import models  # noqa: F401 – rejestruje tabele w Base.metadata

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
