# Amendment (2026-11-25): Gaia DR4 epoch photometry

This project's pre-registration promised that Gaia DR4 epoch photometry (2014-07-25 to 2020-01-20)
would be added as a separately dated amendment. That amendment is now frozen, for this star and
three other one-time occulters together, in
[munimtechnologies/occulters-gaia-dr4](https://github.com/munimtechnologies/occulters-gaia-dr4)
(PREREGISTRATION.md, tag v0.1.0), a week before Gaia DR4 (2026-12-02) and before anyone has seen
the data.

- The Gaia test has its own gates, vetoes, dip rules and expected outcomes; nothing in this
  repository's own pre-registration changes.
- **Combination rule, fixed now:** a trial period is excluded overall if it is excluded in this
  repository's primary scan or in the Gaia primary scan; where the grids differ, the Gaia flag
  at the nearest Gaia grid period is used. Any Gaia dip candidate is checked against this
  project's ground/TESS data before it is called anything more than a candidate.

Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com). CC BY 4.0.
