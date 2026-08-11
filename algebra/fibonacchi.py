from __future__ import annotations

"""
FIBONACCI — A CINEMATIC MANIM YOUTUBE SHORT
============================================

A self-contained vertical Manim short that visualizes the Fibonacci sequence,
its recursive rule, Fibonacci squares, a continuous quarter-circle spiral,
neighboring ratios approaching the golden ratio, and a related golden-angle
packing pattern.

The workflow intentionally feels like a production renderer:
- quick validation mode
- dedicated output + previews folders
- preview PNGs captured during the render
- contact sheet generation
- clear overall percentage milestones in the terminal
- Manim's own per-animation progress bars
- JSON summary / render manifest
- final MP4 copied to a predictable output path when launched with Python

Install
-------
    pip install manim pillow

Normal vertical render
----------------------
    python fibonacci_youtube_short.py

Fast validation render
----------------------
    FIBONACCI_SHORT_QUICK=1 python fibonacci_youtube_short.py

Direct Manim usage also works
-----------------------------
    manim -pqh fibonacci_youtube_short.py FibonacciShort

Outputs
-------
    fibonacci_short_output/
        fibonacci_short.mp4              # when launched with python
        fibonacci_short_summary.json
        previews/
            01_hook.png
            02_sequence.png
            03_squares.png
            04_spiral.png
            05_ratio.png
            06_growth.png
            07_finale.png
            contact_sheet.jpg
        media/                            # Manim working/render files
        logs/
        
Scientific / mathematical framing
---------------------------------
- The sequence shown begins 1, 1, 2, 3, 5, ... .
- Each term after the first two is the sum of the previous two.
- The drawn spiral is constructed from quarter-circle arcs inside Fibonacci
  squares. It is commonly called a Fibonacci spiral; it approximates, but is
  not exactly, a logarithmic golden spiral.
- Ratios of consecutive Fibonacci numbers approach the golden ratio.
- The final dot pattern is a related golden-angle packing visualization, not a
  claim that every natural spiral follows Fibonacci numbers exactly.

"""

import json
import math
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
from manim import *
from PIL import Image as PILImage


