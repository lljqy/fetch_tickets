import os
import sys
from pathlib import Path

BASE_DIR = str(Path(sys.argv[0]).absolute().parent)
sys.path.append(BASE_DIR)
os.environ.setdefault('BASE_DIR', BASE_DIR)

if __name__ == '__main__':
    from apps.qq.spider import QQProcessor
    from apps._12306.spider import TicketProcessor
    # from apps.xc.spider import CTripProcessor

    processor = TicketProcessor()
    # processor = QQProcessor()
    # processor = CTripProcessor(js_path=r"F:\develop\python\github\fetch_tickets\apps\xc\js\test_ab.js")
    processor.run()
