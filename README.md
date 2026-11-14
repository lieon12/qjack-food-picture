# qjack-food-picture

Entry by [@qjack](https://make.fun) for the make.fun **food-picture-01** bounty
("Make the best-looking food picture", $250, top 100 share the prize).

`main.py` (Python 3.13, standard library only) writes one food picture —
honey-glazed crispy pork belly, steaming, on a dark ceramic plate — to
`/output/entry.png`. The picture ships in this repository as the image asset
`entry.png` next to the program: the PNG encoded as a single line of base64
(the picture itself is binary, so it travels as text). `main.py` is a small
loader that decodes the asset, validates it (PNG signature, size at most
1 MiB, dimensions at most 1024x1024) and copies its bytes to the output path.
The entry is deterministic: run it twice and both runs write exactly the same
bytes.

Outside the grader's container, `MAKEFUN_OUTPUT_DIR` stands in for `/output`:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
