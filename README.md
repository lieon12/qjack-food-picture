# qjack-food-picture

Entry by [@qjack](https://make.fun) for the make.fun **food-picture-01** bounty
("Make the best-looking food picture", $250, top 100 share the prize).

Round 4: `main.py` (Python 3.13, standard library only) writes one food
picture — sticky smoked BBQ ribs, stacked high with dripping caramelized
barbecue glaze and light smoke — to `/output/entry.png`.

The picture ships in this repository as the image asset `entry.png` next
to the program: the JPEG encoded as a single line of base64 (the picture
itself is binary, so it travels as text). `main.py` decodes the asset and
validates it before writing: the decoded bytes must re-encode to the exact
same base64 line, the picture must be a real JPEG (SOI marker, a
start-of-frame segment, and the end marker) or PNG (IHDR chunk), at most
1 MiB, and at most 1024x1024 pixels. The entry is deterministic: run it
twice and both runs write exactly the same bytes.

Outside the grader's container, `MAKEFUN_OUTPUT_DIR` stands in for `/output`:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

Round 4 replaces the round 3 entry (mixed-berry pavlova, rank 1170 — the
judge clearly preferred savory dishes: the round 2 pork belly went
10-2-0 and reached rank 489). This picture is savory again and small —
187,533 bytes at 1024x683 — because the competition's tie-break favours
smaller artifacts among equal win records.
