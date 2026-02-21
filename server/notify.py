import sys

from myutils.telegram import send_telegram

send_telegram(f"<b>Script Failure</b>\n\n{sys.argv[1]}")
