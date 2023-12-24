from pathlib import Path
from typing import List
import pytest


def test_structure(structure):
    assert structure.representation() == structure.blueprint
