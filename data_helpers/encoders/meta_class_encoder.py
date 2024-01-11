import json
from dataclasses import asdict, is_dataclass, fields


default_class_meta = {
    int: {
        "label": "Integer",
        "default": 0,
        "type": int,
    },
    float: {
        "label": "Float",
        "default": 0.0,
        "type": float,
    },
    str: {
        "label": "String",
        "default": "",
        "type": str,
    },
    bool: {
        "label": "Boolean",
        "default": False,
        "type": bool,
    },
    list: {
        "label": "List",
        "default": [],
        "type": list,
    },
    dict: {
        "label": "Dictionary",
        "default": {},
        "type": dict,
    },
    tuple: {
        "label": "Tuple",
        "default": (),
        "type": tuple,
    },
    set: {
        "label": "Set",
        "default": set(),
        "type": set,
    },
}



class MetaClassJsonEncoder(json.JSONEncoder):
    """ Special json encoder that outputs class meta data.

    Usage
    =====

    class


    json.dumps(data, cls=AdvancedJsonEncoder, indent=4, sort_keys=True)

    """

    def default(self, obj):
        assert type(obj) == type
        if is_dataclass(obj):
            #  This is an adaption of the dataclasses.asdict function
            result = {
                "name": obj.__name__,
                "fields": {

                }
            }
            for f in fields(obj):
                if is_dataclass(f.type):
                    result['fields'][f.name] = asdict(f.type)
                else:
                    result['fields'][f.name] = default_class_meta[f.type]
            return result
        else:
            return str(obj.__name__)
