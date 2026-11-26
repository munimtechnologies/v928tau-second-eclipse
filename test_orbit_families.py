# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. Made with AI agents working in MV2's name.
"""Tests for orbit_families.py (stdlib unittest)."""
import csv
import math
import os
import unittest

import orbit_families as of

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "results", "v0.1.0", "orbits", "orbit_families.csv")


class TestPhysics(unittest.TestCase):
    def test_transverse_speeds_match_paper(self):
        # van Dam et al. 2020: 73.53 km/s (star A), 69.26 km/s (star B)
        self.assertAlmostEqual(of.v_t_kms("A"), 73.53, delta=0.02)
        self.assertAlmostEqual(of.v_t_kms("B"), 69.26, delta=0.02)

    def test_circular_orbit_ruled_out_as_in_paper(self):
        # paper: circular orbit at v_t gives a ~ 0.1 au and P < 66 d
        p, a = of.circular_orbit("A")
        self.assertLess(p, 66.0)
        self.assertTrue(0.09 < a < 0.13, a)

    def test_kepler_consistency(self):
        o = of.orbit(365.25, "A", mp_mjup=0.0, m_star=1.0)
        self.assertAlmostEqual(o["a_au"], 1.0, delta=1e-3)
        self.assertAlmostEqual(o["v_circ_kms"], 29.78, delta=0.05)

    def test_periastron_speed_equals_vt(self):
        for n in of.FAMILIES:
            for star in ("A", "B"):
                o = of.orbit(of.D_DAYS / n, star)
                mu = of.GM_SUN * (of.M_STAR + of.MP_MJUP * of.MJUP_MSUN)
                a = o["a_au"] * of.AU
                e = o["e_min"]
                v_peri = math.sqrt(mu * (1 + e) / (a * (1 - e))) / 1000.0
                self.assertAlmostEqual(v_peri, of.v_t_kms(star), delta=1e-6)

    def test_main_claims(self):
        rs = of.rows()
        n1 = [r for r in rs if r["n"] == 1]
        for r in n1:  # 979.7 d family reaches the 3.2 au stability limit
            self.assertGreater(r["r_ap_au"], 3.2)
            self.assertLess(r["r_ap_au"], 3.35)
            self.assertGreater(r["e_min"], 0.84)
        for r in rs:
            if r["n"] >= 2:
                self.assertLess(r["r_ap_au"], 2.05)
            self.assertGreater(r["e_min"], 0.40)
            self.assertTrue(0.18 < r["r_peri_au"] < 0.27, r)
            self.assertGreaterEqual(r["e_min_mp0"], r["e_min"])

    def test_hill_minimum_mass_is_a_few_jupiters(self):
        masses = [of.hill_min_mass_mjup(of.D_DAYS / n, s) for n in of.FAMILIES for s in ("A", "B")]
        self.assertTrue(3.5 < max(masses) < 5.0, max(masses))
        self.assertGreater(min(masses), 0.5)
        # 80 MJup (the paper's value) is comfortably stable in every family
        self.assertTrue(all(m < of.MP_MJUP for m in masses))

    def test_holman_wiegert(self):
        self.assertAlmostEqual(of.holman_wiegert_ac(33.119, 0.554), 3.39, delta=0.01)
        self.assertAlmostEqual(of.holman_wiegert_ac(1.0, 0.0), 0.274, delta=1e-9)


class TestCommittedTable(unittest.TestCase):
    def test_csv_matches_code(self):
        if not os.path.exists(CSV_PATH):
            self.skipTest("table not present in this checkout")
        with open(CSV_PATH, newline="") as f:
            table = list(csv.DictReader(f))
        rs = of.rows()
        self.assertEqual(len(table), len(rs))
        for t, r in zip(table, rs):
            self.assertEqual(int(t["n"]), r["n"])
            self.assertEqual(t["star"], r["star"])
            self.assertAlmostEqual(float(t["period_d"]), r["period_d"], delta=0.002)
            for k in ("v_t_kms", "v_circ_kms"):
                self.assertAlmostEqual(float(t[k]), r[k], delta=0.002 * r[k] + 0.002)
            for k in ("e_min", "e_min_mp0"):
                self.assertAlmostEqual(float(t[k]), r[k], delta=0.002)
            for k in ("a_au", "r_peri_au", "r_ap_au"):
                self.assertAlmostEqual(float(t[k]), r[k], delta=0.005 * r[k] + 0.0002)


if __name__ == "__main__":
    unittest.main(verbosity=2)
