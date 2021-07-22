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
    """ Special json encoder for numpy types
    https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
    """

    def default(self, obj):
        if isinstance(obj, list):
            return ','.join([str(i) for i in obj])
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif is_dataclass(obj):
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
        return json.JSONEncoder.default(self, obj)
