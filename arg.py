import argparse
from typing import List, Callable

def parse(arg_kwarg_list):
    p = argparse.ArgumentParser()
    for a, k in arg_kwarg_list:
        p.add_argument(*a, **k)
    return p.parse_args()


def act(args, fs: List[Callable]):
    return {f.__name__: f(args) for f in fs}