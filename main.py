import os
import sys
from pathlib import Path

BASE_DIR = str(Path(sys.argv[0]).parent)
sys.path.append(BASE_DIR)
os.environ.setdefault('BASE_DIR', BASE_DIR)

if __name__ == '__main__':
    from apps._12306.spider import TicketProcessor

    tp = TicketProcessor()
    tp.run()
