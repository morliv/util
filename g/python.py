#!/usr/bin/env python3

import os
from pathlib import Path, PurePath
from IPython import embed

from drive import *


os.chdir(Path.home() / 'util/g')
embed()

