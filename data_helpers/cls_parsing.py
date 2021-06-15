
try:
    # From python 3.9+ typing is replaced with generics (PEP 585).
    # Unfortunately this breaks a lot of this code so we attempt to bridge between the two.
    # We try importing get_origin then use if available below
    from typing import get_origin
except:
    pass

from collections.abc import Sequence as CSequence
from enum import Enum
import enum
from warnings import warn
from dataclasses import asdict, is_dataclass, replace
from typing import Any, Callable, NamedTuple, List, Sequence, Union
from copy import deepcopy
from functools import reduce
import numpy as np

from data_helpers.dictionary_helpers import get_nested_val
from data_helpers.comparisons import isNamedTuple


def rgetattr(obj: object, attr: Union[str, List[str]], *args):
    """Get nested properties with dot notation or list of string path.

    https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties

    Properties
    ----------
    obj: object  [description]
    attr: OneOf[str, List[str]]  Either a dot notation string or list of strings
    """
    def _getattr(obj, attr):
        return obj[int(attr)] if isinstance(obj, list) \
            else obj[int(attr)] if type(obj).__module__ == 'numpy' \
            else obj.get(attr, None) if isinstance(obj, dict) \
            else getattr(obj, attr, *args)
    attr_list = attr if isinstance(attr, list) else attr.split(
        '.') if isinstance(attr, str) else [attr]
    return reduce(_getattr, [obj] + attr_list)


def rsetattr(obj: object, attr: Union[str, List[str]], val: Any):
    """Set nested attributes with dot string path or string list

    https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties

    Properties
    ----------
    obj: object  [description]
    attr: OneOf[str, List[str]]  Either a dot notation string or list of strings
    val: any
    """
    # obj_copy = deepcopy(obj) # deep copy takes 10 times as long!
    obj_copy = obj
    pre, _, post = [attr[0], '.', '.'.join(attr[1:])] if isinstance(attr, list) \
        else attr.rpartition('.') if isinstance(attr, str) else [None, None, attr]
    # target = deepcopy(rgetattr(obj, pre) if pre else obj)
    target = rgetattr(obj_copy, pre) if pre else obj_copy
    if isinstance(target, list):
        target[int(post)] = val
    elif isinstance(target, dict):
        target[post] = val
    else:
        setattr(target, post, val)
    return obj_copy


def rdelattr(obj: object, attr: Union[str, List[str]]):
    """delete nested attributes with dot string path or string list

    Properties
    ----------
    obj: object  [description]
    attr: OneOf[str, List[str]]  Either a dot notation string or list of strings
    """
    # obj_copy = deepcopy(obj) # deep copy takes 10 times as long!
    obj_copy = obj
    pre, _, post = [attr[0], '.', '.'.join(attr[1:])] if isinstance(attr, list) \
        else attr.rpartition('.') if isinstance(attr, str) else [None, None, attr]
    # target = deepcopy(rgetattr(obj, pre) if pre else obj)
    target = rgetattr(obj_copy, pre) if pre else obj_copy
    if isinstance(target, list):
        del target[int(post)]
    elif isinstance(target, dict):
        if post in target:
            del target[post]
    else:
        setattr(target, post, None)
    return obj_copy


def parse_base_val(f, t, v, strict=False):
    # Check types
    if strict and not isinstance(v, t):
        raise TypeError('{} must be {}'.format(f, t))
    return v


def parse_list_val(f, t, v, strict=False):
    item_type = t.__args__[0]
    if strict and not isinstance(v, list):
        raise TypeError('{} must be {}'.format(f, t))
    if item_type in [int, float, str, bool]:
        return v
    if is_dataclass(item_type):
        return [dict_to_cls(vi, item_type, strict) for vi in v]

    p = get_parser(item_type)
    if p:
        return [p(f, item_type, vi, strict=strict) for vi in v]
    if item_type.__bases__[0].__name__ == 'tuple':
        return [dict_to_cls(vi, item_type, strict) for vi in v]
    return None


def parse_named_tuple_val(f, t, v, strict=False):
    # if type is a Named Tuple then we assume nested and
    # run recursive dict_to_cls
    if strict and not isinstance(v, dict):
        raise TypeError('{} must be {}'.format(f, t))
    return dict_to_cls(v, t, strict)


def parse_dataclass_val(f, t, v, strict=False):
    # if type is a Named Tuple then we assume nested and
    # run recursive dict_to_cls
    if strict and not isinstance(v, dict):
        raise TypeError('{} must be {}'.format(f, t))
    return dict_to_cls(v, t, strict)


def parse_enum_val(f, t, v, strict=False):
    """Parse a enum value."""
    if strict and v not in [e.value for e in t]:
        raise TypeError('{} must be one of {}'.format(f, [e.value for e in t]))
    if not strict and v is None:
        return None
    try:
        return next(e for e in t if e.value == v)
    except StopIteration:
        raise ValueError(f'{v} is not a member of enum {t}')


