"""
Centralized logging configuration
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO"):
    """Configure application-wide logging."""
    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log"),
        ],
    )
    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
