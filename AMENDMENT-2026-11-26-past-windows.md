# Amendment 2026-11-26: the windows that already passed (2025-10 .. 2026-11)

Written 2026-11-26 ~05:30 UTC, before the ZTF alert-stream rows inside these windows were examined.
Made with AI agents working in MV2's name. Nothing in PREREGISTRATION.md or AMENDMENT-2026-11-25-candidate.md
changes.

## Why

v0.1.0 used ZTF DR24 photometry only to 2025-09-30 (BJD 2460948.94). AMENDMENT-2026-11-25-candidate.md section 3
lists windows from 2026-12 onward. The windows between those dates were missed: the families n = 1, 2, 3, 4, 5,
6, 8, 12 also predict eclipse cores in 2025-10 .. 2026-11, which the public ZTF alert stream (ALeRCE object
ZTF19aamthse, data to MJD 61351.4 = 2026-11-07 as of this writing) already covers.

**Disclosure:** before writing this note we had seen the list of alert *detections* after MJD 61000 (2025-12-23):
all 18 have isdiffpos = +1 (brighter than the reference), none is a negative (dimming) alert. We had seen the
non-detection rows only for MJD > 61330 (one window, 2026-11-01, falls in a data gap there: MJD 61340.45 - 61347.29).

## Windows (MJD = BJD - 2400000.5; barycentric correction of a few minutes ignored)

Predicted core of family q = k/n: [57834.40409 + q x 979.6682, 57834.60841 + q x 979.8155] (MJD), i.e. the union
over each family's full timing range (implied_period_ranges.csv), not only its allowed part.

| q | families n | window MJD | UTC |
|---|---|---|---|
| 3.2 | 5 | 60969.342 - 60970.018 | 2025-10-21 08:13 - 2025-10-22 00:26 |
| 3.25 | 4, 8, 12 | 61018.326 - 61019.009 | 2025-12-09 07:49 - 2025-12-10 00:13 |
| 3.3333 | 3, 6, 12 | 61099.965 - 61100.660 | 2026-02-28 23:09 - 2026-03-01 15:50 |
| 3.375 | 8 | 61140.784 - 61141.486 | 2026-04-10 18:49 - 2026-04-11 11:40 |
| 3.4 | 5 | 61165.276 - 61165.981 | 2026-05-05 (Sun in Taurus; no data expected) |
| 3.4167 | 12 | 61181.637 - 61182.345 | 2026-05-21 (Sun in Taurus; no data expected) |
| 3.5 | 2, 4, 6, 8, 12 | 61263.243 - 61263.963 | 2026-08-11 05:50 - 2026-08-11 23:07 |
| 3.5833 | 12 | 61344.882 - 61345.614 | 2026-10-31 21:10 - 2026-11-01 14:44 |
| 3.6 | 5 | 61361.210 - 61361.944 | 2026-11-17 (after the alert data end) |

## Rules (exactly those of AMENDMENT-2026-11-25-candidate.md section 3)

- g band only (fid 1). Veto: a g alert-stream non-detection inside the window with diffmaglim >= g_ref + 3.0 =
  18.0 (g_ref = 15.0, the star's ZTF g median) means flux >= 0.94 of normal at that time.
- Dip: a negative g alert (isdiffpos -1) with drb >= 0.9 and implied drop >= 0.15 inside the window +- 0.10 d.
- Because each window is short (0.68-0.72 d) and a ZTF visit samples one instant, a g veto excludes only the
  trial periods whose core contains that instant. For each window we report the share of the family's timing
  range D in [979.6682, 979.8155] that the vetoes exclude (D is excluded by a veto at time t when
  57834.40409 + qD <= t <= 57834.60841 + qD).
- **Comparison-star check:** the rule asks for comparison stars within 0.05 mag in the PSF catalogue. ZTF's
  public PSF catalogue (DR24) does not reach most of these frames, so vetoes in frames after DR24 are labelled
  PROVISIONAL (to be confirmed when the next ZTF data release is out). A deep difference-image non-detection is
  hard to fake with a bad frame (clouds make diffmaglim shallower, and the >= 18.0 cut removes those).
- Labels per window: RETURN_SEEN, WINDOW_FLAT (vetoes cover at least half the window's timing range, no dip),
  PARTLY_COVERED (some vetoes, less than half), NOT_COVERED.
- A family is EXCLUDED here only if WINDOW_FLAT and every veto in it passes the comparison check; with PROVISIONAL
  vetoes it is reported as DISFAVOURED.
