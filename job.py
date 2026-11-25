# Copyright 2026 Munim, Inc.
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name.
"""V928 Tau second-eclipse test (pre-registered 2026-11-25, PREREGISTRATION.md).

python job.py --data-dir /data --out-dir /out
Writes /out/results.json (rewritten after every stage; key "stage"), CSVs and summary.md.
"""
import argparse
import csv
import json
import math
import os
import sys
import tempfile
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import v928 as vt  # noqa: E402

START = time.time()
_DEPS = {}


def log(msg):
    print("[%7.1fs] %s" % (time.time() - START, msg), flush=True)


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)
    os.replace(tmp, path)


def write_csv(path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def deps():
    """Import the pinned io_tess and asassn_io (fetched into a temp dir on first use)."""
    if not _DEPS:
        import fetch_deps
        d = tempfile.mkdtemp(prefix="mv2deps-")
        fetch_deps.main(dest=d)
        sys.path.insert(0, d)
        import io_tess
        import asassn_io
        _DEPS["io_tess"] = io_tess
        _DEPS["asassn_io"] = asassn_io
    return _DEPS


# ------------------------------------------------------------------------------ K2

def get_k2(data_dir, out_dir, res):
    import io_k2
    info = {}
    res["data"]["k2"] = info
    try:
        lc = io_k2.load(io_k2.fetch(13, os.path.join(data_dir, "k2"), log=log))
    except Exception as exc:
        info["error"] = repr(exc)
        log("K2 C13 failed: %r" % (exc,))
        return None
    t = lc["bjd"]
    r = vt.normalise_binned(t, lc["sap"], bin_days=5.0)
    keep = [i for i in range(len(t)) if r[i] == r[i]]
    t = [t[i] for i in keep]
    r = [r[i] for i in keep]
    s = vt.robust_scatter(r)
    cad = sorted(t[i + 1] - t[i] for i in range(len(t) - 1))[len(t) // 2] if len(t) > 2 else float("nan")
    best, dets = vt.box_search(t, r, cad)
    info.update({"n_all": lc["n_all"], "n_good": lc["n_good"], "n_used": len(t), "scatter": s,
                 "cadence_days": cad, "t_first": t[0] if t else None, "t_last": t[-1] if t else None,
                 "best_box": best, "detections": dets})
    write_csv(os.path.join(out_dir, "k2_c13_sap_norm.csv"), ["bjd", "r_sap"],
              [("%.5f" % a, "%.5f" % b) for a, b in zip(t, r)])
    log("K2 C13: %d pts, scatter %.4f, detections %d, best %s"
        % (len(t), s, len(dets), None if best is None else "%.3f@%.2f" % (best["depth"], best["t_mid"])))
    return (t, r, s)


def gate_g1(k2, res):
    """K2 known answer: the eclipse recovered at depth >= G1_MIN_DEPTH within G1_TOL_DAYS of the
    published time, and no other detection in C13."""
    if k2 is None:
        return "K2_UNAVAILABLE", None
    t, r, _ = k2
    meas = vt.measure_core(t, r)
    dets = res["data"]["k2"]["detections"]
    hit = [d for d in dets if abs(d["t_mid"] - vt.T_MIN_PUBLISHED) <= vt.G1_TOL_DAYS and d["depth"] >= vt.G1_MIN_DEPTH]
    others = [d for d in dets if d not in hit]
    g1 = "K2_EVENT_RECOVERED" if hit and not others else ("K2_EVENT_RECOVERED_PLUS_OTHERS" if hit else "K2_EVENT_MISSED")
    win = [(a, b) for a, b in zip(t, r) if abs(a - vt.T_MIN_PUBLISHED) <= 3.0]
    write_csv(os.path.join(res["_out"], "chart_k2_event.csv"), ["days_from_published_min", "r_sap"],
              [("%.4f" % (a - vt.T_MIN_PUBLISHED), "%.4f" % b) for a, b in win])
    return g1, meas


# ------------------------------------------------------------------------------ ZTF

def get_ztf(data_dir, res):
    import urllib.request
    url = ("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%%20%.6f%%20%.6f"
           "%%20%.6f&BANDNAME=g,r,i&FORMAT=csv&BAD_CATFLAGS_MASK=32768" % (vt.RA, vt.DEC, 0.0005))
    path = os.path.join(data_dir, "ztf_lc.csv")
    info = {"url": url}
    res["data"]["ztf"] = info
    text = None
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=300) as resp:
                text = resp.read().decode("utf-8", "replace")
            with open(path, "w") as fh:
                fh.write(text)
            break
        except Exception as exc:
            info["error_try_%d" % (k + 1)] = repr(exc)
            time.sleep(30 * (k + 1))
    if text is None:
        info["status"] = "failed"
        return []
    pts, meta = vt.parse_ztf(text)
    info.update({"status": "ok", "meta": meta, "n_used": len(pts)})
    log("ZTF points used: %d" % len(pts))
    return pts


# ------------------------------------------------------------------------------ ASAS-SN

def get_asassn(data_dir, res):
    info = {}
    res["data"]["asassn"] = info
    try:
        aio = deps()["asassn_io"]
        info["client"] = aio.ensure_client()
        path = os.path.join(data_dir, "asassn_lc.csv")
        finfo = aio.fetch(vt.RA, vt.DEC, path, radius_arcsec=10.0, log=log)
        info["fetch"] = finfo
        if finfo.get("status") != "ok":
            return []
        by_band, lmeta = aio.load_points(path)
        pts, nmeta = aio.normalise(by_band)
        info.update({"load": lmeta, "groups": nmeta, "n_used": len(pts)})
        log("ASAS-SN points used: %d" % len(pts))
        return pts
    except Exception as exc:
        info["error"] = repr(exc)
        info["traceback"] = traceback.format_exc()[-1500:]
        log("ASAS-SN failed: %r" % (exc,))
        return []


# ------------------------------------------------------------------------------ TESS

def get_tess(data_dir, out_dir, res):
    info = {"sectors": {}}
    res["data"]["tess"] = info
    rows, events = [], []
    try:
        io_tess = deps()["io_tess"]
        secs, dropped = vt.real_sectors(io_tess.sectors(vt.RA, vt.DEC, log=log))
    except Exception as exc:
        info["error"] = repr(exc)
        info["traceback"] = traceback.format_exc()[-1500:]
        return rows, events
    info["sector_list"] = secs
    info["dropped_sector_numbers"] = dropped
    for s in secs:
        si = {}
        info["sectors"][str(s)] = si
        try:
            path = io_tess.fetch_cutout(vt.RA, vt.DEC, s, os.path.join(data_dir, "tesscut"), log=log)
            ph = io_tess.photometry(path)
        except Exception as exc:
            si["error"] = repr(exc)
            log("TESS sector %d failed: %r" % (s, exc))
            continue
        t = ph["bjd"]
        f3_med = sorted(ph["f3"])[len(ph["f3"]) // 2] if ph["f3"] else float("nan")
        r3 = vt.normalise_binned(t, ph["f3"])
        r1 = vt.normalise_binned(t, ph["f1"])
        keep = [i for i in range(len(t)) if r3[i] == r3[i] and r1[i] == r1[i]]
        t = [t[i] for i in keep]
        r3 = [r3[i] for i in keep]
        r1 = [r1[i] for i in keep]
        cad = ph["cadence_days"]
        s3 = vt.robust_scatter(r3)
        share = vt.tess_share(f3_med)
        fexp = vt.tess_fexp(share)
        si.update({k: ph[k] for k in ("cadence_days", "n_good", "n_all", "aperture_centre",
                                      "n_bkg_pixels", "frac_aperture_in_peak") if k in ph})
        si.update({"t_first": t[0] if t else None, "t_last": t[-1] if t else None, "scatter_r3": s3,
                   "n_used": len(t), "f3_median": f3_med, "target_share_est": share, "fexp_core": fexp})
        if len(t) < 50:
            si["note"] = "too few points"
            continue
        best, dets = vt.box_search(t, r3, cad)
        si["best_box"] = best
        for d in dets:
            w, c = d["width"], d["t_mid"]
            inbox = [r1[i] for i in range(len(t)) if abs(t[i] - c) <= w / 2]
            d1 = 1.0 - sum(inbox) / len(inbox) if inbox else float("nan")
            d["depth_peak_pixel"] = d1
            d["peak_ratio"] = d1 / d["depth"] if d["depth"] else float("nan")
            d["strong"] = bool(d1 == d1 and d1 >= 0.5 * d["depth"])
            d["sector"] = s
            events.append({"t_mid": c, "depth_max": d["depth"], "sources": ["tess"], "strong": d["strong"],
                           "sector": s, "snr": d["snr"], "peak_ratio": d["peak_ratio"]})
            write_csv(os.path.join(out_dir, "tess_event_%.2f.csv" % c), ["bjd", "r_3x3", "r_peak"],
                      [("%.5f" % t[i], "%.5f" % r3[i], "%.5f" % r1[i]) for i in range(len(t)) if abs(t[i] - c) <= 3.0])
        si["detections"] = dets
        # injection-recovery: a K2-like eclipse (30% blended, diluted by the share), 10 times
        inj = []
        span = t[-1] - t[0]
        dinj = 0.30 * min(1.0, share) if share == share else 0.30
        for k in range(10):
            T = t[0] + span * (k + 0.5) / 10.0
            have = sum(1 for x in t if abs(x - T) <= 0.2)
            if have < 0.7 * 0.4 / cad:
                inj.append({"T": T, "covered": False})
                continue
            _, dd = vt.box_search(t, vt.inject(t, r3, T, dinj), cad)
            inj.append({"T": T, "covered": True, "recovered": any(abs(x["t_mid"] - T) <= 0.5 for x in dd)})
        cov = [x for x in inj if x["covered"]]
        si["injection"] = {"depth_in_aperture": dinj, "n_covered": len(cov),
                           "n_recovered": sum(1 for x in cov if x["recovered"])}
        b = vt.bin_series(t, r3, 1.0 / 48)
        write_csv(os.path.join(out_dir, "tess_s%03d_30min.csv" % s), ["bjd", "r_3x3", "n"],
                  [("%.5f" % tb, "%.5f" % rb, nb) for tb, rb, nb in b])
        if fexp is not None:
            for tb, rb, nb in b:
                rows.append((tb, rb, s3 / math.sqrt(nb), "tess", fexp))
        else:
            si["veto_note"] = "target share below %.2f: not used for vetoes" % vt.TESS_SHARE_MIN
        log("TESS sector %d: %d pts, scatter %.4f, share %.2f, detections %d, injection %s"
            % (s, len(t), s3, share, len(dets), si["injection"]))
    return rows, events


# ------------------------------------------------------------------------------ main

def run_scan(label, pts, grid, core, t_lo, t_hi, out_dir, res, min_veto=vt.MIN_VETO):
    n_ex, runs = vt.scan(pts, grid, core, t_lo, t_hi, min_veto)
    fr = vt.binned_fraction(grid, runs, vt.CHART_EDGES)
    a_lo, a_hi = vt.AUTHORS_RANGE
    res["scan"][label] = {"n_points": len(pts), "n_veto_capable": len(pts.vt), "min_veto": min_veto,
                          "n_excluded": n_ex, "frac_excluded": n_ex / len(grid),
                          "frac_excluded_66d_2p8yr": vt.range_fraction_excluded(grid, runs, a_lo, a_hi),
                          "n_allowed_runs": len(runs),
                          "by_bin": [{"P_lo": a, "P_hi": b, "n": n, "n_allowed": k, "frac_allowed": f}
                                     for a, b, n, k, f in fr]}
    write_csv(os.path.join(out_dir, "allowed_periods_%s.csv" % label), ["P_first", "P_last", "n_trials"],
              [("%.5f" % x[0], "%.5f" % x[1], x[2]) for x in runs])
    write_csv(os.path.join(out_dir, "chart_allowed_fraction_%s.csv" % label),
              ["P_lo", "P_hi", "n_trials", "n_allowed", "frac_allowed"],
              [("%.0f" % x[0], "%.0f" % x[1], x[2], x[3], "%.4f" % x[4]) for x in fr])
    log("scan %s: excluded %d / %d (%.3f), 66 d-2.8 yr %.3f, %d allowed runs"
        % (label, n_ex, len(grid), n_ex / len(grid), res["scan"][label]["frac_excluded_66d_2p8yr"], len(runs)))
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    a = ap.parse_args()
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    rpath = os.path.join(a.out_dir, "results.json")
    res = {"version": vt.VERSION, "target": vt.TARGET, "ra": vt.RA, "dec": vt.DEC, "stage": "start",
           "data": {}, "preregistration": "PREREGISTRATION.md (2026-11-25)", "_out": a.out_dir}
    write_json(rpath, res)

    k2 = get_k2(a.data_dir, a.out_dir, res)
    g1, meas = gate_g1(k2, res)
    lo, hi, how = vt.choose_core(meas)
    res["gates"] = {"G1": g1}
    res["core"] = {"measured": meas, "lo": lo, "hi": hi, "how": how, "length_days": hi - lo,
                   "lo_date": vt.bjd_to_date(lo), "hi_date": vt.bjd_to_date(hi)}
    res["stage"] = "k2"
    write_json(rpath, res)
    log("G1 %s; core %.3f..%.3f (%s, %.2f d)" % (g1, lo, hi, how, hi - lo))
    core = (lo, hi)

    k2rows = []
    if k2 is not None:
        t, r, s = k2
        k2rows = [(ti, ri, s, "k2", vt.CORE_FLUX) for ti, ri in zip(t, r)]
    ztf = get_ztf(a.data_dir, res)
    res["stage"] = "ztf"
    write_json(rpath, res)
    asn = get_asassn(a.data_dir, res)
    res["stage"] = "asassn"
    write_json(rpath, res)
    tess_rows, tess_events = get_tess(a.data_dir, a.out_dir, res)
    res["stage"] = "tess"
    write_json(rpath, res)

    ztf_rows = [(p[0], p[1], p[2], "ztf", vt.CORE_FLUX) for p in ztf]
    asn_rows = [(p[0], p[1], p[2], "asassn", vt.CORE_FLUX) for p in asn]
    write_csv(os.path.join(a.out_dir, "ztf_points.csv"), ["bjd", "date", "r", "sigma", "oid", "filter"],
              [("%.5f" % p[0], vt.bjd_to_date(p[0]), "%.5f" % p[1], "%.5f" % p[2], p[4], p[5]) for p in ztf])
    write_csv(os.path.join(a.out_dir, "asassn_points.csv"), ["bjd", "date", "r", "sigma", "band", "camera"],
              [("%.5f" % p[0], vt.bjd_to_date(p[0]), "%.5f" % p[1], "%.5f" % p[2], p[4], p[5]) for p in asn])
    allp = vt.Points(k2rows + ztf_rows + asn_rows + tess_rows)
    k2p = vt.Points(k2rows)
    newp = vt.Points(ztf_rows + asn_rows + tess_rows)
    if len(allp) == 0:
        res.update({"stage": "done", "outcome": ["NO_DATA"]})
        res.pop("_out", None)
        write_json(rpath, res)
        log("OUTCOME NO_DATA")
        return
    t_lo, t_hi = allp.t[0], allp.t[-1]
    srcs = ("k2", "ztf", "asassn", "tess")
    res["span"] = {"t_lo": t_lo, "t_hi": t_hi, "date_lo": vt.bjd_to_date(t_lo), "date_hi": vt.bjd_to_date(t_hi),
                   "by_source": {c: allp.src.count(c) for c in srcs},
                   "veto_capable_by_source": {c: allp.vsrc.count(c) for c in srcs}}

    # new events
    dips = vt.dip_points(allp)
    gev = vt.group_events(dips)
    write_csv(os.path.join(a.out_dir, "ground_dip_points.csv"), ["bjd", "date", "r", "sigma", "source"],
              [("%.5f" % d[0], vt.bjd_to_date(d[0]), "%.4f" % d[1], "%.4f" % d[2], d[3]) for d in dips])
    events = gev + tess_events
    strong = [e for e in events if e["strong"]]
    res["events"] = {"ground_dip_points": len(dips), "ground_events": gev, "tess_events": tess_events,
                     "n_strong": len(strong)}
    res["stage"] = "events"
    write_json(rpath, res)
    log("ground dip points %d, ground events %d (strong %d), TESS events %d (strong %d)"
        % (len(dips), len(gev), sum(1 for e in gev if e["strong"]), len(tess_events),
           sum(1 for e in tess_events if e["strong"])))

    # scans
    grid = vt.period_grid(vt.P_MIN, vt.P_MAX, 0.5 * (lo + hi), t_lo, t_hi)
    res["scan"] = {"n_trials": len(grid), "tol_days": vt.GRID_TOL, "P_min": vt.P_MIN, "P_max": vt.P_MAX}
    log("scan grid: %d trials" % len(grid))
    runs_k2 = run_scan("k2_only", k2p, grid, core, t_lo, t_hi, a.out_dir, res)
    res["gates"]["G2"] = vt.bound_check(runs_k2, grid) if len(k2p) else {"verdict": "NOT_RUN"}
    write_json(rpath, res)
    run_scan("all", allp, grid, core, t_lo, t_hi, a.out_dir, res)
    run_scan("new_only", newp, grid, core, t_lo, t_hi, a.out_dir, res)
    run_scan("all_one_point_veto", allp, grid, core, t_lo, t_hi, a.out_dir, res, min_veto=1)
    write_json(rpath, res)

    implied = []
    tref = 0.5 * (lo + hi)
    for e in strong:
        for n, P in vt.periods_from_event(e["t_mid"], tref):
            ex, inf = vt.trial(P, allp, core, t_lo, t_hi)
            implied.append({"event_t": e["t_mid"], "date": vt.bjd_to_date(e["t_mid"]), "n": n, "P": P,
                            "excluded": ex, "veto": inf, "sources": e["sources"]})
    res["implied_periods"] = implied
    write_csv(os.path.join(a.out_dir, "implied_periods.csv"), ["event_t", "date", "n", "P", "excluded", "sources"],
              [("%.4f" % x["event_t"], x["date"], x["n"], "%.4f" % x["P"], x["excluded"], "+".join(x["sources"]))
               for x in implied])

    hl = vt.headline(strong, len(newp))
    out = [hl, "G1=" + g1, "G2=" + res["gates"]["G2"]["verdict"],
           "excluded_all=%.3f" % res["scan"]["all"]["frac_excluded"],
           "excluded_all_66d_2p8yr=%.3f" % res["scan"]["all"]["frac_excluded_66d_2p8yr"],
           "excluded_k2_only=%.3f" % res["scan"]["k2_only"]["frac_excluded"]]
    res["outcome"] = out
    res["stage"] = "done"
    res["runtime_s"] = time.time() - START
    res.pop("_out", None)
    write_json(rpath, res)
    with open(os.path.join(a.out_dir, "summary.md"), "w") as fh:
        fh.write("# V928 Tau second-eclipse test v%s\n\nOutcome: %s\n\n" % (vt.VERSION, ", ".join(out)))
        fh.write("Core: %s .. %s (%s)\n\nG2: %s\n\nStrong events: %d\n"
                 % (res["core"]["lo_date"], res["core"]["hi_date"], how, json.dumps(res["gates"]["G2"]), len(strong)))
    log("OUTCOME " + " ".join(out))


if __name__ == "__main__":
    main()
