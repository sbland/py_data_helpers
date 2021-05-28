import datetime
from data_helpers.time_data import get_julian_day, get_row_index


def test_get_row_index():
    row_index = get_row_index(0, 0)
    assert row_index == 0
    row_index = get_row_index(0, 1)
    assert row_index == 1
    row_index = get_row_index(1, 0)
    assert row_index == 24
    row_index = get_row_index(1, 1)
    assert row_index == 25


def test_get_julian_day():
    fmt = "%Y.%m.%d"
    ds = '2012.10.02'
    dt = datetime.datetime.strptime(ds, fmt)
    jd = get_julian_day(dt)
    assert jd == 276

    ds = '2012.01.01'
    dt = datetime.datetime.strptime(ds, fmt)
    jd = get_julian_day(dt)
    assert jd == 1

    ds = '2012.01.02'
    dt = datetime.datetime.strptime(ds, fmt)
    jd = get_julian_day(dt)
    assert jd == 2
