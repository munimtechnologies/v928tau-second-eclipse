# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Fetch io_tess.py, asassn_io.py and ecl.py, unchanged, from the commit of
munimtechnologies/epic2202-second-eclipse that ran the EPIC 220208795 test
(9dfda1bfbee43274ba50dfee769609a69d617baf):
- io_tess.py: TESScut download and 3x3 / peak-pixel aperture photometry
- asassn_io.py: the ASAS-SN Sky Patrol v2 client and normalisation (it imports robust_scatter from ecl.py)
"""
import os
import sys
import time
import urllib.request

COMMIT = "9dfda1bfbee43274ba50dfee769609a69d617baf"
BASE = "https://raw.githubusercontent.com/munimtechnologies/epic2202-second-eclipse/%s/" % COMMIT
FILES = ("io_tess.py", "asassn_io.py", "ecl.py")
MUST = {"io_tess.py": "def photometry", "asassn_io.py": "def normalise", "ecl.py": "def robust_scatter"}


def main(dest=None):
    here = dest or os.path.dirname(os.path.abspath(__file__))
    for name in FILES:
        err = None
        for k in range(5):
            try:
                req = urllib.request.Request(BASE + name, headers={"User-Agent": "mv2-research-job/1.0"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                break
            except Exception as e:
                err = e
                time.sleep(5 * (k + 1))
        else:
            raise RuntimeError("could not fetch %s: %r" % (name, err))
        text = data.decode("utf-8")
        if MUST[name] not in text:
            raise RuntimeError("%s does not look like the pinned module" % name)
        with open(os.path.join(here, name), "w", encoding="utf-8") as f:
            f.write(text)
        print("fetched %s (%d bytes) from commit %s" % (name, len(data), COMMIT[:10]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
