# Copyright 2026 Munim, Inc.
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name.
"""Core of the V928 Tau second-eclipse test (stdlib only; imported by the tests).

van Dam et al. (2020, AJ 160, 285; arXiv:2010.11199) found one asymmetric eclipse of the young
binary V928 Tau (EPIC 247795097 = TIC 268324580) in K2 Campaign 13: about 30% deep in the
blended light (one star dims ~60%), about half a day long, near BJD 2457835.0. It did not repeat
before the campaign ended, so P > 66 d; ground-based folds over 66 d - 2.8 yr found "no
unambiguous period".

Adapted from occ.py of munimtechnologies/epic2043-second-occultation (v0.1.0, commit f1735b98),
with V928 Tau's numbers and the changes listed in PREREGISTRATION.md. Everything here is fixed by
PREREGISTRATION.md (2026-11-25) before any light curve of the star was looked at.
"""
import bisect
import csv
import io
import math
import statistics

VERSION = "0.1.0"
TARGET = "V928 Tau = EPIC 247795097 = TIC 268324580"
RA, DEC = 68.078683, 24.374087          # ExoFOP / TIC, epoch 2015.5
TMAG = 11.6784                          # TIC 8 (ExoFOP)
KBJD0 = 2454833.0
T_MIN_PUBLISHED = 2457835.01            # van Dam et al. 2020: BJD ~2457835, model offset 0.0099 d

# event core: K2 C13 points with flux <= CORE_FLUX around the minimum (blended light);
# fallback T_MIN_PUBLISHED +- CORE_HALF_DEFAULT
CORE_FLUX = 0.85
CORE_HALF_DEFAULT = 0.12
CORE_MIN_LEN = 0.15
CORE_SEARCH_HALF = 1.0
CORE_MAX_GAP = 0.10

# gate G1
G1_TOL_DAYS = 0.5
G1_MIN_DEPTH = 0.15

# vetoes (PREREGISTRATION.md section 4)
VETO_MAX_DIP = {"k2": 0.06, "tess": 0.06, "ztf": 0.08, "asassn": 0.08}
VETO_NSIGMA = 4.0
STRONG_VETO_NSIGMA = 10.0
MIN_VETO = 2
TESS_SHARE_MIN = 0.3
TESS_PSF_FRAC = 0.75                    # share of a point source's flux in a 3x3 TESS aperture
TESS_ZP_FLUX = 15000.0                  # e-/s at Tmag 10
TESS_MAX_SECTOR = 999                   # TESScut also lists a 'sector 1751'; not a real sector

# new-event search
BOX_WIDTHS = (0.15, 0.25, 0.40)
BOX_STEP = 0.02
BOX_MIN_DEPTH = 0.10
BOX_MIN_SNR = 10.0
FLANK = 1.5
FLANK_GAP = 0.05
FLANK_TOL = 0.04
FLANK_MIN_N = 10
DIP_MIN_DEPTH = 0.15                    # ZTF / ASAS-SN dip point
DIP_NSIGMA = 5.0
DIP_GROUP_DAYS = 1.0

# period scan
P_MIN, P_MAX = 60.0, 3000.0
AUTHORS_RANGE = (66.0, 1022.0)          # 66 d to 2.8 yr
GRID_TOL = 0.02
CHART_EDGES = [60.0, 70.0, 80.0, 100.0, 125.0, 150.0, 200.0, 300.0, 400.0, 500.0, 700.0,
               1022.0, 1500.0, 2000.0, 3000.0]

# gate G2: the authors' K2-only bound
G2_START = (62.0, 70.0)


def robust_scatter(values):
    """1.4826 x median absolute deviation."""
    v = [x for x in values if x == x]
    if len(v) < 2:
        return float("nan")
    m = statistics.median(v)
    return 1.4826 * statistics.median([abs(x - m) for x in v])


def bjd_to_date(bjd):
    """Calendar date (UTC, ignoring the ~1 min BJD-UTC offset) as YYYY-MM-DD HH:MM."""
    import datetime
    d = datetime.datetime(2000, 1, 1, 12) + datetime.timedelta(days=bjd - 2451545.0)
    return d.strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------------- normalisation and binning

