# Data Sources and Limitations

## Primary data sources

### 1. RGPH 2008 — General Population and Housing Census

**Producer:** Office National des Statistiques (ONS), Algeria  
**Date:** 2008  
**Access:** Published national commune-level tables (paper and digital), ONS, Algiers  
**Variables used:** Population, housing, household counts; settlement structure (ACL/AS/dispersed zone shares)  
**Notes:** The 2008 RGPH is the most recent census published in full at the commune level. Subsequent censuses (2017 and later) have not been released with comparable commune-level detail. All demographic variables in this study therefore use 2008 population figures, held frozen across the fiscal panel years. This is appropriate for the structural analysis conducted here (which targets morphological and fiscal structure rather than conjunctural change) but means the study cannot capture population dynamics within the 2010–2020 period.

---

### 2. Annual commune fiscal files (DGCL)

**Producer:** Direction Générale des Collectivités Locales (DGCL), Ministry of the Interior and Local Collectivities, Algeria  
**Years covered:** 2010, 2011, 2012, 2014, 2015, 2016, 2018, 2019, 2020  
**Format:** dBase III / IV (.DBF) and Microsoft Excel (.xlsx) — the format changed across years  
**Variables:** Commune code, name, population, eight own-revenue fiscal lines, three transfer lines  
**Access:** Administrative internal files; not publicly distributed. The processed panel CSV in this repository is the author-harmonised version for research replication.

#### Known limitations and missing data

| Issue | Detail |
|---|---|
| **Missing years** | Fiscal files for 2013 and 2017 are not available for upload in this release; the Theil decomposition for those years uses values verified against the complete panel held by the author |
| **Transfer fields sparse before 2013** | The `PEREQUATIO` and `PERQ_BONIF` fields (FCCL equalisation) are irregularly populated in the 2010–2012 files; transfer-dependent analyses use 2013–2019 |
| **2020 transfer omission** | The 2020 file contains no transfer fields; all 2020 analysis is therefore restricted to own-revenue measures |
| **Variable renaming across years** | Field names changed between the dBase and Excel formats (e.g., `TAP` → `T_ACTIVITE`, `TVA` → `T_VALEURAJ`); harmonisation logic is documented in `code/analysis.py` |
| **Encoding** | dBase files use Latin-1 encoding with Arabic transliterated commune names |

---

### 3. Geospatial layers

#### Administrative boundaries
**Source:** Humanitarian Data Exchange (HDX) — COD-AB Algeria dataset  
**URL:** https://data.humdata.org/dataset/cod-ab-dza  
**Use:** Commune polygon boundaries for area calculation and centroid derivation  
**Caveat:** Boundary vintage may not match every historical legal delimitation; this does not affect the computed orders of magnitude

#### Digital elevation model
**Source:** Shuttle Radar Topography Mission (SRTM) 250 m global mosaic  
**Producer:** NASA / USGS  
**URL:** https://srtm.csi.cgiar.org/  
**Use:** Mean elevation per commune boundary

#### Human settlement layer
**Source:** Global Human Settlement Layer — GHS Urban Centre Database  
**Producer:** European Commission / Copernicus  
**URL:** https://human-settlement.emergency.copernicus.eu/  
**Use:** Urban centre footprints for settlement-character classification validation

#### Coastline reference
**Source:** Natural Earth 10 m physical coastline  
**URL:** https://www.naturalearthdata.com/  
**Use:** Computation of commune-centroid-to-coast distance

---

## Key methodological limitations

1. **Frozen population denominator.** All per-capita measures use RGPH 2008 population. Communes that grew or declined significantly between 2008 and 2020 will have slightly biased per-capita figures. The autonomy ratio (the primary measure) is unaffected, as it does not use population.

2. **Operating section only.** The fiscal panel captures operating-section (fonctionnement) receipts. Capital allocations under the PCD (communal development plan) and PSD (sectoral development plan) equipment programmes are administered and recorded separately by sector ministries, and are not in these files. The autonomy ratio therefore measures **operating fiscal self-reliance**, not total budget independence.

3. **Nominal values only.** No price deflation is applied. This is appropriate because: (a) the autonomy ratio is a within-year quotient in which a common deflator cancels; (b) the Theil T index is scale-invariant. Cross-year trend interpretations should note that nominal growth may partly reflect inflation.

4. **Commune matching.** Of 1,541 communes, 1,523 (98.8%) match between the fiscal and geospatial files. The 18 unmatched cases are due to transliteration variants and all fall within the Tell belt; they are not a source of systematic selection bias (see Appendix A.2 in the article).

5. **Missing fiscal years.** The years 2013 and 2017 are not available for upload here. The analysis covers years 2010–2020 with these two gaps. The Theil decomposition results for 2013 and 2017 reported in Figure 2 of the article were computed on the complete files held by the author.

---

## Legal sources (not redistributed)

The following Algerian legal texts are cited in the article and are available on the official Algerian legal database:

- **Law No. 11-10 of 22 June 2011** on the commune — JORA No. 37, 3 July 2011  
- **Law No. 12-07 of 21 February 2012** on the wilaya — JORA No. 12, 29 February 2012  
- **Constitution of the PDRA, revision of 1 November 2020** — JORA No. 82, 30 December 2020  
- **Law No. 19-12 of 11 December 2019** creating ten new wilayas in the South  

Official source: https://www.joradp.dz/
