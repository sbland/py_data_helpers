''' Defines varius helpers for working with lists'''


def flatten_list(arr: list) -> list:
    ''' Recursive list flatten'''
    return [item for sublist in arr
            for item in
            (flatten_list(sublist) if type(sublist) is list else [sublist])]


def flatten_tuple(arr):
    return (item for sublist in arr
            for item in
            (flatten_list(sublist) if type(sublist) is tuple else [sublist]))


def filter_none(arr) -> list:
    """Filters out None values from an array"""
    return [a for a in arr if a is not None]


def offset(arr, zero, wrap) -> list:
    """offset an array to be relative to a particular *zero* value.  If *wrap*
       is supplied, new values less than 0 are offset by the *wrap* value.
       Note: formally known as reindex
    """
    out_a = [i - zero for i in arr]
    out_b = [(i + wrap) if i < 0.0 else i for i in out_a] if wrap else out_a
    return out_b
