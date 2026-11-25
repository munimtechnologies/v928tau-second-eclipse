# Copyright 2026 Munim, Inc.
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name.
"""Tests for v928.py (standard library only)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import v928 as vt  # noqa: E402

T0 = vt.T_MIN_PUBLISHED


def k2_like(core, step=0.0204, t_start=2457820.5, n=3922, sigma=0.005, depth_r=0.7):
    """Rows covering t_start .. t_start + n*step with the event inside `core`."""
    rows = []
    for k in range(n):
        t = t_start + k * step
        r = depth_r if core[0] <= t <= core[1] else 1.0
        rows.append((t, r, sigma, "k2", vt.CORE_FLUX))
    return rows


class TestCore(unittest.TestCase):
    def test_measure_core_v_shape(self):
        t = [T0 + k * 0.02 for k in range(-100, 101)]
        r = [1.0 - 0.3 * max(0.0, 1.0 - abs(x - T0) / 0.3) for x in t]
        m = vt.measure_core(t, r)
        self.assertAlmostEqual(m["t_min"], T0, places=6)
        self.assertAlmostEqual(m["lo"], T0 - 0.14, places=6)
        self.assertAlmostEqual(m["hi"], T0 + 0.14, places=6)
        self.assertEqual(m["n"], 15)
        lo, hi, how = vt.choose_core(m)
        self.assertEqual(how, "measured")

    def test_choose_core_default(self):
        lo, hi, how = vt.choose_core({"t_min": T0, "r_min": 0.9, "lo": None, "hi": None, "n": 0})
        self.assertEqual(how, "default")
        self.assertAlmostEqual(hi - lo, 2 * vt.CORE_HALF_DEFAULT)
        self.assertEqual(vt.choose_core(None)[2], "default")


class TestVetoes(unittest.TestCase):
    def test_veto_capability(self):
        p = vt.Points([(1.0, 1.0, 0.005, "k2", 0.85),     # strong veto
                       (2.0, 1.0, 0.02, "ztf", 0.85),     # veto, not strong
                       (3.0, 0.90, 0.005, "k2", 0.85),    # dip 0.10 >= 0.06: not veto-capable
                       (4.0, 0.88, 0.01, "ztf", 0.85)])   # dip 0.12 >= 0.08: not veto-capable
        self.assertEqual(p.vt, [1.0, 2.0])
        self.assertEqual(p.vstrong, [True, False])

    def test_two_point_rule(self):
        p = vt.Points([(100.0, 1.0, 0.02, "ztf", 0.85)])
        core = (0.0, 0.3)
        ex2, _ = vt.trial(100.0, p, core, -1.0, 200.0)
        ex1, info = vt.trial(100.0, p, core, -1.0, 200.0, min_veto=1)
        self.assertFalse(ex2)
        self.assertTrue(ex1)
        self.assertEqual(info["n"], 1)

    def test_event_refs(self):
        self.assertEqual(vt.event_refs(10.0, (0.0, 1.0), -25.0, 25.0), [-2, -1, 1, 2])

    def test_k2_bound_reproduced(self):
        core = (T0 - 0.125, T0 + 0.125)
        pts = vt.Points(k2_like(core))
        t_lo, t_hi = pts.t[0], pts.t[-1]
        grid = vt.period_grid(60.0, 200.0, 0.5 * (core[0] + core[1]), t_lo, t_hi)
        n_ex, runs = vt.scan(pts, grid, core, t_lo, t_hi)
        self.assertGreater(n_ex, 0)
        bc = vt.bound_check(runs, grid)
        self.assertEqual(bc["verdict"], "BOUND_REPRODUCED")
        self.assertTrue(65.0 < bc["continuous_from"] < 66.5)
        self.assertEqual(len(runs), 1)


class TestScanHelpers(unittest.TestCase):
    def test_bound_check_labels(self):
        grid = [60.0, 100.0, 200.0]
        self.assertEqual(vt.bound_check([[60.0, 61.0, 5], [65.6, 200.0, 100]], grid)["verdict"],
                         "BOUND_REPRODUCED")
        self.assertEqual(vt.bound_check([[65.6, 150.0, 100]], grid)["verdict"], "BOUND_DIFFERENT")
        self.assertEqual(vt.bound_check([[75.0, 200.0, 100]], grid)["verdict"], "BOUND_DIFFERENT")
        self.assertEqual(vt.bound_check([], grid)["verdict"], "BOUND_DIFFERENT")

    def test_range_fraction_excluded(self):
        grid = [60.0, 70.0, 80.0, 90.0, 100.0]
        self.assertAlmostEqual(vt.range_fraction_excluded(grid, [[70.0, 80.0, 2]], 60.0, 100.0), 0.6)
        fr = vt.binned_fraction(grid, [[70.0, 80.0, 2]], [60.0, 75.0, 101.0])
        self.assertEqual([(x[2], x[3]) for x in fr], [(2, 1), (3, 1)])

    def test_periods_from_event(self):
        out = vt.periods_from_event(2457835.0 + 300.0, 2457835.0)
        self.assertEqual([n for n, _ in out], [1, 2, 3, 4, 5])
        self.assertAlmostEqual(out[-1][1], 60.0)
        neg = vt.periods_from_event(2457835.0 - 120.0, 2457835.0)
        self.assertEqual([n for n, _ in neg], [-1, -2])


class TestSearch(unittest.TestCase):
    def series(self):
        cad = 200.0 / 86400.0
        t = [2459000.0 + k * cad for k in range(4320)]
        r = [1.002 if k % 2 else 0.998 for k in range(4320)]
        return t, r, cad

    def test_box_search_finds_injected_eclipse(self):
        t, r, cad = self.series()
        T = t[0] + 5.0
        _, dets = vt.box_search(t, vt.inject(t, r, T, 0.3), cad)
        self.assertEqual(len(dets), 1)
        self.assertLess(abs(dets[0]["t_mid"] - T), 0.1)
        self.assertGreater(dets[0]["depth"], 0.2)

    def test_box_search_clean(self):
        t, r, cad = self.series()
        _, dets = vt.box_search(t, r, cad)
        self.assertEqual(dets, [])

    def test_dips_and_groups(self):
        p = vt.Points([(10.0, 0.80, 0.01, "ztf", 0.85), (10.3, 0.82, 0.01, "asassn", 0.85),
                       (50.0, 0.80, 0.01, "ztf", 0.85), (60.0, 0.90, 0.01, "ztf", 0.85),
                       (70.0, 0.70, 0.01, "tess", 0.87)])
        d = vt.dip_points(p)
        self.assertEqual([x[0] for x in d], [10.0, 10.3, 50.0])
        ev = vt.group_events(d)
        self.assertEqual(len(ev), 2)
        self.assertTrue(ev[0]["strong"])
        self.assertEqual(ev[0]["sources"], ["asassn", "ztf"])
        self.assertFalse(ev[1]["strong"])


class TestMisc(unittest.TestCase):
    def test_real_sectors(self):
        self.assertEqual(vt.real_sectors([43, 44, 70, 71, 1751]), ([43, 44, 70, 71], [1751]))

    def test_tess_fexp(self):
        self.assertAlmostEqual(vt.tess_fexp(0.9), 1.0 - 0.15 * 0.9)
        self.assertAlmostEqual(vt.tess_fexp(1.5), 0.85)
        self.assertIsNone(vt.tess_fexp(0.2))
        self.assertIsNone(vt.tess_fexp(float("nan")))

    def test_tess_share(self):
        f = vt.TESS_ZP_FLUX * 10 ** (-0.4 * (vt.TMAG - 10.0)) * vt.TESS_PSF_FRAC
        self.assertAlmostEqual(vt.tess_share(f), 1.0)
        self.assertAlmostEqual(vt.tess_share(2 * f), 0.5)

    def test_parse_ztf(self):
        lines = ["oid,filtercode,hjd,mag,magerr,catflags"]
        for k in range(10):
            lines.append("111,zg,%.5f,13.0,0.02,0" % (2458500.0 + k))
        lines.append("111,zg,2458520.0,13.5,0.02,32768")
        lines.append("222,zr,2458500.0,12.5,0.02,0")
        pts, meta = vt.parse_ztf("\n".join(lines) + "\n")
        self.assertEqual(len(pts), 10)
        self.assertAlmostEqual(pts[0][1], 1.0)
        self.assertAlmostEqual(pts[0][2], 0.921 * 0.02)
        self.assertFalse(meta["oids"]["222"]["used"])

    def test_headline(self):
        self.assertEqual(vt.headline([], 0), "NO_NEW_DATA")
        self.assertEqual(vt.headline([{"strong": True}], 5), "SECOND_ECLIPSE_CANDIDATE")
        self.assertEqual(vt.headline([], 5), "NO_SECOND_ECLIPSE")

    def test_bin_series(self):
        t = [0.0, 0.01, 0.03, 0.05]
        b = vt.bin_series(t, [1.0, 3.0, 5.0, 7.0], 0.02)
        self.assertEqual([x[2] for x in b], [2, 1, 1])
        self.assertAlmostEqual(b[0][1], 2.0)

    def test_dates(self):
        self.assertEqual(vt.bjd_to_date(2451545.0), "2000-01-01 12:00")


if __name__ == "__main__":
    unittest.main()
