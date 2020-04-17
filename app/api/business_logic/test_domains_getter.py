import pytest

from .domain_getter import TimeRange, WrongTimestampFormat


def test_time_range():
    from_ = "2020-04-16T11:39:40"
    to    = "2020-04-16T11:40:20"

    check_list = list(TimeRange(from_, to))

    assert len(check_list) == 41
    assert check_list[0] == "2020-04-16T11:39:40"
    assert check_list[3] == "2020-04-16T11:39:43"
    assert check_list[5] == "2020-04-16T11:39:45"
    assert check_list[10] == "2020-04-16T11:39:50"
    assert check_list[20] == "2020-04-16T11:40:00"
    assert check_list[30] == "2020-04-16T11:40:10"
    assert check_list[40] == "2020-04-16T11:40:20"

def test_wrong_time_format():
    from_ = "2020-04-16T11:39:40a"
    to    = "2020-04-16 T11:40:20"

    try:
        check_list = list(TimeRange(from_, to))
    except WrongTimestampFormat:
        assert True
        return

    assert False 