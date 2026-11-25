# Amendment 2026-11-25: follow-up of the 2019-11-27 candidate (fixed before the data exist)

Written 2026-11-25 (UTC), after grading v0.1.0 (GRADING.md) and **before** Gaia DR4 (release 2026-12-02)
and before any of the predicted windows below. Nothing in PREREGISTRATION.md changes; this adds the follow-up
that section 6 ("Follow-up") requires for a strong candidate. Made with AI agents working in MV2's name.

## 1. What is being tested

H: the grey ~25% dip of V928 Tau on 2019-11-27 (BJD 2458814.7196-2458814.7767) is a return of the 2017 K2
eclipser, with the same 0.204-d core. Then P = D / n with D in [979.6682, 979.8155] d, and the families still
allowed are n = 1, 2, 3, 4, 5, 6, 8, 12 (results/v0.1.0/vetting/implied_period_ranges.csv, primary rule).
A trial period P "predicts" a core at [2457834.90409 + kP, 2457835.10841 + kP] for whole k.

## 2. Gaia DR4 epoch photometry (2014-07 .. 2020-01)

Uses the outputs of munimtechnologies/occulters-gaia-dr4 (target v928tau) unchanged: its normalisation,
veto and dip definitions (that repository's PREREGISTRATION.md, section 3).

- **R1, the 2019 event itself.** Gaia G transits with BJD in 2458814.57-2458814.92:
  - COVERED_DIM if any transit has r <= 0.85 and BP or RP <= 0.925
  - COVERED_NORMAL if any transit between BJD 2458814.7196 and 2458814.7767 (the ZTF dip itself) has
    r >= 0.94, more than 4 sigma above 0.85, with BP or RP >= 0.88. This contradicts ZTF; it is reported first
    and is a red flag for the candidate.
  - otherwise COVERED_UNCLEAR (in window, neither) or NOT_COVERED.
- **R2, families.** For each family n, the share of its primary-allowed range that Gaia's primary veto
  scan also allows (nearest Gaia grid period). A family with 0% left is EXCLUDED_BY_GAIA.
- **R3, support.** A Gaia confirmed dip (occgaia definition, depth >= 0.15) whose time falls inside the
  predicted core (+- 0.10 d) of an allowed trial period in a surviving family SUPPORTS that family.
- **Headline:** CONFIRMED_BY_GAIA (R1 COVERED_DIM, or any R3 support), NARROWED_BY_GAIA (no support, at
  least one family excluded), UNTESTED_BY_GAIA (neither). R1 COVERED_NORMAL is reported alongside whatever
  the headline is.

Expectation, stated now: UNTESTED_BY_GAIA or NARROWED_BY_GAIA is most likely (Gaia visits a few times a month;
the cores are 0.2 d). A Gaia point inside the 2019 dip would be a lucky strike.

## 3. Ground windows after 2026-11-25

Windows (results/v0.1.0/vetting/predictions.csv): **2026-12-12 01:42 UTC +- 0.27 d (n = 8)**,
**2027-01-21 21:26 UTC +- 0.27 d (n = 3, 6, 12)**, then 2027-04-13 (4, 8, 12), 2027-06-01 (5),
2027-07-04 (6, 12), 2027-08-14 (8), 2027-09-23 (12), and **2027-12-14 11:22 UTC +- 0.30 d (all)**.

- **Data:** public photometry only. The ZTF alert stream (ALeRCE, object ZTF19aamthse), g band only
  (r-band difference photometry of this star is unreliable, GRADING.md section 2), and any later ZTF data
  release. Other public light curves (e.g. AAVSO) may be added in a dated note before their data for the
  window are looked at.
- **Veto (excludes a trial period):** a g measurement inside that period's predicted core whose flux is
  >= 0.94 of normal and more than 4 sigma above 0.85, in a frame whose comparison stars (same quadrant,
  catflags 0 in the PSF catalogue) are within 0.05 mag of their medians. For an alert-stream non-detection
  the flux is >= 0.94 when the limiting difference magnitude is >= g_ref + 3.0.
- **Dip (supports a trial period):** a negative g alert with drb >= 0.9, implied drop >= 0.15, in a frame
  passing the same comparison check, inside that period's predicted core +- 0.10 d.
- **Labels per window:** RETURN_SEEN (a dip), WINDOW_FLAT (vetoes cover at least half of the window's trial
  periods and no dip), NOT_COVERED (otherwise).
- A RETURN_SEEN would make the period one of the window's families and is the result this project exists
  for. It goes to Sheehan before any claim beyond "candidate".

## 4. What is not changed

The v0.1.0 labels, gates and numbers stand. The one-point-rule fractions stay secondary.
