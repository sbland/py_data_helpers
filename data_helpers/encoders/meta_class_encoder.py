import json
from dataclasses import asdict, is_dataclass, fields
from data_helpers.cls_parsing import is_enum
from typing import List

default_class_meta = {
    int: {
        "__meta__": {
            "label": "Integer",
            "default": 0,
            "uid": "int",
            "base_type": "_base"
        }
    },
    float: {
        "__meta__": {
            "label": "Float",
            "default": 0.0,
            "uid": "float",
            "base_type": "_base"
        }
    },
    str: {
        "__meta__": {
            "label": "String",
            "default": "",
            "uid": "str",
            "base_type": "_base"
        }
    },
    bool: {
        "__meta__": {
            "label": "Boolean",
            "default": False,
            "uid": "bool",
            "base_type": "_base"
        }
    },
    list: {
        "__meta__": {
            "label": "List",
            "default": [],
            "uid": "list",
            "base_type": "_base"
        }
    },
    dict: {
        "__meta__": {
            "label": "Dictionary",
            "default": {},
            "uid": "dict",
            "base_type": "_base"
        }
    },
    tuple: {
        "__meta__": {
            "label": "Tuple",
            "default": (),
            "uid": "tuple",
            "base_type": "_base"
        }
    },
    set: {
        "__meta__": {
            "label": "Set",
            "default": set(),
            "uid": "set"
        }
    }
}


def parse_objects(obj: any, strict: bool = True):
    if type(obj) == type and obj in default_class_meta:
        return default_class_meta[obj]
    elif is_dataclass(obj) and type(obj) != type:
        # TODO: Should test this more to make sure valid for all uses of dataclasses
        return dict(__meta__=asdict(obj))
    elif is_dataclass(obj) and type(obj) == type:
        result = dict(
            __meta__=dict(
                label=obj.__name__,
                type=dict(
                    __meta__=dict(
                        # TODO: Handle type here
                        label="Dataclass",
                        base_type="_base",
                        uid="dataclass",
                        default=None,
                    ),
                ),
            ),
        )
        for f in fields(obj):
            result[f.name] = parse_objects(f.type, strict=strict)
        return result
    elif is_enum(obj):
        return dict(
            __meta__=dict(
                label=obj.__name__,
                default=str(obj.__members__[list(obj.__members__.keys())[0]]),
                type=dict(
                    __meta__=dict(
                        # TODO: Handle type here
                        label="Enum",
                        base_type="_base",
                        uid="enum",
                        default=None,
                    ),
                ),
                options=[str(i) for i in obj.__members__.keys()],
            ),
        )
    elif type(obj) == type(List):
        return dict(
            __meta__=dict(
                type="list",
            ),
            _=parse_objects(obj.__args__[0], strict=strict),
        )
    elif isinstance(obj, List):
        return [parse_objects(i) for i in obj]
    else:
        if strict:
            raise NotImplementedError(f"Cannot parse type: {obj} has type {type(obj)}")
        else:
            return str(obj)


class MetaClassJsonEncoder(json.JSONEncoder):
    """ Special json encoder that outputs class meta data.

    Usage
    =====

    class


    json.dumps(data, cls=AdvancedJsonEncoder, indent=4, sort_keys=True)

    """

    strict: bool = True

    def default(self, obj):
        return parse_objects(obj, strict=self.strict)
