from pathlib import Path

import pytest

from px4_dataset_builder.utils.synthetic_ulog import generate_synthetic_ulog


@pytest.fixture
def synthetic_ulog(tmp_path: Path) -> Path:
    return generate_synthetic_ulog(tmp_path / "synthetic.ulg")
