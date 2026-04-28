from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from glassbox.storage import Storage


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "glassbox.db"


@pytest.fixture
def storage(temp_db_path: Path) -> Generator[Storage, None, None]:
    store = Storage(temp_db_path)
    yield store
    store.close()
