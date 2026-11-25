"""CPS-1 palette word -> RGB888 (MAME formula) -> SNES BGR555.

Input is a captured palette RAM word, NOT a ROM graphics byte.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def cps1_rgb(word: int) -> tuple[int, int, int]:
    if not 0 <= word <= 0xffff:
        raise ValueError('palette word must be 0..65535')
    bright = 0x0f + (((word >> 12) & 0xf) << 1)
    return tuple((((word >> shift) & 0xf) * 0x11 * bright) // 0x2d for shift in (8, 4, 0))


def rgb_to_bgr555(rgb: tuple[int, int, int]) -> int:
    if len(rgb) != 3 or any(not 0 <= v <= 255 for v in rgb):
        raise ValueError('RGB channels must be 0..255')
    r, g, b = ((v * 31 + 127) // 255 for v in rgb)
    return (b << 10) | (g << 5) | r


def decode_words(raw: bytes, *, byteorder: str = 'big') -> list[dict]:
    if byteorder not in ('big', 'little'):
        raise ValueError('byteorder must be big or little')
    if len(raw) % 2:
        raise ValueError('palette dump length must be even')
    result = []
    for offset in range(0, len(raw), 2):
        word = int.from_bytes(raw[offset:offset+2], byteorder)
        rgb = cps1_rgb(word)
        result.append({'index': offset // 2, 'cps1_word': f'{word:04X}', 'rgb888': list(rgb), 'snes_bgr555': f'{rgb_to_bgr555(rgb):04X}'})
    return result


def main() -> None:
    p = argparse.ArgumentParser(description='Convert captured CPS-1 palette words to SNES BGR555')
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--byteorder', choices=('big', 'little'), default='big')
    a = p.parse_args()
    data = decode_words(a.input.read_bytes(), byteorder=a.byteorder)
    a.output.write_text(json.dumps({'source': 'captured CPS-1 palette RAM words', 'byteorder': a.byteorder, 'colors': data}, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
