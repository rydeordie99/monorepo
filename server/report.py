import re
from io import StringIO

from myutils.config import Setup
from myutils.email import send_email

from .utils import hdd_temperature, run_as_sudo, run_command, zfs_health

s = Setup("server_report")

body = StringIO()

uptime_output = run_command("uptime")
body.write(f"<b>Up Time:</b><br>{uptime_output}<br><br>")

free_output = run_command("free -m")
mem = free_output.split()
mem_percent = f"{int(mem[8]) / int(mem[7]):.1%}"
body.write(
    f"<b>Memory Usage</b><br>Used:{mem[8]}<br>Total:{mem[7]}<br>Used %:{mem_percent}<br><br>"
)

df_output = run_command("df")
re_df = re.compile(r"/dev/nvme0n1p2.+\s(\d+%)")
df_search = re_df.search(df_output)
disk_percent = df_search.group(1) if df_search else "N/A"
body.write(f"<b>Main Disk Usage:</b> {disk_percent}<br><br>")

zfs_status = zfs_health()
body.write(f"<b>ZFS Status:</b> {zfs_status}<br>")

zfs_space = run_as_sudo("zfs list pool/main -H").split("\t")
body.write(f"<b>Used:</b> {zfs_space[1]}<br>")
body.write(f"<b>Free:</b> {zfs_space[2]}<br><br>")

temps = hdd_temperature()
body.write("<b>Hard drive temperatures:</b><br>")
for temp in temps:
    body.write(f"/dev/{temp[0]}: {temp[1]}°C<br>")

send_email("ServerReport", "Server Report", body.getvalue())

s.ping()
