import os
from datetime import datetime

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
BASE_DIR = os.environ.get('BASE_DIR', '')


def time_print(msg: str) -> None:
    print(f"[{datetime.now().strftime(TIME_FORMAT)}] {msg}")
