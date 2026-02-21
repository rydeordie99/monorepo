import os
from typing import Unpack

import httpx


class Api:
    def __init__(self, local: bool = False) -> None:
        if local:
            self.BASE_URL = "http://127.0.0.1:8000"
            self.headers = {"Authorization": "Token INSECURE_LOCAL_KEY"}
        else:
            self.BASE_URL = os.environ.get("INTERNAL_API_URL")
            self.headers = {"Authorization": f"Token {os.environ.get('INTERNAL_API_KEY')}"}

    def request(self, path: str, **kwargs: Unpack[tuple]) -> dict:
        return httpx.get(f"{self.BASE_URL}{path}", **kwargs, headers=self.headers).json()
