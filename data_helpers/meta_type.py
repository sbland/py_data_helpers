"""A meta type for adding additional info in the type of a variable."""

from dataclasses import dataclass

def field_type(cls):
    """Define a class as being a field type.

    Field type classes are intended for use in the type annotation of a field in a dataclass.
    They can be used to add additional meta data to a field type such as label and unit.

    Example:
        @dataclass
        class MyDataClass:
            my_field: FieldType(label="My Field") = None

    """
    assert cls.__annotations__['type'], f'Field type must have a type attribute {cls.__annotations__}'
    setattr(cls, '__is_field_type__', True)
    return cls

@field_type
@dataclass
class FieldType:
    label: str
    type: type
    default: any = None
    description: str = None


# TODO: Should implement an existing unit or science library here
@field_type
@dataclass
class SciFieldType:
    label: str
    type: type
    default: None = None
    description: str = None
    unit: str = None
