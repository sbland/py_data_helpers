"""A meta type for adding additional info in the type of a variable."""

from dataclasses import dataclass

@dataclass
class FieldType:
    label: str
    default: float
    type: type


