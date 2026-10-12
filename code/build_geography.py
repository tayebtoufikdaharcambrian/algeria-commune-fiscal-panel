"""
build_geography.py  (v1.2)
==========================
Repairs and documents the link between 2008 census communes and the OCHA
commune polygons, and recomputes the polygon-based geography.

Two problems in the v1.1 census master are corrected:

1. Census-to-polygon identity. Five pairs of communes were attached to each
   other's polygon (28-0031/28-0032, 35-0030/35-0031, 37-0001/37-0002,
   44-0028/44-0029, 46-0003/46-0022). Every census commune is re-matched to an
   OCHA polygon by name within its province, using the fiscal-file French names,
   which agree with the census Arabic names. All polygon-derived fields
   (area, centroid, elevation, GHSL, boundary codes) move with the polygon.

2. Distance to the coast. The v1.1 field measured the distance from the
   nearest point of each commune polygon to the coastline, although it was
   documented as a centroid distance. For large Saharan communes the two
   differ by hundreds of kilometres. v1.2 defines distance_to_coast_km as the
   distance from the polygon centroid (computed in an Albers equal-area
   projection) to the Algerian Mediterranean coastline (Natural Earth 1:10m
   coastline, segments between 2.25 W and 8.7 E). The v1.1 polygon-edge
   distance is kept as distance_to_coast_polygon_edge_km_v11.

Raw inputs (data/raw/, not redistributed):
  dza_admin_boundaries.shp.zip  OCHA COD-AB Algeria (HDX cod-ab-dza)
  ne_10m_coastline.geojson      Natural Earth 1:10m coastline (public domain)

Outputs:
  data/processed/rgph2008_communes_master_1541_geo_physical_enriched.csv (overwritten, v1.2)
  data/processed/geography_corrections_v1.2.csv  (old vs new values for changed fields)

Run:  python code/build_geography.py   (input master must be the v1.1 file)
Requires: geopandas shapely pandas numpy scipy
"""
import os, re, zipfile, difflib, unicodedata
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union
from scipy.optimize import linear_sum_assignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")
MASTER = os.path.join(PROC, "rgph2008_communes_master_1541_geo_physical_enriched.csv")

G = pd.read_csv(MASTER, dtype={"rgph2008_commune_id": str})
if "distance_to_coast_polygon_edge_km_v11" in G.columns:
    raise SystemExit("Master is already v1.2; run on the v1.1 file.")
X = pd.read_csv(os.path.join(PROC, "crosswalk_fiscal_to_rgph2008.csv"), dtype={"rgph2008_commune_id": str})
with zipfile.ZipFile(os.path.join(RAW, "dza_admin_boundaries.shp.zip")) as z:
    z.extractall(os.path.join(RAW, "dza_admin_boundaries"))
poly = gpd.read_file(os.path.join(RAW, "dza_admin_boundaries", "dza_admin2.shp"))
coast = gpd.read_file(os.path.join(RAW, "ne_10m_coastline.geojson"))

# ---- 1. name-based re-match within province -------------------------------
def norm(x):
    x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().upper()
    x = re.sub(r"\(.*?\)", "", x)
    x = re.sub(r"[^A-Z]", "", x)
    for a, b in [("OU", "U"), ("EL", ""), ("BENI", "BNI"), ("DJ", "J"), ("KH", "K"),
                 ("GH", "G"), ("CH", "C"), ("EE", "E"), ("AA", "A"), ("II", "I")]:
        x = x.replace(a, b)
    return x

G = G.merge(X[["rgph2008_commune_id", "commune_name_fiscal"]], on="rgph2008_commune_id", how="left")
G["_w"] = G.rgph2008_commune_id.str[:2]
w2adm1 = G.groupby("_w").boundary_adm1_pcode.agg(lambda s: s.mode().iloc[0]).to_dict()
new_pcode = {}
for w, adm1 in w2adm1.items():
    a = G[G._w == w].reset_index(drop=True)
    b = poly[poly.adm1_pcode == adm1].reset_index(drop=True)
    S = np.array([[max(difflib.SequenceMatcher(None, norm(f), norm(y)).ratio(),
                       difflib.SequenceMatcher(None, norm(e), norm(y)).ratio()) for y in b.adm2_name]
                  for f, e in zip(a.commune_name_fiscal, a.commune_name)])
    r, c = linear_sum_assignment(-S)
    for i, j in zip(r, c):
        new_pcode[a.rgph2008_commune_id[i]] = b.adm2_pcode[j]
G["_new_pcode"] = G.rgph2008_commune_id.map(new_pcode)
changed_ids = G.loc[G._new_pcode != G.boundary_adm2_pcode, "rgph2008_commune_id"].tolist()
print("Census communes re-linked to a different polygon:", changed_ids)

