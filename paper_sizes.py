"""Paper class and paper sizes objects."""
from typing import NamedTuple


class Paper(NamedTuple):
    """Paper sheet sizes."""

    width: int
    height: int


# Paper sizes.
A4_PAPER = Paper(width=210, height=297)
A3_PAPER = Paper(width=297, height=420)
ROLL_PAPER = Paper(width=914, height=300)
