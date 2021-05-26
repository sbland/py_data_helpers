from dataclasses import asdict, is_dataclass
import json
import numpy as np
from functools import reduce


class NumpyEncoder(json.JSONEncoder):
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
            if obj.dtype in [np.integer, np.floating, np.character, np.float64]:
                return ','.join([str(i) for i in obj.tolist()])
            else:
                return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def prep_data_for_snapshot(data):
    def _r(acc, ik):
        key, value = ik
        if isinstance(value, list):
            acc[key] = ', '.join([str(i) for i in value])
        return acc
    return reduce(_r, data.items(), {})
