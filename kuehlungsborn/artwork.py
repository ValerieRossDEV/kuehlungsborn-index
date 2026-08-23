from __future__ import annotations

import math
import random

from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import Conditions, DailyAssessment
from .scoring import score_text


WIDTH = 1200
HEIGHT = 1660

PAPER = (243, 241, 235)
INK = (22, 27, 34)
GRID = (120, 126, 132)
LIGHT_GRID = (170, 174, 178)
ACCENT = (125, 145, 165)


def compass_short(degrees: float) -> str:
    labels = ["N", "NO", "O", "SO", "S", "SW", "W", "NW"]
    index = int((degrees + 22.5) // 45) % 8
    return labels[index]


def _font_path(
    *,
    bold: bool = False,
    condensed: bool = False,
) -> str | None:
    candidates: list[str] = []

    if condensed and bold:
        candidates.extend(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
            ]
        )

    if bold:
        candidates.extend(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "C:/Windows/Fonts/arial.ttf",
            ]
        )

    for candidate in candidates:
        if Path(candidate).exists():
            return candidate

    return None


def font(
    size: int,
    *,
    bold: bool = False,
    condensed: bool = False,
):
    path = _font_path(
        bold=bold,
        condensed=condensed,
    )

    if path:
        return ImageFont.truetype(
            path,
            size=size,
        )

    return ImageFont.load_default()


def _rule(
    draw: ImageDraw.ImageDraw,
    y: int,
    x0: int,
    x1: int,
    *,
    width: int = 2,
) -> None:
    draw.line(
        (x0, y, x1, y),
        fill=INK,
        width=width,
    )


def _dotted_rule(
    draw: ImageDraw.ImageDraw,
    y: int,
    x0: int,
    x1: int,
    *,
    step: int = 11,
    dot_width: int = 3,
) -> None:
    for x in range(x0, x1, step):
        draw.line(
            (x, y, x + dot_width, y),
            fill=INK,
            width=1,
        )


def _dotted_square(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int,
) -> None:
    spacing = size // 4

    for row in range(5):
        for col in range(5):
            cx = x + col * spacing
            cy = y + row * spacing

            draw.ellipse(
                (
                    cx - 2,
                    cy - 2,
                    cx + 2,
                    cy + 2,
                ),
                fill=INK,
            )


def _dashed_line(
    draw: ImageDraw.ImageDraw,
    p1: tuple[float, float],
    p2: tuple[float, float],
    *,
    dash: float = 5.0,
    gap: float = 5.0,
    fill=GRID,
    width: int = 1,
) -> None:
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)

    if length == 0:
        return

    ux = dx / length
    uy = dy / length

    position = 0.0

    while position < length:
        end = min(position + dash, length)

        draw.line(
            (
                x1 + ux * position,
                y1 + uy * position,
                x1 + ux * end,
                y1 + uy * end,
            ),
            fill=fill,
            width=width,
        )

        position += dash + gap


def _dashed_circle(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    radius: int,
    *,
    segments: int = 72,
    fill=GRID,
    width: int = 1,
) -> None:
    cx, cy = center

    box = (
        cx - radius,
        cy - radius,
        cx + radius,
        cy + radius,
    )

    step = 360 / segments

    for index in range(segments):
        if index % 2 == 0:
            start = index * step
            end = start + step * 0.55

            draw.arc(
                box,
                start=start,
                end=end,
                fill=fill,
                width=width,
            )


def _angular_distance(
    first: float,
    second: float,
) -> float:
    difference = abs(first - second) % 360
    return min(difference, 360 - difference)


