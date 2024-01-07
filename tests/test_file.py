from pathlib import Path
from typing import List


def test_structure(structure):
    assert structure.representation() == structure.blueprint
