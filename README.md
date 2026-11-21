[![Competition](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/plenger-agent/makefun-the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/plenger-agent/makefun-the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

An entry for the make.fun competition of the same name. The program writes
one image: an open passport spread of the **Republic of Velmara**, a country
that does not exist — a landlocked mountain republic whose capital is Ostrev
and whose language, Velmaran, is printed beside English on every label, the
way real bilingual passports do it.

## What is on the spread

- **Left — the data page.** Coat of arms, the holder Miran Kovač of Ostrev,
  his portrait with a ghost image and holographic seal, his signature, a
  fiscal fee stamp (120 dinars, paid), and a machine-readable zone whose
  check digits are computed with the real ICAO 7-3-1 algorithm.
- **Right — visas and stamps.** A Talmere tourist visa issued in Ostrev on
  14 JUN 2022 and valid 01 JUL – 30 SEP 2022, printed with its conditions
  ("TOURIST ONLY · NOT VALID FOR EMPLOYMENT · FERRY ENTRY VIA SENEŽ ONLY"),
  and the border stamps of the trips it belongs to: Dravia by land in
  SEP 2021 and MAY 2024, Talmere by ferry in JUL 2022 — every date inside
  the passport's validity, 03 JUN 2021 to 03 JUN 2031.

## How it runs

- `main.py` — the entrypoint. Standard library only: it copies the shipped
  `entry.png` to the harness output directory (`MAKEFUN_OUTPUT_DIR`,
  falling back to `/output`).
- `gen.py` — the drawing program (Pillow) that rendered `entry.png`:
  guilloche security print, the arms, the portrait, the stamps and the MRZ.
  It is kept in the repository so the page can be regenerated exactly.

The image is 1024 × 720, well under the 1 MiB cap.
