"""Spin squeezing by a non-demolition measurement in an optical cavity.

N atoms each in the same superposition of |g> and |e> add up to one
collective spin, J = sum of the atoms' spin-1/2s, with its tip on the Bloch
sphere's equator. Each atom still projects on its own at readout, so the tip
is blurred by a disc of quantum noise, Delta J_z = sqrt(N)/2 wide: the
coherent spin state, whose phase resolution 1/sqrt(N) is the standard quantum
limit.

Put the atoms in an optical cavity tuned to the 689 nm line, which only |g>
drives (Chen et al., PRL 106, 133601 (2011), did this on Rb's D2 line). The
atoms in |g> share one excitation with the cavity mode, and that collective
coupling splits the cavity's line into two normal modes 2 g sqrt(N_g) apart:
the vacuum Rabi splitting. Measuring the splitting counts N_g -- which, with
N known, is J_z = (N_e - N_g)/2 -- and a probe on the split modes sits
g sqrt(N_g) off the atoms, so it scatters little and flips no atom: a
quantum non-demolition measurement. Once J_z is
known better than sqrt(N)/2, the disc is squeezed along J_z and stretched
along the phase; a rotation about the mean spin turns the narrow direction
onto the phase, and the interferometer resolves it to xi / sqrt(N), xi < 1.

The pieces it is drawn with are general and live in core: the Bloch sphere
and the noise patch on it in manim_atoms.core.bloch, the cavity and its
transmission in manim_atoms.core.optics. What is squeezing's own is here:
the atoms in the cavity mode, drawn in the superposition's colour.
"""

from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import make_cloud


def cavity_atoms(center, radius, n=40, seed=4):
    """The atoms in the cavity mode, each in the same superposition of |g>
    and |e>, so drawn halfway between the two states' colours."""
    color = interpolate_color(ATOM_COLOR, KICKED_COLOR, 0.5)
    return make_cloud(center, color, n=n, radius=radius, seed=seed)
