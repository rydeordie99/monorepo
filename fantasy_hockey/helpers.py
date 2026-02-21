import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from xml.etree import ElementTree as ET

import httpx
from myutils.date_util import today


class Position(StrEnum):
    BN = "BN"
    C = "C"
    LW = "LW"
    RW = "RW"
    D = "D"
    UTIL = "Util"
    G = "G"
    IR = "IR"
    IRPLUS = "IR+"


@dataclass
class Player:
    key: str
    name: str
    team: str
    primary_position: str
    current_position: str
    eligible_positions: list[str]
    status: str


def parse_xml(raw_xml: str) -> list[Player]:
    players = ET.fromstring(raw_xml).findall("./team/roster/players/player")
    roster = []
    for player in players:
        key_find = player.find("player_key")
        key = key_find.text if key_find is not None else ""
        name_find = player.find("name/full")
        name = name_find.text if name_find is not None else ""
        team_find = player.find("editorial_team_full_name")
        team = team_find.text if team_find is not None else ""
        primary_position_find = player.find("primary_position")
        primary_position = primary_position_find.text if primary_position_find is not None else ""
        current_position_find = player.find("selected_position/position")
        current_position = current_position_find.text if current_position_find is not None else ""
        eligible_positions = [str(x.text) for x in player.findall("eligible_positions/position")]

        status_find = player.find("status")
        status = status_find.text if status_find is not None else ""

        roster.append(
            Player(
                str(key),
                str(name),
                str(team),
                str(primary_position),
                str(current_position),
                eligible_positions,
                str(status),
            )
        )
    return roster


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def get_goalie_list() -> list[str]:
    r = httpx.get(
        f"https://www.rotowire.com/hockey/tables/projected-goalies.php?date={today}"
    ).json()
    goalies = []
    for x in r:
        goalies.extend((x["homePlayer"], x["visitPlayer"]))

    return goalies
