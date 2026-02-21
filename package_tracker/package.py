import datetime
import logging
from dataclasses import dataclass

from myutils.date_util import date_modifier, now
from myutils.telegram import send_telegram

from .internal_api import Api
from .providers import function_dict

api = Api()


@dataclass
class Package:
    carrier_id: int
    db_id: int
    package_id: str
    description: str
    timestamp_old: datetime.datetime
    timestamp_new: datetime.datetime | None = None
    status: str = ""
    location: str = ""
    is_delivered: bool = False
    url: str = ""

    def check_same(self) -> bool:
        logging.info("Processing: %s", self.package_id)
        self.timestamp_new, self.status, self.location, self.is_delivered, self.url = function_dict[
            self.carrier_id
        ](self.package_id)
        logging.info("new: %s, old: %s", self.timestamp_new, self.timestamp_old)
        return self.timestamp_new == self.timestamp_old

    def notify(self) -> None:
        date_nice = f"{self.timestamp_new:%H:%M, %B %{date_modifier}d}".lstrip("0")
        send_telegram(
            f"<b>{self.description}</b>\n\n{self.location} at {date_nice}.\n\n"
            f"{self.status}\n\n{self.url + self.package_id}\n-------"
        )

    def delete_package(self) -> None:
        logging.info("Deleting: %s", self.package_id)
        _ = api.request(f"/script/api/package/{self.db_id}/", method="DELETE")

    def update_package(self) -> None:
        logging.info("Updating: %s", self.package_id)
        if self.timestamp_new is None:
            self.timestamp_new = now
        data = {"timestamp": self.timestamp_new.isoformat(), "status": self.status}
        _ = api.request(f"/script/api/package/{self.db_id}/", json=data, method="PATCH")


def get_packages() -> list[Package]:
    r = api.request("/script/api/package/")
    packages = []
    for package in r:
        if package["timestamp"] is None:
            timestamp = datetime.datetime(2020, 1, 1).astimezone()
        else:
            timestamp = datetime.datetime.fromisoformat(package["timestamp"])
        packages.append(
            Package(
                package["carrier"],
                package["id"],
                package["package_id"],
                package["description"],
                timestamp,
            )
        )
    return packages
