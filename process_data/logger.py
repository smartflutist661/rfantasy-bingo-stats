"""
Created on Apr 21, 2024

@author: fred
"""
import logging

LOGGER = logging.getLogger("bingo-stats-generator")
for handler in LOGGER.handlers:
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
LOGGER.setLevel(logging.INFO)
