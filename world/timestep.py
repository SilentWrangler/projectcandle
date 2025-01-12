from candle.settings import TIMESTEP_MODULES
from importlib import import_module


def do_full_time_step():
    for modname in TIMESTEP_MODULES:
        mod = import_module(modname)
        mod.do_time_step()
