# Grading: V928 Tau second-eclipse test v0.1.0 (job v928-eclipse-v1)

Graded 2026-11-25 (UTC) against PREREGISTRATION.md (fixed 2026-11-25, commit 869d495). Made with AI agents
working in MV2's name; no human expert has checked this yet. Text CC BY 4.0.

Raw outputs: `results/v0.1.0/` (results.json, summary.md, stdout.txt and every CSV the job wrote).
Hand vetting of the flagged event: `results/v0.1.0/vetting/` (sources and query URLs in each file).

## 1. Headline (pre-registered label)

**SECOND_ECLIPSE_CANDIDATE.** Gates: G1 = K2_EVENT_RECOVERED, G2 = BOUND_REPRODUCED.

| item | value |
|---|---|
| K2 eclipse recovered | box at BJD 2457835.001, width 0.25 d, depth 0.216, S/N 36.8; no other K2 detection |
| K2 core (blended flux <= 0.85) | BJD 2457834.9041 - 2457835.1084 (2017-03-22 09:41 - 14:36 UTC), 0.204 d, minimum 0.723 |
| G2 (K2 alone) | every period allowed from 66.22 d to 3000 d (pre-registered P0 window 62-70 d): authors' P > 66 d reproduced |
| measurements used | K2 3,646; ZTF 1,066 (DR24, to 2025-09-30); ASAS-SN 778 (2012-01 to 2025-01); TESS 4,603 30-min bins (S43, S44, S70, S71) |
| TESS injection-recovery | 10/10, 10/10, 8/8, 8/8 (S43, S44, S70, S71); no TESS detection |
| excluded, all data (primary rule) | 41.1% of 60-3000 d; **51.5% of the authors' range 66 d - 2.8 yr** (K2 alone: 0.1%) |
| excluded, one-point veto (secondary) | 54.1% of 60-3000 d; 68.1% of 66 d - 2.8 yr |
| strong ground events | **1: ZTF, 2019-11-27, three points in g and r, 23-25% deep** |
| single dip points (inspection only) | 1: ASAS-SN g, 2024-03-28, 0.79 (single exposure; not on any candidate period below) |

## 2. The flagged event: 2019-11-27

The job flagged three ZTF measurements on one night (BJD 2458814.7196 and .7205 in r, .7767 in g;
05:16-06:38 UTC), each at 0.77 of the star's median flux. The pre-registration requires inspection before
any claim. We checked (all by hand, 2026-11-25, files in `results/v0.1.0/vetting/`):

1. **Comparison stars on the same CCD quadrant (field 609, CCD 7, quadrant 4) stayed normal.**
   `ztf_comparison_stars.csv`: in the two r exposures, three stars of r = 14.5, 15.0 and 17.1 are
   +0.004 to +0.037 mag from their local medians (MJD 58795-58840, catflags 0), while V928 Tau is
   +0.278 and +0.280 mag (flux 0.774, 0.773). In the g exposure, stars of g = 15.7, 16.7 and 19.1 are
   +0.001, +0.015 and +0.128 (2 sigma) mag; V928 Tau is +0.305 mag (flux 0.755). The images are
   catflags 0 with limiting magnitudes 20.5-21.1, so a bad or cloudy frame is ruled out.
2. **Independent pipeline: ZTF difference imaging.** The public ZTF alert stream (ALeRCE object
   ZTF19aamthse) has a *negative* g-band detection in the same g exposure (MJD 58814.2708):
   difference magnitude 16.52 +- 0.05, deep real-bogus score drb = 0.9993. Against the local g median
   (15.005) that is a 24.7% drop, matching the PSF photometry (24.5%).
3. **Both bands, same depth.** r 22.6-22.7%, g 24.5%: grey to within a few percent, as expected for an
   opaque occulter and as the authors modelled the K2 event (an opaque disk).
4. **Short.** ZTF r was normal 1.9 d before (MJD 58812.26-58812.30) and the next data are normal: ASAS-SN g
   1.0 d after (BJD 2458815.787, 0.986) and ZTF 16 d after. The dip lasted at least 1.4 h and at most about
   3 d, consistent with the half-day K2 eclipse.
5. **Not in the discovery paper's data.** The authors' public photometry
   (github.com/dmvandam/v928tau, data/photometry/all_data.txt) ends ZTF at JD 2458684.97 (2019-07-30) and
   all data at about JD 2458772 (2019-10). Their paper (Table 4) lists a 363-370 d ZTF baseline. The
   2019-11-27 dip is after all of it.

**Caveats found while vetting (reported, not explained away):**
- The two r exposures at MJD 58814.2138/58814.2147 produced *no* r-band alert: ALeRCE lists a
  non-detection with limiting difference magnitude 19.99, although the catalogue PSF photometry of the same
  images shows the 23% drop. The star is r = 13.1, close to ZTF's saturation, and the r-band alert history
  of this star contains implausible +-20% "brightenings" (e.g. MJD 60948.41, r = 14.72), so r-band
  difference photometry looks unreliable for it; we do not know the exact cause.
