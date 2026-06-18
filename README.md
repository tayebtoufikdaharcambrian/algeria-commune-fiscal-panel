# Algeria Commune Fiscal Panel — 2010–2020

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Data and code for:

> Dahar, T. T. (2025). *Uniform Law, Unequal Capacity: Fiscal Heteronomy and the Limits of Regional Decentralisation in Algeria's Communes, 2010–2020*. **Public Administration and Development** [under review].

---

## What this repository contains

```
algeria-commune-fiscal-panel/
├── data/
│   ├── raw/                    ← (empty — see note on raw data below)
│   └── processed/
│       ├── algeria_commune_fiscal_panel_2010_2020.csv   ← main analysis file
│       └── rgph2008_communes_master_1541_geo_physical_enriched.csv
├── code/
│   └── analysis.py             ← reproduces every figure, table, and statistic
├── figures/                    ← all five publication figures (PNG, 200 dpi)
├── docs/
│   ├── CODEBOOK.md             ← variable definitions for both datasets
│   └── DATA_SOURCES.md         ← provenance, access conditions, limitations
└── README.md
```

---

## Quick start

```bash
git clone https://github.com/[author-handle]/algeria-commune-fiscal-panel
cd algeria-commune-fiscal-panel
pip install pandas numpy matplotlib statsmodels scipy
python code/analysis.py
```

All figures are regenerated in `figures/` and all numbers cited in the article are printed to the console with labels.

---

## Data

### 1. `algeria_commune_fiscal_panel_2010_2020.csv`

The main analysis file. One row per commune per year (1,541 communes × 9 years = 13,869 rows). Contains own-revenue lines, equalisation transfers, and derived autonomy ratios for every Algerian commune across all available years (2010–2020, with 2013 and 2017 missing from this upload — see Codebook).

Constructed by the author from annual administrative fiscal files (Ministry of the Interior and Local Collectivities / DGCL), harmonised from legacy dBase and spreadsheet formats.

### 2. `rgph2008_communes_master_1541_geo_physical_enriched.csv`

A geospatially enriched master file fixed at the 1,541 communes of the 2008 RGPH census. Demographic variables were transcribed from official ONS tables; geospatial attributes (area, density, elevation, coastal distance, settlement character) were derived from internationally standardised open sources.

### Note on raw files

The raw fiscal files are legacy dBase/spreadsheet records from administrative sources and are not redistributed here because: (a) they contain Arabic-script labels that require encoding care; (b) they are administrative rather than open-publication documents. The processed CSV is the authoritative version for replication. Researchers who need the raw files for independent verification should contact the author.

---

## Reproducing the article

Running `code/analysis.py` reproduces:

| Output | Source |
|---|---|
| Table 1 (morphological heterogeneity) | Section 10 / `geo` master |
| Table 1 fiscal rows + Figure 1 | Section 4–5 / fiscal panel 2019 |
| Figure 2 (Lorenz curve) | Section 7 |
| Figure 2 (Theil decomposition) | Section 5 |
| Table 2 + Figure 3 (morphology gradient) | Section 8 |
| Table 3 + Figure 4 (regressions) | Section 9 |
| All appendix data-quality checks | Section 10 |

---

## License

The processed datasets and code in this repository are released under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt the material for any purpose, provided appropriate credit is given.

The underlying raw census and fiscal data are owned by the Office National des Statistiques (ONS) and the Ministry of the Interior and Local Collectivities, Algeria.

---

## Citation

```bibtex
@article{dahar2025,
  author    = {Dahar, Tayeb Toufik},
  title     = {Uniform Law, Unequal Capacity: Fiscal Heteronomy and the
               Limits of Regional Decentralisation in Algeria's Communes,
               2010--2020},
  journal   = {Public Administration and Development},
  year      = {2025},
  note      = {Under review},
  url       = {https://github.com/[author-handle]/algeria-commune-fiscal-panel}
}
```

---

## Contact

Tayeb Toufik Dahar · Faculty of Law, University of Algiers 1  
Doctoral School of State and Public Institutions  
[your institutional email]
