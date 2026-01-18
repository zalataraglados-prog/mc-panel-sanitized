import logging
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "backend.log")

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    return logger


def log_action(user: str, action: str, details: str) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as handle:
        handle.write(f"{datetime.utcnow().isoformat()} {user} {action} {details}\n")
