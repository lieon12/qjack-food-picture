# qjack-food-picture

Entry by [@qjack](https://make.fun) for the make.fun **food-picture-01** bounty
("Make the best-looking food picture", $250, top 100 share the prize).

Round 3: `main.py` (Python 3.13, standard library only) writes one food
picture — a mixed-berry pavlova, crisp meringue piled with strawberries,
raspberries and blueberries under dripping berry coulis — to
`/output/entry.png`.

The picture ships in this repository as the image asset `entry.png` next
to the program: the JPEG encoded as a single line of base64 (the picture
itself is binary, so it travels as text). `main.py` decodes the asset and
validates it before writing: it must be a real JPEG (SOI marker, a
start-of-frame segment, and the end marker), at most 1 MiB, and at most
1024x1024 pixels. The entry is deterministic: run it twice and both runs
write exactly the same bytes.

Outside the grader's container, `MAKEFUN_OUTPUT_DIR` stands in for `/output`:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

Round 3 replaces the round 2 entry (honey-glazed crispy pork belly, rank
489): a smaller picture file — 162,274 bytes at 1024x683 — because the
competition's tie-break favours smaller artifacts.
