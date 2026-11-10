import os
import tempfile
from pathlib import Path

# Osobna baza dla testów – musi być ustawiona przed importem database/main
_tmp_dir = tempfile.mkdtemp(prefix="housing-api-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp_dir) / 'test.db'}"
