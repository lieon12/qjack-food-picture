"""Round 4 entry for make.fun food-picture-01: sticky smoked BBQ ribs.

The dish is stored in this repository as ``entry.png`` — a single line of
base64 text holding a JPEG picture (the push tooling for this repository
only carries text, so the binary picture travels encoded). This script
unpacks that line, proves the bytes are a genuine picture inside the
competition limits, and copies them to ``/output/entry.png``.

Only the standard library is used, and the output is deterministic: run
the program twice and both runs write byte-identical files.
"""

import base64
import os
import struct
import sys
from pathlib import Path

LIMIT_BYTES = 1_048_576
LIMIT_SIDE = 1024
ASSET_FILE = "entry.png"
DEST_NAME = "entry.png"

JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def check_round_trip(encoded: str, data: bytes) -> None:
    """Prove the asset text round-trips: re-encoding must reproduce it.

    A base64 line that decodes cleanly can still be silently truncated or
    altered; if the decoded bytes do not encode back to the exact same
    text, the stored picture is not the one that was published.
    """
    if base64.b64encode(data).decode("ascii") != encoded:
        raise SystemExit("picture asset failed its round-trip check")


def read_bundled_image() -> bytes:
    """Decode the base64 picture stored beside this script."""
    asset_path = Path(__file__).resolve().parent / ASSET_FILE
    if not asset_path.is_file():
        raise SystemExit(f"missing picture asset: {ASSET_FILE}")
    encoded = asset_path.read_text(encoding="ascii").strip()
    if not encoded or len(encoded) % 4 != 0:
        raise SystemExit(f"picture asset {ASSET_FILE} is not valid base64")
    try:
        picture = base64.b64decode(encoded, validate=True)
    except Exception as exc:  # noqa: BLE001 - surface a broken asset plainly
        raise SystemExit(f"picture asset {ASSET_FILE} is not valid base64: {exc}")
    check_round_trip(encoded, picture)
    return picture


def sniff_format(data: bytes) -> tuple[str, tuple[int, int]]:
    """Identify the picture format and return (format, (width, height))."""
    if data[:2] == JPEG_SOI:
        return "jpeg", jpeg_size(data)
    if data[:8] == PNG_MAGIC:
        return "png", png_size(data)
    raise SystemExit("decoded asset is neither JPEG nor PNG")


def jpeg_size(data: bytes) -> tuple[int, int]:
    """Read (width, height) from a JPEG by scanning for its SOF segment."""
    cursor = 2
    while cursor + 4 <= len(data):
        if data[cursor] != 0xFF:
            raise SystemExit(f"corrupt JPEG marker at byte {cursor}")
        marker = data[cursor + 1]
        cursor += 2
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD9:
            continue
        if cursor + 2 > len(data):
            break
        (span,) = struct.unpack(">H", data[cursor : cursor + 2])
        if span < 2 or cursor + span > len(data):
            raise SystemExit("truncated JPEG segment")
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[cursor + 3 : cursor + 7])
            return width, height
        cursor += span
    raise SystemExit("JPEG has no start-of-frame segment")


def png_size(data: bytes) -> tuple[int, int]:
    """Read (width, height) from a PNG's IHDR chunk."""
    if len(data) < 24 or data[12:16] != b"IHDR":
        raise SystemExit("PNG is missing its IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def guard_limits(data: bytes, fmt: str, size: tuple[int, int]) -> None:
    """Refuse any picture outside the competition's size rules."""
    if len(data) > LIMIT_BYTES:
        raise SystemExit(
            f"picture is {len(data)} bytes, over the {LIMIT_BYTES} limit"
        )
    width, height = size
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        raise SystemExit(
            f"picture is {width}x{height}, over the "
            f"{LIMIT_SIDE}x{LIMIT_SIDE} limit"
        )
    if fmt == "jpeg" and not data.endswith(JPEG_EOI):
        raise SystemExit("JPEG picture is truncated (no end marker)")


def publish(data: bytes) -> Path:
    """Write the picture to the grader's output location."""
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / DEST_NAME
    destination.write_bytes(data)
    return destination


def run() -> None:
    picture = read_bundled_image()
    fmt, size = sniff_format(picture)
    guard_limits(picture, fmt, size)
    destination = publish(picture)
    width, height = size
    print(f"wrote {destination} ({fmt} {width}x{height}, {len(picture)} bytes)")


if __name__ == "__main__":
    try:
        run()
    except SystemExit as problem:
        print(f"error: {problem}", file=sys.stderr)
        raise
