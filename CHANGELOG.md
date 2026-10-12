# Changelog

## v1.2.1 — October 2026 (documentation only; no data or results changed)

- `CHECKSUMS.sha256`: SHA-256 hashes of every file in `data/processed/`, so that the exact
  files used for the submitted paper can be verified.
- Night-light extraction documented in full in `code/nightlights.py` and `docs/CODEBOOK.md`:
  composite, grid, units, pixel-centre inclusion rule, zero handling and flare mask.
- Zero receipts documented: TAP is zero in four commune-years. For Chiffa (09-0008) in 2020
  every revenue line is zero after TAP of 309 million DA in 2019, which indicates a missing
  report. All four are treated as missing in logarithmic specifications, Theil indices, rank
  statistics and transition matrices.
- The submitted paper corresponds to tag `v1.2.1`.

## v1.2 — October 2026

### Correction: census communes to boundary polygons
Five pairs of neighbouring communes were attached to each other's OCHA polygon in the
census master: 28-0031/28-0032 (M'Sila), 35-0030/35-0031 (Boumerdès), 37-0001/37-0002
(Tindouf), 44-0028/44-0029 (Aïn Defla) and 46-0003/46-0022 (Aïn Témouchent). Every census
commune was re-matched to its polygon by name within its province (fiscal-file French names,
which agree with the census Arabic names); 1,531 links were confirmed and the five pairs
corrected. All polygon-derived fields (area, centroid, elevation, GHSL, boundary codes) and
the night-light totals now follow the verified links.

### Correction: distance to the coast
The v1.1 field `distance_to_coast_km` measured the distance from the nearest point of each
commune polygon to the coastline, although it was documented as a centroid distance. For
large Saharan communes the two differ by hundreds of kilometres. From v1.2 it is the
distance from the polygon centroid (Albers equal-area) to the Algerian Mediterranean
coastline (Natural Earth 1:10m). The v1.1 values are kept as
`distance_to_coast_polygon_edge_km_v11`. Centroids are recomputed from the polygons, and
`near_coast_25km`, `near_coast_50km` and `coastal_commune_1km` are redefined accordingly.

### Added
- `code/build_geography.py` (applies both corrections to the v1.1 master) and
  `data/processed/geography_corrections_v1.2.csv` (old and new values for every commune)
- `code/make_figures.py` (produces the five figures of the paper)
- Additional statistics in `code/revision_analysis.py`: Spearman correlation of TAP and lights,
  shares for a common group of communes, Theil levels for TAP and lights under both weightings,
  leading-commune and Algiers comparisons

### Notes
- TAP receipts are zero in four commune-years and never negative; zeros are excluded from
  logarithmic specifications, Theil indices and persistence statistics.
- Of the 193 Algerian flare sites, 192 fall inside commune polygons; one LNG-terminal flare lies
  on the shoreline just outside the polygon edge. All 193 are masked in the raster.
- The census population (`pop_total` in the master) is the authoritative population. The
  `population_rgph2008` field in the fiscal panel is a reference population carried in the
  ministry files; it differs from the census for about a third of communes and is not used.
- Versions are tagged in git; v1.1 files are retrievable from tag `v1.1`.

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
