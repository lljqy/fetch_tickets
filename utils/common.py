import os
from datetime import datetime

from .constants import TIME_FORMAT

BASE_DIR = os.environ.get('BASE_DIR')


def _time_print(msg: str) -> None:
    print(f"[{datetime.now().strftime(TIME_FORMAT)}] {msg}")
