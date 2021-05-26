"""Other utility functions"""

from math import isclose
from typing import List


def PLF_value(points: List[List[float]], x: float) -> float:
    """Calculate the value of a piecewise linear function at a particular x value.

    Given an array of points (2xN) which describe a piecewise linear function,
    this function gets the y value for the given x value.  Values before/after
    the range of the function are set to the first/last y value respectively.
    Within the range of the function, zero-width segments are ignored so that
    discontinuous functions can be defined - be aware that the the value at the
    shared x value will come from the first of the two segments that share it.

    real, dimension(: , : ), intent( in ) : : points
    real, intent(in ) : : x
    real: : y
    """
    # TODO: sanity-check points: should be size 2 in first dimension, and
    #       x values should never decrease.

    n = len(points[1]) - 1
    if x < points[0][0]:
        y = points[1][0]
    elif x > points[0][n]:
        y = points[1][n]
    else:
        bx = points[0][0]
        by = points[1][0]

        for i in range(1, n + 1):
            ax = bx
            ay = by
            bx = points[0][i]
            by = points[1][i]

            # Skip zero-width pieces(this should be equivalent to an # equality check,
            # but checking floating point equality is evil # and the compiler warns about it)
            if isclose(abs(ax - bx), 0.0):
                continue

            if (x <= bx):
                y = ay + (by - ay) * ((x - ax) / (bx - ax))
                break
    return y
