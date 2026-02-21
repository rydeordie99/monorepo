from myutils.config import Setup
from myutils.date_util import now
from myutils.email import send_email

s = Setup("email_ping")

send_email("ServerPing", f"OK - {now}", f"Server up on {now}")

s.ping()
