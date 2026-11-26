# What orbit would each candidate period need? (derived 2026-11-26, after grading)

Made with AI agents working in MV2's name (Munim, Inc.). No human expert has checked it yet.
Licence: Apache-2.0 (code), CC BY 4.0 (text and table).

This note is a **derivation, not a new test**. It combines two published inputs:

1. The candidate period families of this repository (GRADING.md, AMENDMENT-2026-11-25-candidate.md):
   if the 2019-11-27 ZTF dip is the 2017 K2 eclipser returning, P = D/n with
   D = 979.668-979.816 d, and n = 1, 2, 3, 4, 6 (fully allowed) or 5, 8, 12 (partly allowed).
2. The K2 eclipse model of van Dam et al. 2020 (AJ 160, 285; arXiv:2010.11199): the occulting disk
   crosses the star at 6.637 +- 0.002 R*/day (73.53 km/s if it orbits V928 Tau A, 69.26 km/s if B);
   stellar radii 1.376 and 1.296 Rsun and masses 0.70 Msun (Dartmouth magnetic models); disk radius
   0.9923 R*; disk stability r_disk < 0.3 r_Hill at periastron with Mp = 80 MJup; apastron limit
   r_ap < 3.2 au (10% of the 32 au projected binary separation, Quarles et al.). They showed that
   a circular orbit at this speed would have a ~ 0.1 au and P < 66 d, which the K2 data exclude,
   so the orbit must be eccentric, and they mapped eccentricity over a grid of periods (their
   Figure 9). They had no period to evaluate it at.

## Method

The speed of a body on a Kepler orbit is largest at periastron, v_peri^2 = mu (1+e) / (a (1-e)).
The occulter's transverse speed cannot exceed that, so for each period

    e_min = (x^2 - 1)/(x^2 + 1),  x = v_t / v_circ,  v_circ = (2 pi mu / P)^(1/3),  mu = G (M* + Mp).

e_min is reached if the eclipse happened at periastron with the motion across the line of sight;
any other geometry needs a larger e. Code: `orbit_families.py` (stdlib), tests
`test_orbit_families.py` (they also check the committed table against the code).
Table: `results/v0.1.0/orbits/orbit_families.csv` (Mp = 80 MJup; column e_min_mp0 is Mp -> 0).

## Result

| n | P (d) | e_min (star A / B) | apastron at e_min, au (A / B) |
|---|---|---|---|
| 1 | 979.7 | 0.866 / 0.850 | 3.31 / 3.28 |
| 2 | 489.9 | 0.795 / 0.772 | 2.01 / 1.98 |
| 3 | 326.6 | 0.740 / 0.712 | 1.48 / 1.46 |
| 4 | 244.9 | 0.694 / 0.661 | 1.19 / 1.17 |
| 5 | 195.9 | 0.653 / 0.617 | 1.00 / 0.98 |
| 6 | 163.3 | 0.617 / 0.578 | 0.87 / 0.85 |
| 8 | 122.5 | 0.554 / 0.511 | 0.69 / 0.67 |
| 12 | 81.6 | 0.453 / 0.404 | 0.49 / 0.48 |

- **Every family needs a strongly eccentric orbit**, e >= 0.40 even for the shortest period, and
  e >= 0.85 for 979.7 d. Periastron falls at 0.18-0.27 au in every family (it is set mainly by
  v_t, r_peri ~ 2 mu / v_t^2), so the 2017 eclipse would have happened near closest approach.
- **The n = 1 family (979.7 d) reaches the discoverers' stability limit**: at its minimum
  eccentricity its apastron is 3.28-3.31 au (3.19-3.21 au as Mp -> 0), at or just beyond the
  3.2 au limit van Dam et al. adopted, and beyond the 2.56 au prograde limit (8%). Every shorter
  family stays inside 2.01 au. The 979.7 d family is therefore dynamically marginal, and the
  shorter families are favoured, if the binary separation is near 32 au. For the binary orbit
  fitted by van Dam et al. (a = 33.1 au, e = 0.554, HPD 18.8-57.7 au), the Holman & Wiegert (1999)
  critical semi-major axis is 0.102 a_bin = 3.39 au (1.9-5.9 au over the HPD range), so this is
  a preference, not an exclusion.
- **The disk is Hill-stable in every family** for any companion above about 4 Jupiter masses
  (the largest minimum, ~4.2 MJup, is for n = 12 around star A; the tests check 3.5-5 MJup), so
  the Hill criterion does not separate the families; the 80 MJup brown dwarf the discoverers
  considered is comfortably stable in all of them.

## What this changes for observers

Nothing about the dates: every family still predicts 2027-12-14. It ranks them: the 2026-12-12
window (n = 8, e >= 0.51-0.55) and the 2027-01-21 window (n = 3, 6, 12) test families that are
dynamically comfortable, while the 979.7 d family alone would need e >= 0.85 and an orbit reaching
the edge of the stable zone.

## Limits

- Circular binary-stability rules applied to an eccentric companion are approximate; the 3.2 au
  limit itself rests on a projected separation.
- Masses from magnetic models (0.70 Msun). With the standard models (0.45 Msun) the orbits shrink
  by (0.45/0.70)^(1/3) and e_min rises (n = 1: about 0.90, apastron about 2.8 au), but the binary
  orbit and its stability limit would shrink too.
- The derivation assumes the 2019 dip is the same occulter, which is not established.
