"""Where the data shipped with the package lives."""

from importlib.resources import files
from pathlib import Path


def data_path(*parts):
    """A path under aionanim/data/, e.g. data_path("gw_sensitivity", "ligo.csv")."""
    return Path(str(files("aionanim").joinpath("data", *parts)))
