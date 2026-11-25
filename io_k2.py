# Copyright 2026 Munim, Inc.
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name.
"""K2 Campaign 13 long-cadence light curve of V928 Tau (EPIC 247795097) from MAST
(job only; needs numpy, astropy). Adapted from munimtechnologies/epic2043-second-occultation io_k2.py."""
import os
import time
import urllib.request

URLS = {
    13: "https://archive.stsci.edu/missions/k2/lightcurves/c13/247700000/95000/ktwo247795097-c13_llc.fits",
}
# attitude tweak, safe mode, coarse point, earth point, desaturation, manual exclude,
# no fine point, thruster firing
BAD_BITS = 1 | 2 | 4 | 8 | 32 | 128 | 32768 | 1048576


def fetch(campaign, out_dir, tries=4, log=print):
    os.makedirs(out_dir, exist_ok=True)
    url = URLS[campaign]
    path = os.path.join(out_dir, os.path.basename(url))
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        return path
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-research-job/1.0"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = resp.read()
            with open(path, "wb") as fh:
                fh.write(data)
            log("K2 C%d: %d bytes" % (campaign, len(data)))
            return path
        except Exception as exc:
            last = repr(exc)
            log("K2 C%d try %d failed: %s" % (campaign, k + 1, last))
            time.sleep(20 * (k + 1))
    raise RuntimeError(last)


def load(path):
    """dict(bjd, sap, pdc, n_all, n_good). Cadences with BAD_BITS or non-finite SAP flux dropped."""
    import numpy as np
    from astropy.io import fits
    with fits.open(path, memmap=False) as h:
        d = h[1].data
        cols = [c.name for c in h[1].columns]
        t = np.array(d["TIME"], dtype=float)
        sap = np.array(d["SAP_FLUX"], dtype=float)
        pdc = np.array(d["PDCSAP_FLUX"], dtype=float) if "PDCSAP_FLUX" in cols else np.full_like(sap, np.nan)
        qcol = "SAP_QUALITY" if "SAP_QUALITY" in cols else "QUALITY"
        q = np.array(d[qcol], dtype=np.int64)
    good = np.isfinite(t) & np.isfinite(sap) & (sap > 0) & ((q & BAD_BITS) == 0)
    order = np.argsort(t[good])
    return {"bjd": (t[good][order] + 2454833.0).tolist(), "sap": sap[good][order].tolist(),
            "pdc": pdc[good][order].tolist(), "n_all": int(len(t)), "n_good": int(good.sum())}
