import datetime
import logging
import random
import re
import sys
import time

import httpx
from myutils.config import Setup
from myutils.date_util import today

from .helpers import Position, get_goalie_list, parse_xml, strip_accents
from .xml_class import Xml
from .yahoo_api import Yahoo

setup = Setup("yahoo")

yahoo = Yahoo()

roster_raw = yahoo.get_roster()
roster_xml = re.sub(r' xmlns="[^"]+"', "", roster_raw)

xml = Xml()

players = parse_xml(roster_xml)

for player in players:
    # Do not touch IR players
    if player.status is not None:  # noqa: SIM102
        if player.status in {Position.IR, Position.IRPLUS}:
            continue

    if player:
        xml.update_player(player.key, Position.BN)

yahoo.update_roster(xml.to_str())

r = httpx.get("https://api.nhle.com/stats/rest/en/team").json()
team_list = {k["triCode"]: v["fullName"] for (k, v) in zip(r["data"], r["data"], strict=False)}

r = httpx.get(f"https://api-web.nhle.com/v1/schedule/{today}").json()

task_list = {}

if r["gameWeek"][0]["numberOfGames"] == 0:
    logging.info("No games today")
else:
    for game in r["gameWeek"][0]["games"]:
        try:
            home_team = team_list[strip_accents(game["awayTeam"]["abbrev"])]

            away_team = team_list[strip_accents(game["homeTeam"]["abbrev"])]
        except KeyError:
            logging.warning("Team does not exist, possible all-star games?")
            sys.exit()
        logging.info("home_team: %s, away_team: %s", home_team, away_team)
        for player in players:
            if player.team in {home_team, away_team}:
                if player.team in task_list:
                    continue

                game_time = datetime.datetime.fromisoformat(game["startTimeUTC"]).astimezone()
                task_list[player.team] = game_time
                logging.info("Creating task: %s for %s", player.team, game_time)

remaining_position = {
    "C": 2,
    "LW": 2,
    "RW": 2,
    "D": 3,
    "Util": 1,
    "G": 2,
    "IR": 1,
    "IR+": 1,
}

while task_list:
    time.sleep(3530)
    update_flag = False

    xml = Xml()

    now = datetime.datetime.now().astimezone()

    for team, game_time in task_list.copy().items():
        if now + datetime.timedelta(minutes=60) < game_time:
            continue

        goalies = get_goalie_list()

        for player in players:
            if player.current_position in {Position.IR, Position.IRPLUS}:
                continue

            if player.team != team:
                continue

            if player.status is not None:
                continue

            if player.primary_position == Position.G and player.name not in goalies:
                continue

            logging.info(
                "possible positions for %s are %s",
                player.name,
                player.eligible_positions,
            )

            util_flag = False
            if Position.UTIL in player.eligible_positions:
                player.eligible_positions.remove(Position.UTIL)
                util_flag = True
            if Position.IR in player.eligible_positions:
                player.eligible_positions.remove(Position.IR)
            if Position.IRPLUS in player.eligible_positions:
                player.eligible_positions.remove(Position.IRPLUS)

            random.shuffle(player.eligible_positions)

            new_position = None
            for position in player.eligible_positions.copy():
                player.eligible_positions.remove(position)
                if remaining_position[position] == 0:
                    continue

                new_position = position
                break

            if (new_position is None) and util_flag:
                if remaining_position[Position.UTIL] == 0:
                    continue
                new_position = Position.UTIL

            remaining_position[new_position] -= 1
            xml.update_player(player.key, new_position)
            update_flag = True

        task_list.pop(team)

    if update_flag:
        yahoo = Yahoo()
        yahoo.update_roster(xml.to_str())

setup.ping()
