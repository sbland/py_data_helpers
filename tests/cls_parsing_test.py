import typing
import sys
from typing import Union
from enum import Enum
from dataclasses import dataclass
from typing import NamedTuple, List, Sequence, Tuple
import pytest

from data_helpers.cls_parsing import (
    dict_to_cls,
    _replace_recursive,
    get_parser,
    get_val_from_tuple,
    parse_base_val,
    parse_dataclass_val,
    parse_enum_val,
    parse_list_val,
    rsetattr,
)

if sys.version_info <= (3, 9):
    list = List
    tuple = Tuple
    sequence = Sequence

class DemoEnum(Enum):
    DEFAULT="default"

@dataclass
class DemoDataclass:
    foo: int
    bar: str = "hello"

@dataclass
class DemoDataclassSimple:
    foo: int = 0


@pytest.mark.parametrize(['f', 't', 'v', 'result'], [
    ('field', type(1), 1, 1),
    ('field', type("a"), "a", "a"),
    ('field', type(True), True, True),
])
def test_parse_base_val(f, t, v, result):
    assert parse_base_val(f, t, v) == result


@pytest.mark.parametrize(['f', 't', 'v', 'result', 'error'], [
    ('field', type([]), [1,2,3], None, TypeError),
    ('field', List[int], [1,2,3], [1,2,3], None),
    # ('field', List[int], ['1','2','3'], [1,2,3], None), # TODO: fix this test
])
def test_parse_list_val(f, t, v, result, error):
    if error:
        with pytest.raises(error):
            parse_list_val(f, t, v) == result
    else:
        assert parse_list_val(f, t, v) == result




@pytest.mark.parametrize(['f', 't', 'v', 'result', 'error'], [
    ('field', DemoDataclass, {"foo": 1, "bar": "world"}, DemoDataclass(1, "world"), None),
    ('field', DemoDataclass, {}, None, None),
    ('field', DemoDataclassSimple, {}, DemoDataclassSimple(), None),
])
def test_parse_dataclass_val(f, t, v, result, error):
    if error:
        with pytest.raises(error):
            parse_dataclass_val(f, t, v) == result
    else:
        assert parse_dataclass_val(f, t, v) == result




def test_dict_to_cls():
    class B(NamedTuple):
        foo: str = None

    class A(NamedTuple):
        b: B = B()
        c: int = None
        e: int = None

    d = {
        "b": {
            "foo": "bar"
        },
        "c": 1,
    }

    new_object = dict_to_cls(d, A)
    assert new_object == A(B('bar'), 1)



def test_dict_to_dataclass():
    @dataclass
    class B:
        foo: str = None

    @dataclass
    class A:
        b: B = B()
        c: int = None
        e: int = None

    d = {
        "b": {
            "foo": "bar"
        },
        "c": 1,
    }

    new_object = dict_to_cls(d, A)
    assert new_object == A(B('bar'), 1)


def test_dict_to_cls_b():
    class B(NamedTuple):
        foo: str = None

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()

    d = {
        "a": {
            "lat": 52.2,
            "lon": -1.12,
        },
    }

    new_object = dict_to_cls(d, Wrap)
    assert new_object == Wrap(a=A(lat=52.2, lon=-1.12))


