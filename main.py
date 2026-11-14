"""qjack-food-picture: make.fun food-picture-01 entry (Python 3.13, stdlib only).

Writes one food picture -- honey-glazed crispy pork belly, steaming, on a dark
ceramic plate -- to /output/entry.png.

The picture ships in this repository as the image asset entry.png next to this
program. The asset is the PNG encoded as one line of base64 (the picture
itself is binary, so it travels as text); the program decodes it, validates
the result (PNG signature, size at most 1 MiB, dimensions at most 1024x1024)
and copies its bytes to the output path, creating the output directory if
needed. Deterministic: every run writes exactly the same bytes.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import base64
import binascii
import os
import struct
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ASSET_NAME = "entry.png"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1_048_576  # 1 MiB: the competition's per-image gate
MAX_DIMENSION = 1024  # pixels: the competition's per-side gate


def output_dir() -> Path:
    override = os.environ.get("MAKEFUN_OUTPUT_DIR")
    return Path(override) if override else Path("/output")


def load_asset() -> tuple[bytes, int, int]:
    asset = Path(__file__).resolve().parent / ASSET_NAME
    try:
        text = asset.read_text(encoding="ascii")
    except OSError as exc:
        print(f"cannot read image asset {asset}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except UnicodeDecodeError as exc:
        print(f"image asset {asset} is not base64 text: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    try:
        data = base64.b64decode(text.strip(), validate=True)
    except (binascii.Error, ValueError) as exc:
        print(f"image asset {asset} is not valid base64: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if not data.startswith(PNG_SIGNATURE):
        print(f"image asset {asset} does not decode to a PNG file", file=sys.stderr)
        raise SystemExit(1)
    if not 0 < len(data) <= MAX_BYTES:
        print(
            f"image asset {asset} is {len(data)} bytes,"
            f" outside 1..{MAX_BYTES}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    width, height = png_dimensions(data, asset)
    if not 0 < width <= MAX_DIMENSION or not 0 < height <= MAX_DIMENSION:
        print(
            f"image asset {asset} is {width}x{height}px,"
            f" outside the {MAX_DIMENSION}x{MAX_DIMENSION} gate",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return data, width, height


def png_dimensions(data: bytes, asset: Path) -> tuple[int, int]:
    """Read width and height from the PNG IHDR chunk (13 bytes)."""
    ihdr = data[8:33]
    if len(ihdr) < 25 or ihdr[4:8] != b"IHDR":
        print(f"image asset {asset} has no PNG IHDR chunk", file=sys.stderr)
        raise SystemExit(1)
    width, height = struct.unpack(">II", ihdr[8:16])
    return width, height


def main() -> None:
    data, width, height = load_asset()
    out_dir = output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / OUTPUT_NAME
    out.write_bytes(data)
    print(f"wrote {out} ({len(data)} bytes, {width}x{height}px)")


if __name__ == "__main__":
    main()
