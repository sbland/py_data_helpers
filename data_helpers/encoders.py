import re
import importlib
from dataclasses import asdict, is_dataclass
import json
import numpy as np
from functools import reduce

from enum import Enum


def is_enum(t) -> bool:
    if issubclass(t, Enum):
        return True
    return False


class AdvancedJsonEncoder(json.JSONEncoder):
    """ Special json encoder.
    """

    def default(self, obj):

        if getattr(obj, '__asdict__', None) and type(obj) != type:
            return {**obj.__asdict__(), "_parentcls": type(obj)}
        elif isinstance(obj, list):
            return ','.join([str(i) for i in obj])
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif is_dataclass(obj) and type(obj) != type:
            return asdict(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
            # TODO: Check why we did this
            # if obj.dtype in [np.integer, np.floating, np.character, np.float64]:
            #     return '[' + ','.join([str(i) for i in obj.tolist()]) + ']'
            # else:
            #     return obj.tolist()
        elif issubclass(type(obj), Enum):
            return obj.value
        elif type(obj) == type:
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class AdvancedJsonDecoder(json.JSONDecoder):
    """Special json decoder."""

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "_parentcls" in dct:
            cls_str = re.match("<class '(.*)'>", dct['_parentcls']).groups()[0]
            cls_module = importlib.import_module('.'.join(cls_str.split('.')[:-1]))
            cls = getattr(cls_module, cls_str.split('.')[-1])
            del dct['_parentcls']
            return cls(**dct)
        return dct
