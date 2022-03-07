import pytest
import json
from data_helpers.encoders import *
import numpy as np
from dataclasses import dataclass

from enum import Enum


@dataclass
class Foo:
    hello: str = "world"


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
    ('dataclass', Foo(), '{"hello": "world"}'),
    ('dataclass_nested', Bar(Foo()), '{"inner": {"hello": "world"}}'),
    ('Enum', {"hello": EnumA.HELLO}, '{"hello": "WORLD"}'),
    ('SimpleClass_with_asdict', SimpleCls("world"),
     '{"hello": "world", "_parentcls": "<class \'tests.encoders_test.SimpleCls\'>"}'),
    ('Type', {"hello": str}, '{"hello": "<class \'str\'>"}'),
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
