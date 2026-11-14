"""Round 3 entry for make.fun food-picture-01: mixed-berry pavlova.

The picture ships in this repository as ``entry.png``: one line of base64
holding a JPEG (binary pictures cannot travel through this repo's push
tool, so the bytes ride as text). This program decodes that line, checks
the picture is a real JPEG of the allowed size, and writes it to
``/output/entry.png``. Standard library only, deterministic: every run
writes exactly the same bytes.
"""

import base64
import os
import struct
import sys
from pathlib import Path

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
ASSET_NAME = "entry.png"
OUTPUT_NAME = "entry.png"


def load_asset() -> bytes:
    """Read the base64 asset sitting next to this file and decode it."""
    asset = Path(__file__).resolve().parent / ASSET_NAME
    try:
        text = asset.read_text(encoding="ascii").strip()
    except OSError as exc:
        raise SystemExit(f"cannot read asset {ASSET_NAME}: {exc}")
    try:
        return base64.b64decode(text, validate=True)
    except Exception as exc:  # noqa: BLE001 - report the bad asset plainly
        raise SystemExit(f"asset {ASSET_NAME} is not valid base64: {exc}")


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) from a JPEG's start-of-frame marker.

    Walks the marker segments after the SOI marker until it finds an SOF
    segment (0xC0-0xCF, excluding the non-frame markers) and reads the
    height and width stored there.
    """
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        raise SystemExit("decoded asset is not a JPEG (missing SOI marker)")
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            raise SystemExit(f"bad JPEG marker at offset {pos}")
        marker = data[pos + 1]
        pos += 2
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD9:
            continue  # standalone markers carry no length field
        if pos + 2 > len(data):
            break
        (segment_len,) = struct.unpack(">H", data[pos : pos + 2])
        if segment_len < 2 or pos + segment_len > len(data):
            raise SystemExit("truncated JPEG segment")
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[pos + 3 : pos + 7])
            return width, height
        pos += segment_len
    raise SystemExit("no start-of-frame marker found in JPEG")


def check_picture(data: bytes) -> tuple[int, int]:
    """Enforce the competition's picture limits and report its size."""
    if len(data) > MAX_BYTES:
        raise SystemExit(
            f"picture is {len(data)} bytes, over the {MAX_BYTES} limit"
        )
    if not data.endswith(b"\xff\xd9"):
        raise SystemExit("picture is truncated (missing JPEG end marker)")
    width, height = jpeg_dimensions(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit(
            f"picture is {width}x{height}, over the {MAX_SIDE}x{MAX_SIDE} limit"
        )
    return width, height


def write_output(data: bytes) -> Path:
    """Write the picture to the output path and return it."""
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / OUTPUT_NAME
    target.write_bytes(data)
    return target


def main() -> None:
    picture = load_asset()
    width, height = check_picture(picture)
    target = write_output(picture)
    print(f"wrote {target} ({width}x{height}, {len(picture)} bytes)")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
