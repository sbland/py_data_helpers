"""Generic helpers related to time data"""

from datetime import date


def get_row_index(day: int, hour: int) -> int:
    """Gets the row index based on day and hour assuming row per hour"""
    row_index: int = (day * 24) + hour
    return row_index


def get_julian_day(dt: date) -> int:
    tt = dt.timetuple()
    return tt.tm_yday
