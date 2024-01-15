import json
from dataclasses import dataclass
from typing import List
from enum import Enum
from data_helpers.encoders.meta_class_encoder import MetaClassJsonEncoder
from data_helpers.cls_parsing import rgetattr
from data_helpers.meta_type import FieldType


@dataclass
class NestedField:
    label: FieldType("Label", str, "Nested")


class MyEnum(Enum):
    A = 1
    B = 2


@dataclass
class Point:
    x: FieldType("X field", int, 0)
    y: FieldType("Y field", int, 0) = 0
    label: FieldType("Label", str, "Point") = "MISSING_LABEL"
    number: int = 1  # TODO: Get default from  = 1
    data: dict = None
    nested: NestedField = None
    enum: MyEnum = MyEnum.A
    listNested: List[NestedField] = None


# TODO: Change primative to primative
example_result = json.dumps(dict(
    __meta__=dict(label="Point", id=None, type=dict(
        __meta__=dict(
            label="Dataclass",
            primative=False,
            uid="dataclass",
            default=None,
        ),
    )),
    x=dict(
        __meta__=dict(
            label="X field",
            id="x",
            default=0,
            description=None,
            type=dict(
                __meta__=dict(
                    label="Integer",
                    primative=True,
                    uid="int",
                    default=0,
                ),
            ),
        )),
    y=dict(
        __meta__=dict(
            label="Y field",
            id="y",
            default=0,
            description=None,
            type=dict(
                __meta__=dict(
                    label="Integer",
                    primative=True,
                    uid="int",
                    default=0,
                ),
            ),
        )),
    label=dict(
        __meta__=dict(
            label="Label",
            id="label",
            default="Point",
            description=None,
            type=dict(
                __meta__=dict(
                    label="String",
                    default="",
                    primative=True,
                    uid="str",
                ),
            ),
        ),
    ),
    number=dict(
        __meta__=dict(
            label="number",
            id="number",
            type=dict(
                __meta__=dict(
                    label="Integer",
                    primative=True,
                    default=0,
                    uid="int",
                ),
            ),
        ),
    ),
    data=dict(
        __meta__=dict(
            label="data",
            id="data",
            type=dict(
                __meta__=dict(
                    label="Dictionary",
                    primative=False,
                    default={},
                    uid="dict",
                ),
            ),
        ),
    ),
    nested=dict(
        __meta__=dict(
            label="NestedField",
            id="nested",
            type=dict(
                __meta__=dict(
                    label="Dataclass",
                    primative=False,
                    uid="dataclass",
                    default=None,
                ),
            ),
        ),
        label=dict(
            __meta__=dict(
                label="Label",
                id="label",
                default="Nested",
                description=None,
                type=dict(
                    __meta__=dict(
                        default="",
                        primative=True,
                        label="String",
                        uid="str",
                    ),
                )
            ),
        ),
    ),
    enum=dict(__meta__=dict(
        label="MyEnum",
        id="enum",
        default="MyEnum.A",
        type=dict(
            __meta__=dict(
                label="Enum",
                primative=True,
                uid="enum",
                default=None,
            ),
        ),
        options=["A", "B"],
    )),
    listNested=dict(
        __meta__=dict(
            id="listNested",
            label="listNested",
            type=dict(
                __meta__=dict(
                    label="List",
                    primative=False,
                    default=[],
                    uid="list",
                ),
            ),
        ),
        _=dict(
            __meta__=dict(
                label="NestedField",
                id="_",
                type=dict(
                    __meta__=dict(
                        label="Dataclass",
                        primative=False,
                        uid="dataclass",
                        default=None,
                    ),
                ),
            ),
            label=dict(
                __meta__=dict(
                    id="label",
                    label="Label",
                    default="Nested",
                    description=None,
                    type=dict(
                        __meta__=dict(
                            default="",
                            primative=True,
                            label="String",
                            uid="str",
                        ),
                    ),
                ),
            ),
        ),
    ),
),
    indent=4,
    sort_keys=True,
)


class TestMetaClassJsonEncoder:

    def test_can_encode_simple_object(self):
        out = json.dumps(
            Point,
            cls=MetaClassJsonEncoder,
            indent=4,
            sort_keys=True,
        )
        print(out)
        assert out == example_result

    def test_can_access_a_variable_with_dot_notation(self):
        out = json.loads(json.dumps(
            Point,
            cls=MetaClassJsonEncoder,
            indent=4,
            sort_keys=True,
        ))
        nested_val = rgetattr(out, 'x.__meta__.label')
        assert nested_val == "X field"

        nested_val = rgetattr(out, 'listNested._.__meta__.label')
        print(nested_val)
        assert nested_val == "NestedField"
