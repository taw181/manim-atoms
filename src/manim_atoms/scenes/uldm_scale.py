"""How big an ultralight dark-matter wave is, measured against the solar system.

DarkMatterScale comes after DarkMatterField. The mass sets the scale, through
the Compton wavelength lambda_C = h / (m_phi c): the distance light covers in
one oscillation of the field. The scene goes through AION's range from
heavy to light, so each step zooms out: it opens on the heavy end, where
lambda_C is about a tenth of the Earth, pulls back to the middle of the
range, where it is the distance to the Moon, and then to the light end,
where it is about the Earth-Sun distance. Even the shortest dwarfs any lab,
which is why DarkMatterField could draw it as just phi(t) at one place.

AION's range is 1e-17 to 1e-12 eV (Badurina et al., JCAP 05 (2020) 011,
arXiv:1911.11755). The same paper's reach in the photon coupling sits in an
inset on the right, with the mass of each step marked across it: the mark
slides along the mass axis as the camera pulls back. The formula and each
step's numbers make a column down the left.

The wave is drawn moving at c, so what it shows is lambda_C, as the caption
says. The field itself is coherent over its de Broglie wavelength, about
c / v ~ 1e3 times longer, since galactic dark matter moves at v ~ 1e-3 c.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.uldm_plot import mass_label, mass_mark, uldm_inset


# --- the numbers ------------------------------------------------------------
HC = 1.23984e-6  # eV m
H = 4.135668e-15  # eV s
EARTH_RADIUS = 6.371e6  # m
MOON_RADIUS = 1.737e6
SUN_RADIUS = 6.957e8
EARTH_MOON = 3.844e8
EARTH_SUN = 1.496e11
AION_MASSES = (1e-17, 1e-12)  # eV, light end and heavy end
# the mass whose Compton wavelength is the Earth-Moon distance: 3.2e-15 eV
MOON_MASS = HC / EARTH_MOON


def compton(mass):
    """lambda_C in metres for a mass in eV."""
    return HC / mass


# --- the layout ---------------------------------------------------------------
# Each view is how many metres one scene unit stands for, and where the Earth's
# centre sits on screen. Zooming animates both at once, the scale in log space, so the
# bodies move as they would under a real camera.
DS_Y = -1.55  # the line the bodies and the wave sit on: low, under the inset
DS_SPAN = 9.0  # Earth to Moon, or Earth to Sun, on screen
VIEW_MOON = (EARTH_MOON / DS_SPAN, -0.5 * DS_SPAN, DS_Y)
# Close enough in that the Earth is its limb along the bottom of the frame and
# a wavelength is wide enough to brace: the whole disc at this scale would
# crowd ten wavelengths into a strip too fine to read.
EARTH_VIEW_RADIUS = 6.5
VIEW_EARTH = (
    EARTH_RADIUS / EARTH_VIEW_RADIUS, 0.0, DS_Y - 1.0 - EARTH_VIEW_RADIUS
)
VIEW_SUN = (EARTH_SUN / DS_SPAN, -0.5 * DS_SPAN, DS_Y)
DS_AMPLITUDE = 0.65
DS_X = (-7.2, 7.2)  # the wave runs off both edges of the frame
# One period of the drawn wave, in seconds of scene time. The real periods run
# from milliseconds to minutes across the range, so this is a display rate,
# the same in every view.
DS_PERIOD = 2.0
DS_ZOOM_TIME = 2.5
DS_STATS = np.array([-6.6, 1.2, 0.0])  # upper-left corner of the numbers
# AION's reach, top right over the wave, beside the column of text: the
# lower-left corner of its axes, and their size. Its tick labels and axis
# names hang off the left and bottom of that, down to just clear of the
# wave's crests; its top stays under the end of the title.
DS_INSET_ORIGIN = np.array([1.9, 0.1, 0.0])
DS_INSET_WIDTH = 4.8
DS_INSET_HEIGHT = 3.0


class DarkMatterScale(Scene):
    """An ultralight dark-matter wave laid across the Earth, Moon and Sun.

    The stops go through hold(), one period of the wave, as in DarkMatterField,
    so a slide can loop each of them without a jump.
    """

    def hold(self):
        """Let the wave run through one whole period."""
        self.play(
            self.theta.animate.increment_value(TAU),
            rate_func=linear, run_time=DS_PERIOD,
        )

    def construct(self):
        title = Tex(
            r"Ultralight dark matter: a wave on astronomical scales",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        formula = VGroup(
            MathTex(
                r"\lambda_C = \frac{h}{m_\phi c}",
                font_size=FONT_ANNOTATION, color=FIELD_COLOR,
            ),
            Tex(
                r"the distance light covers in one oscillation",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)  # a column, left of the inset
        formula.next_to(title, DOWN, buff=0.3).align_to(title, LEFT)

        # --- the camera, and what it is looking at ---------------------------
        self.log_scale = ValueTracker(np.log10(VIEW_EARTH[0]))
        self.earth_x = ValueTracker(VIEW_EARTH[1])
        self.earth_y = ValueTracker(VIEW_EARTH[2])
        self.theta = ValueTracker(0.0)
        self.wavelength = compton(AION_MASSES[1])  # metres
        self.wave_opacity = ValueTracker(0.0)
        # the mass the mark on the inset stands at, moved with the camera
        self.log_mass = ValueTracker(np.log10(AION_MASSES[1]))
        inset = uldm_inset(DS_INSET_ORIGIN, DS_INSET_WIDTH, DS_INSET_HEIGHT)
        self.inset_axes = inset.axes

        def mark():
            return mass_mark(inset.axes, 10 ** self.log_mass.get_value(), label=None)

        def body(metres, radius, color):
            r = max(radius / 10 ** self.log_scale.get_value(), BODY_MIN_RADIUS)
            return Circle(
                radius=r, stroke_width=0, fill_color=color, fill_opacity=BODY_OPACITY,
            ).move_to([self.screen_x(metres), self.earth_y.get_value(), 0])

        def moon():
            m = body(EARTH_MOON, MOON_RADIUS, MOON_COLOR)
            # Fades as it closes on the Earth in the wide view, where the two
            # would otherwise be one blob with a bump on it.
            gap = self.screen_x(EARTH_MOON) - self.earth_x.get_value()
            return m.set_fill(opacity=BODY_OPACITY * np.clip((gap - 0.15) / 0.3, 0, 1))

        bodies = [
            always_redraw(lambda: body(0.0, EARTH_RADIUS, EARTH_COLOR)),
            always_redraw(moon),
            always_redraw(lambda: body(EARTH_SUN, SUN_RADIUS, SUN_COLOR)),
        ]

        def wave():
            k = TAU * 10 ** self.log_scale.get_value() / self.wavelength
            x_e = self.earth_x.get_value()
            theta = self.theta.get_value()
            return FunctionGraph(
                lambda x: DS_Y + DS_AMPLITUDE * np.cos(k * (x - x_e) - theta),
                x_range=[*DS_X, 0.01],
                color=FIELD_COLOR, stroke_width=FIELD_STROKE_WIDTH,
            ).set_stroke(opacity=self.wave_opacity.get_value())

        self.add(*bodies)
        self.add(always_redraw(wave))
        self.play(FadeIn(title), run_time=0.8)
        labels = VGroup(Tex(
            r"Earth", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
        ).to_corner(DL, buff=0.5))
        self.play(FadeIn(labels), run_time=0.6)

        # --- the heavy end: the Earth --------------------------------------------
        marks = self.wavelength_marks(
            AION_MASSES[1], r"\lambda_C \approx 1200\ \text{km}",
            r"240\ \text{Hz}", r"heavy end of AION's range",
        )
        # The mark faded in as a still and swapped for the live one, which
        # an always_redraw has to be: it cannot be faded itself.
        still = mark()
        self.play(
            FadeIn(formula), FadeIn(marks), FadeIn(inset), FadeIn(still),
            self.wave_opacity.animate.set_value(1.0),
            self.theta.animate.increment_value(TAU * 0.5),
            rate_func=linear, run_time=DS_PERIOD / 2,
        )
        self.remove(still)
        self.add(always_redraw(mark))
        self.play(
            self.theta.animate.increment_value(TAU * 0.5),
            rate_func=linear, run_time=DS_PERIOD / 2,
        )
        self.hold()

        # --- the middle of the range: out to the Moon ---------------------------
        self.fly_to(VIEW_MOON, MOON_MASS, [labels, marks])
        labels = self.body_labels(("Earth", 0.0, EARTH_RADIUS), ("Moon", EARTH_MOON, MOON_RADIUS))
        marks = self.wavelength_marks(
            MOON_MASS, r"\lambda_C \approx \text{Earth--Moon}", r"0.8\ \text{Hz}",
        )
        self.reveal(labels, marks)
        self.hold()

        # --- the light end: out to the Sun --------------------------------------
        self.fly_to(VIEW_SUN, AION_MASSES[0], [labels, marks])
        labels = self.body_labels(("Earth", 0.0, EARTH_RADIUS), ("Sun", EARTH_SUN, SUN_RADIUS))
        marks = self.wavelength_marks(
            AION_MASSES[0], r"\lambda_C \approx 0.8\ \text{AU}",
            r"2.4\ \text{mHz}", r"light end of AION's range",
        )
        self.reveal(labels, marks)
        self.hold()

        # --- and so, in the lab ---------------------------------------------------
        # Even the heavy end is a thousand kilometres: a lab never sees the
        # wave's shape, only the field rising and falling where it is.
        verdict = Tex(
            r"any lab sits inside one wavelength: it sees only $\phi(t)$",
            font_size=FONT_ANNOTATION,
        ).to_edge(DOWN, buff=0.35)
        self.play(
            FadeIn(verdict, shift=UP * 0.15),
            self.theta.animate.increment_value(TAU * 0.5),
            rate_func=linear, run_time=DS_PERIOD / 2,
        )
        self.play(
            self.theta.animate.increment_value(TAU * 0.5),
            rate_func=linear, run_time=DS_PERIOD / 2,
        )
        self.hold()

    # --- pieces ---------------------------------------------------------------
    def screen_x(self, metres):
        return self.earth_x.get_value() + metres / 10 ** self.log_scale.get_value()

    def body_labels(self, *named):
        """A name under each body, at the current view: (name, x, radius)."""
        group = VGroup()
        for name, metres, radius in named:
            r = max(radius / 10 ** self.log_scale.get_value(), BODY_MIN_RADIUS)
            group.add(Tex(
                name, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ).move_to([self.screen_x(metres), self.earth_y.get_value() + r + 0.35, 0]))
        return group

    def wavelength_marks(self, mass, wavelength, frequency, note=None):
        """One wavelength braced under the wave, and the numbers for this mass.

        The brace starts at the Earth: in the Moon view that puts its far end
        on the Moon, which is the comparison being made. The m_phi at the foot
        of the inset's mark comes and goes with the numbers, while the mark
        itself slides.
        """
        start = self.screen_x(0.0)
        end = self.screen_x(compton(mass))
        span = Line([start, 0, 0], [end, 0, 0])
        brace = Brace(span, DOWN, buff=0, color=lighten(GUIDE_COLOR))
        brace.shift(UP * (DS_Y - DS_AMPLITUDE - 0.15 - brace.get_top()[1]))
        tag = MathTex(r"\lambda_C", font_size=FONT_LEGEND, color=FIELD_COLOR)
        tag.next_to(brace, DOWN, buff=0.1)

        exponent = int(np.floor(np.log10(mass)))
        mantissa = mass / 10 ** exponent
        mass_tex = (
            rf"10^{{{exponent}}}" if np.isclose(mantissa, 1)
            else rf"{mantissa:.0f}\times 10^{{{exponent}}}"
        )
        rows = [
            MathTex(rf"m_\phi \approx {mass_tex}\ \text{{eV}}", font_size=FONT_ANNOTATION),
            MathTex(wavelength, font_size=FONT_ANNOTATION, color=FIELD_COLOR),
            MathTex(rf"f = m_\phi c^2/h \approx {frequency}", font_size=FONT_LEGEND,
                    color=lighten(GUIDE_COLOR)),
        ]
        if note is not None:
            rows.append(Tex(note, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)))
        stats = VGroup(*rows).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        stats.move_to(DS_STATS, aligned_edge=UL)
        return VGroup(brace, tag, stats, mass_label(self.inset_axes, mass))

    def fly_to(self, view, mass, outgoing):
        """Move the camera to `view`, with the wave out of sight while it goes.

        A wave drawn at a fixed wavelength in metres would alias into noise on
        the way through a factor of hundreds in scale, so it fades, changes
        mass while it is gone, and comes back in reveal().
        """
        self.play(
            *[FadeOut(m) for m in outgoing],
            self.wave_opacity.animate.set_value(0.0),
            run_time=0.6,
        )
        self.play(
            self.log_scale.animate.set_value(np.log10(view[0])),
            self.earth_x.animate.set_value(view[1]),
            self.earth_y.animate.set_value(view[2]),
            self.log_mass.animate.set_value(np.log10(mass)),
            run_time=DS_ZOOM_TIME, rate_func=smooth,
        )
        self.wavelength = compton(mass)

    def reveal(self, labels, marks):
        self.play(
            FadeIn(labels), FadeIn(marks),
            self.wave_opacity.animate.set_value(1.0),
            self.theta.animate.increment_value(TAU * 0.5),
            rate_func=linear, run_time=DS_PERIOD / 2,
        )
        self.play(
            self.theta.animate.increment_value(TAU * 0.5),
            rate_func=linear, run_time=DS_PERIOD / 2,
        )