def get_parser(t) -> Callable[[str, type, Any, bool], object]:
    """Get the function that can parse the supplied type.

    Python 3.9 introduced breaking changes for type checking.
    We use get_origin if available(3.9+) else check with type(t)

    Parameters
    ----------
    t : type
        The type to be checked. E.g. int, str, list

    Returns
    -------
    function
        A function that parses values of the supplied type

    Raises
    ------
    TypeError
        Raised if the supplied type has not been implemented
    """
    if t in [int, float, str, bool]:
        return parse_base_val
    # Py >= 3.9
    if get_origin:
        if get_origin(t) == list:
            return parse_list_val
        if get_origin(t) == Sequence:
            return parse_list_val
        if get_origin(t) == CSequence:
            return parse_list_val
    # Py < 3.9
    else:
        if type(t) == type(List):
            return parse_list_val
        if type(t) == type(Sequence):
            return parse_list_val
        if type(t) == type(CSequence):
            return parse_list_val
    if is_dataclass(t):
        return parse_dataclass_val
    if issubclass(t, Enum):
        return parse_enum_val
    try:
        # A hack to check if type is a named tuple
        if t.__bases__ and t.__bases__[0].__name__ == 'tuple':
            return parse_named_tuple_val
    except AttributeError:
        pass
    raise TypeError('{} is invalid type'.format(t))


def dict_to_cls(data: dict, Cls, strict=False):
    """Parses a nested dictionary to a specific class using class attributes"""
    if not isinstance(data, dict):
        raise Exception('Data is invalid {}'.format(type(data)))

    cls_fields = [f for (f, t) in Cls.__annotations__.items() if f in data]
    # if strict ensure that no invalid data fields
    if strict:
        invalid_data_keys = [k for k in data.keys() if k not in cls_fields]
        if len(invalid_data_keys) > 0:
            first_invalid_key = invalid_data_keys[0]
            raise Exception('{} must be in {} fields'.format(first_invalid_key, Cls.__name__))

    cls_field_types = [t for (f, t) in Cls.__annotations__.items() if f in data]
    data_values = [data[f] for f in cls_fields]

    new_data = {}
    # f = field; t = type; v = value
    for (f, t, v) in zip(cls_fields, cls_field_types, data_values):
        parser = get_parser(t)
        d = parser(f, t, v)
        new_data[f] = d

    cls_out = Cls(**new_data)
    return cls_out


def get_next_val(last_val, k):
    next_val = None
    next_val = last_val[k] if isinstance(last_val, dict) else next_val
    next_val = last_val[int(k)] if isinstance(last_val, list) else next_val
    next_val = last_val[int(k)] if isinstance(last_val, np.ndarray) else next_val
    next_val = getattr(last_val, k) if is_dataclass(last_val) else next_val
    next_val = last_val._asdict()[k] if isNamedTuple(last_val) else next_val
    return next_val


def set_list_val(l, k, v):
    """ functional update list helper"""
    l_new = deepcopy(l)
    l_new[k] = v
    return l_new


def set_dict_val(d, k, v):
    """ functional update dict helper"""
    d_new = deepcopy(d)
    d_new[k] = v
    return d_new


def set_next_val(obj, acc):
    next_val = None
    next_val = set_dict_val(obj, acc[0], acc[1]) if isinstance(obj, dict) else next_val
    next_val = set_list_val(obj, int(acc[0]), acc[1]) if isinstance(obj, list) else next_val
    next_val = set_list_val(obj, int(acc[0]), acc[1]) if isinstance(obj, np.ndarray) else next_val
    next_val = replace(obj, **dict([acc])) if is_dataclass(obj) else next_val
    next_val = obj._replace(**dict([acc])) if isNamedTuple(obj) else next_val
    if next_val is None:
        raise ValueError()
    return next_val


def _replace_recursive(
        data_tuple: NamedTuple,
        location: str,
        value: any) -> NamedTuple:
    """replaces a value in a tuple using a dot notation str location"""
    locations = location.split('.')

    def get_val(arr, k):
        last_val = arr[-1][1]
        next_val = get_next_val(last_val, k)
        return arr + [(k, next_val)]
    tree = reduce(get_val, locations, [('root', data_tuple)])
    tree_new = tree[:-1] + [(locations[-1], value)]
    tree_new_reversed = reversed(tree_new)
    # tree is a key value list where key

    def set_vals(acc, leaf):
        # return (leaf[0], leaf[1]._replace(**dict([acc])))
        return (leaf[0], set_next_val(leaf[1], acc))
    new_data = reduce(set_vals, tree_new_reversed)
    return new_data[1]


def get_val_from_tuple(data_tuple: NamedTuple, location: str):
    """Helper class to get a nested value from a tuple
    uses get_nested_val"""
    return get_nested_val(data_tuple._asdict(), location)


def unpack(obj):
    """https://stackoverflow.com/questions/33181170/how-to-convert-a-nested-namedtuple-to-a-dict"""
    if isinstance(obj, dict):
        return {key: unpack(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [unpack(value) for value in obj]
    elif isNamedTuple(obj):
        return {key: unpack(value) for key, value in obj._asdict().items()}
    elif isinstance(obj, tuple):
        return tuple(unpack(value) for value in obj)
    elif is_dataclass(obj):
        return unpack(asdict(obj))
    elif isinstance(obj, np.ndarray):
        return unpack(obj.tolist())
    elif issubclass(type(obj), enum.Enum):
        return obj.name
    else:
        return obj


def check_types(obj):
    """Check all input types are correct. Raises Exception if not."""
    for f, f_type in obj.__annotations__.items():
        actual_f_type = getattr(obj, f)
        if actual_f_type is not None and not isinstance(actual_f_type, f_type):
            raise TypeError('{} must be {} but is {}'
                            .format(f, f_type, actual_f_type))
    return obj
