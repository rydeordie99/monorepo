import datetime
import platform

date_modifier = "#" if platform.system() == "Windows" else "-"

date_fmt = f"%B %{date_modifier}d, %Y"

now = datetime.datetime.now().astimezone()
today = now.date()
last_month = today.replace(day=1) - datetime.timedelta(days=1)
last_month_range = (last_month.replace(day=1), last_month)
next_week = now + datetime.timedelta(7)
