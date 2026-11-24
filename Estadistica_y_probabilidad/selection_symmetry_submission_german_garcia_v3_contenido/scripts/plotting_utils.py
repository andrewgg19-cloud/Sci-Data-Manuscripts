"""Tiny standard-library PNG plotting helpers for reproducible figures."""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path


Color = tuple[int, int, int]
WHITE: Color = (255, 255, 255)
BLACK: Color = (25, 25, 25)
GRID: Color = (220, 225, 228)

FONT_5X7: dict[str, tuple[str, ...]] = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01000", "10000"),
    "(": ("00100", "01000", "10000", "10000", "10000", "01000", "00100"),
    ")": ("10000", "01000", "00100", "00100", "00100", "01000", "10000"),
    "/": ("00010", "00010", "00100", "00100", "01000", "01000", "10000"),
    "=": ("00000", "11110", "00000", "11110", "00000", "00000", "00000"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "11100"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
}


def write_png(path: Path, width: int, height: int, pixels: list[list[Color]]) -> None:
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for red, green, blue in row:
            raw.extend((red, green, blue))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def canvas(width: int = 1152, height: int = 756, color: Color = WHITE) -> list[list[Color]]:
    return [[color for _ in range(width)] for _ in range(height)]


def set_px(img: list[list[Color]], x: int, y: int, color: Color) -> None:
    if 0 <= y < len(img) and 0 <= x < len(img[0]):
        img[y][x] = color


