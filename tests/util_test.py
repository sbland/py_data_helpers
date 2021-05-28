from data_helpers.util import PLF_value


def test_PLF_value():
    points = [
        [1, 2, 3, 4],
        [0.0, 0.8, 1.5, 1.9]
    ]
    y = [PLF_value(points, x) for x in [0, 1, 1.5, 3.5, 4, 4.5]]
    assert y == [0.0, 0.0, 0.4, 1.7, 1.9, 1.9]
