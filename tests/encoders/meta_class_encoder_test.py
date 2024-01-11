import json
import pytest
from dataclasses import dataclass
from data_helpers.encoders.meta_class_encoder import MetaClassJsonEncoder


@dataclass
class SciField:
    label: str
    default: float
    type: type



@dataclass
class Point:
    x: SciField("X field", 0, int)
    y: SciField("Y field", 0, int)
    label: SciField("Label", "Point", str)
    number: int
    data: dict


examples = [
    ('point class', Point, json.dumps(dict(
        name="Point",
        fields=dict(
            x=dict(label="X field", default=0, type="int"),
            y=dict(label="Y field", default=0, type="int"),
            label=dict(label="Label", default="Point", type="str"),
            number=dict(label="Integer", default=0, type="int"),
            data=dict(label="Dictionary", default={}, type="dict"),
        )
    ), indent=4, sort_keys=True)),
]


class TestMetaClassJsonEncoder:

    @pytest.mark.parametrize('name, example_obj, correct_encoding', examples)
    def test_can_encode_simple_object(self, name, example_obj, correct_encoding):
        out = json.dumps(
            example_obj,
            cls=MetaClassJsonEncoder,
            indent=4,
            sort_keys=True,
        )
        assert out == correct_encoding
