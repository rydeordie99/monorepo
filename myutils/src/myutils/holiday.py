import calendar
import datetime

VICTORIA_DAY_END = 24
VICTORIA_DAY_START = 18
THANKSGIVING_START = 8
THANKSGIVING_END = 14
FIRST_WEEK = 7
REMEMBRANCE_DAY = 11
CHRISTMAS_DAY = 25
MAX_DAYS = 31


def _get_holiday(date_test: datetime.date) -> str:  # noqa: PLR0911
    if date_test.month == calendar.JANUARY and date_test.day == 1:
        return "New Year's Day"
    if date_test.month == calendar.FEBRUARY and date_test.weekday() == calendar.MONDAY:
        three_weeks_ago = date_test - datetime.timedelta(21)
        two_weeks_ago = date_test - datetime.timedelta(14)
        if two_weeks_ago.month == calendar.FEBRUARY and three_weeks_ago.month == calendar.JANUARY:
            return "Alberta Family Day"
    if date_test.month in {calendar.MARCH, calendar.APRIL} and _is_good_friday(date_test):
        return "Good Friday"
    if (
        date_test.month == calendar.MAY
        and VICTORIA_DAY_START <= date_test.day <= VICTORIA_DAY_END
        and date_test.weekday() == calendar.MONDAY
    ):
        return "Victoria Day"
    if date_test.month == calendar.JULY and date_test.day == 1:
        return "Canada Day"
    if (
        date_test.month == calendar.SEPTEMBER
        and date_test.day <= FIRST_WEEK
        and date_test.weekday() == calendar.MONDAY
    ):
        return "Labour Day"
    if (
        date_test.month == calendar.OCTOBER
        and THANKSGIVING_START <= date_test.day <= THANKSGIVING_END
        and date_test.weekday() == calendar.MONDAY
    ):
        return "Thanksgiving Day"
    if date_test.month == calendar.NOVEMBER and date_test.day == REMEMBRANCE_DAY:
        return "Remembrance Day"
    if date_test.month == calendar.DECEMBER and date_test.day == CHRISTMAS_DAY:
        return "Christmas Day"
    return ""


def _is_good_friday(date_test: datetime.date) -> bool:
    year = date_test.year
    a = year % 19
    b = year % 4
    c = year % 7
    d = (19 * a + 24) % 30
    e = ((2 * b) + (4 * c) + (6 * d) + 5) % 7

    day_in_march = 22 + d + e

    special_years = (1954, 1981, 2049, 2076)
    if year in special_years:
        day_in_march -= 7

    if day_in_march > MAX_DAYS:
        easter_date = datetime.date(year, calendar.APRIL, day_in_march - MAX_DAYS)
    else:
        easter_date = datetime.date(year, calendar.MARCH, day_in_march)

    good_friday_date = easter_date - datetime.timedelta(days=2)
    return date_test == good_friday_date


def is_it_observed_holiday(date_test: datetime.datetime | datetime.date) -> str | bool:
    if isinstance(date_test, datetime.datetime):
        date_test = date_test.date()

    if date_test.weekday() in {calendar.SATURDAY, calendar.SUNDAY}:
        return False

    if date_test.weekday() == calendar.MONDAY:
        for i in (2, 1):
            if holiday_check := _get_holiday(date_test - datetime.timedelta(i)):
                return f"{holiday_check} (Observed)"

    return holiday_check if (holiday_check := _get_holiday(date_test)) else False
