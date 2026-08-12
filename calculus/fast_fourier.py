from __future__ import annotations

"""
FFT — A CINEMATIC MANIM YOUTUBE SHORT
======================================

A self-contained vertical Manim short that visualizes the Fast Fourier
Transform as a change of viewpoint:

    waveform -> samples -> divide-and-conquer -> frequency peaks

The animation deliberately distinguishes the Fourier transform idea from the
FFT algorithm. The Fourier transform reveals frequency content; the FFT is an
efficient algorithm for computing a discrete Fourier transform.



Install
-------
    pip install manim pillow numpy

Normal vertical render
----------------------
    python fft_youtube_short_pro.py

Fast validation render
----------------------
    FFT_SHORT_QUICK=1 python fft_youtube_short_pro.py

Direct Manim usage
------------------
    manim -pqh fft_youtube_short_pro.py FFTShort

Outputs
-------
    fft_short_output/
        fft_short.mp4
        fft_short_summary.json
        previews/
            01_hook.png
            02_components.png
            03_samples.png
            04_fft_split.png
            05_butterfly.png
            06_spectrum.png
            07_finale.png
            contact_sheet.jpg
        media/
        logs/


"""

import json
import math
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from manim import *
from PIL import Image as PILImage


# =============================================================================
# Configuration
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = BASE_DIR / "fft_short_output"
PREVIEW_DIR = OUTPUT_ROOT / "previews"
MEDIA_DIR = OUTPUT_ROOT / "media"
LOG_DIR = OUTPUT_ROOT / "logs"
for directory in (OUTPUT_ROOT, PREVIEW_DIR, MEDIA_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

QUICK_MODE = os.environ.get("FFT_SHORT_QUICK", "0") == "1"

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
RED = "#FB7185"

SAMPLE_COUNT = 64
DURATION_S = 1.0
COMPONENTS = [
    (2.0, 1.00, CYAN),
    (5.0, 0.65, GOLD),
    (8.0, 0.35, VIOLET),
]

SHOT_PLAN = [
    ("hook", 0, 12),
    ("components", 12, 28),
    ("samples", 28, 43),
    ("fft_split", 43, 60),
    ("butterfly", 60, 76),
    ("spectrum", 76, 90),
    ("finale", 90, 100),
]


# =============================================================================
# Numeric signal used by the visuals
# =============================================================================

SAMPLE_T = np.arange(SAMPLE_COUNT, dtype=float) / SAMPLE_COUNT
SAMPLE_SIGNAL = sum(
    amplitude * np.sin(2 * np.pi * frequency * SAMPLE_T)
    for frequency, amplitude, _ in COMPONENTS
)
FFT_VALUES = np.fft.rfft(SAMPLE_SIGNAL)
FFT_MAG = np.abs(FFT_VALUES) / (SAMPLE_COUNT / 2.0)
FFT_FREQS = np.fft.rfftfreq(SAMPLE_COUNT, d=DURATION_S / SAMPLE_COUNT)


def signal_value(t: float) -> float:
    return float(
        sum(
            amplitude * math.sin(2.0 * math.pi * frequency * t)
            for frequency, amplitude, _ in COMPONENTS
        )
    )


# =============================================================================
# Production helpers
# =============================================================================

def rt(seconds: float) -> float:
    return max(0.05, seconds * TIME_SCALE)


def hold(seconds: float) -> float:
    return max(0.04, seconds * TIME_SCALE)


def print_progress(percent: int, label: str) -> None:
    width = 28
    percent = max(0, min(100, int(percent)))
    filled = int(round(width * percent / 100))
    bar = "█" * filled + "░" * (width - filled)
    print(f"[FFT SHORT]       [{bar}] {percent:3d}%  {label}", flush=True)


def build_contact_sheet() -> Path | None:
    paths = [
        PREVIEW_DIR / "01_hook.png",
        PREVIEW_DIR / "02_components.png",
        PREVIEW_DIR / "03_samples.png",
        PREVIEW_DIR / "04_fft_split.png",
        PREVIEW_DIR / "05_butterfly.png",
        PREVIEW_DIR / "06_spectrum.png",
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
    peaks = []
    for frequency, magnitude in zip(FFT_FREQS, FFT_MAG):
        if magnitude > 0.20:
            peaks.append(
                {
                    "frequency_hz": float(frequency),
                    "normalized_magnitude": float(magnitude),
                }
            )

    payload = {
        "title": "FFT — How a Messy Wave Reveals Hidden Frequencies",
        "format": "9:16 vertical YouTube Short",
        "engine": "Manim Community Edition",
        "quick_mode": QUICK_MODE,
        "resolution": [config.pixel_width, config.pixel_height],
        "fps": config.frame_rate,
        "sample_count": SAMPLE_COUNT,
        "synthetic_components_hz": [frequency for frequency, _, _ in COMPONENTS],
        "synthetic_component_amplitudes": [amplitude for _, amplitude, _ in COMPONENTS],
        "fft_detected_peaks": peaks,
        "chapters": [name for name, _, _ in SHOT_PLAN],
        "preview_files": [path.name for path in sorted(PREVIEW_DIR.glob("*.png"))],
        "contact_sheet": str((PREVIEW_DIR / "contact_sheet.jpg").resolve())
        if (PREVIEW_DIR / "contact_sheet.jpg").exists()
        else None,
        "final_video": str(final_video.resolve()) if final_video and final_video.exists() else None,
        "rendered_at_utc": datetime.now(timezone.utc).isoformat(),
        "notes": [
            "The Fourier transform is the mathematical transform; the FFT is an efficient algorithm for computing a DFT.",
            "The spectrum shown is calculated from the synthetic sampled waveform using numpy.fft.rfft.",
            "The N² and N log₂N numbers shown are asymptotic scaling terms, not exact instruction counts.",
        ],
    }
    path = OUTPUT_ROOT / "fft_short_summary.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


# =============================================================================
# Scene
# =============================================================================

class FFTShort(Scene):
    def setup(self):
        self.camera.background_color = BG
        self._preview_paths: list[Path] = []
        print_progress(0, "Starting Manim scene")

        rng = np.random.default_rng(20260810)
        count = 55 if QUICK_MODE else 120
        stars = VGroup()

        for _ in range(count):
            dot = Dot(
                [
                    rng.uniform(-4.25, 4.25),
                    rng.uniform(-7.7, 7.7),
                    0,
                ],
                radius=rng.uniform(0.006, 0.020),
                color=WHITE,
                fill_opacity=rng.uniform(0.10, 0.35),
                stroke_opacity=0,
            )
            stars.add(dot)

        atmosphere = VGroup(
            Circle(radius=3.1, stroke_color=CYAN, stroke_opacity=0.030, stroke_width=16).move_to(DOWN * 1.7),
            Circle(radius=2.2, stroke_color=VIOLET, stroke_opacity=0.028, stroke_width=12).move_to(DOWN * 1.7),
        )
        self.add(stars, atmosphere)

    def construct(self):
        self.section_hook()
        self.section_components()
        self.section_samples()
        self.section_fft_split()
        self.section_butterfly()
        self.section_spectrum()
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

    # ------------------------------------------------------------------
    # Reusable visual helpers
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
        base = Line(
            LEFT * 3.25,
            RIGHT * 3.25,
            color=MUTED,
            stroke_opacity=0.20,
            stroke_width=3,
        ).move_to(UP * y)

        active = Line(
            LEFT * 3.25,
            LEFT * 3.25 + RIGHT * (6.5 * step / total),
            color=CYAN,
            stroke_width=5,
        ).move_to(UP * y)

        dots = VGroup()
        for i in range(total + 1):
            x = -3.25 + 6.5 * i / total
            dots.add(
                Dot(
                    [x, y, 0],
                    radius=0.055,
                    color=GOLD if i <= step else MUTED,
                    fill_opacity=0.92 if i <= step else 0.25,
                    stroke_opacity=0,
                )
            )
        return VGroup(base, active, dots)

    def make_axes(
        self,
        x_range=(0, 1, 0.25),
        y_range=(-2, 2, 1),
        width=7.7,
        height=4.1,
    ) -> Axes:
        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=width,
            y_length=height,
            axis_config={
                "color": MUTED,
                "stroke_opacity": 0.40,
                "stroke_width": 2,
                "include_ticks": False,
                "include_tip": False,
            },
        )
        return axes

    def waveform(
        self,
        axes: Axes,
        fn,
        color: str,
        stroke_width: float = 5,
        opacity: float = 1.0,
    ) -> ParametricFunction:
        graph = axes.plot(
            fn,
            x_range=[0, 1, 1 / 180],
            color=color,
            stroke_width=stroke_width,
        )
        graph.set_stroke(opacity=opacity)
        return graph

    def small_frequency_chip(self, text: str, color: str) -> VGroup:
        box = RoundedRectangle(
            corner_radius=0.14,
            width=1.75,
            height=0.70,
            stroke_color=color,
            stroke_opacity=0.35,
            fill_color=PANEL,
            fill_opacity=0.90,
        )
        copy = Text(text, font_size=25, weight=BOLD, color=color).move_to(box)
        return VGroup(box, copy)

    # ------------------------------------------------------------------
    # 1. Hook
    # ------------------------------------------------------------------

    def section_hook(self):
        eyebrow = self.eyebrow("SIGNAL PROCESSING // VISUALIZED", CYAN)

        title = Text(
            "THIS MESSY WAVE\nHIDES 3 FREQUENCIES",
            font_size=63,
            weight=BOLD,
            color=WHITE,
            line_spacing=0.86,
        ).move_to(UP * 3.0)

        axes = self.make_axes(width=7.5, height=3.2).move_to(DOWN * 0.4)
        wave = self.waveform(axes, signal_value, CYAN, stroke_width=6)
        baseline = Line(
            axes.c2p(0, 0),
            axes.c2p(1, 0),
            color=MUTED,
            stroke_opacity=0.18,
            stroke_width=2,
        )

        frequency_chips = VGroup(
            self.small_frequency_chip("2 Hz", CYAN),
            self.small_frequency_chip("5 Hz", GOLD),
            self.small_frequency_chip("8 Hz", VIOLET),
        ).arrange(RIGHT, buff=0.22).move_to(DOWN * 3.2)

        question = Text("CAN WE FIND THEM?", font_size=34, weight=BOLD, color=GOLD).move_to(DOWN * 4.25)
        caption = self.caption("The FFT turns a changing signal into a map of its frequencies.", GOLD)

        self.play(FadeIn(eyebrow, shift=UP * 0.15), run_time=rt(0.40))
        self.play(FadeIn(title, shift=UP * 0.25), run_time=rt(0.70))
        self.play(FadeIn(axes), FadeIn(baseline), Create(wave), run_time=rt(1.20))
        self.play(LaggedStart(*[FadeIn(chip, scale=0.75) for chip in frequency_chips], lag_ratio=0.18), run_time=rt(0.75))
        self.play(FadeIn(question, shift=UP * 0.12), FadeIn(caption), run_time=rt(0.35))
        self.wait(hold(0.70))

        self.save_preview("01_hook.png", 12, "Hook complete")

        self.play(
            *[
                FadeOut(m)
                for m in (eyebrow, title, axes, baseline, wave, frequency_chips, question, caption)
            ],
            run_time=rt(0.55),
        )

    # ------------------------------------------------------------------
    # 2. Build the messy waveform from clean components
    # ------------------------------------------------------------------

    def section_components(self):
        heading = self.heading("FIRST: BUILD THE SIGNAL", GOLD)
        progress = self.top_progress_line(1)
        self.play(FadeIn(heading), FadeIn(progress), run_time=rt(0.45))

        axes = self.make_axes(width=7.7, height=2.65).move_to(UP * 1.25)

        component_graphs = VGroup()
        chip_group = VGroup()

        for frequency, amplitude, color in COMPONENTS:
            graph = self.waveform(
                axes,
                lambda t, f=frequency, a=amplitude: a * math.sin(2 * math.pi * f * t),
                color,
                stroke_width=4,
                opacity=0.92,
            )
            component_graphs.add(graph)
            chip_group.add(self.small_frequency_chip(f"{frequency:g} Hz", color))

        chip_group.arrange(RIGHT, buff=0.22).move_to(DOWN * 1.35)

        plus_signs = VGroup(
            Text("+", font_size=34, color=MUTED),
            Text("+", font_size=34, color=MUTED),
        )
        plus_signs[0].move_to((chip_group[0].get_center() + chip_group[1].get_center()) / 2)
        plus_signs[1].move_to((chip_group[1].get_center() + chip_group[2].get_center()) / 2)

        self.play(FadeIn(axes), run_time=rt(0.30))
        for graph, chip in zip(component_graphs, chip_group):
            self.play(Create(graph), FadeIn(chip, scale=0.80), run_time=rt(0.55))
        self.play(FadeIn(plus_signs), run_time=rt(0.20))

        mix_axes = self.make_axes(width=7.7, height=2.65).move_to(DOWN * 3.45)
        mix_wave = self.waveform(mix_axes, signal_value, WHITE, stroke_width=6)
        equals = Text("=", font_size=42, weight=BOLD, color=GOLD).move_to(DOWN * 2.10)

        self.play(FadeIn(equals), FadeIn(mix_axes), Create(mix_wave), run_time=rt(1.0))

        caption = self.caption("Three clean sine waves can combine into one waveform that looks much more complicated.", CYAN)
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.65))

        self.save_preview("02_components.png", 28, "Signal components combined")

        self.play(
            *[
                FadeOut(m)
                for m in (
                    heading,
                    progress,
                    axes,
                    component_graphs,
                    chip_group,
                    plus_signs,
                    mix_axes,
                    mix_wave,
                    equals,
                    caption,
                )
            ],
            run_time=rt(0.58),
        )

    # ------------------------------------------------------------------
    # 3. Sampling
    # ------------------------------------------------------------------

    def section_samples(self):
        heading = self.heading("COMPUTERS SEE SAMPLES", BLUE)
        progress = self.top_progress_line(2)
        self.play(FadeIn(heading), FadeIn(progress), run_time=rt(0.45))

        axes = self.make_axes(width=7.8, height=4.0).move_to(UP * 0.6)
        wave = self.waveform(axes, signal_value, CYAN, stroke_width=4, opacity=0.35)

        visible_samples = 16
        indices = np.linspace(0, SAMPLE_COUNT - 1, visible_samples).round().astype(int)
        dots = VGroup()
        stems = VGroup()

        for index in indices:
            x = SAMPLE_T[index]
            y = SAMPLE_SIGNAL[index]
            p = axes.c2p(float(x), float(y))
            stem = Line(axes.c2p(float(x), 0), p, color=MUTED, stroke_opacity=0.25, stroke_width=2)
            dot = Dot(p, radius=0.085, color=GOLD, stroke_opacity=0)
            stems.add(stem)
            dots.add(dot)

        bits = VGroup()
        for i in range(16):
            label = Text(str(i), font_size=17, color=MUTED)
            label.move_to(axes.c2p(float(SAMPLE_T[indices[i]]), -2.25))
            bits.add(label)

        brace = Brace(VGroup(dots), DOWN, color=VIOLET)
        brace_label = Text("DISCRETE SAMPLES", font_size=24, weight=BOLD, color=VIOLET).next_to(brace, DOWN, buff=0.18)

        self.play(FadeIn(axes), Create(wave), run_time=rt(0.65))
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(Create(stem), GrowFromCenter(dot))
                    for stem, dot in zip(stems, dots)
                ],
                lag_ratio=0.045,
            ),
            run_time=rt(1.30),
        )
        self.play(FadeIn(bits), GrowFromCenter(brace), FadeIn(brace_label), run_time=rt(0.45))

        caption = self.caption("The discrete Fourier transform works on sampled values, not on an infinitely smooth curve.", BLUE)
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.65))

        self.save_preview("03_samples.png", 43, "Sampling stage complete")

        self.play(
            *[FadeOut(m) for m in (heading, progress, axes, wave, stems, dots, bits, brace, brace_label, caption)],
            run_time=rt(0.55),
        )

    # ------------------------------------------------------------------
    # 4. FFT divide-and-conquer split
    # ------------------------------------------------------------------

    def section_fft_split(self):
        heading = self.heading("FFT: SPLIT THE PROBLEM", VIOLET)
        progress = self.top_progress_line(3)
        self.play(FadeIn(heading), FadeIn(progress), run_time=rt(0.45))

        source_values = VGroup()
        for i in range(16):
            node = RoundedRectangle(
                corner_radius=0.08,
                width=0.42,
                height=0.55,
                stroke_color=CYAN,
                stroke_opacity=0.28,
                fill_color=PANEL,
                fill_opacity=0.92,
            )
            txt = Text(str(i), font_size=18, color=WHITE).move_to(node)
            source_values.add(VGroup(node, txt))

        source_values.arrange(RIGHT, buff=0.07).scale_to_fit_width(7.75).move_to(UP * 3.55)
        source_label = Text("16 SAMPLES", font_size=24, weight=BOLD, color=CYAN).next_to(source_values, UP, buff=0.18)

        self.play(FadeIn(source_label), LaggedStart(*[FadeIn(x, scale=0.75) for x in source_values], lag_ratio=0.035), run_time=rt(0.85))

        even = VGroup()
        odd = VGroup()
        for i in range(0, 16, 2):
            even.add(source_values[i].copy())
        for i in range(1, 16, 2):
            odd.add(source_values[i].copy())

        even.arrange(RIGHT, buff=0.10).scale(0.86).move_to(LEFT * 2.05 + UP * 1.55)
        odd.arrange(RIGHT, buff=0.10).scale(0.86).move_to(RIGHT * 2.05 + UP * 1.55)

        even_label = Text("EVEN INDEX", font_size=22, weight=BOLD, color=GOLD).next_to(even, UP, buff=0.18)
        odd_label = Text("ODD INDEX", font_size=22, weight=BOLD, color=VIOLET).next_to(odd, UP, buff=0.18)

        arrows = VGroup(
            Arrow(source_values.get_bottom(), even.get_top(), buff=0.18, color=GOLD, stroke_width=3, max_tip_length_to_length_ratio=0.08),
            Arrow(source_values.get_bottom(), odd.get_top(), buff=0.18, color=VIOLET, stroke_width=3, max_tip_length_to_length_ratio=0.08),
        )

        self.play(Create(arrows), TransformFromCopy(VGroup(*source_values[::2]), even), TransformFromCopy(VGroup(*source_values[1::2]), odd), run_time=rt(1.0))
        self.play(FadeIn(even_label), FadeIn(odd_label), run_time=rt(0.30))

        levels = VGroup()
        level_texts = ["8", "4", "2", "1"]
        y_positions = [0.0, -1.15, -2.30, -3.45]

        previous_y = 1.1
        for level_index, (label, y) in enumerate(zip(level_texts, y_positions)):
            group = VGroup()
            count = 2 ** (level_index + 1)
            boxes_per_branch = min(count, 8)
            spacing = 7.2 / max(boxes_per_branch - 1, 1)
            for i in range(boxes_per_branch):
                x = -3.6 + i * spacing
                box = RoundedRectangle(
                    corner_radius=0.08,
                    width=0.62 if boxes_per_branch <= 4 else 0.48,
                    height=0.48,
                    stroke_color=CYAN if level_index % 2 == 0 else VIOLET,
                    stroke_opacity=0.24,
                    fill_color=PANEL,
                    fill_opacity=0.80,
                ).move_to([x, y, 0])
                group.add(box)
            level_label = Text(
                f"subproblems of size {label}",
                font_size=19,
                color=MUTED,
            ).move_to([0, y - 0.48, 0])
            levels.add(VGroup(group, level_label))
            self.play(FadeIn(group, shift=DOWN * 0.12), FadeIn(level_label), run_time=rt(0.32))
            previous_y = y

        complexity = VGroup(
            Text("DIVIDE", font_size=30, weight=BOLD, color=VIOLET),
            Text("→", font_size=30, color=MUTED),
            Text("SOLVE SMALLER DFTs", font_size=30, weight=BOLD, color=CYAN),
            Text("→", font_size=30, color=MUTED),
            Text("COMBINE", font_size=30, weight=BOLD, color=GOLD),
        ).arrange(RIGHT, buff=0.18).scale_to_fit_width(7.7).move_to(DOWN * 4.45)

        self.play(FadeIn(complexity, shift=UP * 0.12), run_time=rt(0.45))

        caption = self.caption("For power-of-two sizes, a radix-2 FFT repeatedly separates even and odd indexed samples.", VIOLET)
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.65))

        self.save_preview("04_fft_split.png", 60, "FFT divide-and-conquer split complete")

        self.play(
            *[
                FadeOut(m)
                for m in (
                    heading,
                    progress,
                    source_values,
                    source_label,
                    even,
                    odd,
                    even_label,
                    odd_label,
                    arrows,
                    levels,
                    complexity,
                    caption,
                )
            ],
            run_time=rt(0.60),
        )

    # ------------------------------------------------------------------
    # 5. Butterfly combination
    # ------------------------------------------------------------------

    def section_butterfly(self):
        heading = self.heading("THEN COMBINE WITH BUTTERFLIES", GOLD)
        progress = self.top_progress_line(4)
        self.play(FadeIn(heading), FadeIn(progress), run_time=rt(0.45))

        left_x = -2.65
        right_x = 2.65
        ys = [2.9, 1.65, 0.40, -0.85]

        left_nodes = VGroup()
        right_nodes = VGroup()
        lines = VGroup()

        for i, y in enumerate(ys):
            left_dot = Dot([left_x, y, 0], radius=0.10, color=CYAN, stroke_opacity=0)
            right_dot = Dot([right_x, y, 0], radius=0.10, color=GOLD, stroke_opacity=0)
            left_nodes.add(left_dot)
            right_nodes.add(right_dot)

        # A compact illustrative butterfly network.
        connections = [
            (0, 0), (0, 1),
            (1, 0), (1, 1),
            (2, 2), (2, 3),
            (3, 2), (3, 3),
        ]
        for a, b in connections:
            line = Line(left_nodes[a].get_center(), right_nodes[b].get_center(), color=MUTED, stroke_opacity=0.25, stroke_width=2)
            lines.add(line)

        mid_labels = VGroup()
        for y, text, color in [
            (2.28, "+", GREEN),
            (1.03, "× Wₖ", VIOLET),
            (-0.22, "+", GREEN),
            (-1.47, "× Wₖ", VIOLET),
        ]:
            mid_labels.add(Text(text, font_size=29, weight=BOLD, color=color).move_to([0, y, 0]))

        left_label = Text("SMALLER DFTs", font_size=24, weight=BOLD, color=CYAN).move_to([left_x, 3.75, 0])
        right_label = Text("COMBINED OUTPUTS", font_size=24, weight=BOLD, color=GOLD).move_to([right_x, 3.75, 0])

        self.play(FadeIn(left_label), FadeIn(right_label), FadeIn(left_nodes), run_time=rt(0.45))
        self.play(LaggedStart(*[Create(line) for line in lines], lag_ratio=0.08), run_time=rt(1.0))
        self.play(FadeIn(mid_labels), FadeIn(right_nodes), run_time=rt(0.48))

        twiddle = MathTex(
            r"W_N^k = e^{-i2\pi k/N}",
            font_size=48,
            color=VIOLET,
        ).move_to(DOWN * 2.55)

        twiddle_box = RoundedRectangle(
            corner_radius=0.18,
            width=6.7,
            height=1.25,
            stroke_color=VIOLET,
            stroke_opacity=0.28,
            fill_color=PANEL,
            fill_opacity=0.78,
        ).move_to(twiddle)

        self.play(FadeIn(twiddle_box), Write(twiddle), run_time=rt(0.65))

        speed = VGroup(
            Text("DFT scaling", font_size=25, color=MUTED),
            Text("N²", font_size=42, weight=BOLD, color=RED),
            Text("FFT scaling", font_size=25, color=MUTED),
            Text("N log₂N", font_size=42, weight=BOLD, color=GREEN),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.65, 0.20), col_alignments="ll").move_to(DOWN * 4.1)

        self.play(FadeIn(speed, shift=UP * 0.12), run_time=rt(0.55))

        caption = self.caption("The FFT reuses smaller results and combines them with complex phase factors called twiddle factors.", GOLD)
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.65))

        self.save_preview("05_butterfly.png", 76, "Butterfly combination visual complete")

        self.play(
            *[
                FadeOut(m)
                for m in (
                    heading,
                    progress,
                    left_nodes,
                    right_nodes,
                    lines,
                    mid_labels,
                    left_label,
                    right_label,
                    twiddle,
                    twiddle_box,
                    speed,
                    caption,
                )
            ],
            run_time=rt(0.58),
        )

    # ------------------------------------------------------------------
    # 6. Actual FFT spectrum
    # ------------------------------------------------------------------

    def section_spectrum(self):
        heading = self.heading("NOW THE HIDDEN FREQUENCIES APPEAR", GREEN)
        progress = self.top_progress_line(5)
        self.play(FadeIn(heading), FadeIn(progress), run_time=rt(0.45))

        axes = Axes(
            x_range=[0, 12, 2],
            y_range=[0, 1.15, 0.25],
            x_length=7.55,
            y_length=5.0,
            axis_config={
                "color": MUTED,
                "stroke_opacity": 0.38,
                "include_tip": False,
                "include_ticks": True,
                "font_size": 18,
            },
        ).move_to(UP * 0.45)

        x_label = Text("FREQUENCY (Hz)", font_size=20, color=MUTED).next_to(axes, DOWN, buff=0.22)

        bars = VGroup()
        peak_labels = VGroup()

        max_freq_to_show = 12
        for frequency, magnitude in zip(FFT_FREQS, FFT_MAG):
            if frequency > max_freq_to_show:
                break

            x0 = axes.c2p(float(frequency), 0)
            x1 = axes.c2p(float(frequency), float(magnitude))
            is_peak = any(abs(frequency - f) < 1e-9 for f, _, _ in COMPONENTS)

            if is_peak:
                color = next(color for f, _, color in COMPONENTS if abs(frequency - f) < 1e-9)
                width = 0.25
                opacity = 0.96
            else:
                color = MUTED
                width = 0.09
                opacity = 0.22

            bar = Line(x0, x1, color=color, stroke_width=max(2, int(width * 20)), stroke_opacity=opacity)
            bars.add(bar)

            if is_peak:
                label = Text(f"{int(frequency)} Hz", font_size=22, weight=BOLD, color=color)
                label.next_to(bar, UP, buff=0.10)
                peak_labels.add(label)

        self.play(FadeIn(axes), FadeIn(x_label), run_time=rt(0.35))
        self.play(LaggedStart(*[Create(bar) for bar in bars], lag_ratio=0.035), run_time=rt(1.20))
        self.play(LaggedStart(*[FadeIn(label, shift=UP * 0.10) for label in peak_labels], lag_ratio=0.15), run_time=rt(0.55))

        result = Text(
            "2 Hz   •   5 Hz   •   8 Hz",
            font_size=40,
            weight=BOLD,
            color=WHITE,
        ).move_to(DOWN * 4.25)

        self.play(FadeIn(result, scale=0.85), run_time=rt(0.35))

        caption = self.caption("The spectrum is computed from the sampled waveform — and the three injected frequencies become clear peaks.", GREEN)
        self.play(FadeIn(caption), run_time=rt(0.28))
        self.wait(hold(0.70))

        self.save_preview("06_spectrum.png", 90, "FFT spectrum revealed")

        self.play(
            *[FadeOut(m) for m in (heading, progress, axes, x_label, bars, peak_labels, result, caption)],
            run_time=rt(0.58),
        )

    # ------------------------------------------------------------------
    # 7. Finale
    # ------------------------------------------------------------------

    def section_finale(self):
        eyebrow = self.eyebrow("SAME SIGNAL // DIFFERENT VIEW", CYAN)

        title = Text(
            "TIME DOMAIN\n↓\nFREQUENCY DOMAIN",
            font_size=58,
            weight=BOLD,
            color=WHITE,
            line_spacing=0.88,
        ).move_to(UP * 2.85)

        arrow = Arrow(
            UP * 0.55,
            DOWN * 0.55,
            color=GOLD,
            stroke_width=5,
            max_tip_length_to_length_ratio=0.18,
        ).move_to(DOWN * 0.25)

        left_panel = RoundedRectangle(
            corner_radius=0.18,
            width=3.65,
            height=3.1,
            stroke_color=CYAN,
            stroke_opacity=0.25,
            fill_color=PANEL,
            fill_opacity=0.82,
        ).move_to(LEFT * 2.05 + DOWN * 2.35)

        right_panel = RoundedRectangle(
            corner_radius=0.18,
            width=3.65,
            height=3.1,
            stroke_color=GOLD,
            stroke_opacity=0.25,
            fill_color=PANEL,
            fill_opacity=0.82,
        ).move_to(RIGHT * 2.05 + DOWN * 2.35)

        left_axes = Axes(
            x_range=[0, 1, 1],
            y_range=[-2, 2, 2],
            x_length=3.0,
            y_length=2.1,
            axis_config={"stroke_opacity": 0.14, "include_tip": False, "include_ticks": False},
        ).move_to(left_panel)
        left_wave = self.waveform(left_axes, signal_value, CYAN, stroke_width=4)

        mini_bars = VGroup()
        for f, a, color in COMPONENTS:
            x = right_panel.get_left()[0] + 0.55 + (f / 10.0) * 2.55
            bottom = right_panel.get_bottom()[1] + 0.50
            top = bottom + a * 1.65
            mini_bars.add(Line([x, bottom, 0], [x, top, 0], color=color, stroke_width=9))

        fft_badge = RoundedRectangle(
            corner_radius=0.16,
            width=2.25,
            height=0.80,
            stroke_color=GOLD,
            stroke_opacity=0.45,
            fill_color=GOLD,
            fill_opacity=0.10,
        ).move_to(DOWN * 0.45)
        fft_text = Text("FFT", font_size=38, weight=BOLD, color=GOLD).move_to(fft_badge)

        speed_note = Text(
            "FAST BECAUSE IT REUSES STRUCTURE",
            font_size=25,
            weight=BOLD,
            color=GREEN,
        ).move_to(DOWN * 4.55)

        caption = self.caption("The Fourier transform changes the representation. The FFT makes that computation dramatically more efficient.", CYAN)

        self.play(FadeIn(eyebrow), FadeIn(title, shift=UP * 0.20), run_time=rt(0.65))
        self.play(FadeIn(left_panel), FadeIn(right_panel), Create(left_wave), LaggedStart(*[Create(bar) for bar in mini_bars], lag_ratio=0.18), run_time=rt(1.0))
        self.play(GrowArrow(arrow), FadeIn(fft_badge), FadeIn(fft_text, scale=0.75), run_time=rt(0.50))
        self.play(FadeIn(speed_note, shift=UP * 0.12), FadeIn(caption), run_time=rt(0.35))
        self.wait(hold(0.95))

        self.save_preview("07_finale.png", 99, "Final frame captured")


# =============================================================================
# Python launcher
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
    print("FFT MANIM YOUTUBE SHORT")
    print("=" * 72)
    print("Mode:", "QUICK VALIDATION" if QUICK_MODE else "FULL 1080x1920")
    print("Resolution:", f"{config.pixel_width}x{config.pixel_height}")
    print("FPS:", config.frame_rate)
    print("Samples used for FFT:", SAMPLE_COUNT)
    print("Hidden frequencies:", ", ".join(f"{frequency:g} Hz" for frequency, _, _ in COMPONENTS))
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
        "fft_short",
        str(Path(__file__).resolve()),
        "FFTShort",
    ]

    print("Running:", " ".join(command))
    print("Manim will show per-animation progress; this script also reports overall milestones.\n")

    result = subprocess.run(command)

    final_video: Path | None = None
    if result.returncode == 0:
        rendered = locate_rendered_video()
        if rendered:
            final_video = OUTPUT_ROOT / "fft_short.mp4"
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

