"""
Centralized logging configuration using loguru.
Import `logger` from this module anywhere in the backend.
"""

import sys
from pathlib import Path

from loguru import logger

from backend.config import settings

# Remove default handler so we control formatting
logger.remove()

# Console logging
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

# File logging (rotates at 10 MB, keeps 5 backups)
log_path = Path(settings.log_file)
log_path.parent.mkdir(parents=True, exist_ok=True)
logger.add(
    settings.log_file,
    level=settings.log_level,
    rotation="10 MB",
    retention=5,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

__all__ = ["logger"]
