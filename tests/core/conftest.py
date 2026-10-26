import pytest

from volsegtools import WorkingStore


@pytest.fixture
def working_store_path(tmp_path):
    """Return an isolated path for a local working store."""
    return tmp_path / "working_store"


@pytest.fixture
def working_store(working_store_path) -> WorkingStore:
    """Create a local working store inside pytest's temporary directory."""
    return WorkingStore(working_store_path)


@pytest.fixture
def memory_working_store() -> WorkingStore:
    """Create an in-memory working store."""
    return WorkingStore()
