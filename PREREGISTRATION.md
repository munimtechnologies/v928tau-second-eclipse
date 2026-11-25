# Pre-registration: did V928 Tau's asymmetric eclipse happen again?

Fixed on 2026-11-25, before any light curve of V928 Tau (K2, TESS, ZTF or ASAS-SN) was downloaded or looked
at by us, and before any period scan was run. MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents
working in MV2's name; no human expert has checked it. Code Apache-2.0; text CC BY 4.0.

## 1. The near miss

van Dam, Kenworthy, David et al. (2020, AJ 160, 285; [arXiv:2010.11199](https://arxiv.org/abs/2010.11199);
code [github.com/dmvandam/v928tau](https://github.com/dmvandam/v928tau)) found one deep, asymmetric eclipse of
the young weak-lined T Tauri binary V928 Tau (EPIC 247795097 = TIC 268324580, Taurus, about 145 pc). It
appeared in K2 Campaign 13 near BJD 2457835 (2017-03-22).

- **Shape.** One star of the 0.24-arcsec pair dims by about 60% over about 9 hours and recovers about 5 hours
  later. That is about 30% in the blended light, and about half a day in all.
- **Proposed cause.** A substellar companion carrying a tilted disk or ring system, on an eccentric orbit.
- **Period.** The eclipse did not repeat before the campaign ended, so P > 66 d. Stability caps the search at
  2.8 yr. Folding about ten years of ground photometry (ASAS, ASAS-SN, ATLAS, CRTS, KELT, PTF, SuperWASP, the
  first year of ZTF and AAVSO observers) gave "no unambiguous period". The authors note that a half-day eclipse
  is easily lost in the day-night cycle.

Since then, TESS has observed the star in Sectors 43 and 44 (September to November 2021) and Sectors 70 and
71 (September to November 2023). That is about 100 days of continuous coverage. ZTF has also kept imaging it
through DR24 (to 2025-10-22). Our searches on 2026-11-25 (notes/scoop-check-2026-11-25.md) turned up nothing
that reports a second eclipse, a period, or a search of the TESS data for this star. None of the 12 works
OpenAlex lists as citing the paper is a follow-up of the eclipse.

## 2. Data (all public; fetched by job.py)

- **K2 Campaign 13.** Long-cadence light curve from MAST (ktwo247795097-c13_llc.fits), using SAP flux.
  Cadences with quality bits 1, 2, 4, 8, 32, 128, 32768 or 1048576 (thruster firing) are dropped. The flux is
  divided by 5-day bin medians.
- **ZTF.** Light curves from IRSA (DR24 at the time of the run). Points are kept if catflags = 0 and
  magerr <= 0.30. Each object is normalised by its median, with sigma = max(0.921 magerr, the object's robust
  scatter).
- **ASAS-SN Sky Patrol v2.** Fetched with the pyasassn client (the light curves end around 2025-02). Points
  must have quality G and relative error <= 0.05. Each band and camera is normalised by its median, with sigma =
  max(error, robust scatter).
- **TESS.** Every TESScut sector numbered 1-999 (expected: 43, 44, 70, 71). TESScut also lists a "sector 1751",
  which is dropped and reported. From an 11x11 cutout we take a 3x3 aperture and the peak pixel, with local
  background subtraction, divide by 5-day bin medians and use 30-minute bins for vetoes.
  - io_tess.py and asassn_io.py are pinned unchanged from munimtechnologies/epic2202-second-eclipse commit
    9dfda1bf.
  - The target's share of the aperture flux is estimated from TIC Tmag 11.678 (15000 e-/s at Tmag 10, 75% of
    the PSF in 3x3), divided by the measured median aperture flux.

Spot modulation (2.25 d and 2.48 d, 2% and 1.1%; van Dam et al.) is not removed. The veto and detection
thresholds below are set wide enough to tolerate it.

## 3. Gates (known answers first)

- **G1, the K2 eclipse.** The box search (section 5) must find a detection within 0.5 d of BJD 2457835.01 with
  depth >= 0.15, and nothing else in C13.
  - Labels: K2_EVENT_RECOVERED, K2_EVENT_RECOVERED_PLUS_OTHERS (each extra detection is then shown and judged
    in the grading), K2_EVENT_MISSED, K2_UNAVAILABLE.
- **G2, the authors' bound.** The period scan on K2 alone must allow every trial period from some P0 up to
  3000 d, with P0 in 62-70 d. This is the authors' P > 66 d. Labels: BOUND_REPRODUCED / BOUND_DIFFERENT.
- A failed gate is reported first, together with the results, and any article says so.

## 4. The eclipse core and vetoes

- **Core.** In K2 C13 the job takes the lowest point within 1 d of BJD 2457835.01 and the contiguous run around
  it with blended flux <= 0.85. A gap > 0.1 d ends the run. If that run is at least 0.15 d long it is the core.
  Otherwise the core is BJD 2457835.01 +- 0.12 d. We expect a core of about 0.3 d.
- **Prediction.** For a trial period P, the core repeats at core + nP (n != 0). The eclipse is assumed to repeat
  with the same shape. An eccentric orbit does this; changing ring geometry might not.
- **Veto points.** A point inside a predicted core is a veto if both of these hold:
  - its dip 1 - r is below 0.06 (K2 and TESS 30-min bins) or 0.08 (ZTF and ASAS-SN)
  - r - f_exp > 4 sigma. Here f_exp is the flux the source would show in the core: 0.85 for K2, ZTF and
    ASAS-SN, and 1 - 0.15 x share for TESS. TESS is not used for vetoes if share < 0.3.

  A veto is strong if r - f_exp > 10 sigma.
- **Excluded period (primary).** One predicted core holds two veto points, or one strong veto. Exclusion
  therefore means "no repeat of at least half the K2 depth through the whole core". A shallower or shorter
  repeat is not excluded.
- **Secondary scan, reported but not the headline.** A single veto point is enough to exclude ("one-point veto").
  This matters for sparse ground data, where two points rarely fall in a 0.3-d core.

## 5. Second-eclipse search

- **K2 and TESS.** Box search with widths 0.15, 0.25 and 0.40 d in 0.02-d steps. A detection needs all of:
  - depth >= 0.10 in the aperture and S/N >= 10
  - >= 60% of the in-box cadences present
  - >= 10 points on each flank (0.05-1.5 d outside the box), with flank medians within 0.04 of 1

  Detections within 0.5 d are merged. A TESS detection is strong if its peak-pixel depth is at least half the
  aperture depth.
- **ZTF and ASAS-SN.** A dip point has depth >= 0.15 and >= 5 sigma. Points within 1 d are grouped, and an event
  is strong with >= 2 dip points. Single dip points are listed for inspection only.
- **TESS injection-recovery.** A 0.6-d trapezoid (0.1-d flat bottom) of depth 0.30 x share is injected at 10
  evenly spaced times. It is recovered if detected within 0.5 d.
- **Inspection.** Every strong event is inspected by eye and in pixel data before any claim. This is the lesson
  of the EPIC 220208795 test, where three flagged TESS events turned out to be scattered light. A strong event is
  only ever called a candidate.

## 6. Period scan and outcomes

- **Trial periods.** 60-3000 d on a geometric grid, stepped so the farthest predicted core drifts at most 0.02 d
  between steps.
- **Four scans:**
  - K2 only: the authors' state, used for gate G2
  - all data: the headline
  - ZTF + ASAS-SN + TESS only: what is new
  - all data with the one-point veto
- **Reported.** For each scan: the excluded fraction overall, in the authors' range 66-1022 d, and in bins
  60-70-80-100-125-150-200-300-400-500-700-1022-1500-2000-3000 d, plus the allowed period runs.
- **Headline.** One of:
  - SECOND_ECLIPSE_CANDIDATE: any strong event in TESS, ZTF or ASAS-SN. The implied periods with the K2 eclipse
    are then listed, with whether each survives all the data.
  - NO_SECOND_ECLIPSE
  - NO_NEW_DATA
- **Follow-up.** Any strong candidate goes to a pre-registered follow-up (pixel-level vetting, and the next
  predicted eclipse dates for the surviving periods) before an article calls it more than a flagged dip.

## 7. Later amendments (dated, made before the new data are looked at)

- Gaia DR4 epoch photometry (2014-07 to 2020-01; release 2026-12-02) as a further veto set.
- Sky Patrol v2 after its announced full rebuild, if that extends the light curves past 2025-02.

## 8. People to tell (after grading, with Sheehan's OK)

D. M. van Dam, M. A. Kenworthy, T. J. David, E. E. Mamajek and the other authors of van Dam et al. (2020).
