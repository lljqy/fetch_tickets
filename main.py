import sys
from pathlib import Path

if __name__ == '__main__':
    PROJECT_PATH = str(Path(__file__).absolute().parent)
    sys.path.append(PROJECT_PATH)
    from core.core import TicketProcessor

    tp = TicketProcessor()
    tp.run()
