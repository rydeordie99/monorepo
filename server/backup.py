import logging
import shutil
from pathlib import Path

from myutils.config import Setup

s = Setup("server_backup")

dir_path = Path("/etc/systemd/system/")

files = dir_path.glob("py*.*")

for file in files:
    shutil.copy(file, "/scratch/backup/timers")

logging.info("server backed up")

s.ping()
