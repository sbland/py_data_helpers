import json
from dataclasses import asdict, is_dataclass, fields
from data_helpers.cls_parsing import is_enum

default_class_meta = {
    int: {
        "label": "Integer",
        "default": 0,
        "uid": "int",
    },
    float: {
        "label": "Float",
        "default": 0.0,
        "uid": "float",
    },
    str: {
        "label": "String",
        "default": "",
        "uid": "str",
    },
    bool: {
        "label": "Boolean",
        "default": False,
        "uid": "bool",
    },
    list: {
        "label": "List",
        "default": [],
        "uid": "list",
    },
    dict: {
        "label": "Dictionary",
        "default": {},
        "uid": "dict",
    },
    tuple: {
        "label": "Tuple",
        "default": (),
        "uid": "tuple",
    },
    set: {
        "label": "Set",
        "default": set(),
        "uid": "set",
    },
}


def parse_objects(obj: any):
    if type(obj) == type and obj in default_class_meta:
        return default_class_meta[obj]
    elif is_dataclass(obj) and type(obj) != type:
        return asdict(obj)
    elif is_dataclass(obj) and type(obj) == type:
        result = {
            "name": obj.__name__,
            "fields": {

            }
        }
        for f in fields(obj):
            result['fields'][f.name] = parse_objects(f.type)
        return result
    elif is_enum(obj):
        return dict(
            label=obj.__name__,
            default=str(obj.__members__[list(obj.__members__.keys())[0]]),
            type="enum",
            options=[str(i) for i in obj.__members__.keys()],
        )
    else:
        raise NotImplementedError(f"Cannot parse type: {obj} has type {type(obj)}")


class MetaClassJsonEncoder(json.JSONEncoder):
    """ Special json encoder that outputs class meta data.

    Usage
    =====

    class


    json.dumps(data, cls=AdvancedJsonEncoder, indent=4, sort_keys=True)

    """

    def default(self, obj):
        return parse_objects(obj)
