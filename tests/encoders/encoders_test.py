import pytest
import json
from enum import Enum
from datetime import datetime
from data_helpers.encoders import *
import numpy as np
from dataclasses import dataclass
from data_helpers.meta_type import FieldType


@dataclass
class Foo:
    hello: str = "world"
    number: FieldType("Number Field", int, 1) = 1


@dataclass
class Bar:
    inner: Foo


class SimpleCls:

    def __init__(self, hello) -> None:
        self.hello = hello

    def __asdict__(self) -> dict:
        return {
            "hello": self.hello,
        }


class EnumA(Enum):
    HELLO = "WORLD"


examples = [
    ('simple', {"hello": "world"}, '{"hello": "world"}'),
    ('simple_list', {"hello": ["world"]}, '{"hello": ["world"]}'),
    ('simple_list_outer', [{"hello": "world"}], '[{"hello": "world"}]'),
    ('numpy_simple', {"hello": np.array(["world"])}, '{"hello": ["world"]}'),
    ('numpy_nested', {"hello": [np.array(["world"])]}, '{"hello": [["world"]]}'),
    ('numpy_multi_dim', {"hello": np.arange(4).reshape((2, 2))}, '{"hello": [[0, 1], [2, 3]]}'),
    ('dataclass', Foo(), '{"hello": "world", "number": 1}'),
    ('dataclass_nested', Bar(Foo()), '{"inner": {"hello": "world", "number": 1}}'),
    ('Enum', {"hello": EnumA.HELLO}, '{"hello": "WORLD"}'),
    ('SimpleClass_with_asdict', SimpleCls("world"),
     '{"hello": "world", "_parentcls": "<class \'tests.encoders.encoders_test.SimpleCls\'>"}'),
    ('Type', {"hello": str}, '{"hello": "<class \'str\'>"}'),
    ('datetime', {'datetime': {"hello": datetime(2021, 1, 1, 0, 0)}},
     '{"datetime": {"hello": "2021-01-01T00:00:00"}}'),
    ('timedelta', {'datetime': {"hello": datetime(2021, 1, 1, 0, 0) -
     datetime(2020, 1, 1, 0, 0)}}, '{"datetime": {"hello": 31622400.0}}'),
]


class TestAdvancedJsonEncoder:

    @pytest.mark.parametrize('name, example_obj, correct_encoding', examples)
    def test_can_encode_simple_object(self, name, example_obj, correct_encoding):
        out = json.dumps(
            example_obj,
            cls=AdvancedJsonEncoder,
        )
        assert out == correct_encoding


class TestAdvancedJsonDecoder:

    @pytest.mark.parametrize('name, example_obj, correct_encoding', examples)
    def test_can_encode_simple_object(self, name, example_obj, correct_encoding):
        out = json.loads(
            correct_encoding,
            cls=AdvancedJsonDecoder,
        )
        # assert out == example_obj
        out_recoded = json.dumps(
            out,
            cls=AdvancedJsonEncoder,
        )
        assert out_recoded == correct_encoding
