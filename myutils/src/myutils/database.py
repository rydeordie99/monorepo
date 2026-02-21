import sqlite3
from itertools import chain


class Database:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.con = sqlite3.connect(db_name)
        self.cur = self.con.cursor()
        if "/" in db_name:
            self.table_name = db_name.split("/", maxsplit=1)[-1].removesuffix(".db")
        else:
            self.table_name = db_name

    def _table_name_check(self, table_name: str) -> None:
        if table_name != "":
            self.table_name = table_name

    def add_table(self, table_name: str = "", **columns: str) -> None:
        self._table_name_check(table_name)
        cols = ", ".join(f"{col_name} {col_type}" for col_name, col_type in columns.items())

        self.con.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} ({cols})")

    def insert(self, data_in: tuple, table_name: str = "") -> None:
        self._table_name_check(table_name)
        self.cur.execute(f"INSERT INTO {self.table_name} VALUES(?)", data_in)
        self.con.commit()

    def insert_from_web(self, data_in: dict, table_name: str = "") -> None:
        self._table_name_check(table_name)
        self.cur.execute(
            f"INSERT INTO {self.table_name} {tuple(data_in.keys())} VALUES(?)",
            str(tuple(chain.from_iterable(data_in.values()))),
        )
        self.con.commit()

    def remove(self, table_name: str = "", where: int = 1) -> None:
        self._table_name_check(table_name)
        self.cur.execute(f"DELETE FROM {self.table_name} WHERE {where}")
        self.con.commit()

    def get_columns(self, table_name: str = "") -> list[str]:
        self._table_name_check(table_name)
        self.cur.execute(f"SELECT * FROM {self.table_name}")
        return [x[0] for x in self.cur.description]

    def get_items(self, table_name: str = "", where: int = 1) -> str | list:
        self._table_name_check(table_name)
        items = self.cur.execute(f"SELECT * FROM {self.table_name} WHERE {where}")
        self.con.commit()

        items = list(items)

        try:
            return [x[0] for x in items] if len(items[0]) == 1 else items
        except IndexError:
            return [""]

    def close(self) -> None:
        self.con.close()
