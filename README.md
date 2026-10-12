# Algeria Commune Fiscal Panel, 2010–2020

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

An annual panel of local tax receipts for all 1,541 communes of Algeria, matched to a
geospatially enriched file of the 2008 population census, with code to reproduce the
statistics computed from it.

Algeria publishes no commune-level output data. The communes' own fiscal records,
in particular the tax on professional activity (TAP), levied on the turnover of each
establishment in the commune where it is located, give an annual, spatially exact record
of formal taxable activity. This repository makes those records usable for research.

**Current version: v1.2** (October 2026). See [CHANGELOG.md](CHANGELOG.md), which documents
corrections to the fiscal-to-census matching (v1.1) and to the census-to-polygon links and
the distance-to-coast variable (v1.2).

---

## Contents

```
algeria-commune-fiscal-panel/
├── data/
│   ├── raw/                     ← not tracked; see docs/DATA_SOURCES.md
│   └── processed/
│       ├── algeria_commune_fiscal_panel_2010_2020.csv            fiscal panel (13,869 commune-years)
│       ├── rgph2008_communes_master_1541_geo_physical_enriched.csv  census + geography master
│       ├── crosswalk_fiscal_to_rgph2008.csv                      join key between the two
│       ├── commune_nightlights_2019.csv                          VIIRS 2019 lights, flares masked
│       └── geography_corrections_v1.2.csv                        log of v1.2 geographic corrections
├── code/
│   ├── revision_analysis.py    spatial statistics, robustness and night-light validation
│   ├── make_figures.py         produces the five figures of the paper
│   ├── build_geography.py      verifies polygon links and computes centroids and coast distance
│   ├── nightlights.py          builds commune_nightlights_2019.csv from the raw rasters
│   └── analysis.py             fiscal-autonomy descriptives and figures
├── figures/
├── docs/
│   ├── CODEBOOK.md             variable definitions for every file
│   └── DATA_SOURCES.md         provenance, what the TAP measures, limitations
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Quick start

```bash
git clone https://github.com/tayebtoufikdaharcambrian/algeria-commune-fiscal-panel
cd algeria-commune-fiscal-panel
pip install pandas numpy scipy statsmodels matplotlib
python code/revision_analysis.py     # all spatial statistics, printed with labels
python code/make_figures.py          # the five figures of the paper
python code/analysis.py              # fiscal-autonomy descriptives and figures
```

`code/build_geography.py` and `code/nightlights.py` additionally need `geopandas shapely
rasterio rasterstats openpyxl` and the raw files listed in their headers; their outputs are
already included in `data/processed/`.

**Joining the files:** always link the fiscal panel to the census master through
`crosswalk_fiscal_to_rgph2008.csv`. The two sources number communes differently in
Blida, Algiers, Boumerdès and Tipaza.

## The data

**Fiscal panel.** One row per commune per year, for 2010, 2011, 2012, 2014, 2015, 2016,
2018, 2019 and 2020 (2013 and 2017 are not included). It contains the TAP, seven other
own-revenue lines, equalisation transfers and derived autonomy ratios, in nominal dinars.
Built from the annual commune fiscal files of the Ministry of the Interior and Local
Authorities (DGCL), harmonised from legacy dBase and spreadsheet formats.

**Census master.** The 1,541 communes of the 2008 census (RGPH), with population and
housing variables transcribed from official ONS tables, plus area, density, elevation,
distance from the commune centroid to the Algerian Mediterranean coast, settlement type and
OCHA boundary codes. Its `pop_total` is the authoritative population for all analyses.

**Night lights.** Commune totals of VIIRS 2019 night-time radiance with gas-flare sites
masked, for validating fiscal measures against an independent indicator of activity.

**What the TAP measures.** Turnover booked by each establishment in its commune, not
value added or production. See `docs/DATA_SOURCES.md` before interpreting it as a measure
of economic activity.

## Possible uses

- Spatial distribution and concentration of formal economic activity
- Local public finance, fiscal capacity and equalisation
- Validation of remote-sensing proxies (night lights, built-up area) against fiscal data
- Comparative work with other countries that levy origin-based local business taxes

## Citation

```bibtex
@dataset{dahar_algeria_commune_fiscal_panel,
  author  = {Dahar, Tayeb Toufik},
  title   = {Algeria Commune Fiscal Panel, 2010--2020},
  version = {1.2},
  year    = {2026},
  url     = {https://github.com/tayebtoufikdaharcambrian/algeria-commune-fiscal-panel}
}
```

## License

Processed data and code: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The underlying census and fiscal records belong to the Office National des Statistiques
(ONS) and the Ministry of the Interior and Local Authorities, Algeria. Third-party layers
(VIIRS, VNF, OCHA COD-AB) are subject to their providers' terms and are not redistributed.

## Contact

Tayeb Toufik Dahar · Faculty of Law, University of Algiers 1 · Cambrian College, Canada
tdahar@mycambrian.ca
