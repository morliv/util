#!/usr/bin/env python3
import os
from pathlib import Path
from IPython import embed

import drive
os.chdir(Path.home() / 'util/g')
embed()
