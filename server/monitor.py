from myutils.config import Setup

from .utils import hdd_temperature, zfs_health

s = Setup("server_monitor")

_ = hdd_temperature()
_ = zfs_health()

s.ping()
