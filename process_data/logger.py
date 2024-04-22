"""
Created on Apr 21, 2024

@author: fred
"""

import logging
import sys
from logging import StreamHandler

LOGGER = logging.getLogger("bingo-stats-generator")
handler = StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