def _draw_windrose(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    outer_radius: int,
    c: Conditions,
    date_key: str,
) -> None:
    cx, cy = center
    inner_radius = 34

    ring_count = 6
    ring_step = (
        outer_radius - inner_radius
    ) / ring_count

    draw.ellipse(
        (
            cx - outer_radius,
            cy - outer_radius,
            cx + outer_radius,
            cy + outer_radius,
        ),
        outline=LIGHT_GRID,
        width=1,
    )

    for index in range(1, ring_count):
        radius = int(
            inner_radius + index * ring_step
        )

        _dashed_circle(
            draw,
            (cx, cy),
            radius,
        )

    for degrees in range(0, 360, 15):
        theta = math.radians(
            degrees - 90
        )

        target = (
            cx + math.cos(theta) * outer_radius,
            cy + math.sin(theta) * outer_radius,
        )

        _dashed_line(
            draw,
            (cx, cy),
            target,
            dash=4 if degrees % 90 == 0 else 3,
            gap=4 if degrees % 90 == 0 else 5,
            fill=GRID if degrees % 90 == 0 else LIGHT_GRID,
        )

    label_font = font(
        22,
        bold=True,
        condensed=True,
    )

    draw.text(
        (cx - 8, cy - outer_radius - 42),
        "N",
        font=label_font,
        fill=INK,
    )
    draw.text(
        (cx - 8, cy + outer_radius + 8),
        "S",
        font=label_font,
        fill=INK,
    )
    draw.text(
        (cx - outer_radius - 42, cy - 12),
        "W",
        font=label_font,
        fill=INK,
    )
    draw.text(
        (cx + outer_radius + 18, cy - 12),
        "O",
        font=label_font,
        fill=INK,
    )

    ring_font = font(14, bold=True)

    for value, factor in (
        ("20", 1),
        ("40", 2.5),
        ("60", 4),
    ):
        draw.text(
            (
                cx + 8,
                cy
                - int(
                    inner_radius
                    + ring_step * factor
                )
                - 10,
            ),
            value,
            font=ring_font,
            fill=INK,
        )

    rng = random.Random(
        f"{date_key}:"
        f"{round(c.wind_direction)}:"
        f"{round(c.wind_speed)}:"
        f"{round(c.wind_gusts)}"
    )

    bins = 72

    spread = 45 + min(
        25,
        max(
            0,
            c.wind_gusts - c.wind_speed,
        ),
    )

    max_length = (
        outer_radius
        - inner_radius
        - 12
    )

    for index in range(bins):
        degrees = index * (360 / bins)

        delta = _angular_distance(
            degrees,
            c.wind_direction,
        )

        influence = math.exp(
            -(delta**2)
            / (2 * spread**2)
        )

        base = rng.uniform(6, 20)

        directional = influence * (
            c.wind_speed * 8 + 85
        )

        gust_noise = rng.uniform(-10, 10) * (
            1
            + max(
                0,
                c.wind_gusts - c.wind_speed,
            )
            / 20
        )

        bar_length = max(
            8,
            min(
                max_length,
                base
                + directional
                + gust_noise,
            ),
        )

        if influence < 0.28:
            line_width = 1
        elif influence < 0.55:
            line_width = 2
        else:
            line_width = 4

        theta = math.radians(
            degrees - 90
        )

        start_radius = inner_radius + 4
        end_radius = (
            start_radius + bar_length
        )

        draw.line(
            (
                cx + math.cos(theta) * start_radius,
                cy + math.sin(theta) * start_radius,
                cx + math.cos(theta) * end_radius,
                cy + math.sin(theta) * end_radius,
            ),
            fill=INK,
            width=line_width,
        )

    draw.ellipse(
        (
            cx - inner_radius,
            cy - inner_radius,
            cx + inner_radius,
            cy + inner_radius,
        ),
        fill=PAPER,
        outline=INK,
        width=2,
    )

    draw.ellipse(
        (
            cx - 7,
            cy - 7,
            cx + 7,
            cy + 7,
        ),
        fill=INK,
    )


def _draw_seagull_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
) -> None:
    draw.arc(
        (
            cx - 32,
            cy - 12,
            cx - 2,
            cy + 12,
        ),
        start=205,
        end=335,
        fill=INK,
        width=2,
    )

    draw.arc(
        (
            cx - 2,
            cy - 12,
            cx + 28,
            cy + 12,
        ),
        start=205,
        end=335,
        fill=INK,
        width=2,
    )

    draw.arc(
        (
            cx - 30,
            cy + 18,
            cx + 30,
            cy + 34,
        ),
        start=200,
        end=340,
        fill=INK,
        width=2,
    )


