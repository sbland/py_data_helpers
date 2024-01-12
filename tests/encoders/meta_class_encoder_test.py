import json
import pytest
from dataclasses import dataclass
from data_helpers.encoders.meta_class_encoder import MetaClassJsonEncoder
from enum import Enum
from typing import List


@dataclass
class SciField:
    label: str
    default: float
    type: type


@dataclass
class NestedField:
    label: SciField("Label", "Nested", str)


class MyEnum(Enum):
    A = 1
    B = 2


@dataclass
class Point:
    x: SciField("X field", 0, int)
    y: SciField("Y field", 0, int) = 0
    label: SciField("Label", "Point", str) = "MISSING_LABEL"
    number: int = 1  # TODO: Get default from  = 1
    data: dict = None
    nested: NestedField = None
    enum: MyEnum = MyEnum.A
    listNested: List[NestedField] = None


examples = [
    ('point class', Point, json.dumps(dict(
        name="Point",
        fields=dict(
            x=dict(label="X field", default=0, type=dict(
                default=0,
                label="Integer",
                uid="int"
            )),
            y=dict(label="Y field", default=0, type=dict(
                default=0,
                label="Integer",
                uid="int"
            )),
            label=dict(label="Label", default="Point", type=dict(
                default="",
                label="String",
                uid="str",
            )),
            number=dict(label="Integer", default=0, uid="int"),
            data=dict(label="Dictionary", default={}, uid="dict"),
            nested=dict(
                name="NestedField",
                fields=dict(
                    label=dict(label="Label", default="Nested", type=dict(
                        default="",
                        label="String",
                        uid="str",
                    )),
                ),
            ),
            enum=dict(label="MyEnum", default="MyEnum.A", type="enum", options=["A", "B"]),
            listNested=dict(
                type="list",
                itemType=dict(
                    name="NestedField",
                    fields=dict(
                        label=dict(label="Label", default="Nested", type=dict(
                            default="",
                            label="String",
                            uid="str",
                        )),
                    ),
                ),
            ),
        ),
    ),
        indent=4,
        sort_keys=True,
    )),
]


class TestMetaClassJsonEncoder:

    @ pytest.mark.parametrize('name, example_obj, correct_encoding', examples)
    def test_can_encode_simple_object(self, name, example_obj, correct_encoding):
        out = json.dumps(
            example_obj,
            cls=MetaClassJsonEncoder,
            indent=4,
            sort_keys=True,
        )
        # print(out)
        assert out == correct_encoding
