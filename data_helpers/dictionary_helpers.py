from itertools import zip_longest
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
        if is_base_cls(type(a[0])):
            return b
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
        setattr(out, k, v) if v is not None else None

    return out


def merge_dictionaries(a, b, list_method=ListMergeMethods.REPLACE_ALL):
    """Deep merge 2 dictionaries. B overrides a"""
    assert type(a) == type({}) and type(b) == type({})
    out = deepcopy(a)
    for k in b.keys():
        v_b = b.get(k)
        v_a = a.get(k)
        v = merge_objects(v_a, v_b, list_method)
        out[k] = v if v is not None else None

    return out


def find_key(obj: object, k: str, prefix: str = "") -> str:
    """Find a key in a dictionary and return the full key path

    e.g.
    k="foo"
    obj = {
        "bar": {
            "foo": 2,
            "roo": 3,
            "ree": {
                "foo": 4,
                "sow": 5,
            }
        }
    }


    Will return "bar.foo"

    """
    if type(obj) == type({}):
        for kk in obj.keys():
            if kk == k:
                return prefix + kk
            else:
                if isinstance(obj[kk], dict):
                    sub_k = find_key(obj[kk], k, prefix + kk + ".")
                    if sub_k is not None:
                        return sub_k
                if isinstance(obj[kk], list):
                    for i, v in enumerate(obj[kk]):
                        sub_k = find_key(v, k, prefix + kk + "." + str(i) + ".")
                        if sub_k is not None:
                            return sub_k
    return None


def find_all_keys(obj: object, k: str, prefix: str = '') -> List[str]:
    """Find all keys in a dictionary and return the full key paths

    e.g.
    k="foo"
    obj = {
        "bar": {
            "foo": 2,
            "roo": 3,
            "ree": {
                "foo": 4,
                "sow": 5,

            }
        }
    }

    Will return ["bar.foo", "bar.ree.foo"]

    """
    keys = []
    if type(obj) == type({}):
        for kk in obj.keys():
            if kk == k:
                keys.append(prefix + kk)
            else:
                if isinstance(obj[kk], dict):
                    keys.extend(find_all_keys(obj[kk], k, prefix + kk + "."))
                if isinstance(obj[kk], list):
                    for i, v in enumerate(obj[kk]):
                        keys.extend(find_all_keys(v, k, prefix + kk + "." + str(i) + "."))
    return keys


def _flatten_dict_item(k, v, parent_key='', sep='.') -> dict:
    new_key = f"{parent_key}{sep}{k}" if parent_key else k
    out = {}
    if isinstance(v, dict):
        out.update(flatten_dict(v, new_key, sep=sep))
    elif isinstance(v, list):
        for i, vv in enumerate(v):
            new_key_nested = f"{parent_key}{sep}{k}{sep}{i}" if parent_key else f"{k}{sep}{i}"
            nested_val = _flatten_dict_item(new_key_nested, vv, parent_key, sep)
            out.update(nested_val)
    else:
        out[new_key] = v
    return out


def flatten_dict(data: dict, parent_key='', sep='.') -> dict:
    """Flatten a nested dictionary.

    Args:
        data (dict): The nested dictionary to flatten.
        parent_key (str, optional): The parent key. Defaults to ''.
        sep (str, optional): The separator. Defaults to '.'.

    Returns:
        dict:  The flattened dictionary.
    """
    out = {}
    for k, v in data.items():
        v = _flatten_dict_item(k, v, parent_key, sep)
        out.update(v)
    return out
