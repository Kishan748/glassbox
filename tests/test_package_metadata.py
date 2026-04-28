from __future__ import annotations

from importlib.metadata import version

import glassbox


def test_package_version_matches_alpha_release() -> None:
    assert glassbox.__version__ == "0.1.0a3"
    assert version("glassbox") == glassbox.__version__
