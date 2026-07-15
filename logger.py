import sys
from pathlib import Path
from datetime import datetime


class Logger:
    def __init__(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")

        self.file = open(log_dir / filename, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, text):
        if self.stdout is not None:
            self.stdout.write(text)

        self.file.write(text)

    def flush(self):
        if self.stdout is not None:
            self.stdout.flush()

        self.file.flush()