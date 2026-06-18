# Codebook

## File 1: `algeria_commune_fiscal_panel_2010_2020.csv`

One row per commune per year. All monetary values are **nominal Algerian dinars (DZD)**,
as recorded in the administrative source files. No deflation is applied; see article
Section 4.2 and Appendix A.5 for the inflation-invariance argument.

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

### Key variables used in the article

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
| `settlement_character_2008` | RGPH 2008 settlement layer | Five-class typology based on shares of ACL (chef-lieu agglomeration), AS (secondary agglomeration), and dispersed zone population — see article Appendix A.2 |
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
> documented in article Appendix A.2.
