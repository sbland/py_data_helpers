from enum import Enum
from copy import deepcopy
from dataclasses import asdict, is_dataclass, replace
from typing import List

import numpy as np

from data_helpers.comparisons import BASE_TYPES, is_base_cls, isNamedTuple, is_enum, is_iterable


def get_val_from_obj(obj, k):
    if isinstance(obj, dict):
        return obj[k]   # dictionary access
    if isinstance(obj, list):
        return obj[int(k)]   # list access
    if isinstance(obj, np.ndarray):
        return obj[int(k)]   # numpy array access
    if isNamedTuple(obj):
        return obj._asdict()[k]   # namedtuple access
    if is_dataclass(obj):
        return getattr(obj, k)   # dataclass access
    raise ValueError(f'Cannot get {k} from {obj}')


def get_nested_val(data: dict, location_str: str):
    """ Helper function to get a value from a dictionary
    when given a dot notation string

    e.g.

    ```
    data = {
        'foo': 1,
        'bar': {
            'roo': 4,
            'ree': {
                'sow': 10,
                }
            },
        'a': A(),
        'arr': [1, 2, 3],
        'deepmatrix': [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
        'dictlist': [{'foo': 'abc'}, {'foo': 'def'}],
        }
    ```

    ```
    result = get_nested_val(data, 'bar.ree.sow')
    assert result == 10
    result = get_nested_val(data, 'arr.1')
    assert result == 2

    ## Wildcards
    result = get_nested_val(data, 'deepmatrix._.1')
    assert result == []
    ```
    """
    loc_split = location_str.split('.')
    loc_arr = [loc_split[i:] for i in range(0, len(loc_split))]
    out = data
    for i in range(len(loc_arr)):
        k = loc_split[i]
        if k != '_':
            out = get_val_from_obj(out, k)
        if k == '_':
            if i == len(loc_arr) - 1:
                out = out
            else:
                out = [get_nested_val(o, '.'.join(loc_arr[i + 1])) for o in out]
            break
    return out


class ListMergeMethods(Enum):

    REPLACE_ALL = "REPLACE_ALL"
    ZIP = "ZIP"


def merge_objects(a, b, list_method):
    if a is None:
        v = b
    elif b is None:
        v = a
    elif type(a) in BASE_TYPES or is_enum(type(a)):
        v = b
    elif is_dataclass(a):
        v = merge_dataclasses(a, b, list_method)
    elif type(a) == type({}):
        v = merge_dictionaries(a, b, list_method)
    elif is_iterable(type(a)):
        if len(a) == 0:
            v = b
        elif len(b) == 0:
            v = a
        else:
            v = merge_iterable(a, b, method=list_method)
    else:
        print(type(a))
        raise ValueError("Invalid type")
    return v

from itertools import zip_longest
def merge_iterable(a, b, method="REPLACE_ALL"):
    """Deep merge 2 iterables.

    Methods
    -------
    ZIP
    REPLACE
    JOIN
    REPLACE_ALL

    """
    if method == ListMergeMethods.ZIP:
        if is_base_cls(type(a[0])): return b
        return [merge_objects(v_a, v_b, method) for v_a, v_b in zip_longest(a, b)]
    if method == "REPLACE":
        raise NotImplementedError("REPLACE method not implemented")
    if method == "JOIN":
        raise NotImplementedError("JOIN method not implemented")
    if method == ListMergeMethods.REPLACE_ALL:
        return b
    else:
        raise ValueError("Invalid Merge Method")


def merge_dataclasses(a, b, list_method=ListMergeMethods.REPLACE_ALL):
    """Deep merge 2 dataclasses. B overrides a"""
    assert is_dataclass(a) and is_dataclass(b)
    out = replace(a)
    for k in asdict(b).keys():
        v_b = getattr(b, k)
        v_a = getattr(a, k)
        v = merge_objects(v_a, v_b, list_method)
        setattr(out, k, v) if v is not None else 0

    return out


def merge_dictionaries(a, b, list_method=ListMergeMethods.REPLACE_ALL):
    """Deep merge 2 dictionaries. B overrides a"""
    assert type(a) == type({}) and type(b) == type({})
    out = deepcopy(a)
    for k in b.keys():
        v_b = b.get(k)
        v_a = a.get(k)
        v = merge_objects(v_a, v_b, list_method)
        out[k] = v if v is not None else 0

    return out
