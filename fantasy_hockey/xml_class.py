# type: ignore[attr-defined]

from xml.etree import ElementTree as ET

from myutils.date_util import today


class Xml:
    def __init__(self) -> None:
        self.root = ET.Element("fantasy_content")
        self.d = None

        self.create_skeleton()

    def create_skeleton(self) -> None:
        a = ET.SubElement(self.root, "roster")
        b = ET.SubElement(a, "coverage_type")
        b.text = "date"
        c = ET.SubElement(a, "date")
        c.text = str(today)
        self.d = ET.SubElement(a, "players")

    def update_player(self, player_key: str, position: str) -> None:
        e = ET.SubElement(self.d, "player")
        f = ET.SubElement(e, "player_key")
        f.text = player_key
        g = ET.SubElement(e, "position")
        g.text = position

    def to_str(self) -> str:
        return ET.tostring(self.root, encoding="unicode")
