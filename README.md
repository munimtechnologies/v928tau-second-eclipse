# v928tau-second-eclipse

**Did the young binary V928 Tau's deep, asymmetric eclipse happen again?** This is a pre-registered,
blind test using public K2, TESS, ZTF and ASAS-SN photometry.

In 2017 the K2 mission saw one star of the young Taurus binary V928 Tau dim by about 60% for about half a day
([van Dam et al. 2020, AJ 160, 285](https://arxiv.org/abs/2010.11199)). The eclipse was asymmetric, which
points to a dusty disk or ring system around an unseen companion. It did not repeat before the campaign ended,
so the period is longer than 66 days, and a decade of ground photometry gave no unambiguous period. Since then
TESS has watched the star for about 100 days (2021 and 2023), and ZTF has kept imaging it.

This test does three things:

1. It reproduces the K2 eclipse and the authors' P > 66 d bound. These are the gates.
2. It searches all the newer data for a second eclipse.
3. It maps which periods from 60 to 3000 days the data now rule out.

A second eclipse would give the companion's period and predict the next eclipse.

- `PREREGISTRATION.md`: the rules, fixed 2026-11-25 before any data were looked at
- `v928.py`: the core (standard library). It is adapted from munimtechnologies/epic2043-second-occultation
- `job.py`: the pipeline. `python job.py --data-dir data --out-dir out`
- `fetch_deps.py`: fetches io_tess.py and asassn_io.py, unchanged, from munimtechnologies/epic2202-second-eclipse
  (commit 9dfda1bf)
- `io_k2.py`: the K2 C13 light curve from MAST
- `test_v928.py`: tests. `python -m unittest -v test_v928`
- `notes/`: the scoop check

Credit: van Dam, Kenworthy, David, Mamajek et al. (2020) found and modelled the eclipse and set the period
bound. Their code is at github.com/dmvandam/v928tau. Data: K2 and TESS (MAST), ZTF (IRSA), ASAS-SN Sky Patrol.

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human expert has checked
it yet. Code: Apache-2.0. Text and result files: CC BY 4.0.
