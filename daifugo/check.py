"""
This module contains functions to help with correctness
testing. The idea is that we provide two solutions, generate
a bunch of inputs and check that their outputs are always
the same. 
"""

from collections import Sequence, Mapping, Sized

def as_tupleset(seq):
    return set(tuple(s) for s in seq)

def test_equal(a,b, transform=None):
    if transform is not None:
      a = transform(a)
      b = transform(b)
    # floats can differ by up to `EPSILON` and still be considered identical
    if isinstance(a,float) and isinstance(b,float):
        return abs(a - b) < EPSILON

    # Sized types must have the same size
    if isinstance(a, Sized) and isinstance(b, Sized):
        if len(a) != len(b):
            return False

    # strings require special treatment as each item is still a string
    if isinstance(a, basestring) and isinstance(b, basestring):
        return a == b
    
    # Sequences must have all items equal
    if isinstance(a, Sequence) and isinstance(b, Sequence):
        return all(test_equal(x,y) for x,y in zip(a,b))

    # Mappings must have all sorted k-v pairs equal
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        return test_equal(sorted(a.items()), sorted(b.items()))

    # for everything else, we use the built-in notion of equality
    else:
        return a == b

def compare_solutions(canonical, user, t_args=[], t_kwargs={}, transform=None):
    expval = canonical(*t_args, **t_kwargs)
    try:
        userval = user(*t_args, **t_kwargs)
    except Exception, e:
        return False, e, expval
    retval = test_equal(userval, expval, transform), userval, expval
    return retval