- ZTF also issued negative g alerts on 2019-11-24 (MJD 58811.27, 58811.29) and 2019-12-02 (58819.23), but
  those frames are flagged (catflags 32768) and their comparison stars are off by 0.13-0.83 mag: bad frames,
  unlike 2019-11-27.
- V928 Tau is a young, spotted binary (2% spot modulation). A 25%, few-hour, grey dip is far beyond the
  spots, but a different occulter than the K2 one cannot be excluded.

**Verdict of the inspection:** a real, grey, roughly 25% dimming of V928 Tau on 2019-11-27, 979.7 days after
the K2 eclipse. Following the pre-registration it is called a **candidate second eclipse**, not a detection.

## 3. What periods it implies (with all the other data)

If the 2019 dip is the K2 eclipser returning with the same 0.204-d core, the three ZTF points must lie
inside one repeat of the core. That pins the time since K2 to 979.668-979.816 d. The orbital period is then
that interval divided by a whole number n. `results/v0.1.0/vetting/implied_period_ranges.csv` lists, for each n, the share of
that period range still allowed by all the data (primary rule and the stricter one-point rule), read
from out/allowed_periods_all*.csv:

| n | period (d) | allowed, primary | allowed, one-point |
|---|---|---|---|
| 1 | 979.67-979.82 | 100% | 100% |
| 2 | 489.83-489.91 | 100% | 54% |
| 3 | 326.56-326.61 | 100% | 37% |
| 4 | 244.92-244.95 | 100% | 55% |
| 5 | 195.93-195.96 | 42% | 0% |
| 6 | 163.28-163.30 | 100% | 13% |
| 7 | 139.95-139.97 | 0% | 0% |
| 8 | 122.46-122.48 | 62% | 5% |
| 9-11, 13-16 | 61-109 | 0% | 0% |
| 12 | 81.64-81.65 | 57% | 0% |

Eight families survive the primary rule. The job's own implied-period list (out/implied_periods.csv, tested
only at the central value) marks n = 8 excluded because its central value falls in a 0.007-d excluded gap;
62% of the n = 8 range is allowed. Fractions are read off a discrete grid (0.02-d drift per step) and are
approximate. All of them lie inside the discovery paper's search range (66 d to 2.8 yr).

## 4. Predictions (testable from the ground)

Every surviving family predicts an eclipse on **2027-12-14** (core mid BJD 2461753.97 +- 0.30, 11:22 UTC).
Before that, subsets predict (core mid, +- range from the timing constraint; the dip lasts about half a day):

| core mid (UTC) | BJD | +- d | families n | sky |
|---|---|---|---|---|
| **2026-12-12 01:42** | 2461386.571 | 0.27 | 8 | dark-sky, near opposition |
| **2027-01-21 21:26** | 2461427.393 | 0.27 | 3, 6, 12 | evening sky |
| 2027-04-13 12:55 | 2461509.038 | 0.28 | 4, 8, 12 | near the Sun |
| 2027-06-01 12:37 | 2461558.026 | 0.28 | 5 | behind the Sun |
| 2027-07-04 05:12 | 2461590.717 | 0.28 | 6, 12 | dawn |
| 2027-08-14 00:09 | 2461631.506 | 0.29 | 8 | dawn |
| 2027-09-23 19:54 | 2461672.329 | 0.29 | 12 | morning sky |
| **2027-12-14 11:22** | 2461753.974 | 0.30 | all (1, 2, 3, 4, 5, 6, 8, 12) | night sky (Asia, Pacific) |

(`results/v0.1.0/vetting/predictions.csv`; times = 2457835.00625 + q x 979.7419 d with q = k/n.) The star is r = 13.1, g = 15.0 in ZTF;
a 25% dip is easy for small telescopes. A flat light curve through a window rules out the families listed for it; a
dip confirms the return and narrows the period.

## 5. What this does and does not show

- New: the first report of a second deep dimming of V928 Tau, its independent confirmation in ZTF
  difference imaging, and the first period constraints from TESS 2021/2023 and ZTF to 2025 (51.5% of the
  authors' 66 d - 2.8 yr range now excluded under the pre-registered rule).
- Not shown: that the 2019 dip is the same eclipser. Two events cannot fix a period; that needs a dip in one
  of the windows above or in Gaia DR4 epoch photometry (2014-2020, out 2026-12-02), pre-registered in
  AMENDMENT-2026-11-25-candidate.md.

People to tell (after Sheehan's OK): D. M. van Dam, M. A. Kenworthy, T. J. David, E. E. Mamajek
(van Dam et al. 2020, AJ 160, 285, arXiv:2010.11199).
