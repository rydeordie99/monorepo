import logging
import re

import httpx
from myutils.config import Setup
from myutils.database import Database
from myutils.email import send_email

from .app_db import apps
from .helpers import docker_version_check, get_key_by_path

s = Setup("version_check")
db = Database("host/version_check.db")

for app in apps:
    logging.info("Checking: %s", app["name"])
    db.add_table(app["name"], id="TEXT")
    old = db.get_items(app["name"])

    latest_version = html = subject = ""
    if "github_tag_url" in app:
        r_github = httpx.get(f"https://api.github.com/repos/{app['github_tag_url']}/tags").json()

        for tag in r_github:
            if tag["name"].startswith("archive"):
                continue
            if tag["name"].endswith("-RC1"):
                continue
            if tag["name"].endswith("-RC2"):
                continue
            latest_version = tag["name"]
            break

        if latest_version in old:
            continue

        html = "NO BODY<br><br>"
        html += f"https://github.com/{app['github_tag_url']}<br><br>"

        if "docker_url" in app:
            if not docker_version_check(app["docker_url"], latest_version):
                continue
            html += f"<br><br>https://hub.docker.com/r/{app['docker_url']}"

    elif "github_url" in app:
        r_github = httpx.get(
            f"https://api.github.com/repos/{app['github_url']}/releases/latest"
        ).json()

        latest_version = r_github["tag_name"]

        if latest_version in old:
            continue
        if r_github["prerelease"]:
            continue
        if "-rc" in latest_version:
            continue

        html = r_github["html_url"]

        if "docker_url" in app:
            if not docker_version_check(app["docker_url"], latest_version):
                continue
            html += f"<br><br>https://hub.docker.com/r/{app['docker_url']}"

    else:
        r = httpx.get(app["url"])

        if "dict_path" in app:
            latest_version = get_key_by_path(r.json(), app["dict_path"])
            if latest_version in old:
                continue
        else:
            re_pattern = re.compile(app["index_pattern"], re.DOTALL)
            matches = re_pattern.findall(r.text)
            if not matches:
                logging.error("no regex matches on index page")
                continue

            flag = False
            for match in matches[:2]:
                if flag:
                    flag = False
                if "page_pattern" in app:
                    latest_version = match[1].strip()
                    if latest_version in old:
                        break
                    page_url = app["url"] + match[0]
                    r_page = httpx.get(page_url).text
                    re_page = re.compile(app["page_pattern"], re.DOTALL)
                    searcher = re_page.search(r_page)
                    html = searcher.group(1) if searcher else r_page
                    html += "<br><br>" + page_url
                    flag = True
                else:
                    latest_version = match[0].strip()
                    if latest_version in old:
                        break
                    html = match[1]
                    page_url = app["url"]
                    html += "<br><br>" + page_url
                    flag = True
            if not flag:
                continue

        if "discourse_thread_url" in app:
            r2 = httpx.get(f"{app['discourse_thread_url']}.json").json()
            r3 = httpx.get(f"{app['discourse_thread_url']}/{r2['highest_post_number']}.json").json()
            latest_version_search = latest_version.split("-")[0]

            for post in r3["post_stream"]["posts"]:
                if latest_version_search in post["cooked"]:
                    html = post["cooked"]
                    html += "<br><br>" + latest_version
                    break

    subject = f"[{app['name']}] Release: {latest_version}"
    db.insert((latest_version,), app["name"])
    send_email("VersionCheck", subject, html)
