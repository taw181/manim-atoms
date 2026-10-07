"""Stepping an atom through a sequence of pulses: which arms each one splits,
kicks or merges, where it lands on them, and the legs flown in between.

lmt_history is the engine: it takes a list of (time, kind, stage) pulses --
kinds "split", "up", "down", "merge", described below -- and returns, per
pulse, where it lands, what it does to each arm (via core.primitives.recoil)
and the legs to the next. interferometry.tools.lmt writes such sequences for
large momentum transfer (lmz_pulses); LMTMachZehnder animates one.
"""

import numpy as np

from manim_atoms.core.primitives import recoil

# --- pulse sequences --------------------------------------------------------


# A sequence is a list of (time, kind, stage). The kinds:
#   "split"  a pi/2 from below: every arm splits into itself, left alone
#            (name + "0"), and a kicked copy (name + "1"). The two form a pair.
#   "up"     a pi pulse that drives every arm, from whichever side pushes the
#   "down"   kicked arm of each pair up (or down); its partner, in the other
#            state, goes the other way.
#   "merge"  the closing pi/2: each pair, met again, leaves by two ports.
LMT_PORT = 0.7  # how far the output ports are drawn


def lmt_history(pulses, t0, z0, u, port=LMT_PORT):
    """Step through a sequence: for each event, where it lands and what it
    does to each arm, and the legs flown until the next one.

    Starts from one arm, "", in |g> and at rest at (t0, z0). Returns a list of
    dicts: ``x``, ``from_below``, ``stage``, ``kind``,
    ``splits`` [(parent, left alone, kicked)], ``hits`` [(arm, point, new
    state)], and ``legs`` [(arm, start, end, state)] from this event to the
    next -- after the merge, the output ports, named pair + "g"/"e".
    """
    arms = {"": dict(z=z0, v=0, state="g")}
    pairs = []
    history = []
    for k, (t, kind, stage) in enumerate(pulses):
        x = t0 + t
        from_below, splits, hits, legs = True, [], [], []

        def at(arm):
            return np.array([x, arm["z"], 0.0])

        if kind == "split":
            pairs = []
            for name, arm in list(arms.items()):
                dv, state = recoil(arm["state"], True)
                arms[name + "0"] = dict(arm)
                arms[name + "1"] = dict(arm, v=arm["v"] + dv, state=state)
                del arms[name]
                pairs.append((name + "0", name + "1"))
                splits.append((name, name + "0", name + "1"))
                hits.append((name + "1", at(arm), state))
        elif kind in ("up", "down"):
            # the side that gives the kicked arms the push asked for
            dv, _ = recoil(arms[pairs[0][1]]["state"], True)
            from_below = dv == (1 if kind == "up" else -1)
            for name, arm in arms.items():
                dv, arm["state"] = recoil(arm["state"], from_below)
                arm["v"] += dv
                hits.append((name, at(arm), arm["state"]))
        if kind == "merge":
            for stay, kicked in pairs:
                a, b = arms[stay], arms[kicked]
                assert abs(a["z"] - b["z"]) < 1e-9, "the arms have not closed"
                ground = a if a["state"] == "g" else b
                start = at(ground)
                for state, v in (("g", ground["v"]), ("e", ground["v"] + 1)):
                    legs.append((stay[:-1] + state, start,
                                 start + [port, port * v * u, 0], state))
        else:
            dt = pulses[k + 1][0] - t
            for name, arm in arms.items():
                start = at(arm)
                arm["z"] += arm["v"] * u * dt
                legs.append((name, start, np.array([x + dt, arm["z"], 0.0]),
                             arm["state"]))
        history.append(dict(x=x, from_below=from_below, stage=stage, kind=kind,
                            splits=splits, hits=hits, legs=legs))
    return history
