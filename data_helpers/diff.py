from dataclasses import asdict, is_dataclass
from data_helpers.list_helpers import flatten_list
from typing import List
from data_helpers.comparisons import is_base_cls, is_dictionary, is_iterable
from math import isclose


def diff(field, a, b) -> List[str]:
    changes = []
    item_type = type(a) if a is not None else type(b)

    if is_iterable(type(a)) or is_iterable(type(b)) or a != b:
        if a is None or b is None:
            changes.append(f"{field}: {a} -> {b}")
        elif is_base_cls(item_type):
            if item_type == float and isclose(a, b, rel_tol=1e-3):
                pass
            else:
                changes.append(f'{field}: {a} -> {b}')
        elif is_dictionary(item_type):
            changes += diff_dicts(field, a, b)
        elif is_iterable(item_type):
            changes += flatten_list([diff(f"{field}.{i}", va, vb) for i, (va, vb) in enumerate(zip(a, b))])
        elif is_dataclass(item_type):
            changes += diff_dicts(field, asdict(a), asdict(b))
        else:
            raise ValueError(f"Invalid type{item_type}")
    return changes

def diff_dicts(field, a, b):
    changes = []
    a_is_dict = is_dictionary(a)
    b_is_dict = is_dictionary(b)

    if not a_is_dict and b_is_dict:
        changes.append(f"{field}: {a} -> {b}")

    if a_is_dict and not b_is_dict:
        changes.append(f"{field}: {a} -> {b}")

    for k in set(list(a.keys()) + list(b.keys())):
        va = a.get(k, None)
        vb = b.get(k, None)
        changes += diff(f"{field}.{k}",va, vb)
    return changes
