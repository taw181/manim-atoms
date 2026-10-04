"""Where the data shipped with the package lives."""

from importlib.resources import files
from pathlib import Path


def data_path(*parts):
    """A path under manim_atoms/data/, e.g. data_path("gw_sensitivity", "ligo.csv")."""
    return Path(str(files("manim_atoms").joinpath("data", *parts)))