def test_dict_to_cls_nested_named_tuple():
    class B(NamedTuple):
        parameters: List[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()

    d = {
        "a": {
            "lat": 52.2,
            "lon": -1.12,
        },
    }

    new_object = dict_to_cls(d, Wrap)
    assert new_object == Wrap(a=A(lat=52.2, lon=-1.12))

def test_dict_to_cls_empty():
    class B(NamedTuple):
        parameters: List[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    @dataclass
    class Wrap():
        a: A = None
        b: B = None

    d = {
        "a": {},
    }

    new_object = dict_to_cls(d, Wrap)
    assert new_object == Wrap(a=A(lat=None, lon=None))



def test_dict_to_cls_nested_list_of_lists():

    class Wrap(NamedTuple):
        a: List[List[int]] = [[0]]

    d = {
        "a": [
            [
                1, 2, 3
            ],
            [
                4, 5, 6,
            ]
        ],
    }

    new_object = dict_to_cls(d, Wrap)
    assert new_object == Wrap(a=[[1, 2, 3], [4, 5, 6]])


class FooEnum(Enum):
    A = 0
    B = 1


class BarEnum(Enum):
    A = "a"
    B = "b"


def test_dict_to_cls_with_enum():
    class Obj(NamedTuple):
        a: FooEnum
        b: FooEnum = FooEnum.B
        c: BarEnum = BarEnum.A

    d = {
        "a": 0,
        "c": "a"
    }

    new_object = dict_to_cls(d, Obj)
    assert new_object == Obj(a=FooEnum.A, b=FooEnum.B, c=BarEnum.A)


def test_dict_to_cls_list():
    class B(NamedTuple):
        parameters: List[str] = []
        parameters_alt: list[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()
        c: List[str] = []

    d = {
        "c": ["a", "b"]
    }

    new_object = dict_to_cls(d, Wrap)
    assert new_object == Wrap(c=["a", "b"])


def test_dict_to_cls_nested_list():
    class B(NamedTuple):
        parameters: List[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()
        c: List[str] = []

    d = {
        "b": {
            "parameters": [
                "a", "b"
            ]
        }
    }

    new_object = dict_to_cls(d, Wrap)
    assert new_object == Wrap(b=B(parameters=["a", "b"]))


def test_dict_to_cls_nested_list_of_tuple():
    class B(NamedTuple):
        parameters: List[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()
        c: Sequence[A] = []

    d = {
        "c": [
            {
                "lat": 52.2,
                "lon": -1.12,
            },
            {
                "lat": 20.2,
                "lon": -10.12,
            },
        ]
    }

    new_object = dict_to_cls(d, Wrap)
    assert new_object == Wrap(c=[A(lat=52.2, lon=-1.12), A(lat=20.2, lon=-10.12)])


def test_dict_to_cls_invalid():
    class B(NamedTuple):
        foo: str = None

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()

    d = {
        "a": {
            "lat": False,
            "lon": -1.12,
        },
        "b": 4,
    }

    with pytest.raises(Exception):
        dict_to_cls(d, Wrap, strict=True)

    d2 = {
        "b": 4,
    }

    with pytest.raises(Exception):
        dict_to_cls(d2, Wrap, strict=True)

    d3 = {
        "z": 4,
    }

    with pytest.raises(Exception):
        dict_to_cls(d3, Wrap, strict=True)


class TestGetParser():

    def test_get_parser_Union(self):
        t = Union[int, float]
        parser = get_parser(t)
        assert parser == parse_base_val

    def test_get_parser_Union_enum(self):

        t = Union[DemoEnum,DemoEnum]
        parser = get_parser(t)
        assert parser == parse_enum_val

    def test_get_parser_Union_incompatible(self):
        # Should throw error if union types are not similar

        class A(NamedTuple):
            foo: float = None

        class B(NamedTuple):
            foo: List[str] = []

        t = Union[A, B]

        with pytest.raises(Exception) as e:
            get_parser(t)

        assert "Invalid Union Type" in str(e)

    def test_get_parser_typing_tuple(self):
        t = typing.Tuple
        parser = get_parser(t)
        assert parser == parse_list_val


def test_replace_recursive():
    class B(NamedTuple):
        foo: str = 'hello'

    class A(NamedTuple):
        lat: float = 2
        lon: float = 3

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()
        c: int = 4

    # updated_wrap = _replace_recursive(Wrap(), 'c', 5)
    # # print(updated_wrap)
    # assert updated_wrap.c == 5

    updated_wrap_b = _replace_recursive(Wrap(), 'a.lat', 5)
    # print(updated_wrap_b)
    assert updated_wrap_b.a.lat == 5


def test_replace_recursive_with_list():
    class B(NamedTuple):
        foo: str = 'hello'

    class A(NamedTuple):
        lat: float = 2
        lon: float = 3

    class Wrap(NamedTuple):
        a: A = A()
        b: List[B] = [B(), B()]
        c: int = 4

    updated_wrap_b = _replace_recursive(Wrap(), 'b.0.foo', 'world')
    assert updated_wrap_b.b[0].foo == 'world'


def test_get_nested_args_from_tuple():
    class A(NamedTuple):
        val: int = 1

    class Tup(NamedTuple):
        foo: int = 1
        a: A = A()
        arr: List[int] = [1, 2, 3]
    tup = Tup()

    result = get_val_from_tuple(tup, 'foo')
    assert result == 1
    result = get_val_from_tuple(tup, 'arr.1')
    assert result == 2
    result = get_val_from_tuple(tup, 'a.val')
    assert result == 1

class TestRsetattr:

    def test_can_set_base_attribute(self):
        base = {}
        out = rsetattr(base, 'foo', 'bar')
        assert out['foo'] == 'bar'

    def test_can_set_nested_attribute(self):
        base = { "foo": { }}
        out = rsetattr(base, 'foo.bar', 'bar')
        assert out['foo']['bar'] == 'bar'
        base = { "foo": { "bar": {} }}
        out = rsetattr(base, 'foo.bar.zoo', 'bar')
        assert out['foo']['bar']['zoo'] == 'bar'

    def test_can_create_missing_dicts(self):
        base = { }
        out = rsetattr(base, 'foo.bar', 'bar', create_missing_dicts=True)
        assert out['foo']['bar'] == 'bar'

    def test_can_create_missing_lists(self):
        base = { }
        out = rsetattr(base, 'foo.0', 'bar', create_missing_dicts=True)
        print(out)
        assert out['foo'][0] == 'bar'

    def test_can_create_missing_lists_padded(self):
        base = { }
        out = rsetattr(base, 'foo.3', 'bar', create_missing_dicts=True)
        print(out)
        assert out['foo'][3] == 'bar'
        assert out['foo'][0] == None
        assert len(out['foo']) == 4