# =============================================================================
# Configuration
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = BASE_DIR / "fibonacci_short_output"
PREVIEW_DIR = OUTPUT_ROOT / "previews"
MEDIA_DIR = OUTPUT_ROOT / "media"
LOG_DIR = OUTPUT_ROOT / "logs"
for directory in (OUTPUT_ROOT, PREVIEW_DIR, MEDIA_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

QUICK_MODE = os.environ.get("FIBONACCI_SHORT_QUICK", "0") == "1"

if QUICK_MODE:
    config.pixel_width = 540
    config.pixel_height = 960
    config.frame_rate = 15
    TIME_SCALE = 0.34
else:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_rate = 30
    TIME_SCALE = 1.0

config.frame_width = 9
config.frame_height = 16
config.media_dir = str(MEDIA_DIR)
config.background_color = "#040713"

BG = "#040713"
PANEL = "#0A1021"
WHITE = "#F6F8FF"
MUTED = "#9AA8C2"
CYAN = "#67E8F9"
GOLD = "#F8C15C"
VIOLET = "#A78BFA"
GREEN = "#7EE2A8"
PINK = "#F48FB1"
BLUE = "#78A7FF"

SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

SHOT_PLAN = [
    ("hook", 0, 12),
    ("sequence", 12, 34),
    ("squares", 34, 55),
    ("spiral", 55, 72),
    ("ratio", 72, 86),
    ("growth", 86, 96),
    ("finale", 96, 100),
]


def rt(seconds: float) -> float:
    """Animation runtime scaled for quick-mode validation."""
    return max(0.05, seconds * TIME_SCALE)


def hold(seconds: float) -> float:
    return max(0.04, seconds * TIME_SCALE)


def fib(n: int) -> list[int]:
    values = [1, 1]
    while len(values) < n:
        values.append(values[-1] + values[-2])
    return values[:n]


def print_progress(percent: int, label: str) -> None:
    width = 28
    percent = max(0, min(100, int(percent)))
    filled = int(round(width * percent / 100))
    bar = "█" * filled + "░" * (width - filled)
    print(f"[FIBONACCI SHORT] [{bar}] {percent:3d}%  {label}", flush=True)


def build_contact_sheet() -> Path | None:
    paths = [
        PREVIEW_DIR / "01_hook.png",
        PREVIEW_DIR / "02_sequence.png",
        PREVIEW_DIR / "03_squares.png",
        PREVIEW_DIR / "04_spiral.png",
        PREVIEW_DIR / "05_ratio.png",
        PREVIEW_DIR / "06_growth.png",
        PREVIEW_DIR / "07_finale.png",
    ]
    paths = [path for path in paths if path.exists()]
    if not paths:
        return None

    thumb_w = 240 if QUICK_MODE else 360
    thumb_h = int(round(thumb_w * 16 / 9))
    cols = 4
    rows = math.ceil(len(paths) / cols)
    sheet = PILImage.new("RGB", (thumb_w * cols, thumb_h * rows), (4, 7, 19))

    for index, path in enumerate(paths):
        image = PILImage.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), PILImage.Resampling.LANCZOS)
        canvas = PILImage.new("RGB", (thumb_w, thumb_h), (4, 7, 19))
        x = (thumb_w - image.width) // 2
        y = (thumb_h - image.height) // 2
        canvas.paste(image, (x, y))
        sheet.paste(canvas, ((index % cols) * thumb_w, (index // cols) * thumb_h))

    output = PREVIEW_DIR / "contact_sheet.jpg"
    sheet.save(output, quality=92)
    return output


def write_summary(final_video: Path | None = None) -> Path:
    preview_files = [path.name for path in sorted(PREVIEW_DIR.glob("*.png"))]
    payload = {
        "title": "The Fibonacci Sequence Builds a Spiral",
        "format": "9:16 vertical YouTube Short",
        "engine": "Manim Community Edition",
        "quick_mode": QUICK_MODE,
        "resolution": [config.pixel_width, config.pixel_height],
        "fps": config.frame_rate,
        "sequence": SEQUENCE,
        "chapters": [name for name, _, _ in SHOT_PLAN],
        "preview_files": preview_files,
        "contact_sheet": str((PREVIEW_DIR / "contact_sheet.jpg").resolve())
        if (PREVIEW_DIR / "contact_sheet.jpg").exists()
        else None,
        "final_video": str(final_video.resolve()) if final_video and final_video.exists() else None,
        "rendered_at_utc": datetime.now(timezone.utc).isoformat(),
        "notes": [
            "Fibonacci spiral uses quarter-circle arcs inside Fibonacci squares.",
            "The Fibonacci spiral is an approximation to a logarithmic golden spiral.",
            "The golden-angle dot pattern is a related mathematical visualization, not a universal model of plant growth.",
        ],
    }
    path = OUTPUT_ROOT / "fibonacci_short_summary.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


# =============================================================================
# Scene
# =============================================================================

class FibonacciShort(Scene):
    def setup(self):
        self.camera.background_color = BG
        self._preview_paths: list[Path] = []
        print_progress(0, "Starting Manim scene")

        # Persistent cinematic background field.
        rng = np.random.default_rng(20260810)
        count = 55 if QUICK_MODE else 120
        stars = VGroup()
        for _ in range(count):
            x = rng.uniform(-4.25, 4.25)
            y = rng.uniform(-7.7, 7.7)
            radius = rng.uniform(0.006, 0.020)
            opacity = rng.uniform(0.10, 0.38)
            dot = Dot([x, y, 0], radius=radius, color=WHITE, fill_opacity=opacity, stroke_opacity=0)
            stars.add(dot)

        atmosphere = VGroup(
            Circle(radius=3.2, stroke_color=CYAN, stroke_opacity=0.035, stroke_width=16).move_to(DOWN * 1.7),
            Circle(radius=2.2, stroke_color=VIOLET, stroke_opacity=0.035, stroke_width=12).move_to(DOWN * 1.7),
        )
        self.add(stars, atmosphere)

    def construct(self):
        self.section_hook()
        self.section_sequence()
        self.section_squares_and_spiral()
        self.section_ratio()
        self.section_growth()
        self.section_finale()

        contact = build_contact_sheet()
        write_summary()
        if contact:
            print(f"Preview contact sheet: {contact.resolve()}")
        print_progress(100, "Scene complete")

    # ------------------------------------------------------------------
    # Production helpers
    # ------------------------------------------------------------------

    def save_preview(self, filename: str, percent: int, label: str) -> None:
        path = PREVIEW_DIR / filename
        try:
            # After a play()/wait(), the renderer camera already contains the
            # current frame. update_frame is attempted for extra robustness.
            try:
                self.renderer.update_frame(self)
            except Exception:
                pass
            image = self.renderer.camera.get_image()
            image.save(path)
            self._preview_paths.append(path)
            print(f"Preview saved: {path.resolve()}")
        except Exception as exc:
            print(f"Preview capture skipped ({filename}): {exc}")
        print_progress(percent, label)

    def safe_fade_all(self, *keep: Mobject, run_time: float = 0.5) -> None:
        keep_ids = {id(obj) for obj in keep}
        removable = [mob for mob in list(self.mobjects) if id(mob) not in keep_ids]
        # Stars/background were added first. Preserve low-opacity background field
        # by only removing prominent scene objects.
        prominent = [mob for mob in removable if getattr(mob, "z_index", 0) >= 0]
        if prominent:
            self.play(*[FadeOut(mob) for mob in prominent], run_time=rt(run_time))

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def heading(self, text: str, color: str = WHITE) -> Mobject:
        return Text(text, font_size=40, weight=BOLD, color=color).move_to(UP * 6.45)

    def eyebrow(self, text: str, color: str = MUTED) -> Mobject:
        return Text(text, font_size=20, weight=BOLD, color=color).move_to(UP * 7.18)

    def caption(self, text: str, accent: str = CYAN) -> VGroup:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if len(candidate) <= 45:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        copy = Text("\n".join(lines), font_size=27, color=WHITE, line_spacing=0.92)
        if copy.width > 7.4:
            copy.scale_to_fit_width(7.4)
        panel = RoundedRectangle(
            corner_radius=0.20,
            width=8.0,
            height=max(1.12, copy.height + 0.48),
            stroke_color=accent,
            stroke_opacity=0.20,
            fill_color=PANEL,
            fill_opacity=0.91,
        ).move_to(DOWN * 6.18)
        copy.move_to(panel.get_center())
        return VGroup(panel, copy)

    def top_progress_line(self, step: int, total: int = 6) -> VGroup:
        y = 5.78
        line = Line(LEFT * 3.25, RIGHT * 3.25, color=MUTED, stroke_opacity=0.20, stroke_width=3).move_to(UP * y)
        active = Line(
            LEFT * 3.25,
            LEFT * 3.25 + RIGHT * (6.5 * step / total),
            color=CYAN,
            stroke_width=5,
        ).move_to(UP * y)
        dots = VGroup()
        for i in range(total + 1):
            x = -3.25 + 6.5 * i / total
            color = GOLD if i <= step else MUTED
            opacity = 0.92 if i <= step else 0.25
            dots.add(Dot([x, y, 0], radius=0.055, color=color, fill_opacity=opacity, stroke_opacity=0))
        return VGroup(line, active, dots)

    # ------------------------------------------------------------------
    # 1. Hook
    # ------------------------------------------------------------------

    def section_hook(self):
        eyebrow = self.eyebrow("MATHEMATICS // VISUALIZED", CYAN)
        title = Text(
            "ONE RULE\nBUILDS THIS",
            font_size=72,
            weight=BOLD,
            color=WHITE,
            line_spacing=0.86,
        ).move_to(UP * 2.6)

        numbers = Text("1  1  2  3  5  8  13  21...", font_size=35, color=GOLD).next_to(title, DOWN, buff=0.52)

        spiral = ParametricFunction(
            lambda t: np.array([0.095 * t * math.cos(t), 0.095 * t * math.sin(t), 0]),
            t_range=[0, 6.1 * math.pi],
            color=CYAN,
            stroke_width=7,
        ).scale(1.02).move_to(DOWN * 2.15)

        rings = VGroup(
            Circle(radius=1.45, color=CYAN, stroke_width=18, stroke_opacity=0.08),
            Circle(radius=1.85, color=VIOLET, stroke_width=12, stroke_opacity=0.05),
        ).move_to(DOWN * 2.15)

        caption = self.caption("The Fibonacci sequence starts small, then builds itself one number at a time.", GOLD)

        self.play(FadeIn(eyebrow, shift=UP * 0.15), run_time=rt(0.45))
        self.play(FadeIn(title, shift=UP * 0.25), run_time=rt(0.75))
        self.play(Write(numbers), run_time=rt(0.65))
        self.play(FadeIn(rings), Create(spiral), run_time=rt(1.35))
        self.play(FadeIn(caption), run_time=rt(0.30))
        self.wait(hold(0.8))
        self.save_preview("01_hook.png", 12, "Hook complete")

        self.play(*[FadeOut(m) for m in (eyebrow, title, numbers, spiral, rings, caption)], run_time=rt(0.55))

    # ------------------------------------------------------------------
    # 2. Recursive sequence
    # ------------------------------------------------------------------

    def section_sequence(self):
        heading = self.heading("EACH NUMBER USES THE TWO BEFORE IT", GOLD)
        progress = self.top_progress_line(1)
        self.play(FadeIn(heading, shift=UP * 0.15), FadeIn(progress), run_time=rt(0.5))

        nums = fib(10)
        number_cards = VGroup()
        number_texts = VGroup()
        for value in nums:
            card = RoundedRectangle(
                corner_radius=0.12,
                width=0.72 if value < 10 else 0.84,
                height=0.80,
                stroke_color=CYAN,
                stroke_opacity=0.22,
                fill_color=PANEL,
                fill_opacity=0.88,
            )
            txt = Integer(value, font_size=39, color=WHITE)
            txt.move_to(card)
            group = VGroup(card, txt)
            number_cards.add(group)
            number_texts.add(txt)

        number_cards.arrange(RIGHT, buff=0.10)
        number_cards.scale_to_fit_width(8.0)
        number_cards.move_to(UP * 2.0)

        self.play(FadeIn(number_cards[0], scale=0.7), FadeIn(number_cards[1], scale=0.7), run_time=rt(0.5))

        equation_box = RoundedRectangle(
            corner_radius=0.18,
            width=6.5,
            height=1.35,
            stroke_color=VIOLET,
            stroke_opacity=0.25,
            fill_color=PANEL,
            fill_opacity=0.76,
        ).move_to(DOWN * 0.2)
        self.play(FadeIn(equation_box), run_time=rt(0.25))

        equation = None
        for i in range(2, len(nums)):
            if equation is not None:
                self.play(FadeOut(equation), run_time=rt(0.12))

            a = number_texts[i - 2]
            b = number_texts[i - 1]
            c = number_texts[i]
            equation = Text(
                f"{nums[i-2]}  +  {nums[i-1]}  =  {nums[i]}",
                font_size=47,
                weight=BOLD,
                color=WHITE,
            ).move_to(equation_box)
            equation[-len(str(nums[i])):].set_color(GOLD)

            self.play(
                a.animate.set_color(CYAN).scale(1.12),
                b.animate.set_color(CYAN).scale(1.12),
                FadeIn(equation, shift=UP * 0.10),
                run_time=rt(0.28),
            )
            self.play(FadeIn(number_cards[i], scale=0.70), c.animate.set_color(GOLD), run_time=rt(0.24))
            self.play(
                a.animate.set_color(WHITE).scale(1 / 1.12),
                b.animate.set_color(WHITE).scale(1 / 1.12),
                c.animate.set_color(WHITE),
                run_time=rt(0.18),
            )

        caption = self.caption("Add the previous two terms. Repeat. The sequence keeps growing.", CYAN)
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.75))
        self.save_preview("02_sequence.png", 34, "Recursive sequence complete")

        to_fade: list[Mobject] = [heading, progress, number_cards, equation_box, caption]
        if equation is not None:
            to_fade.append(equation)
        self.play(*[FadeOut(m) for m in to_fade], run_time=rt(0.55))

    # ------------------------------------------------------------------
    # 3 + 4. Fibonacci squares and continuous quarter-circle spiral
    # ------------------------------------------------------------------

    def section_squares_and_spiral(self):
        heading = self.heading("TURN THE NUMBERS INTO SQUARES", VIOLET)
        progress = self.top_progress_line(2)
        self.play(FadeIn(heading), FadeIn(progress), run_time=rt(0.45))

        # Fibonacci tiling coordinates are lower-left corners in a compact grid.
        # These six squares tile one growing rectangle without overlap.
        tile_data = [
            (1, 0.0, 0.0),
            (1, 1.0, 0.0),
            (2, 0.0, 1.0),
            (3, -3.0, 0.0),
            (5, -3.0, -5.0),
            (8, 2.0, -5.0),
        ]
        unit = 0.49
        tiles = VGroup()
        labels = VGroup()

        for side, x, y in tile_data:
            square = Square(
                side_length=side * unit,
                stroke_color=CYAN,
                stroke_width=4,
                fill_color=PANEL,
                fill_opacity=0.12,
            )
            square.move_to([(x + side / 2) * unit, (y + side / 2) * unit, 0])
            label = Integer(side, font_size=max(22, int(42 - side * 1.5)), color=GOLD).move_to(square)
            tiles.add(square)
            labels.add(label)

        tiling = VGroup(tiles, labels).move_to(DOWN * 0.65).scale(0.94)

        for square, label in zip(tiles, labels):
            self.play(Create(square), FadeIn(label, scale=0.60), run_time=rt(0.38))

        caption = self.caption("Use Fibonacci numbers as square side lengths and a larger rectangle emerges.", VIOLET)
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.55))
        self.save_preview("03_squares.png", 55, "Fibonacci squares complete")
        self.play(FadeOut(caption), run_time=rt(0.25))

        new_heading = self.heading("CONNECT QUARTER-CIRCLES", CYAN)
        self.play(Transform(heading, new_heading), Transform(progress, self.top_progress_line(3)), run_time=rt(0.45))

        # Continuous arc chain, from the smallest square outward.
        arc_specs = [
            (unit * 0.94, tiles[0].get_corner(DL), PI / 2, -PI / 2),
            (unit * 0.94, tiles[1].get_corner(UL), -PI / 2, PI / 2),
            (2 * unit * 0.94, tiles[2].get_corner(DL), 0, PI / 2),
            (3 * unit * 0.94, tiles[3].get_corner(DR), PI / 2, PI / 2),
            (5 * unit * 0.94, tiles[4].get_corner(UR), PI, PI / 2),
            (8 * unit * 0.94, tiles[5].get_corner(UL), 3 * PI / 2, PI / 2),
        ]
        arcs = VGroup()
        for radius, center, start, angle in arc_specs:
            arc = Arc(radius=radius, start_angle=start, angle=angle, color=GOLD, stroke_width=8)
            arc.move_arc_center_to(center)
            arcs.add(arc)

        self.play(
            *[square.animate.set_stroke(opacity=0.34) for square in tiles],
            *[label.animate.set_opacity(0.30) for label in labels],
            run_time=rt(0.40),
        )
        self.play(LaggedStart(*[Create(arc) for arc in arcs], lag_ratio=0.13), run_time=rt(2.0))

        spiral_caption = self.caption(
            "Quarter-circle arcs form the Fibonacci spiral — a geometric approximation to a golden spiral.",
            GOLD,
        )
        self.play(FadeIn(spiral_caption), run_time=rt(0.28))
        self.wait(hold(0.85))
        self.save_preview("04_spiral.png", 72, "Spiral construction complete")

        self.play(*[FadeOut(m) for m in (heading, progress, tiling, arcs, spiral_caption)], run_time=rt(0.6))

    # ------------------------------------------------------------------
    # 5. Ratio convergence
    # ------------------------------------------------------------------

    def section_ratio(self):
        heading = self.heading("THE RATIOS SETTLE TOWARD 1.618", GOLD)
        progress = self.top_progress_line(4)
        self.play(FadeIn(heading), FadeIn(progress), run_time=rt(0.45))

        pairs = [(8, 5), (13, 8), (21, 13), (34, 21), (55, 34), (89, 55)]
        rows = VGroup()
        for top, bottom in pairs:
            ratio = top / bottom
            row = VGroup(
                Text(f"{top} ÷ {bottom}", font_size=30, color=WHITE),
                Text(f"{ratio:.4f}", font_size=31, weight=BOLD, color=CYAN),
            ).arrange(RIGHT, buff=0.9)
            rows.add(row)
        rows.arrange(DOWN, buff=0.23, aligned_edge=LEFT).move_to(UP * 0.7)

        target = Text("φ  ≈  1.618034", font_size=52, weight=BOLD, color=GOLD).move_to(DOWN * 2.5)
        target_ring = RoundedRectangle(
            corner_radius=0.18,
            width=5.6,
            height=1.25,
            stroke_color=GOLD,
            stroke_opacity=0.35,
            fill_color=PANEL,
            fill_opacity=0.78,
        ).move_to(target)

        for index, row in enumerate(rows):
            self.play(FadeIn(row, shift=RIGHT * 0.16), run_time=rt(0.28))
            if index >= 2:
                self.play(row[1].animate.set_color(GOLD), run_time=rt(0.12))

        self.play(FadeIn(target_ring), FadeIn(target, scale=0.75), run_time=rt(0.55))
        caption = self.caption("Consecutive Fibonacci ratios get closer and closer to the golden ratio.", GOLD)
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.65))
        self.save_preview("05_ratio.png", 86, "Golden-ratio convergence complete")

        self.play(*[FadeOut(m) for m in (heading, progress, rows, target_ring, target, caption)], run_time=rt(0.55))

    # ------------------------------------------------------------------
    # 6. Related golden-angle packing visual
    # ------------------------------------------------------------------

    def section_growth(self):
        heading = self.heading("A RELATED PATTERN APPEARS IN GROWTH", GREEN)
        progress = self.top_progress_line(5)
        self.play(FadeIn(heading), FadeIn(progress), run_time=rt(0.45))

        golden_angle = math.radians(137.50776405003785)
        count = 70 if QUICK_MODE else 125
        dots = VGroup()
        for n in range(1, count + 1):
            r = 0.31 * math.sqrt(n)
            theta = n * golden_angle
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            color = CYAN if n % 3 else GOLD
            dot = Dot([x, y, 0], radius=0.045 if QUICK_MODE else 0.040, color=color, stroke_opacity=0)
            dots.add(dot)
        dots.scale(0.80).move_to(DOWN * 0.6)

        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in dots], lag_ratio=0.018), run_time=rt(2.15))

        angle_text = Text("GOLDEN ANGLE  ≈  137.5°", font_size=31, weight=BOLD, color=GOLD).move_to(DOWN * 4.7)
        self.play(FadeIn(angle_text, shift=UP * 0.12), run_time=rt(0.38))

        caption = self.caption(
            "Golden-angle packing is related to Fibonacci ratios and appears in some plant growth patterns.",
            GREEN,
        )
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.70))
        self.save_preview("06_growth.png", 96, "Related growth pattern complete")

        self.play(*[FadeOut(m) for m in (heading, progress, dots, angle_text, caption)], run_time=rt(0.55))

    # ------------------------------------------------------------------
    # 7. Finale
    # ------------------------------------------------------------------

    def section_finale(self):
        eyebrow = self.eyebrow("ONE RECURSIVE IDEA", CYAN)
        final_numbers = Text("1  1  2  3  5  8  13  21  34", font_size=34, color=GOLD).move_to(UP * 4.4)
        final_title = Text(
            "ADD THE LAST TWO.\nWATCH THE PATTERN GROW.",
            font_size=58,
            weight=BOLD,
            color=WHITE,
            line_spacing=0.90,
        ).move_to(UP * 1.8)

        spiral = ParametricFunction(
            lambda t: np.array([0.095 * t * math.cos(t), 0.095 * t * math.sin(t), 0]),
            t_range=[0, 6.4 * math.pi],
            color=CYAN,
            stroke_width=8,
        ).scale(1.08).move_to(DOWN * 2.25)

        gold_dot = Dot(spiral.get_end(), radius=0.10, color=GOLD)
        caption = self.caption("That is the Fibonacci sequence: a tiny rule with a surprisingly rich geometry.", CYAN)

        self.play(FadeIn(eyebrow), Write(final_numbers), run_time=rt(0.6))
        self.play(FadeIn(final_title, shift=UP * 0.20), run_time=rt(0.7))
        self.play(Create(spiral), run_time=rt(1.65))
        self.play(GrowFromCenter(gold_dot), FadeIn(caption), run_time=rt(0.42))
        self.wait(hold(1.0))
        self.save_preview("07_finale.png", 99, "Final frame captured")


