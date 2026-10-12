# Codebook

## File 1: `algeria_commune_fiscal_panel_2010_2020.csv`

One row per commune per year. All monetary values are **nominal Algerian dinars (DZD)**,
as recorded in the administrative source files. No deflation is applied; all statistics computed in `code/` are within-year ratios, scale-invariant inequality
indices or rank measures, so common price levels cancel.

### Identifier variables

| Variable | Type | Description |
|---|---|---|
| `commune_code` | string | 4-digit commune code: first 2 digits = wilaya code; last 2 = in-wilaya sequence |
| `commune_name` | string | Commune name in Arabic transliteration (from administrative file) |
| `wilaya_code` | string | 2-digit wilaya (province) code |
| `commune_seq` | string | 2-digit within-wilaya commune sequence number |
| `YEAR` | integer | Fiscal year (2010–2020; 2013 and 2017 not included in this upload) |

### Demographic variable

| Variable | Type | Description |
|---|---|---|
| `population_rgph2008` | integer | Commune population from RGPH 2008 census, **frozen** across years — no annual population update is available at commune level |

### Own-revenue lines (DZD, operating section)

All eight lines are drawn from the annual DGCL fiscal files and represent **operating-section (fonctionnement) fiscal receipts only**. Capital allocations under the PCD and PSD equipment programmes are not included.

| Variable | Original code | Description |
|---|---|---|
| `tax_professional_activity` | TAP | Tax on professional activity — levied on enterprise turnover; the dominant communal revenue source (68.6% of all own revenue in 2019) |
| `property_tax` | T_FONCIERE | Property tax on built and unbuilt property |
| `vat_share` | T_VALEURAJ (TVA) | Communal share of value-added tax redistributed from the centre |
| `operating_receipts` | PRODUITEXP | Receipts from operating concessions and services |
| `domain_receipts` | PRODUIT_DO | Receipts from communal domain (land, buildings) |
| `slaughter_tax` | TAXEABATTA | Tax on animal slaughter |
| `single_flat_rate_tax` | IFU | Impôt forfaitaire unique — flat-rate tax on small informal enterprises |
| `income_tax_share` | IRG | Communal share of global income tax |

### Constructed own-revenue aggregate

| Variable | Description |
|---|---|
| `own_revenue` | Sum of all eight own-revenue lines above (DZD) |

### Transfer variables (DZD)

| Variable | Original code | Availability | Description |
|---|---|---|---|
| `transfer_equalisation` | PEREQUATIO | **2013–2019 only** | Equalisation allocation from the Fonds Commun des Collectivités Locales (FCCL) |
| `transfer_bonified` | PERQ_BONIF | **2013–2019 only** | Bonified (enhanced) equalisation component |
| `transfer_tap_compensation` | TAPCOMPENS | **2010–2015 only** | Compensation for TAP revenue shortfalls |
| `transfer_total` | — | see above | Sum of the three transfer lines |
| `total_resources` | — | see above | `own_revenue + transfer_total` |

> ⚠️ **Missing-data warning:** The `transfer_equalisation` and `transfer_bonified` fields are
> sparsely or inconsistently populated before 2013. The 2020 file omits all transfer fields.
> Set `transfer_reliable = 1` rows should be used for any transfer-dependent analysis.

### Derived analytical variables

| Variable | Formula | Description |
|---|---|---|
| `autonomy_ratio` | `own_revenue / total_resources` | Fiscal autonomy ratio (0–1). `NaN` where `total_resources = 0` |
| `transfer_recorded` | 1 if `transfer_total > 0` | Flag: transfers are non-zero in this row |
| `transfer_reliable` | 1 if `YEAR ∈ [2013, 2019]` and `transfer_total > 0` | Flag: transfers are from a reliably recorded year |

---

## File 2: `rgph2008_communes_master_1541_geo_physical_enriched.csv`

One row per commune (1,541 rows). Fixed at the 2008 RGPH territorial organisation.

### Key variables

| Variable | Source | Description |
|---|---|---|
| `rgph2008_commune_id` | ONS | Commune identifier in `WW-SSSS` format (wilaya-sequence) |
| `commune_name` | ONS | Commune name |
| `wilaya_code` | ONS | 2-digit wilaya code |
| `pop_total` | RGPH 2008 | Total commune population |
| `commune_area_sqkm` | HDX COD-AB boundary → area calculation | Commune area in km² |
| `population_density_2008_per_sqkm` | Derived | Pop / area |
| `distance_to_coast_km` | Natural Earth coastline → centroid distance | Distance from commune centroid to nearest coastline point |
| `near_coast_50km` | Derived | 1 if `distance_to_coast_km ≤ 50`, else 0 |
| `elevation_mean_m` | SRTM DEM | Mean elevation within commune boundary |
| `macro_physical_region` | Author classification | One of: `Tell / northern coastal-mountain belt` · `High Plateaus / steppe belt` · `Saharan belt` |
| `settlement_character_2008` | RGPH 2008 settlement layer | Five-class typology based on shares of ACL (chef-lieu agglomeration), AS (secondary agglomeration), and dispersed zone population |
| `commune_area_size_class` | Derived | Categorical area size class |

