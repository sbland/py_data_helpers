import pytest
from typing import NamedTuple, List
from collections.abc import Sequence as CSequence
import typing
from enum import Enum

import numpy as np

from data_helpers.fill_np_array import fill_np_array_with_cls

from data_helpers.comparisons import are_equal_safe, compare_named_tuples, is_enum, is_iterable, tuples_are_equal


class DemoEnum(Enum):
    DEFAULT = "default"


def test_are_equal_safe_floats():
    assert are_equal_safe(1.2, 1.4) is False
    assert are_equal_safe(1, 1.0) is False
    assert are_equal_safe(1.2, 1.2) is True


def test_are_equal_safe_ints():
    assert are_equal_safe(1, 2) is False
    assert are_equal_safe(1, 1) is True


def test_are_equal_safe_nonetype():
    assert are_equal_safe(None, 2) is False
    assert are_equal_safe(None, None) is True


def test_are_equal_safe_numpy():
    a = np.zeros(5)
    b = np.full(5, 3)
    c = np.full(5, 3)
    d = np.full(6, 3)
    assert are_equal_safe(a, b) is False
    assert are_equal_safe(b, c) is True
    assert are_equal_safe(c, d) is False


def test_are_equal_safe_namedtuple():
    class A(NamedTuple):
        foo: int

    a = A(1)
    b = A(2)
    c = A(2)
    assert are_equal_safe(a, b) is False
    assert are_equal_safe(b, c) is True


def test_are_equal_safe_namedtuple_nested():
    class A(NamedTuple):
        foo: int

    class B(NamedTuple):
        bar: A
        roo: int = 1

    a = B(bar=A(1))
    b = B(bar=A(2))
    c = B(bar=A(2))
    d = B(bar=A(2), roo=4)
    assert are_equal_safe(a, b) is False
    assert are_equal_safe(b, c) is True
    assert are_equal_safe(c, d) is False


def test_are_equal_safe_namedtuple_nested_array():
    class A(NamedTuple):
        foo: int

    class B(NamedTuple):
        bar: List[A]
        roo: int = 1

    a = B(bar=[A(1)])
    b = B(bar=[A(2)])
    c = B(bar=[A(2)])
    d = B(bar=[A(2)], roo=4)
    assert are_equal_safe(a, b) is False
    assert are_equal_safe(b, c) is True
    assert are_equal_safe(c, d) is False


def test_are_equal_safe_namedtuple_nested_numpy():
    class A(NamedTuple):
        foo: int

    class B(NamedTuple):
        bar: List[A]
        roo: int = 1

    # def fill_args(*args, **kwargs):
    #     def apply(shape, cls):
    #         return fill_np_array_with_cls(shape, cls, *args, **kwargs)
    def fill_args(shape, cls):
        def apply(*args, **kwargs):
            return fill_np_array_with_cls(shape, cls, *args, **kwargs)
        return apply
    fill_args_demo = fill_args((1, 2, ), A)

    a = B(bar=fill_args_demo(foo=1))
    b = B(bar=fill_args_demo(foo=2))
    c = B(bar=fill_args_demo(foo=2))
    d = B(bar=fill_args_demo(foo=2), roo=4)
    assert are_equal_safe(a, b) is False
    assert are_equal_safe(b, c) is True
    assert are_equal_safe(c, d) is False


def test_compare_named_tuples():
    class A(NamedTuple):
        foo: int

    a = A(1)
    b = A(2)
    c = A(2)
    assert compare_named_tuples(a, b) == [('foo', False, 1, 2)]
    assert compare_named_tuples(b, c) == [('foo', True, 2, 2)]


def test_tuples_are_equal():
    class A(NamedTuple):
        foo: int
    a = A(1)
    b = A(2)
    c = A(2)
    assert tuples_are_equal(a, b) is False
    assert tuples_are_equal(b, c) is True


@pytest.mark.parametrize(['value', 'result'], [
    (type([1, 2, 3]), True),
    (type((1, 2, 3)), True),
    (typing.List, True),
    (typing.Tuple, True),
    (typing.Sequence, True),
    (type("a"), False),
    (type(1), False),
])
def test_is_iterable(value, result):
    assert is_iterable(value) == result


@ pytest.mark.parametrize(['value', 'result'], [
    (DemoEnum, True),
    (type(1), False),
    (type("a"), False),
    ("a", False),
])
def test_is_enum(value, result):
    assert is_enum(value) == result