def _draw_thermometer_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
) -> None:
    draw.rounded_rectangle(
        (
            cx - 6,
            cy - 26,
            cx + 6,
            cy + 12,
        ),
        radius=6,
        outline=INK,
        width=2,
    )

    draw.ellipse(
        (
            cx - 14,
            cy + 4,
            cx + 14,
            cy + 32,
        ),
        outline=INK,
        width=2,
    )

    draw.line(
        (
            cx,
            cy - 18,
            cx,
            cy + 16,
        ),
        fill=INK,
        width=3,
    )


def _draw_rain_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
) -> None:
    draw.arc(
        (
            cx - 28,
            cy - 10,
            cx - 2,
            cy + 16,
        ),
        start=180,
        end=360,
        fill=INK,
        width=2,
    )

    draw.arc(
        (
            cx - 8,
            cy - 20,
            cx + 18,
            cy + 8,
        ),
        start=180,
        end=360,
        fill=INK,
        width=2,
    )

    draw.arc(
        (
            cx + 4,
            cy - 10,
            cx + 30,
            cy + 16,
        ),
        start=180,
        end=360,
        fill=INK,
        width=2,
    )

    draw.line(
        (
            cx - 28,
            cy + 16,
            cx + 30,
            cy + 16,
        ),
        fill=INK,
        width=2,
    )

    for offset in (-14, 0, 14):
        draw.line(
            (
                cx + offset,
                cy + 24,
                cx + offset,
                cy + 40,
            ),
            fill=INK,
            width=2,
        )


def _draw_sun_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
) -> None:
    draw.arc(
        (
            cx - 22,
            cy - 2,
            cx + 22,
            cy + 42,
        ),
        start=180,
        end=360,
        fill=INK,
        width=2,
    )

    draw.line(
        (
            cx - 34,
            cy + 20,
            cx + 34,
            cy + 20,
        ),
        fill=INK,
        width=2,
    )


def _draw_wave_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
) -> None:
    points = [
        (
            cx - 36 + index * 2,
            cy + math.sin(index / 6) * 14,
        )
        for index in range(41)
    ]

    draw.line(
        points,
        fill=INK,
        width=3,
    )


def _draw_sea_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
) -> None:
    for row in range(4):
        y = cy - 18 + row * 12

        points = [
            (
                cx - 34 + index * 2,
                y + math.sin(index / 3) * 3,
            )
            for index in range(41)
        ]

        draw.line(
            points,
            fill=INK,
            width=2,
        )


def _fit_text_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    *,
    start_size: int,
    min_size: int,
) -> int:
    size = start_size

    while size > min_size:
        selected = font(
            size,
            bold=True,
            condensed=True,
        )

        bbox = draw.textbbox((0, 0), text, font=selected)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            return size

        size -= 2

    return min_size


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    selected_font,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        candidate = (
            word
            if not current
            else f"{current} {word}"
        )

        if (
            draw.textlength(
                candidate,
                font=selected_font,
            )
            <= max_width
        ):
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def _metric_box(
    draw: ImageDraw.ImageDraw,
    left: int,
    top: int,
    width: int,
    height: int,
    *,
    title: str,
    value: str,
    icon_name: str,
    note: str | None = None,
) -> None:
    title_font = font(
        16,
        bold=True,
        condensed=True,
    )

    value_font = font(
        36,
        bold=True,
        condensed=True,
    )

    draw.text(
        (
            left + 18,
            top + 18,
        ),
        title,
        font=title_font,
        fill=INK,
    )

    _dotted_rule(
        draw,
        top + 56,
        left + 18,
        left + width - 18,
        step=10,
        dot_width=4,
    )

    cx = left + width // 2
    icon_y = top + 112

    if icon_name == "gull":
        _draw_seagull_icon(
            draw,
            cx,
            icon_y,
        )
    elif icon_name == "temp":
        _draw_thermometer_icon(
            draw,
            cx,
            icon_y,
        )
    elif icon_name == "rain":
        _draw_rain_icon(
            draw,
            cx,
            icon_y,
        )
    elif icon_name == "sun":
        _draw_sun_icon(
            draw,
            cx,
            icon_y,
        )
    elif icon_name == "wave":
        _draw_wave_icon(
            draw,
            cx,
            icon_y,
        )
    elif icon_name == "sea":
        _draw_sea_icon(
            draw,
            cx,
            icon_y,
        )

    value_width = draw.textlength(
        value,
        font=value_font,
    )

    value_y = top + 195

    draw.text(
        (
            left + (width - value_width) / 2,
            value_y,
        ),
        value,
        font=value_font,
        fill=INK,
    )

    if note:
        note_font = font(
            10,
            bold=True,
            condensed=True,
        )

        lines = _wrap_text(
            draw,
            note,
            note_font,
            width - 20,
        )[:2]

        line_y = top + 242

        for line in lines:
            line_width = draw.textlength(
                line,
                font=note_font,
            )

            draw.text(
                (
                    left
                    + (width - line_width) / 2,
                    line_y,
                ),
                line,
                font=note_font,
                fill=INK,
            )

            line_y += 14


