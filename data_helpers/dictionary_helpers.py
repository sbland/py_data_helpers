from dataclasses import is_dataclass

import numpy as np

from data_helpers.comparisons import isNamedTuple


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