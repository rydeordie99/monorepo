import datetime

from myutils.holiday import is_it_observed_holiday


def test_correct_nonobserved_holiday():
    date_test = datetime.datetime(2022, 1, 1).astimezone()
    result = is_it_observed_holiday(date_test)
    assert result is False


def test_correct_observed_holiday_name():
    date_test = datetime.datetime(2022, 1, 3).astimezone()
    result = is_it_observed_holiday(date_test)
    assert result == "New Year's Day (Observed)"
