import pytest

from .domain_getter import WrongTimestampFormat, DomainGetter


def test_wrong_time_format():
    from_ = "2020-04-16T11:39:40a"
    to    = "2020-04-16 T11:40:20"

    with pytest.raises(WrongTimestampFormat):
        test_domain_getter = DomainGetter(from_, to)

@pytest.mark.parametrize(
        ('from_', 'to', 'mask'),
        [("2020-04-16T11:39:40", "2020-04-16T11:40:20", "2020-04-16T11:*"), # h
        ("2020-04-20T11:40:40", "2020-04-20T11:41:20", "2020-04-20T11:4*"), #m
        ("2020-04-20T11:40:40", "2020-04-20T11:40:48", "2020-04-20T11:40:4*"), # s
        ("2020-04-20T11:39:40", "2020-04-21T11:40:20", "2020-04-2*"), # d
        ("2020-04-20T11:39:40", "2020-05-21T11:40:20", "2020-0*"), # m
        ("2020-04-20T11:39:40", "2021-04-21T11:40:20", "202*")] # y
    )
def test_get_mask(from_, to, mask):
    assert DomainGetter.get_mask(from_, to) == mask