def render_daily_image(
    path: Path,
    now: datetime,
    c: Conditions,
    assessment: DailyAssessment,
) -> None:
    image = Image.new(
        "RGB",
        (
            WIDTH,
            HEIGHT,
        ),
        PAPER,
    )

    draw = ImageDraw.Draw(image)

    margin = 42
    content_width = WIDTH - margin * 2

    _rule(
        draw,
        24,
        margin,
        WIDTH - margin,
        width=4,
    )

    header_font = font(
        40,
        bold=True,
        condensed=True,
    )

    draw.text(
        (
            margin,
            52,
        ),
        (
            "KÜHLUNGSBORN / "
            f"{now.strftime('%d.%m.%Y')}"
        ),
        font=header_font,
        fill=INK,
    )

    _dotted_rule(
        draw,
        116,
        margin,
        WIDTH - margin,
        step=10,
        dot_width=4,
    )

    left_x = margin
    top_y = 165

    score_font = font(
        190,
        bold=True,
        condensed=True,
    )

    draw.text(
        (
            left_x,
            top_y,
        ),
        f"{assessment.score}%",
        font=score_font,
        fill=INK,
    )

    _rule(
        draw,
        top_y + 300,
        left_x,
        left_x + 250,
    )

    draw.text(
        (
            left_x,
            top_y + 335,
        ),
        "KÜHLUNGSBORN-INDEX",
        font=font(
            21,
            bold=True,
            condensed=True,
        ),
        fill=INK,
    )

    draw.rectangle(
        (
            left_x,
            top_y + 420,
            left_x + 110,
            top_y + 434,
        ),
        fill=ACCENT,
    )

    draw.text(
        (
            left_x,
            top_y + 470,
        ),
        score_text(
            assessment.score
        ),
        font=font(
            18,
            bold=True,
            condensed=True,
        ),
        fill=INK,
    )

    _dotted_rule(
        draw,
        top_y + 595,
        left_x,
        left_x + 270,
    )

    wind_font = font(
        34,
        bold=True,
        condensed=True,
    )

    draw.text(
        (
            left_x,
            top_y + 630,
        ),
        (
            f"{compass_short(c.wind_direction)}"
            f" / {c.wind_speed:.0f} KM/H"
        ),
        font=wind_font,
        fill=INK,
    )

    draw.text(
        (
            left_x,
            top_y + 705,
        ),
        (
            f"BÖEN / "
            f"{c.wind_gusts:.0f} KM/H"
        ),
        font=wind_font,
        fill=INK,
    )

    _draw_windrose(
        draw,
        (
            790,
            515,
        ),
        315,
        c,
        now.strftime("%d.%m.%y"),
    )

    _rule(
        draw,
        928,
        margin,
        WIDTH - margin,
    )

    _dotted_square(
        draw,
        margin + 8,
        978,
        90,
    )

    verdict_x = 300

    draw.text(
        (
            verdict_x,
            968,
        ),
        "HEUTE ANS MEER",
        font=font(
            28,
            bold=True,
            condensed=True,
        ),
        fill=INK,
    )

    verdict_size = _fit_text_size(
        draw,
        assessment.verdict,
        WIDTH - margin - verdict_x - 36,
        start_size=70,
        min_size=40,
    )

    draw.text(
        (
            verdict_x,
            1032,
        ),
        assessment.verdict,
        font=font(
            verdict_size,
            bold=True,
            condensed=True,
        ),
        fill=INK,
    )

    draw.text(
        (
            verdict_x,
            1150,
        ),
        assessment.verdict_subtitle,
        font=font(
            28,
            bold=True,
            condensed=True,
        ),
        fill=INK,
    )

    metric_top = 1210
    metric_height = 285

    _rule(
        draw,
        metric_top,
        margin,
        WIDTH - margin,
    )

    column_width = content_width // 6

    for index in range(1, 6):
        x = margin + index * column_width

        draw.line(
            (
                x,
                metric_top,
                x,
                metric_top + metric_height,
            ),
            fill=GRID,
            width=1,
        )

    wave_value = (
        "—"
        if c.wave_height_max is None
        else f"{c.wave_height_max:.1f}M"
    )

    sea_value = (
        "—"
        if c.sea_temperature is None
        else f"{c.sea_temperature:.1f}°C"
    )

    metrics = [
        (
            "MÖWENRISIKO",
            f"{assessment.gull_risk}%",
            "gull",
        ),
        (
            "TEMPERATUR",
            f"{c.temperature:.0f}°C",
            "temp",
        ),
        (
            "REGEN",
            f"{c.rain_probability}%",
            "rain",
        ),
        (
            "SONNE",
            f"{round(c.sunshine_hours):.0f}H",
            "sun",
        ),
        (
            "WELLE MAX",
            wave_value,
            "wave",
        ),
        (
            "OSTSEE",
            sea_value,
            "sea",
        ),
    ]

    for index, (
        title,
        value,
        icon_name,
    ) in enumerate(metrics):
        _metric_box(
            draw,
            margin + index * column_width,
            metric_top,
            column_width,
            metric_height,
            title=title,
            value=value,
            icon_name=icon_name,
            note=(
                assessment.gull_risk_summary
                if title == "MÖWENRISIKO"
                else None
            ),
        )

    disclaimer_y = (
        metric_top
        + metric_height
        + 18
    )

    disclaimer_text = (
        "MÖWENRISIKO™: "
        "WISSENSCHAFTLICH VOLLKOMMEN UNBELEGT."
    )

    draw.text(
        (
            margin,
            disclaimer_y,
        ),
        disclaimer_text,
        font=font(
            13,
            bold=True,
            condensed=True,
        ),
        fill=GRID,
    )

    footer_y = disclaimer_y + 34

    _rule(
        draw,
        footer_y,
        margin,
        WIDTH - margin,
        width=1,
    )

    footer_font = font(
        16,
        bold=True,
        condensed=True,
    )

    data_label = (
        "DATA / OPEN-METEO"
    )

    wave_note = (
        "WELLE = TAGESMAXIMUM"
    )

    signature = (
        "VR / "
        f"{now.strftime('%d.%m.%y')}"
    )

    draw.text(
        (
            margin,
            footer_y + 16,
        ),
        data_label,
        font=footer_font,
        fill=INK,
    )

    wave_note_width = draw.textlength(
        wave_note,
        font=footer_font,
    )

    draw.text(
        (
            (WIDTH - wave_note_width) / 2,
            footer_y + 16,
        ),
        wave_note,
        font=footer_font,
        fill=GRID,
    )

    signature_width = draw.textlength(
        signature,
        font=footer_font,
    )

    draw.text(
        (
            WIDTH
            - margin
            - signature_width,
            footer_y + 16,
        ),
        signature,
        font=footer_font,
        fill=INK,
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image.save(path)
