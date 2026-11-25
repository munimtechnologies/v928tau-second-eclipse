# v928tau-second-eclipse

**Did the young binary V928 Tau's deep, asymmetric eclipse happen again?** This is a pre-registered,
blind test using public K2, TESS, ZTF and ASAS-SN photometry.

## Result (v0.1.0, graded 2026-11-25): a candidate second eclipse on 2019-11-27

- **Label: SECOND_ECLIPSE_CANDIDATE.** Both gates passed: the K2 eclipse was recovered and the authors'
  P > 66 d bound reproduced.
- On **2019-11-27** ZTF caught V928 Tau about **25% fainter in both g and r** (three exposures over 1.4 h),
  979.7 days after the K2 eclipse. Comparison stars on the same chip were normal, and ZTF's independent
  difference-imaging alert stream recorded the same g-band drop (real-bogus score 0.999). The discovery
  paper's data end before that night.
- If it is the same eclipser, the period is 979.7/n days. With all data, n = 1, 2, 3, 4, 6 survive in full
  and n = 5, 8, 12 in part. Every surviving period predicts an eclipse on **2027-12-14**; subsets predict
  **2026-12-12** (n = 8) and **2027-01-21** (n = 3, 6, 12).
- 51.5% of the authors' 66 d - 2.8 yr period range is now excluded (0.1% with K2 alone).
- It is a candidate, not a detection: two events cannot fix a period, and a different occulter is possible.
  The follow-up (Gaia DR4 on 2026-12-02 and the windows above) was fixed in advance in
  `AMENDMENT-2026-11-25-candidate.md`.

Details: `GRADING.md`. Outputs: `results/v0.1.0/`; hand vetting and predictions: `results/v0.1.0/vetting/`.

## Background

In 2017 the K2 mission saw one star of the young Taurus binary V928 Tau dim by about 60% for about half a day
([van Dam et al. 2020, AJ 160, 285](https://arxiv.org/abs/2010.11199)). The eclipse was asymmetric, which
points to a dusty disk or ring system around an unseen companion. It did not repeat before the campaign ended,
so the period is longer than 66 days, and a decade of ground photometry gave no unambiguous period. Since then
TESS has watched the star for about 100 days (2021 and 2023), and ZTF has kept imaging it.

## Files

- `PREREGISTRATION.md`: the rules, fixed 2026-11-25 before any data were looked at
- `GRADING.md`, `AMENDMENT-2026-11-25-candidate.md`: the graded result and the pre-registered follow-up
- `v928.py`: the core (standard library). It is adapted from munimtechnologies/epic2043-second-occultation
- `job.py`: the pipeline. `python job.py --data-dir data --out-dir out`
- `fetch_deps.py`: fetches io_tess.py and asassn_io.py, unchanged, from munimtechnologies/epic2202-second-eclipse
  (commit 9dfda1bf)
- `io_k2.py`: the K2 C13 light curve from MAST
- `test_v928.py`: tests. `python -m unittest -v test_v928`
- `notes/`: the scoop checks

Credit: van Dam, Kenworthy, David, Mamajek et al. (2020) found and modelled the eclipse and set the period
bound. Their code and photometry are at github.com/dmvandam/v928tau. Data: K2 and TESS (MAST), ZTF (IRSA;
alerts via ALeRCE), ASAS-SN Sky Patrol.

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human expert has checked
it yet. Code: Apache-2.0. Text and result files: CC BY 4.0.
