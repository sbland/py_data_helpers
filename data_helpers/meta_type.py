"""A meta type for adding additional info in the type of a variable."""

from dataclasses import dataclass

@dataclass
class FieldType:
    label: str
    type: type
    default: any = None
    description: str = None


# TODO: Should implement an existing unit or science library here
@dataclass
class SciFieldType:
    label: str
    type: type
    default: None = None
    description: str = None
    unit: str = None
