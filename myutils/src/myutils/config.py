import argparse
import contextlib
import logging.config
import sqlite3

import httpx

from myutils.database import Database


class Setup:
    def __init__(self, name: str) -> None:
        self.name = name
        self.db: Database | None = None
        self.args: argparse.Namespace | None
        self.log_setup()

    def log_setup(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("-debug", action="store_true")
        parser.add_argument("-command", help="Provide command on/off week/month etc. level")
        parser.add_argument("args", nargs=argparse.REMAINDER)
        self.args, _ = parser.parse_known_args()

        loglevel = logging.DEBUG if self.args.debug else logging.INFO
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {"format": "[%(levelname).1s] %(module)s:%(lineno)s  %(message)s"}
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {"": {"level": loglevel, "handlers": ["console"]}},
        }
        logging.config.dictConfig(logging_config)

    def db_setup(self, **cols: str) -> Database:
        db = Database(f"host/{self.name}.db")
        if cols:
            db.add_table(self.name, **cols)
        else:
            db.add_table(self.name, id="TEXT")
        return db

    def read(self) -> str:
        if not self.db:
            self.db = self.db_setup()
        try:
            item = self.db.get_items()[0]
        except sqlite3.OperationalError:
            item = ""
        return item

    def read_line(self) -> list[str] | str:
        if not self.db:
            self.db = self.db_setup()
        try:
            items = self.db.get_items()
        except sqlite3.OperationalError:
            items = ["", ""]
        return items

    def write(self, data_to_write: str) -> None:
        if self.db:
            self.db.remove()
            self.db.insert((data_to_write,))

    def write_line(self, data_to_write: str) -> None:
        if self.db:
            self.db.insert((data_to_write,))

    def ping(self, slug: str | None = None) -> None:
        if slug is None:
            pass
        else:
            httpx.get(f"https://status.hstia.com/api/push/{slug}?status=up&msg=OK&ping=")
        with contextlib.suppress(AttributeError):
            if self.db:
                self.db.close()
