"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - LOGGING SYSTEM
================================================================================
"""
import logging
import sys
from pathlib import Path

def get_logger(name: str = "EvMotoQA") -> logging.Logger:
    """Mengembalikan instance logger dengan format standar QA."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        log_file = Path(__file__).resolve().parent.parent / "reports" / "automation.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
