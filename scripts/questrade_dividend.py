import datetime
import os

from myutils.config import Setup
from myutils.date_util import date_fmt, now
from myutils.email import send_email

from .questrade_util import Questrade

s = Setup("questrade")

accounts = os.environ.get("QUESTRADE_ACCOUNTS", "").split(",")

yesterday = (now - datetime.timedelta(1)).date()

start_time = f"{yesterday}T00:00:00-05:00"
end_time = f"{yesterday}T23:59:59-05:00"

questrade = Questrade()

for account in accounts:
    r_activity = questrade.get_activity(account, start_time, end_time)

    for activity in r_activity["activities"]:
        if activity["type"] == "Dividends":
            trade_date = datetime.datetime.strptime(
                activity["tradeDate"][:-13], "%Y-%m-%dT%H:%M:%S"
            ).astimezone()

            body = activity["description"]

            amount = "${:,.2f}".format(activity["netAmount"])

            subject = (
                f"{activity['symbol']} - {activity['currency']} {amount} on {trade_date:{date_fmt}}"
            )

            send_email("DividendNotify", subject, body)

s.ping()
