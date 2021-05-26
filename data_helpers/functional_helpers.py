def fp_while(pred, fun, acc, max_iter=99999999999):
    v = acc
    i = 0
    while(pred(v) and i < max_iter):
        v = fun(v)
        i += 1
    return v


def fp_while_i(pred, fun, acc):
    v = acc
    while(pred(*v)):
        v = fun(*v)
    return v


def fp_while_generator(pred, fun, acc, include_last=False):
    v = acc
    while(pred(v)):
        yield v
        v = fun(v)
    if include_last:
        yield v
