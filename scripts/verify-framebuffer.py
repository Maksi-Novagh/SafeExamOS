#!/usr/bin/env python3
"""Check a QEMU PPM for actual launcher styling and optional keyboard-induced changes.

A graphical signature is stronger than merely finding Cage/Chromium PIDs.
It is not OCR, pixel-perfect verification, or a security certification.
"""
import argparse
import sys
from pathlib import Path


def read_ppm(path):
    with Path(path).open("rb") as f:
        def token():
            while True:
                char = f.read(1)
                if not char:
                    raise ValueError("unexpected EOF in PPM header")
                if char == b"#":
                    f.readline()
                elif char not in b" \t\r\n":
                    break
            word = bytearray(char)
            while True:
                char = f.read(1)
                if not char or char in b" \t\r\n":
                    return bytes(word)
                word.extend(char)

        if token() != b"P6":
            raise ValueError("not a P6 PPM")
        width, height, maxval = (int(token()) for _ in range(3))
        if width < 640 or height < 360 or maxval != 255:
            raise ValueError(f"unexpected PPM geometry: {width}x{height} maxval={maxval}")
        pixels = f.read()
    expected = width * height * 3
    if len(pixels) != expected:
        raise ValueError(f"incorrect pixel bytes: got {len(pixels)}, expected {expected}")
    return width, height, pixels


def verify_launcher(pixels):
    white = dark = blue = 0
    for i in range(0, len(pixels), 3):
        r, g, b = pixels[i:i + 3]
        white += r >= 245 and g >= 245 and b >= 245
        dark += r < 90 and g < 90 and b < 90
        blue += r < 90 and 75 <= g <= 195 and b >= 180 and b > r + 80 and b > g + 30
    print(f"Framebuffer colors: white={white}, dark={dark}, blue={blue}")
    if white < 3000 or dark < 100 or blue < 80:
        raise ValueError("expected white panel, dark text, and DodgerBlue launcher accent")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="PPM after launcher startup")
    parser.add_argument("--after-input", help="PPM after QEMU keyboard input")
    parser.add_argument("--managed-child", action="store_true", help="Require rendered orange child window")
    args = parser.parse_args()
    width, height, before = read_ppm(args.baseline)
    verify_launcher(before)
    if args.managed_child:
        orange = sum(
            1 for i in range(0, len(before), 3)
            if before[i] >= 200 and 65 <= before[i + 1] <= 165
            and before[i + 2] <= 85
            and before[i] > before[i + 1] + 65
        )
        print(f"Managed child orange pixels: {orange}")
        if orange < 1500:
            raise ValueError("second WebKitGTK window is not visibly rendered")
    if args.after_input:
        width2, height2, after = read_ppm(args.after_input)
        if (width, height) != (width2, height2):
            raise ValueError("display geometry changed during keyboard input check")
        changed = sum(before[i:i + 3] != after[i:i + 3] for i in range(0, len(before), 3))
        print(f"Framebuffer changed pixels after QEMU keyboard input: {changed}")
        if changed < 1800:
            raise ValueError("no substantial visible response to injected keyboard input")
    print("SafeExamOS framebuffer verification: PASS")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(f"SafeExamOS framebuffer verification: FAIL: {exc}")
