# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. Made with AI agents working in MV2's name.
"""Orbit each candidate period family of V928 Tau would need (post-grading derivation).

If the 2019-11-27 ZTF dip is the 2017 K2 eclipser returning, its period is P = D/n with
D = 979.668-979.816 d (results/v0.1.0/vetting/implied_period_ranges.csv). Van Dam et al.
(2020, AJ 160, 285; arXiv:2010.11199) measured the occulter's transverse speed from the K2
eclipse, 6.637 R*/day (73.53 km/s if it orbits star A, 69.26 km/s if B), and showed this is
too fast for a circular orbit with P > 66 d, so the orbit must be eccentric. The speed of a
body on an eccentric orbit never exceeds its periastron speed,

    v_peri^2 = mu (1 + e) / (a (1 - e)),   mu = G (M* + Mp),

so v_t <= v_peri gives a MINIMUM eccentricity for each period:

    e_min = (x^2 - 1) / (x^2 + 1),   x = v_t / v_circ,   v_circ = (2 pi mu / P)^(1/3).

We report e_min, the semi-major axis, and the periastron and apastron distances at e_min,
and compare the apastron with the 3.2 au stability limit van Dam et al. adopted (10% of the
32 au projected binary separation; Quarles et al.). We also give the smallest companion
mass for which the fitted disk (radius 0.9923 R*) fits inside 0.3 Hill radii at periastron,
their disk-stability criterion. Stellar masses: 0.70 Msun (their magnetic models).

Standard library only.  python orbit_families.py --out results/v0.1.0/orbits/orbit_families.csv
"""
import argparse
import csv
import math

GM_SUN = 1.32712440018e20          # m^3 s^-2
AU = 1.495978707e11                # m
DAY = 86400.0                      # s
R_SUN = 6.957e8                    # m
MJUP_MSUN = 1.26686534e17 / GM_SUN # Jupiter mass in solar masses

D_LO, D_HI = 979.668, 979.816      # days, interval of K2-to-2019 separations (implied_period_ranges.csv)
D_DAYS = 0.5 * (D_LO + D_HI)       # 979.742 d
FAMILIES = [1, 2, 3, 4, 5, 6, 8, 12]  # families still (fully or partly) allowed by all data
VT_RSTAR_PER_DAY = 6.637           # van Dam et al. 2020, opaque slow disk model
STAR_RADIUS_RSUN = {"A": 1.376, "B": 1.296}  # van Dam et al. 2020 Table 1
M_STAR = 0.70                      # Msun, Dartmouth magnetic models (both stars)
MP_MJUP = 80.0                     # companion mass van Dam et al. used for the Hill test
R_DISK_RSTAR = 0.9923              # fitted disk radius, stellar radii
HILL_FRACTION = 0.3                # r_disk < 0.3 r_Hill
R_AP_LIMIT_AU = 3.2                # van Dam et al. apastron limit

COLUMNS = ["n", "period_d", "star", "v_t_kms", "v_circ_kms", "e_min", "a_au",
           "r_peri_au", "r_ap_au", "e_min_mp0"]


def v_t_kms(star):
    """Occulter transverse speed in km/s for the given host star."""
    return VT_RSTAR_PER_DAY * STAR_RADIUS_RSUN[star] * R_SUN / DAY / 1000.0


def orbit(period_d, star, mp_mjup=MP_MJUP, m_star=M_STAR):
    """Minimum-eccentricity orbit for period period_d (days) around the given star."""
    mu = GM_SUN * (m_star + mp_mjup * MJUP_MSUN)
    p = period_d * DAY
    v_c = (2.0 * math.pi * mu / p) ** (1.0 / 3.0)
    a = mu / v_c ** 2
    x2 = (v_t_kms(star) * 1000.0 / v_c) ** 2
    e = max(0.0, (x2 - 1.0) / (x2 + 1.0))
    return {"v_circ_kms": v_c / 1000.0, "e_min": e, "a_au": a / AU,
            "r_peri_au": a * (1.0 - e) / AU, "r_ap_au": a * (1.0 + e) / AU}


def r_disk_au(star):
    return R_DISK_RSTAR * STAR_RADIUS_RSUN[star] * R_SUN / AU


def hill_min_mass_mjup(period_d, star, m_star=M_STAR):
    """Smallest companion mass (MJup) with r_disk <= 0.3 r_Hill at periastron (bisection)."""
    target = r_disk_au(star)

    def margin(mp):
        o = orbit(period_d, star, mp, m_star)
        m_tot = m_star + mp * MJUP_MSUN
        r_h = o["r_peri_au"] * (mp * MJUP_MSUN / (3.0 * m_tot)) ** (1.0 / 3.0)
        return HILL_FRACTION * r_h - target

    lo, hi = 1e-6, 500.0
    if margin(hi) < 0:
        return float("inf")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if margin(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return hi


def holman_wiegert_ac(a_bin_au, e_bin, mu_bin=0.5):
    """Critical semi-major axis for S-type orbits (Holman & Wiegert 1999, eq. 1)."""
    e, m = e_bin, mu_bin
    frac = (0.464 - 0.380 * m - 0.631 * e + 0.586 * m * e + 0.150 * e ** 2
            - 0.198 * m * e ** 2)
    return frac * a_bin_au


def circular_orbit(star, m_star=M_STAR):
    """Period (d) and radius (au) of a circular orbit moving at v_t (the case ruled out)."""
    mu = GM_SUN * m_star
    v = v_t_kms(star) * 1000.0
    return 2.0 * math.pi * mu / v ** 3 / DAY, mu / v ** 2 / AU


def rows():
    out = []
    for n in FAMILIES:
        p = D_DAYS / n
        for star in ("A", "B"):
            o = orbit(p, star)
            o0 = orbit(p, star, mp_mjup=0.0)
            out.append({"n": n, "period_d": p, "star": star, "v_t_kms": v_t_kms(star),
                        "v_circ_kms": o["v_circ_kms"], "e_min": o["e_min"], "a_au": o["a_au"],
                        "r_peri_au": o["r_peri_au"], "r_ap_au": o["r_ap_au"],
                        "e_min_mp0": o0["e_min"]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    rs = rows()
    for r in rs:
        print("n=%2d P=%8.3f d star %s  e_min=%.4f (Mp=0: %.4f)  a=%.4f au  r_peri=%.4f  r_ap=%.4f"
              % (r["n"], r["period_d"], r["star"], r["e_min"], r["e_min_mp0"], r["a_au"],
                 r["r_peri_au"], r["r_ap_au"]))
    for n in FAMILIES:
        for star in ("A", "B"):
            print("Hill-stable disk needs Mp >= %.2f MJup (n=%d, star %s)"
                  % (hill_min_mass_mjup(D_DAYS / n, star), n, star))
    pc, ac = circular_orbit("A")
    print("circular orbit at v_t (star A): P = %.1f d, a = %.3f au" % (pc, ac))
    print("Holman-Wiegert a_c for a_bin = 33.119 au, e = 0.554: %.2f au" % holman_wiegert_ac(33.119, 0.554))
    if args.out:
        with open(args.out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(COLUMNS)
            for r in rs:
                w.writerow([r["n"], "%.3f" % r["period_d"], r["star"], "%.3f" % r["v_t_kms"],
                            "%.3f" % r["v_circ_kms"], "%.4f" % r["e_min"], "%.4f" % r["a_au"],
                            "%.4f" % r["r_peri_au"], "%.4f" % r["r_ap_au"], "%.4f" % r["e_min_mp0"]])


if __name__ == "__main__":
    main()
