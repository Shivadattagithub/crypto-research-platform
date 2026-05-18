"""
Structured Logger
------------------
Configures application-wide logging with file and console output.
"""

import logging
import os
from datetime import datetime


def get_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    logger    = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    fmt       = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    fh        = logging.FileHandler(f"{log_dir}/platform.log")
    fh.setFormatter(fmt)
    ch        = logging.StreamHandler()
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
