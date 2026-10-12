"""
nightlights.py
==============
Builds data/processed/commune_nightlights_2019.csv: total VIIRS night-time
radiance per commune in 2019, with gas flares masked.

Raw inputs (not redistributed; download them into data/raw/):
  1. VNL_v21_npp_2019_global_vcmslcfg_c202205302300.average_masked.dat.tif.gz
     Earth Observation Group, Payne Institute, Colorado School of Mines
     (VIIRS Nighttime Lights v2.1, annual 2019, background/fires/aurora masked)
     https://eogdata.mines.edu/products/vnl/
  2. VIIRS_Global_flaring_2019_web.xlsx
     World Bank GGFR / EOG VIIRS Nightfire flare-site list for 2019
  3. dza_admin_boundaries.shp.zip
     OCHA COD-AB Algeria (HDX dataset cod-ab-dza), layer dza_admin2 (1,541 communes)

Method:
  - input grid: 15 arc-second pixels in geographic coordinates (WGS84, EPSG:4326);
    values are average radiance in nW/cm2/sr;
  - clip the global raster to Algeria;
  - set to zero all pixels within 3 km of each Algerian flare site
    (upstream, refinery and LNG sites in the 2019 list);
  - sum radiance of the pixels whose centres fall inside each commune polygon
    (no area weighting; zero-radiance pixels contribute zero);
  - count flare sites per commune. Of the 193 sites, 192 fall inside commune polygons;
    one LNG-terminal flare lies on the shoreline just outside the polygon edge and is
    masked but not counted in any commune.

Run:  python code/nightlights.py
Requires: rasterio geopandas rasterstats pandas numpy openpyxl
"""
import os
import zipfile
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds
from rasterstats import zonal_stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed", "commune_nightlights_2019.csv")
VNL = os.path.join(RAW, "VNL_v21_npp_2019_global_vcmslcfg_c202205302300.average_masked.dat.tif.gz")
FLR = os.path.join(RAW, "VIIRS_Global_flaring_2019_web.xlsx")
BND = os.path.join(RAW, "dza_admin_boundaries.shp.zip")
FLARE_RADIUS_KM = 3.0

# 1. Clip raster to Algeria
src = rasterio.open("/vsigzip/" + VNL)
win = from_bounds(-9.0, 18.9, 12.2, 37.2, src.transform)
arr = src.read(1, window=win).astype("float32")
T = src.window_transform(win)
H, Wd = arr.shape
lat_c = T.f + T.e * (np.arange(H) + 0.5)
lon_c = T.c + T.a * (np.arange(Wd) + 0.5)

# 2. Mask flares
F = pd.read_excel(FLR, sheet_name="all flares")
F = F[F["ISO Code"] == "DZA"]
k = int(np.ceil(FLARE_RADIUS_KM / (abs(T.e) * 111))) + 1
for _, f in F.iterrows():
    r = int((T.f - f.Latitude) / -T.e)
    c = int((f.Longitude - T.c) / T.a)
    r0, c0 = max(r - k, 0), max(c - k, 0)
    yy = lat_c[r0:r + k + 1][:, None]
    xx = lon_c[c0:c + k + 1][None, :]
    m = (((yy - f.Latitude) * 111) ** 2
         + ((xx - f.Longitude) * 111 * np.cos(np.radians(f.Latitude))) ** 2) <= FLARE_RADIUS_KM ** 2
    arr[r0:r + k + 1, c0:c + k + 1][m] = 0

# 3. Commune polygons and zonal sums
with zipfile.ZipFile(BND) as z:
    z.extractall(os.path.join(RAW, "dza_admin_boundaries"))
g = gpd.read_file(os.path.join(RAW, "dza_admin_boundaries", "dza_admin2.shp"))
zs = zonal_stats(g, arr, affine=T, stats=["sum"], nodata=-999)
g["viirs2019_sum_radiance_flaremasked"] = [s["sum"] or 0.0 for s in zs]

fp = gpd.GeoDataFrame(F, geometry=gpd.points_from_xy(F.Longitude, F.Latitude), crs=4326)
nf = gpd.sjoin(fp, g[["adm2_pcode", "geometry"]], predicate="within").groupby("adm2_pcode").size()
g["vnf2019_flare_sites"] = g.adm2_pcode.map(nf).fillna(0).astype(int)

# 4. Attach census identifiers via the OCHA p-code stored in the master file
G = pd.read_csv(os.path.join(ROOT, "data", "processed",
                             "rgph2008_communes_master_1541_geo_physical_enriched.csv"),
                dtype={"rgph2008_commune_id": str})
out = (G[["rgph2008_commune_id", "commune_name", "boundary_adm2_pcode"]]
       .merge(g[["adm2_pcode", "viirs2019_sum_radiance_flaremasked", "vnf2019_flare_sites"]],
              left_on="boundary_adm2_pcode", right_on="adm2_pcode", how="left")
       .drop(columns="adm2_pcode"))
out.to_csv(OUT, index=False)
print(f"Wrote {OUT}: {len(out)} communes, {int((out.vnf2019_flare_sites > 0).sum())} with flare sites")
