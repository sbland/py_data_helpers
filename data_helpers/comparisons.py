try:
    # From python 3.9+ typing is replaced with generics (PEP 585).
    # Unfortunately this breaks a lot of this code so we attempt to bridge between the two.
    # We try importing get_origin then use if available below
    from typing import get_origin
except:
    pass

from inspect import isclass
from enum import Enum
import numpy as np
from collections.abc import Sequence as CSequence
from typing import NamedTuple, List, Sequence, Union, Tuple

BASE_TYPES = [float, int, str, bool]


def is_union(t) -> bool:
    if get_origin:
        if get_origin(t) == Union:
            return True
    else:
        if t.__args__:
            True
    return False


def is_iterable(t) -> bool:
    if t == type([]):
        return True
    if t == type((1,)):
        return True
    if get_origin:
        if get_origin(t) == list:
            return True
        if get_origin(t) == tuple:
            return True
        if get_origin(t) == Sequence:
            return True
        if get_origin(t) == CSequence:
            return True
    # Py < 3.9 # or 3.8?
    else:
        # TODO: Check no false positives here
        if type(t) == type(List):
            return True
        if type(t) == type(Sequence):
            return True
        if type(t) == type(Tuple):
            return True
        if type(t) == type(CSequence):
            return True

        if t == List:
            return True
        if t == Sequence:
            return True
        if t == Tuple:
            return True
        if t == CSequence:
            return True

    if t == np.ndarray:
        return True
    return False

def is_enum(t) -> bool:
    if isclass(t) and issubclass(t, Enum):
        return True
    return False


def is_named_tuple(t) -> bool:
    try:
        # A hack to check if type is a named tuple
        if t.__bases__ and t.__bases__[0].__name__ == 'tuple':
            return True
    except AttributeError:
        pass
    return False


def is_base_cls(t) -> bool:
    if t in [int, float, str, bool]:
        return True
    return False


def is_dictionary(t) -> bool:
    return t == type({"foo": "bar"})

def isNamedTuple(t):
    '''helper function to check if t is a named tuple.
    This is not a perfect check!'''
    return isinstance(t, tuple) and type(t) is not tuple


def get_dict_differences(dict_a: dict, dict_b: dict):
    assert np.array_equal(dict_a.keys(), dict_b.keys())
    different_keys = list(filter(lambda x: dict_a[x] is not dict_b[x], dict_a.keys()))
    return [(a, str(dict_a[a]) + " => " + str(dict_b[a])) for a in different_keys]


def are_equal_safe(val_a: any, val_b: any):
    '''Safe comparison that deals with lists'''
    while True:
        are_equal = None
        are_same_type = type(val_a) is type(val_b)
        if not are_same_type:
            are_equal = False
            break

        type_of_val = type(val_a)
        if are_same_type and type_of_val == 'NoneType':
            are_equal = val_a == val_b
            break
        if are_same_type and isinstance(val_a, str):
            are_equal = val_a == val_b
            break
        if are_same_type and isinstance(val_a, int):
            are_equal = val_a == val_b
            break
        if are_same_type and val_a is None:
            are_equal = val_a == val_b
            break
        if are_same_type and isinstance(val_a, float):
            are_equal = val_a == val_b
            break
        if are_same_type and type_of_val == 'list':
            are_equal = np.array_equal(val_a, val_b)
            break
        if are_same_type and type_of_val in [np.ndarray, list]:
            are_equal = np.array_equal(val_a, val_b)
            break
        if are_same_type and isinstance(val_a, tuple) and type_of_val is tuple:
            are_equal = np.array_equal(val_a, val_b)
            break
        if are_same_type and isinstance(val_a, tuple) and type_of_val is not tuple:
            # Assume to be NamedTuple
            are_equal = tuples_are_equal(val_a, val_b)
            break

        if are_equal is None:
            raise TypeError('Invalid compare type ', type_of_val, val_a)

    return are_equal


def compare_named_tuples(tuple_a: NamedTuple, tuple_b: NamedTuple):
    comparisons = [
        (label, are_equal_safe(a[1], b[1]), a[1], b[1])
        for label, a, b
        in zip(tuple_a._asdict().keys(), tuple_a._asdict().items(), tuple_b._asdict().items())
    ]
    return comparisons


def tuples_are_equal(tuple_a: NamedTuple, tuple_b: NamedTuple):
    return all([
        are_equal_safe(a[1], b[1])
        for a, b
        in zip(tuple_a._asdict().items(), tuple_b._asdict().items())
    ])


def get_mismatched_tuples(tuple_a: NamedTuple, tuple_b: NamedTuple):
    comparisons = compare_named_tuples(tuple_a, tuple_b)
    filtered_comparisons = list(filter(lambda x: not x[1], comparisons))
    return filtered_comparisons


def assert_matched_tuples(tuple_a: NamedTuple, tuple_b: NamedTuple):
    mismatched_tuples = get_mismatched_tuples(tuple_a, tuple_b)
    passes = (len(mismatched_tuples) == 0)
    if not passes:
        raise AssertionError('Tuples do not match: ', mismatched_tuples)

