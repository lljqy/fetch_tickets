import os
from datetime import datetime

from sqlalchemy import create_engine

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
BASE_DIR = os.environ.get('BASE_DIR', '')
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/crawler')


def time_print(msg: str) -> None:
    print(f"[{datetime.now().strftime(TIME_FORMAT)}] {msg}")
