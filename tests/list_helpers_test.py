from data_helpers.list_helpers import offset


def test_offset():
    arr = [1, 2, 3, 4]
    updated_list = offset(arr, 1.5, 8)
    assert updated_list == [7.5, 0.5, 1.5, 2.5]
