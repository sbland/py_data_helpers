
from dataclasses import dataclass
from typing import Any, NamedTuple

from data_helpers.fill_np_array import fill_np_array_with_cls
from data_helpers.dictionary_helpers import get_nested_val, merge_dataclasses


def test_get_nested_args_from_dict():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'bar': {
            'roo': 4,
            'ree': {
                'sow': 10,
            }
        },
        'arr': [1, 2, 3],
        'a': A(),
    }
    result = get_nested_val(data, 'bar.roo')
    assert result == 4
    result = get_nested_val(data, 'bar.ree.sow')
    assert result == 10
    result = get_nested_val(data, 'arr.1')
    assert result == 2
    result = get_nested_val(data, 'a.val')
    assert result == 1


def test_get_nested_args_with_numpy_list():
    class Sub(NamedTuple):
        name: str = 'dave'

    class A(NamedTuple):
        val: int = 1
        sub: Sub = fill_np_array_with_cls(3, Sub)

    data = {
        'a': A(),
    }
    result = get_nested_val(data, 'a.sub.0.name')
    assert result == 'dave'


def test_get_nested_arg_from_list():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'arr': [1, 2, 3],
        'matrix': [[1, 2, 3], [4, 5, 6]]
    }
    result = get_nested_val(data, 'arr.1')
    assert result == 2
    result = get_nested_val(data, 'matrix.1.1')
    assert result == 5


def test_get_nested_arg_from_list_with_wildcard():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'arr': [1, 2, 3],
        'matrix': [[1, 2, 3], [4, 5, 6]],
        'deepmatrix': [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
        'dictlist': [{'foo': 'abc'}, {'foo': 'def'}]
    }
    # result = get_nested_val(data, 'matrix.1.x')
    # assert result == [4, 5, 6]
    result = get_nested_val(data, 'matrix._.1')
    assert result == [2, 5]
    result = get_nested_val(data, 'deepmatrix._.1._')
    assert result == [[3, 4], [7, 8]]
    result = get_nested_val(data, 'dictlist._.foo')


class TestMergeDataclasses:

    @dataclass
    class Inner:
        a: int = None
        b: int = None

    @dataclass
    class Foo:
        foo: int = None
        bar: int = None
        inner: Any = None

    def test_can_merge_nested_dataclasses(self):
        a = self.Foo(foo=1)
        b = self.Foo(bar=1)
        c = merge_dataclasses(a, b)
        assert c.foo == 1
        assert c.bar == 1

    def test_can_merge_nested_dataclasses_left_clash(self):
        a = self.Foo(foo=1)
        b = self.Foo(foo=2, bar=1)
        c = merge_dataclasses(a, b)
        assert c.foo == 2
        assert c.bar == 1

    def test_can_merge_nested_dataclasses_nested(self):
        a = self.Foo(foo=1)
        b = self.Foo(inner=self.Inner(1))
        c = merge_dataclasses(a, b)
        assert c.foo == 1
        assert c.inner.a == 1

    def test_can_merge_nested_dataclasses_nested_clash(self):
        a = self.Foo(foo=1, inner=self.Inner(2))
        b = self.Foo(inner=self.Inner(1))
        c = merge_dataclasses(a, b)
        assert c.foo == 1
        assert c.inner.a == 1

    def test_can_merge_nested_dataclasses_nested_clash_overlap(self):
        a = self.Foo(foo=1, inner=self.Inner(None, 2))
        b = self.Foo(inner=self.Inner(1))
        c = merge_dataclasses(a, b)
        assert c.foo == 1
        assert c.inner.a == 1
        assert c.inner.b == 2
