from myutils.config import Setup

from .package import get_packages

s = Setup("tracker")

packages = get_packages()

for package in packages:
    if package.check_same():
        continue

    package.notify()

    if package.is_delivered:
        package.delete_package()
    else:
        package.update_package()

s.ping()