def normalise_binned(t, f, bin_days=5.0, min_n=5):
    """Divide f by the median of its bin (bins of bin_days from the first time), with linear
    interpolation of bin medians between bin centres. Returns a list of ratios."""
    if not t:
        return []
    t0 = t[0]
    bins = {}
    for ti, fi in zip(t, f):
        bins.setdefault(int((ti - t0) // bin_days), []).append((ti, fi))
    centres = []
    for k in sorted(bins):
        vals = bins[k]
        if len(vals) < min_n:
            continue
        centres.append((statistics.median(v[0] for v in vals), statistics.median(v[1] for v in vals)))
    if not centres:
        return [float("nan")] * len(t)
    ct = [c[0] for c in centres]
    out = []
    for ti, fi in zip(t, f):
        j = bisect.bisect_left(ct, ti)
        if j <= 0:
            m = centres[0][1]
        elif j >= len(ct):
            m = centres[-1][1]
        else:
            (ta, ma), (tb, mb) = centres[j - 1], centres[j]
            m = ma + (mb - ma) * (ti - ta) / (tb - ta) if tb > ta else ma
        out.append(fi / m if m else float("nan"))
    return out


def bin_series(t, r, width):
    """Average consecutive points into bins of `width` days counted from t[0].
    Returns [(t_mean, r_mean, n)]."""
    out = []
    if not t:
        return out
    t0 = t[0]
    cur_k, acc = None, []
    for ti, ri in zip(t, r):
        k = int(math.floor((ti - t0) / width + 1e-9))
        if cur_k is not None and k != cur_k and acc:
            out.append((sum(a for a, _ in acc) / len(acc), sum(b for _, b in acc) / len(acc), len(acc)))
            acc = []
        cur_k = k
        acc.append((ti, ri))
    if acc:
        out.append((sum(a for a, _ in acc) / len(acc), sum(b for _, b in acc) / len(acc), len(acc)))
    return out


# ---------------------------------------------------------------- the K2 event core

def measure_core(t, r, t_guess=T_MIN_PUBLISHED, search_half=CORE_SEARCH_HALF, thr=CORE_FLUX,
                 max_gap=CORE_MAX_GAP):
    """Lowest point within +-search_half of t_guess, then the contiguous run around it with
    r <= thr (a time gap > max_gap ends the run). Returns dict or None if no point there."""
    idx = [i for i in range(len(t)) if abs(t[i] - t_guess) <= search_half and r[i] == r[i]]
    if not idx:
        return None
    i0 = min(idx, key=lambda i: r[i])
    if r[i0] > thr:
        return {"t_min": t[i0], "r_min": r[i0], "lo": None, "hi": None, "n": 0}
    lo = hi = i0
    while lo - 1 >= 0 and r[lo - 1] <= thr and t[lo] - t[lo - 1] <= max_gap:
        lo -= 1
    while hi + 1 < len(t) and r[hi + 1] <= thr and t[hi + 1] - t[hi] <= max_gap:
        hi += 1
    return {"t_min": t[i0], "r_min": r[i0], "lo": t[lo], "hi": t[hi], "n": hi - lo + 1}


def choose_core(measured):
    """(lo, hi, how): the measured run if it is at least CORE_MIN_LEN long, else the default."""
    if measured and measured.get("lo") is not None and measured["hi"] - measured["lo"] >= CORE_MIN_LEN:
        return measured["lo"], measured["hi"], "measured"
    return T_MIN_PUBLISHED - CORE_HALF_DEFAULT, T_MIN_PUBLISHED + CORE_HALF_DEFAULT, "default"


# ---------------------------------------------------------------- vetoes and the period scan

class Points:
    """Normalised photometry sorted by time. Rows: (t, r, sigma, source, f_exp), where f_exp is
    the flux the source would show inside the event core (CORE_FLUX for K2, ZTF and ASAS-SN,
    diluted for TESS)."""

    def __init__(self, rows):
        rows = sorted(rows, key=lambda x: x[0])
        self.t = [x[0] for x in rows]
        self.r = [x[1] for x in rows]
        self.s = [x[2] for x in rows]
        self.src = [x[3] for x in rows]
        self.fexp = [x[4] for x in rows]
        vc = [x for x in rows if (1.0 - x[1]) < VETO_MAX_DIP.get(x[3], 0.05)
              and x[2] > 0 and (x[1] - x[4]) > VETO_NSIGMA * x[2]]
        self.vt = [x[0] for x in vc]
        self.vsrc = [x[3] for x in vc]
        self.vstrong = [(x[1] - x[4]) > STRONG_VETO_NSIGMA * x[2] for x in vc]

    def __len__(self):
        return len(self.t)


def vetoes(pts, a, b):
    """Veto-capable points with a <= t <= b: list of (t, source, strong)."""
    i = bisect.bisect_left(pts.vt, a)
    j = bisect.bisect_right(pts.vt, b)
    return [(pts.vt[k], pts.vsrc[k], pts.vstrong[k]) for k in range(i, j)]


def vetoed(v, min_veto=MIN_VETO):
    return len(v) >= min_veto or any(x[2] for x in v)


def event_refs(P, core, t_lo, t_hi):
    """Shifts n != 0 whose core [lo + nP, hi + nP] overlaps [t_lo, t_hi]."""
    lo, hi = core
    n0 = int(math.ceil((t_lo - hi) / P))
    n1 = int(math.floor((t_hi - lo) / P))
    return [n for n in range(n0, n1 + 1) if n != 0]


def trial(P, pts, core, t_lo, t_hi, min_veto=MIN_VETO):
    """(excluded?, info): excluded if one predicted core holds a veto."""
    lo, hi = core
    for n in event_refs(P, core, t_lo, t_hi):
        v = vetoes(pts, lo + n * P, hi + n * P)
        if vetoed(v, min_veto):
            return True, {"n": n, "core_mid": 0.5 * (lo + hi) + n * P, "by": sorted(set(x[1] for x in v))}
    return False, None


def period_grid(p_min, p_max, t_ref, span_lo, span_hi, tol=GRID_TOL):
    D = max(abs(span_hi - t_ref), abs(t_ref - span_lo), 1.0)
    fac = 1.0 + tol / D
    P = p_min
    out = []
    while P <= p_max:
        out.append(P)
        P *= fac
    return out


def scan(pts, grid, core, t_lo, t_hi, min_veto=MIN_VETO):
    """(n_excluded, allowed_runs) with runs [P_first, P_last, n_trials]."""
    runs = []
    cur = None
    n_ex = 0
    for P in grid:
        ex, _ = trial(P, pts, core, t_lo, t_hi, min_veto)
        if ex:
            n_ex += 1
            if cur is not None:
                runs.append(cur)
                cur = None
        else:
            if cur is None:
                cur = [P, P, 1]
            else:
                cur[1] = P
                cur[2] += 1
    if cur is not None:
        runs.append(cur)
    return n_ex, runs


def allowed_mask(grid, runs):
    allowed = bytearray(len(grid))
    for a, b, _ in runs:
        i = bisect.bisect_left(grid, a)
        j = bisect.bisect_right(grid, b)
        for x in range(i, j):
            allowed[x] = 1
    return allowed


def binned_fraction(grid, runs, edges):
    """Fraction of grid trials allowed in each [edges[k], edges[k+1]) bin."""
    allowed = allowed_mask(grid, runs)
    out = []
    for k in range(len(edges) - 1):
        i = bisect.bisect_left(grid, edges[k])
        j = bisect.bisect_left(grid, edges[k + 1])
        tot = j - i
        ok = sum(allowed[i:j])
        out.append((edges[k], edges[k + 1], tot, ok, (ok / tot) if tot else float("nan")))
    return out


def range_fraction_excluded(grid, runs, p_lo, p_hi):
    """Excluded fraction of the grid trials with p_lo <= P <= p_hi."""
    allowed = allowed_mask(grid, runs)
    i = bisect.bisect_left(grid, p_lo)
    j = bisect.bisect_right(grid, p_hi)
    tot = j - i
    return (1.0 - sum(allowed[i:j]) / tot) if tot else float("nan")


def bound_check(runs, grid, start=G2_START):
    """Gate G2 on the K2-only scan: the last allowed run must reach the end of the grid and start
    in [start[0], start[1]] (the authors' P > 66 d with everything above allowed)."""
    if not runs or not grid:
        return {"verdict": "BOUND_DIFFERENT", "continuous_from": None}
    last = runs[-1]
    reaches_end = abs(last[1] - grid[-1]) < 1e-9
    p0 = last[0]
    ok = reaches_end and start[0] <= p0 <= start[1]
    return {"continuous_from": p0, "reaches_end": reaches_end,
            "smallest_allowed": runs[0][0], "n_runs": len(runs),
            "verdict": "BOUND_REPRODUCED" if ok else "BOUND_DIFFERENT"}


def periods_from_event(t_event, t_ref, p_lo=P_MIN, p_hi=P_MAX):
    """(n, P) with t_event = t_ref + n P inside [p_lo, p_hi]; n signed."""
    dt = t_event - t_ref
    out = []
    n = 1
    while abs(dt) / n >= p_lo:
        P = abs(dt) / n
        if P <= p_hi:
            out.append((n if dt > 0 else -n, P))
        n += 1
    return out


# ---------------------------------------------------------------- new-event search

def box_search(t, r, cadence, widths=BOX_WIDTHS, step=BOX_STEP, min_depth=BOX_MIN_DEPTH,
               min_snr=BOX_MIN_SNR):
    """Box-dip search on a normalised, time-sorted series. Returns (best, detections); each entry
    dict(t_mid, width, depth, snr, n_in). A detection has depth >= min_depth, snr >= min_snr,
    >= 60% of the expected in-box cadences, and >= FLANK_MIN_N points on each flank
    (FLANK_GAP..FLANK days outside the box) with median within FLANK_TOL of 1.
    Detections closer than 0.5 d are merged (highest snr kept)."""
    n = len(t)
    if n < 20:
        return None, []
    s = robust_scatter(r)
    pre = [0.0]
    for x in r:
        pre.append(pre[-1] + x)
    best = None
    dets = []
    c = t[0]
    k = 0
    while c <= t[-1]:
        for w in widths:
            i = bisect.bisect_left(t, c - w / 2)
            j = bisect.bisect_right(t, c + w / 2)
            m = j - i
            if m < max(3, 0.6 * w / cadence):
                continue
            depth = 1.0 - (pre[j] - pre[i]) / m
            snr = depth / (s / math.sqrt(m)) if s > 0 else 0.0
            cand = {"t_mid": c, "width": w, "depth": depth, "snr": snr, "n_in": m}
            if best is None or snr > best["snr"]:
                best = cand
            if depth >= min_depth and snr >= min_snr:
                li = bisect.bisect_left(t, c - w / 2 - FLANK)
                ri = bisect.bisect_right(t, c + w / 2 + FLANK)
                left = [r[q] for q in range(li, i) if t[q] < c - w / 2 - FLANK_GAP]
                right = [r[q] for q in range(j, ri) if t[q] > c + w / 2 + FLANK_GAP]
                if (len(left) >= FLANK_MIN_N and len(right) >= FLANK_MIN_N
                        and abs(statistics.median(left) - 1) <= FLANK_TOL
                        and abs(statistics.median(right) - 1) <= FLANK_TOL):
                    dets.append(cand)
        k += 1
        c = t[0] + k * step
    merged = []
    for d in sorted(dets, key=lambda x: x["t_mid"]):
        if merged and d["t_mid"] - merged[-1]["t_mid"] <= 0.5:
            if d["snr"] > merged[-1]["snr"]:
                merged[-1] = d
        else:
            merged.append(d)
    return best, merged


def dip_points(pts, sources=("ztf", "asassn"), min_depth=DIP_MIN_DEPTH, nsig=DIP_NSIGMA):
    return [(t, r, s, c) for t, r, s, c in zip(pts.t, pts.r, pts.s, pts.src)
            if c in sources and (1.0 - r) >= min_depth and s > 0 and (1.0 - r) >= nsig * s]


def group_events(dips, gap=DIP_GROUP_DAYS):
    """Group dip points closer than gap. Event: t_mid, n, depth_max, sources, strong (n >= 2)."""
    ev = []
    for d in sorted(dips):
        if ev and d[0] - ev[-1][-1][0] <= gap:
            ev[-1].append(d)
        else:
            ev.append([d])
    return [{"t_mid": sum(x[0] for x in p) / len(p), "n": len(p),
             "depth_max": max(1.0 - x[1] for x in p), "sources": sorted(set(x[3] for x in p)),
             "strong": len(p) >= 2} for p in ev]


def tess_share(f3_median, tmag=TMAG, psf_frac=TESS_PSF_FRAC):
    """Estimated fraction of the 3x3-aperture flux that comes from the target."""
    if not f3_median or f3_median <= 0:
        return float("nan")
    return TESS_ZP_FLUX * 10 ** (-0.4 * (tmag - 10.0)) * psf_frac / f3_median


def tess_fexp(share):
    """In-core aperture flux of the event diluted to `share`; None if too diluted."""
    if share != share or share < TESS_SHARE_MIN:
        return None
    return 1.0 - (1.0 - CORE_FLUX) * min(1.0, share)


def real_sectors(secs):
    """(kept, dropped): TESScut sector numbers above TESS_MAX_SECTOR are not real sectors."""
    kept = [s for s in secs if 0 < s <= TESS_MAX_SECTOR]
    return kept, [s for s in secs if s not in kept]


def inject(t, r, T, depth, full=0.6, flat=0.1):
    """Multiply r by a symmetric trapezoid of total length `full`, flat bottom `flat`, centred T."""
    half_full, half_flat = full / 2.0, flat / 2.0
    out = []
    for ti, ri in zip(t, r):
        u = abs(ti - T)
        if u <= half_flat:
            d = depth
        elif u < half_full:
            d = depth * (half_full - u) / (half_full - half_flat)
        else:
            d = 0.0
        out.append(ri * (1.0 - d))
    return out


# ---------------------------------------------------------------- ZTF

def parse_ztf(text, max_magerr=0.30):
    """IRSA ZTF light-curve CSV -> ([(bjd, r, sigma, 'ztf', oid, filtercode)], meta).
    Keeps catflags == 0 and magerr <= max_magerr; oids with >= 10 points.
    r = 10**(-0.4 (mag - median_oid)); sigma = max(0.921 magerr, robust scatter of r of the oid)."""
    rd = csv.DictReader(io.StringIO(text))
    by = {}
    n_raw = 0
    for row in rd:
        n_raw += 1
        try:
            mag = float(row["mag"])
            err = float(row["magerr"])
            flags = int(float(row["catflags"]))
            hjd = float(row["hjd"])
        except (KeyError, ValueError, TypeError):
            continue
        if flags != 0 or err > max_magerr or mag != mag:
            continue
        t = hjd if hjd > 2400000 else hjd + 2400000.5
        by.setdefault((row.get("oid", "?"), row.get("filtercode", "?")), []).append((t, mag, err))
    out = []
    meta = {"n_raw": n_raw, "oids": {}}
    for (oid, fc), rows in sorted(by.items()):
        if len(rows) < 10:
            meta["oids"][oid] = {"filter": fc, "n": len(rows), "used": False}
            continue
        med = statistics.median(m for _, m, _ in rows)
        rs = [10 ** (-0.4 * (m - med)) for _, m, _ in rows]
        sc = robust_scatter(rs)
        for (t, m, e), r in zip(rows, rs):
            out.append((t, r, max(0.921 * e, sc), "ztf", oid, fc))
        meta["oids"][oid] = {"filter": fc, "n": len(rows), "median_mag": med, "scatter": sc, "used": True,
                             "t_first": min(x[0] for x in rows), "t_last": max(x[0] for x in rows)}
    return out, meta


def headline(strong_events, n_new_points):
    if n_new_points == 0:
        return "NO_NEW_DATA"
    if strong_events:
        return "SECOND_ECLIPSE_CANDIDATE"
    return "NO_SECOND_ECLIPSE"
