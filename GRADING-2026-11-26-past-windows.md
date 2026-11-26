# Grading 2026-11-26: the windows that already passed (2025-10 .. 2026-11)

Graded 2026-11-26 (UTC) under AMENDMENT-2026-11-26-past-windows.md. Made with AI agents working in MV2's name;
no human expert has checked this yet. Text CC BY 4.0. Data: `results/v0.1.0/vetting/past_windows_alerce.csv`.

**Result: every window is NOT_COVERED.** No ZTF alert-stream row of any band falls inside any of the eight
predicted eclipse cores between 2025-10-21 and 2026-11-01. ZTF visited V928 Tau every 1-5 days in season,
and each core lasts about 0.7 d (union over the timing range), so a miss in all of them is not surprising:
three windows fall in the seasonal gap (Sun near Taurus, 2026-03 .. 2026-08), and the rest fell between visits.
The window of 2026-11-17 (n = 5) is after the alert data end (2026-11-07).

- Nothing is excluded and nothing is supported. The family list (n = 1, 2, 3, 4, 6 in full; 5, 8, 12 in part)
  and the predictions in `predictions.csv` stand unchanged.
- One near row, reported, not counted: an r-band negative alert at MJD 60970.420 (2025-10-22 10:05 UTC),
  difference magnitude 15.42 +- 0.19 (about a 12% drop against r = 13.1), real-bogus score 0.55. It lies 0.40 d
  after the latest predicted core end of the n = 5 window, is in the r band (whose difference photometry is
  unreliable for this star) and has drb below 0.9. Under the rules it is neither a dip nor a veto.
- The 18 alert detections after MJD 61000 (2025-12-23) are all positive (brighter than the reference image by up to about 10%
  in g), consistent with the star's spot variability.

**Correction to GRADING.md section 2:** the times "05:16-06:38 UTC" there were converted from BJD and include the
~8-minute barycentric correction. The ZTF exposure times (MJD, UTC) are 05:08 (r), 05:09 (r) and 06:30 (g) on
2019-11-27. No number derived from BJD changes.

Next checks, as fixed in AMENDMENT-2026-11-25-candidate.md: Gaia DR4 (2026-12-02) for the 2019 night itself and
2014-2020 coverage, the 2026-11-17 window when ALeRCE data reach it, then 2026-12-12 (n = 8) and 2027-01-21
(n = 3, 6, 12).