# =============================================================================
# Python launcher — predictable production workflow
# =============================================================================

def locate_rendered_video() -> Path | None:
    candidates = [
        path
        for path in MEDIA_DIR.rglob("*.mp4")
        if "partial_movie_files" not in path.parts and path.is_file()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def launch_render() -> int:
    print("=" * 72)
    print("FIBONACCI MANIM YOUTUBE SHORT")
    print("=" * 72)
    print("Mode:", "QUICK VALIDATION" if QUICK_MODE else "FULL 1080x1920")
    print("Resolution:", f"{config.pixel_width}x{config.pixel_height}")
    print("FPS:", config.frame_rate)
    print("Output root:", OUTPUT_ROOT.resolve())
    print("Previews:", PREVIEW_DIR.resolve())
    print()

    quality_flag = "-ql" if QUICK_MODE else "-qh"
    command = [
        sys.executable,
        "-m",
        "manim",
        quality_flag,
        "--media_dir",
        str(MEDIA_DIR),
        "--log_dir",
        str(LOG_DIR),
        "--progress_bar",
        "leave",
        "-o",
        "fibonacci_short",
        str(Path(__file__).resolve()),
        "FibonacciShort",
    ]

    print("Running:", " ".join(command))
    print("Manim will show per-animation progress; this script also reports overall milestones.\n")
    result = subprocess.run(command)

    final_video: Path | None = None
    if result.returncode == 0:
        rendered = locate_rendered_video()
        if rendered:
            final_video = OUTPUT_ROOT / "fibonacci_short.mp4"
            if rendered.resolve() != final_video.resolve():
                shutil.copy2(rendered, final_video)
        build_contact_sheet()
        summary = write_summary(final_video)

        print("\nRender complete")
        if final_video and final_video.exists():
            print("Final video:   ", final_video.resolve())
        else:
            print("Rendered video remains inside:", MEDIA_DIR.resolve())
        print("Previews:      ", PREVIEW_DIR.resolve())
        print("Contact sheet: ", (PREVIEW_DIR / "contact_sheet.jpg").resolve())
        print("Summary:       ", summary.resolve())
        print_progress(100, "All outputs ready")
    else:
        print(f"\nManim exited with code {result.returncode}")

    return int(result.returncode)

if __name__ == "__main__":
    raise SystemExit(launch_render())