def line(img: list[list[Color]], x0: int, y0: int, x1: int, y1: int, color: Color, width: int = 2) -> None:
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        radius = max(0, width // 2)
        for ox in range(-radius, radius + 1):
            for oy in range(-radius, radius + 1):
                set_px(img, x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def rect(img: list[list[Color]], x0: int, y0: int, x1: int, y1: int, color: Color) -> None:
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    for y in range(ya, yb + 1):
        for x in range(xa, xb + 1):
            set_px(img, x, y, color)


def circle(img: list[list[Color]], cx: int, cy: int, radius: int, color: Color) -> None:
    r2 = radius * radius
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                set_px(img, x, y, color)


def text_width(text: str, scale: int = 2) -> int:
    return len(text) * 6 * scale


def draw_text(img: list[list[Color]], x: int, y: int, text: str, color: Color = BLACK, scale: int = 2) -> None:
    cursor = x
    for char in text.upper():
        glyph = FONT_5X7.get(char, FONT_5X7[" "])
        for row_index, row in enumerate(glyph):
            for col_index, value in enumerate(row):
                if value == "1":
                    rect(
                        img,
                        cursor + col_index * scale,
                        y + row_index * scale,
                        cursor + (col_index + 1) * scale - 1,
                        y + (row_index + 1) * scale - 1,
                        color,
                    )
        cursor += 6 * scale


def draw_axes(img: list[list[Color]], left: int, top: int, right: int, bottom: int, y_ticks: int = 5) -> None:
    for i in range(y_ticks + 1):
        y = bottom - round((bottom - top) * i / y_ticks)
        line(img, left, y, right, y, GRID, 1)
    line(img, left, top, left, bottom, BLACK, 3)
    line(img, left, bottom, right, bottom, BLACK, 3)


def scale_points(
    xs: list[float],
    ys: list[float],
    left: int,
    top: int,
    right: int,
    bottom: int,
    x_min: float | None = None,
    x_max: float | None = None,
    y_min: float | None = None,
    y_max: float | None = None,
) -> list[tuple[int, int]]:
    x0 = min(xs) if x_min is None else x_min
    x1 = max(xs) if x_max is None else x_max
    y0 = min(ys) if y_min is None else y_min
    y1 = max(ys) if y_max is None else y_max
    if math.isclose(x0, x1):
        x1 = x0 + 1.0
    if math.isclose(y0, y1):
        y1 = y0 + 1.0
    points = []
    for x, y in zip(xs, ys):
        px = left + round((x - x0) / (x1 - x0) * (right - left))
        py = bottom - round((y - y0) / (y1 - y0) * (bottom - top))
        points.append((px, py))
    return points


def polyline(img: list[list[Color]], points: list[tuple[int, int]], color: Color, width: int = 4) -> None:
    for start, end in zip(points, points[1:]):
        line(img, start[0], start[1], end[0], end[1], color, width)
    for x, y in points:
        circle(img, x, y, 5, color)


def save_line_plot(
    path: Path,
    series: list[tuple[list[float], list[float], Color]],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    reference_y: float | None = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    labels: list[str] | None = None,
) -> None:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        plt = None

    if plt is not None:
        fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=180)
        for index, (xs, ys, color) in enumerate(series):
            label = labels[index] if labels and index < len(labels) else None
            rgb = tuple(channel / 255.0 for channel in color)
            ax.plot(xs, ys, marker="o", linewidth=2, markersize=3.8, color=rgb, label=label)
        if reference_y is not None:
            ax.axhline(reference_y, color="#444444", linestyle="--", linewidth=1.2, label="reference")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.25)
        if labels or reference_y is not None:
            ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        return

    width, height = 1152, 756
    img = canvas(width, height)
    left, top, right, bottom = 120, 70, 1060, 650
    draw_axes(img, left, top, right, bottom)
    if title:
        draw_text(img, max(10, (width - text_width(title, 3)) // 2), 18, title, BLACK, 3)
    if xlabel:
        draw_text(img, max(10, (width - text_width(xlabel, 2)) // 2), 700, xlabel, BLACK, 2)
    if ylabel:
        draw_text(img, 130, 35, ylabel, BLACK, 2)
    if reference_y is not None:
        pts = scale_points([x_min, x_max], [reference_y, reference_y], left, top, right, bottom, x_min, x_max, y_min, y_max)
        line(img, pts[0][0], pts[0][1], pts[1][0], pts[1][1], (70, 70, 70), 3)
    for xs, ys, color in series:
        pts = scale_points(xs, ys, left, top, right, bottom, x_min, x_max, y_min, y_max)
        polyline(img, pts, color)
    if labels:
        legend_x = 730
        legend_y = 92
        for index, label in enumerate(labels):
            if index >= len(series):
                break
            color = series[index][2]
            y = legend_y + index * 28
            line(img, legend_x, y + 8, legend_x + 42, y + 8, color, 5)
            draw_text(img, legend_x + 54, y, label, BLACK, 2)
    write_png(path, width, height, img)


def save_grouped_bar_plot(
    path: Path,
    labels: list[str],
    left_values: list[float],
    right_values: list[float],
    title: str = "",
    ylabel: str = "",
) -> None:
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ModuleNotFoundError:
        plt = None
        np = None

    if plt is not None and np is not None:
        fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=180)
        x = np.arange(len(labels))
        width = 0.34
        ax.bar(x - width / 2, left_values, width, label="b_max", color="#5b8e7d")
        ax.bar(x + width / 2, right_values, width, label="b_req", color="#c46d5e")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.25)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        return

    width, height = 1152, 756
    img = canvas(width, height)
    left, top, right, bottom = 120, 70, 1060, 650
    draw_axes(img, left, top, right, bottom)
    if title:
        draw_text(img, max(10, (width - text_width(title, 3)) // 2), 18, title, BLACK, 3)
    if ylabel:
        draw_text(img, 130, 35, ylabel, BLACK, 2)
    y_max = max(left_values + right_values) * 1.18
    group_width = (right - left) / len(labels)
    for i, (lv, rv) in enumerate(zip(left_values, right_values)):
        center = left + group_width * (i + 0.5)
        bar_w = int(group_width * 0.22)
        gap = int(group_width * 0.04)
        l_height = round((lv / y_max) * (bottom - top))
        r_height = round((rv / y_max) * (bottom - top))
        rect(img, int(center - gap - 2 * bar_w), bottom - l_height, int(center - gap - bar_w), bottom, (91, 142, 125))
        rect(img, int(center + gap), bottom - r_height, int(center + gap + bar_w), bottom, (196, 109, 94))
        draw_text(img, int(center - text_width(labels[i], 2) / 2), bottom + 22, labels[i], BLACK, 2)
    legend_x = 820
    legend_y = 95
    rect(img, legend_x, legend_y, legend_x + 24, legend_y + 14, (91, 142, 125))
    draw_text(img, legend_x + 34, legend_y, "B_MAX", BLACK, 2)
    rect(img, legend_x, legend_y + 30, legend_x + 24, legend_y + 44, (196, 109, 94))
    draw_text(img, legend_x + 34, legend_y + 30, "B_REQ", BLACK, 2)
    write_png(path, width, height, img)


def save_simple_bar_plot(
    path: Path,
    labels: list[str],
    values: list[float],
    title: str = "",
    ylabel: str = "",
    colors: list[Color] | None = None,
) -> None:
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ModuleNotFoundError:
        plt = None
        np = None

    if plt is not None and np is not None:
        fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=180)
        x = np.arange(len(labels))
        rgb_colors = None
        if colors is not None:
            rgb_colors = [tuple(channel / 255.0 for channel in color) for color in colors]
        ax.bar(x, values, color=rgb_colors or "#5b8e7d")
        ax.axhline(0.0, color="#333333", linewidth=1)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        return

    width, height = 1152, 756
    img = canvas(width, height)
    left, top, right, bottom = 120, 70, 1060, 650
    draw_axes(img, left, top, right, bottom)
    if title:
        draw_text(img, max(10, (width - text_width(title, 3)) // 2), 18, title, BLACK, 3)
    if ylabel:
        draw_text(img, 130, 35, ylabel, BLACK, 2)
    y_min = min(min(values), 0.0)
    y_max = max(max(values), 0.0)
    span = y_max - y_min or 1.0
    y_min -= 0.15 * span
    y_max += 0.15 * span
    zero_y = bottom - round((0.0 - y_min) / (y_max - y_min) * (bottom - top))
    line(img, left, zero_y, right, zero_y, BLACK, 2)
    group_width = (right - left) / len(labels)
    for i, value in enumerate(values):
        center = left + group_width * (i + 0.5)
        bar_w = int(group_width * 0.36)
        y = bottom - round((value - y_min) / (y_max - y_min) * (bottom - top))
        color = colors[i] if colors and i < len(colors) else (91, 142, 125)
        rect(img, int(center - bar_w / 2), y, int(center + bar_w / 2), zero_y, color)
        draw_text(img, int(center - text_width(labels[i], 2) / 2), bottom + 22, labels[i], BLACK, 2)
    write_png(path, width, height, img)