### Settlement character typology (five classes)

| Class label | Definition |
|---|---|
| `Predominantly urban core (ACL >= 75%)` | ≥75% of population in the chef-lieu agglomeration |
| `Predominantly agglomerated (ACL+AS >= 75%)` | ≥75% in ACL + secondary agglomerations combined |
| `Mixed, urban-influenced` | Agglomerated majority but below 75% threshold |
| `Mixed, low-density / rural-influenced` | Mixed with low-density rural predominance |
| `Predominantly dispersed/rural (ZE >= 50%)` | ≥50% of population in the dispersed rural zone |

### Geospatial data sources

| Layer | Source | Version/date used |
|---|---|---|
| Administrative boundaries | Humanitarian Data Exchange — COD-AB Algeria | Downloaded 2024 |
| Digital elevation model | SRTM 250 m (NASA / USGS) | Global mosaic |
| Urban settlement footprints | Global Human Settlement Layer (EC / Copernicus) | GHS-UCDB R2019A |
| Coastline | Natural Earth 10 m physical coastline | v5.1 |

> **Boundary caveat:** Administrative boundary vintages do not reproduce every historical
> legal delimitation exactly. This does not affect the orders of magnitude reported, and is
> documented in `docs/DATA_SOURCES.md`.


---

## 3. `crosswalk_fiscal_to_rgph2008.csv` (added in v1.1)

One row per commune (1,541). Maps the commune sequence number used in the fiscal files
to the sequence number of the 2008 census (RGPH) master file. **Always join the fiscal
panel to the census master through this file.** In four provinces the two numberings differ.

| Variable | Description |
|---|---|
| `wilaya_code` | Province code (48-province system) |
| `commune_seq_fiscal` | Commune sequence number as it appears in the fiscal panel (`commune_seq`) |
| `commune_seq_rgph2008` | Commune sequence number in the census master |
| `rgph2008_commune_id` | Census master identifier (`WW-SSSS`) |
| `commune_name_fiscal` / `commune_name_rgph2008` | Names in each source |
| `name_similarity` | Normalised string similarity of the two names (0–1); low values are renamed communes, verified against Arabic names |
| `key_differs` | 1 if the two sequence numbers differ (94 communes: Blida 21, Algiers 21, Boumerdès 30, Tipaza 22) |

Note: the English `commune_name` column of the census master contains a few label errors
(e.g. Tindouf 37-0001 shows "(ACL)"; Aïn Témouchent 46-0003/46-0022 have English labels
swapped). The Arabic name column `commune_name_ar` is authoritative.

## 4. `commune_nightlights_2019.csv` (added in v1.1)

Built by `code/nightlights.py`. One row per commune (1,541).

| Variable | Description |
|---|---|
| `rgph2008_commune_id` | Census master identifier |
| `commune_name` | Census master name |
| `boundary_adm2_pcode` | OCHA COD-AB p-code used for the polygon join |
| `viirs2019_sum_radiance_flaremasked` | Sum of VIIRS VNL v2.1 2019 average-masked radiance (nW/cm²/sr; 15 arc-second grid, WGS84) over pixels whose centre falls in the commune polygon, without area weighting, after zeroing pixels within 3 km of any of the 193 Algerian 2019 VNF flare sites |
| `vnf2019_flare_sites` | Number of 2019 VNF gas-flare sites located in the commune |

## Known data issues

- Commune 05-0061 (Larbaa, Batna) has no 2008 population in the census master and is
  excluded from per-capita analyses.
- TAP is zero in 4 commune-years (El Khemis 2012; Chiffa, Sidi Medjahed and Mihoub 2020) and
  never negative. For Chiffa 2020 every revenue line is zero after TAP of 309 million DA in 2019,
  which indicates a missing report. All four are treated as missing in log specifications,
  Theil indices, rank statistics and transition matrices.

## 5. Geography fields after v1.2

| Variable | Definition |
|---|---|
| `commune_centroid_lat`, `commune_centroid_lon` | Centroid of the OCHA commune polygon, computed in an Albers equal-area projection (lat_1 = 20, lat_2 = 35, lat_0 = 28, lon_0 = 3) |
| `distance_to_coast_km` | Distance from the centroid to the Algerian Mediterranean coastline (Natural Earth 1:10m coastline, segments between 2.25 W and 8.7 E), in km |
| `distance_to_coast_polygon_edge_km_v11` | v1.1 value: distance from the nearest point of the polygon to the coastline. Kept for reference only |
| `near_coast_25km`, `near_coast_50km` | Centroid within 25 or 50 km of the coastline |
| `coastal_commune_1km` | Polygon within 1 km of the coastline |
| `boundary_match_method` | `name_verified_v1.2` for the ten communes whose polygon link was corrected |

`geography_corrections_v1.2.csv` lists, for every commune, the v1.1 and v1.2 values of the
polygon code, area, elevation, centroid, density and distance to the coast, with a flag for the
ten re-linked communes.

## Population fields

`pop_total` in the census master is the 2008 census population and is used in all analyses.
`population_rgph2008` in the fiscal panel is a reference population carried in the ministry
files; it differs from the census for about a third of communes and is not used.
