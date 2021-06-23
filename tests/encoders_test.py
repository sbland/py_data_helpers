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
]


class TestAdvancedJsonEncoder:

    @pytest.mark.parametrize('name, example_obj, correct_encoding', examples)
    def test_can_encode_simple_object(self, name, example_obj, correct_encoding):
        out = json.dumps(
            example_obj,
            cls=AdvancedJsonEncoder,
        )
        assert out == correct_encoding
