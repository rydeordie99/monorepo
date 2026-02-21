import re
import secrets
import sqlite3
import string

from myutils.database import Database


def generate_password() -> str:
    chars = string.ascii_letters + string.digits
    special_chars = "_!/?"
    length = 12

    while True:
        password = "".join([secrets.choice(chars) for _ in range(length - 1)])
        password += secrets.choice(special_chars)
        if (
            any(s.islower() for s in password)
            and any(s.isupper() for s in password)
            and any(s.isdigit() for s in password)
        ):
            break

    return password


def get_user_agent() -> str:
    try:
        db = Database("../host/user_agent.db")
        return db.get_items()[0]
    except sqlite3.OperationalError:
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
        )


def clean_phone_number(dirty_phone_number: str) -> str:
    phone_number = (
        dirty_phone_number.replace("+1", "")
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    return phone_number.strip()


def clean_filename(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s\.-]", "", text)
