"""A tweezer array's numbers: its sites, which of them load, and the moves
that rearrange the loaded ones into a defect-free block.

No manim. square_sites lays the traps out, load_sites says which caught an
atom, plan_rearrangement pairs loaded traps with target sites, and positions
is where every kept trap is a share of the way through the move. Every trap
moves at once along a straight line, as it does when the SLM's hologram is
updated.
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment


@dataclass(frozen=True)
class Plan:
    """A rearrangement: the traps kept, where each starts and ends, and the
    loaded traps dropped as surplus. ``kept`` and ``dropped`` index the sites;
    ``start`` and ``end`` are (len(kept), 2), in ``kept``'s order."""

    kept: np.ndarray
    start: np.ndarray
    end: np.ndarray
    dropped: np.ndarray


def square_sites(rows, cols, pitch):
    """The (rows * cols, 2) positions of a square lattice of traps ``pitch``
    apart, centred on the origin, row by row from the top left."""
    xs = (np.arange(cols) - (cols - 1) / 2) * pitch
    ys = ((rows - 1) / 2 - np.arange(rows)) * pitch
    return np.array([[x, y] for y in ys for x in xs], dtype=float)


def load_sites(n, fill, rng):
    """Which of n traps caught an atom, each with probability ``fill``.
    ``rng`` is a numpy Generator, seeded so a scene loads the same way every
    render."""
    return rng.random(n) < fill


def plan_rearrangement(sites, loaded, targets):
    """Pair loaded traps with target sites so the summed squared distance is
    least, and drop the loaded traps left over.

    Least squared distance is what makes moving every trap at once safe: no
    pair of moves could be swapped for a shorter one, so no two traps ever
    coincide on the way, and two that start and end at least a pitch apart
    stay at least pitch / sqrt(2) apart throughout."""
    sites = np.asarray(sites, dtype=float)
    targets = np.asarray(targets, dtype=float)
    loaded = np.flatnonzero(np.asarray(loaded, dtype=bool))
    if len(loaded) < len(targets):
        raise ValueError(f"{len(loaded)} atoms loaded for {len(targets)} target sites")
    cost = ((sites[loaded][:, None, :] - targets[None, :, :]) ** 2).sum(axis=-1)
    rows, cols = linear_sum_assignment(cost)
    kept = loaded[rows]
    return Plan(kept=kept, start=sites[kept], end=targets[cols],
                dropped=np.setdiff1d(loaded, kept))


def positions(plan, share):
    """Every kept trap ``share`` of the way from its start to its end."""
    return (1 - share) * plan.start + share * plan.end


def longest_move(plan):
    """The farthest any kept trap travels: what sets how long the move takes."""
    if len(plan.kept) == 0:
        return 0.0
    return float(np.linalg.norm(plan.end - plan.start, axis=1).max())
