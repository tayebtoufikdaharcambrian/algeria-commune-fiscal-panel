# Changelog

## v1.1 — October 2026

### Correction: commune matching
The fiscal files and the 2008 census use different commune sequence numbers in four
provinces: Blida (09), Algiers (16), Boumerdès (35) and Tipaza (42). Version 1.0 joined
the two sources on province code and sequence number. In those four provinces this
dropped 18 communes and attached 76 others to the census record of a different commune.

v1.1 adds `data/processed/crosswalk_fiscal_to_rgph2008.csv`, built by matching names
within each province and checked against the Arabic names. All 1,541 communes now match,
and `code/analysis.py` uses the crosswalk.

What changes: statistics that combine fiscal data with census or geographic variables
(per-capita measures, density and geography regressions, population shares) change
slightly. What does not change: statistics computed from fiscal data alone
(concentration of receipts, Theil decomposition, rank persistence), and the fiscal panel
file itself.

### Added
- `data/processed/rgph2008_communes_master_1541_geo_physical_enriched.csv` (listed in
  v1.0 but not uploaded)
- `data/processed/crosswalk_fiscal_to_rgph2008.csv`
- `data/processed/commune_nightlights_2019.csv` and `code/nightlights.py`
- `code/revision_analysis.py`: province-clustered and Conley standard errors,
  standardised coefficients, gradient decomposition, functional form, rank-size
  sensitivity to the tail cutoff, decile transition matrices, Theil decomposition under
  equal and population weights, and validation against night lights and census
  professional premises
- `LICENSE`, `CHANGELOG.md`
- Documentation of what the TAP measures, its rate changes (2015) and the IFU threshold
  change (2020) in `docs/DATA_SOURCES.md`

### Changed
- README rewritten as a general dataset description
- Figures in `figures/` regenerated with the corrected matching

## v1.0 — initial release
