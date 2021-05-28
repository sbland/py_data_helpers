from data_helpers.functional_helpers import fp_while, fp_while_i


def test_fp_while():
    out = fp_while(lambda x: x < 5, lambda x: x + 1, 1)
    assert out == 5
    out = fp_while(lambda x: x < 5, lambda x: x + 1, 1, 3)
    assert out == 4


def test_fp_while_i():
    out = fp_while_i(lambda x, i: x < 5 and i < 8, lambda x, i: (x + 1, x + 2), (1, 0))
    assert out == (5, 6)
