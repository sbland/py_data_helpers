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
            "primative": True
        }
    },
    float: {
        "__meta__": {
            "label": "Float",
            "default": 0.0,
            "uid": "float",
            "primative": True
        }
    },
    str: {
        "__meta__": {
            "label": "String",
            "default": "",
            "uid": "str",
            "primative": True
        }
    },
    bool: {
        "__meta__": {
            "label": "Boolean",
            "default": False,
            "uid": "bool",
            "primative": True
        }
    },
    list: {
        "__meta__": {
            "label": "List",
            "default": [],
            "uid": "list",
            "primative": False
        }
    },
    dict: {
        "__meta__": {
            "label": "Dictionary",
            "default": {},
            "uid": "dict",
            "primative": False
        }
    },
}


def parse_objects(obj: any, current_key: str = None, strict: bool = True):
    if type(obj) == type and obj in default_class_meta:
        return dict(__meta__=dict(
            label=current_key,
            type=default_class_meta[obj]))
    elif is_dataclass(obj) and type(obj) != type:
        if hasattr(obj, "type"):
            # If the dataclass has a type attribute we should parse
            # it without using the default parser
            obj_dict = asdict(obj)
            return dict(__meta__={**obj_dict,
                "type": default_class_meta[obj_dict['type']]
            })
        return dict(__meta__=asdict(obj))
    elif is_dataclass(obj) and type(obj) == type:
        result = dict(
            __meta__=dict(
                label=obj.__name__,
                type=dict(
                    __meta__=dict(
                        label="Dataclass",
                        primative=False,
                        uid="dataclass",
                        default=None,
                    ),
                ),
            ),
        )
        for f in fields(obj):
            result[f.name] = parse_objects(f.type, current_key=f.name, strict=strict)
        return result
    elif is_enum(obj):
        return dict(
            __meta__=dict(
                label=obj.__name__,
                default=str(obj.__members__[list(obj.__members__.keys())[0]]),
                type=dict(
                    __meta__=dict(
                        label="Enum",
                        primative=True,
                        uid="enum",
                        default=None,
                    ),
                ),
                options=[str(i) for i in obj.__members__.keys()],
            ),
        )
    # elif hasattr(obj, "__args__") and obj.__origin__ == List:
    elif hasattr(obj, "__args__") and obj.__origin__ == list:
        print(obj.__dict__)
        return dict(
            __meta__=dict(
                label=current_key,
                type=default_class_meta[list],
            ),
            _=parse_objects(obj.__args__[0], strict=strict),
        )
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
    # current_key: str = None

    def default(self, obj):
        return parse_objects(obj, strict=self.strict)
