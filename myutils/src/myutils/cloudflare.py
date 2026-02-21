import logging
import socket
import sys
from urllib.error import URLError

import httpx

from myutils.config import Setup
from myutils.email import send_email

IPV4_URL = "https://ipv4.myip.wtf/text"
IPV6_URL = "https://ipv6.myip.wtf/text"


def check_if_ip_changed() -> None:
    s = Setup("cloudflare")
    ip6_new = ""
    try:
        ip4_new = httpx.get(IPV4_URL).text.strip()
    except URLError:
        logging.warning("Connection error")
        s.ping()
        sys.exit()

    try:
        ip6_new = httpx.get(IPV6_URL).text.strip()
    except OSError:
        logging.info("No IPv6 connectivity")

    try:
        ip4_old, ip6_old = s.read().split(",")
    except ValueError:
        s.write(f"{ip4_new},{ip6_new}")
        ip4_old = ip4_new
        ip6_old = ip6_new

    if ip4_new != ip4_old or ip6_new != ip6_old:
        logging.info("New IP address: %s, %s", ip4_new, ip6_new)

        isp = socket.gethostbyaddr(ip4_new)[0]

        send_email(
            "DDNS",
            f"DNS Updated: {socket.gethostname()}",
            f"ISP: {isp}<br><br>"
            f"IPv4: {ip4_new} (old: {ip4_old})<br>"
            f"IPv6: {ip6_new} (old: {ip6_old})",
        )

        s.write(f"{ip4_new},{ip6_new}")

    s.ping()