# polygon-derived fields travel with the polygon
POLY_FIELDS = ["boundary_adm2_pcode", "boundary_commune_name", "boundary_adm1_pcode", "boundary_wilaya_name",
               "commune_area_sqkm", "boundary_valid_on", "boundary_version", "commune_polygon_area_sqkm_calc",
               "ghsl_urban_centre_extent_sqkm", "ghsl_urban_centre_builtup_sqkm", "ghsl_urban_centre_pop2020_alloc",
               "ghsl_urban_centre_count", "ghsl_urban_centre_presence", "area_indicator_completeness",
               "builtup_indicator_scope", "elevation_mean_m", "elevation_min_m", "elevation_max_m",
               "elevation_range_m", "elevation_std_m", "elevation_pixel_count", "elevation_class_mean",
               "commune_area_size_class", "distance_to_coast_km"]
by_pcode = G.set_index("boundary_adm2_pcode")[[f for f in POLY_FIELDS if f != "boundary_adm2_pcode"]]
old = G.copy()
for f in POLY_FIELDS:
    if f == "boundary_adm2_pcode":
        G[f] = G._new_pcode
    else:
        G[f] = G._new_pcode.map(by_pcode[f])
G = G.rename(columns={"distance_to_coast_km": "distance_to_coast_polygon_edge_km_v11"})
G.loc[G.rgph2008_commune_id.isin(changed_ids), "boundary_match_method"] = "name_verified_v1.2"

# ---- 2. centroids and coast distance from polygons -------------------------
AEA = "+proj=aea +lat_1=20 +lat_2=35 +lat_0=28 +lon_0=3 +datum=WGS84 +units=m"
pp = poly.to_crs(AEA).set_index("adm2_pcode")
cent = pp.geometry.centroid
cent_ll = gpd.GeoSeries(cent, crs=AEA).to_crs(4326)
dz_coast = unary_union(coast.clip(box(-2.25, 34.8, 8.7, 37.6)).to_crs(AEA).geometry)
dist_c = pd.Series([pt.distance(dz_coast) / 1000 for pt in cent], index=cent.index)
dist_poly = pd.Series([geom.distance(dz_coast) / 1000 for geom in pp.geometry], index=pp.index)
G["commune_centroid_lat"] = G.boundary_adm2_pcode.map(cent_ll.y)
G["commune_centroid_lon"] = G.boundary_adm2_pcode.map(cent_ll.x)
G["distance_to_coast_km"] = G.boundary_adm2_pcode.map(dist_c).round(3)
G["coastal_commune_1km"] = G.boundary_adm2_pcode.map(dist_poly) <= 1.0
G["near_coast_25km"] = G.distance_to_coast_km <= 25
G["near_coast_50km"] = G.distance_to_coast_km <= 50

# ---- 3. ratios that combine census and polygon fields -----------------------
G["population_density_2008_per_sqkm"] = G.pop_total / G.commune_area_sqkm
G["housing_density_2008_per_sqkm"] = G.log_total / G.commune_area_sqkm
G["ghsl_urban_centre_extent_share_total_area_pct"] = 100 * G.ghsl_urban_centre_extent_sqkm / G.commune_area_sqkm
G["ghsl_urban_centre_builtup_share_total_area_pct"] = 100 * G.ghsl_urban_centre_builtup_sqkm / G.commune_area_sqkm

# ---- 4. log of changes ------------------------------------------------------
keep = ["rgph2008_commune_id", "commune_name", "commune_name_ar"]
cmp_fields = ["boundary_adm2_pcode", "commune_area_sqkm", "elevation_mean_m", "commune_centroid_lat",
              "commune_centroid_lon", "population_density_2008_per_sqkm"]
log = old[keep + cmp_fields + ["distance_to_coast_km"]].rename(columns={c: c + "_v11" for c in cmp_fields + ["distance_to_coast_km"]})
log = log.merge(G[["rgph2008_commune_id"] + cmp_fields + ["distance_to_coast_km"]].rename(
    columns={c: c + "_v12" for c in cmp_fields + ["distance_to_coast_km"]}), on="rgph2008_commune_id")
log["polygon_relinked"] = log.rgph2008_commune_id.isin(changed_ids)
log.to_csv(os.path.join(PROC, "geography_corrections_v1.2.csv"), index=False)

G = G.drop(columns=["_w", "_new_pcode", "commune_name_fiscal"])
G.to_csv(MASTER, index=False)
d = (log.distance_to_coast_km_v12 - log.distance_to_coast_km_v11)
print(f"Wrote v1.2 master. Coast distance change: median {d.median():.1f} km, "
      f"|change|>50 km for {(d.abs() > 50).sum()} communes, max {d.abs().max():.0f} km.")
