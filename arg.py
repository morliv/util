import argparse

def parse(arg_kwarg_list):
    p = argparse.ArgumentParser()
    for a, k in arg_kwarg_list:
        p.add_argument(*a, **k)
    return p.parse_args()
