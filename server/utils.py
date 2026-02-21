import logging
import os
import re
import subprocess

from myutils.email import send_email

MAX_TEMP = 43


def run_command(command: str) -> str:
    commands = command.split()

    cmd = subprocess.Popen(commands, stdout=subprocess.PIPE)

    if cmd.stdout:
        return cmd.stdout.read().decode()
    return ""


def run_as_sudo(command: str) -> str:
    commands = command.split()

    cmd1 = subprocess.Popen(["echo", os.environ.get("SERVER_PASS", "")], stdout=subprocess.PIPE)
    cmd2 = subprocess.Popen(["sudo", "-S", *commands], stdin=cmd1.stdout, stdout=subprocess.PIPE)

    if cmd2.stdout:
        return cmd2.stdout.read().decode()
    return ""


def get_hdd_list() -> list[str]:
    output = run_command("lsblk -dn -o NAME")
    return [x for x in output.split("\n") if x.startswith("sd")]


def hdd_temperature() -> list[tuple[str, int]]:
    re_temp = re.compile(r"Temperature_Celsius.+ {4}(.+)")

    temps = []

    for hdd in get_hdd_list():
        command = f"smartctl -a /dev/{hdd}"

        output = run_as_sudo(command)

        searches = re_temp.search(output)
        temp = 0
        if searches:
            temp = int(searches.group(1).split()[0])

        if temp > MAX_TEMP:
            send_email(
                "ServerMonitor",
                f"High temperature [{temp}°C] on hard drive /dev/{hdd}",
                "Please check temp",
            )

        temps.append((hdd, temp))

    return temps


def zfs_health() -> str:
    output = run_as_sudo("zpool status -x").strip()

    logging.info(output)

    if "healthy" not in output:
        send_email("ServerMonitor", f"ZFS: {output}")

    return output
