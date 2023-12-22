from pathlib import Path
from typing import List
import pytest

import file
from file import Structure, File, Dir
from util.iterable import Comparative
from util.test import TestCase


@pytest.mark.parametrize('blueprint', [
    ['1'],
    ['1', '2'],
    [[]],
    [[], []],
    [['1']],
    [['1'], ['2']],
    [['1', '2'], ['3', '4']],
    [[], '1']
])
def test_structure(blueprint: list):
    s = Structure(blueprint)
    assert s.representation() == blueprint
    s.clean()
