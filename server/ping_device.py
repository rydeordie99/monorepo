import os
import subprocess
import time
from dataclasses import dataclass

from myutils.config import Setup

s = Setup("ping_device")


@dataclass
class Device:
    name: str
    ip: str
    uptime_hash: str


DEVICES = [Device(*d.split(",")) for d in os.environ.get("PING_DEVICES", "").split(":")]

for device in DEVICES:
    time.sleep(2)
    if subprocess.call(("ping", "-c", "1", device.ip)) == 0:
        s.ping(device.uptime_hash)
