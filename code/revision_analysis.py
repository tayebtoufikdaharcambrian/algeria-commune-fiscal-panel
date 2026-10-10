"""
revision_analysis.py
====================
Reproduces the commune-level spatial statistics computed from the panel,
using the corrected fiscal-to-census crosswalk (v1.1).

Inputs (all in data/processed/):
  algeria_commune_fiscal_panel_2010_2020.csv
  rgph2008_communes_master_1541_geo_physical_enriched.csv
  crosswalk_fiscal_to_rgph2008.csv
  commune_nightlights_2019.csv            (produced by code/nightlights.py)

Run:  python code/revision_analysis.py
Requires: pandas numpy statsmodels scipy
All results are printed to the console with labels.
"""
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "processed")

# --------------------------------------------------------------------------
# 0. Load and join
# --------------------------------------------------------------------------
P = pd.read_csv(os.path.join(D, "algeria_commune_fiscal_panel_2010_2020.csv"),
                dtype={"wilaya_code": str, "commune_seq": str, "commune_code": str})
G = pd.read_csv(os.path.join(D, "rgph2008_communes_master_1541_geo_physical_enriched.csv"),
                dtype={"rgph2008_commune_id": str})
X = pd.read_csv(os.path.join(D, "crosswalk_fiscal_to_rgph2008.csv"),
                dtype={"rgph2008_commune_id": str})

P["wilaya_code"] = P["wilaya_code"].astype(int)
P["commune_seq_fiscal"] = P["commune_seq"].astype(int)
P = P.merge(X[["wilaya_code", "commune_seq_fiscal", "rgph2008_commune_id"]],
            on=["wilaya_code", "commune_seq_fiscal"], how="left")
assert P["rgph2008_commune_id"].notna().all(), "crosswalk incomplete"

PANEL = P.merge(G, on="rgph2008_commune_id", how="left", suffixes=("", "_g"))
W = "wilaya_code"


def section(t):
    print("\n" + "=" * 72 + "\n" + t + "\n" + "=" * 72)


def cs(year):
    d = PANEL[PANEL.YEAR == year].copy()
    d = d[d.tax_professional_activity > 0]
    d["ltap"] = np.log(d.tax_professional_activity)
    d["lpop"] = np.log(d.pop_total)
    d["ltap_pc"] = d.ltap - d.lpop
    d["lown_pc"] = np.log(d.own_revenue / d.pop_total)
    d["ldens"] = np.log(d.population_density_2008_per_sqkm)
    d["coast"] = d.distance_to_coast_km / 100.0
    d["elev"] = d.elevation_mean_m / 1000.0
    d["ltap_area"] = np.log(d.tax_professional_activity / d.commune_area_sqkm)
    return d.dropna(subset=["ltap_pc", "ldens", "coast", "elev"]).reset_index(drop=True)


def distance_matrix(d):
    lat = np.radians(d.commune_centroid_lat.values)
    lon = np.radians(d.commune_centroid_lon.values)
    a = (np.sin((lat[:, None] - lat[None, :]) / 2) ** 2
         + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin((lon[:, None] - lon[None, :]) / 2) ** 2)
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def conley_se(model, Dkm, cutoff):
    """Conley (1999) spatial HAC standard errors, Bartlett kernel."""
    X_ = model.model.exog
    e = model.resid.values
    K = np.clip(1 - Dkm / cutoff, 0, None)
    XtXi = np.linalg.inv(X_.T @ X_)
    Xe = X_ * e[:, None]
    V = XtXi @ (Xe.T @ K @ Xe) @ XtXi
    return pd.Series(np.sqrt(np.diag(V)), index=model.params.index)


def cl(f, d):
    return smf.ols(f, d).fit(cov_type="cluster", cov_kwds={"groups": d[W]})


d19 = cs(2019)

# --------------------------------------------------------------------------
# 1. Sample accounting
# --------------------------------------------------------------------------
section("1. SAMPLE ACCOUNTING")
print(f"Communes in panel: {P.rgph2008_commune_id.nunique()}")
print(f"Commune keys re-assigned by crosswalk: {int(X.key_differs.sum())} "
      f"in provinces {sorted(X.loc[X.key_differs == 1, 'wilaya_code'].unique().tolist())}")
print(f"2019 regression sample: {len(d19)}")
print("Commune-years with TAP <= 0, by year:",
      P.groupby("YEAR").tax_professional_activity.apply(lambda s: int((s <= 0).sum())).to_dict())
miss = G[~G.rgph2008_commune_id.isin(d19.rgph2008_commune_id)]
print("Communes outside the 2019 sample:")
print(miss[["rgph2008_commune_id", "commune_name", "pop_total", "population_density_2008_per_sqkm",
            "distance_to_coast_km"]].to_string(index=False))

# --------------------------------------------------------------------------
# 2. Density elasticity: HC1, province-clustered, Conley
# --------------------------------------------------------------------------
section("2. DENSITY ELASTICITY OF PER-CAPITA TAP, 2019")
Dkm = distance_matrix(d19)
specs = {
    "(1) unconditional": "ltap_pc ~ ldens",
    "(2) + coast + elevation": "ltap_pc ~ ldens + coast + elev",
    "(3) + province FE": "ltap_pc ~ ldens + coast + elev + C(wilaya_code)",
    "(4) own revenue, province FE": "lown_pc ~ ldens + coast + elev + C(wilaya_code)",
}
for name, f in specs.items():
    m = smf.ols(f, d19).fit(cov_type="HC1")
    mc = cl(f, d19)
    m0 = smf.ols(f, d19).fit()
    se_c = {c: conley_se(m0, Dkm, c) for c in (50, 100, 200)}
    print(f"\n{name}   N={int(m.nobs)}  adj.R2={m.rsquared_adj:.3f}")
    for v in ["ldens", "coast", "elev"]:
        if v in m.params:
            print(f"   {v:6s} b={m.params[v]:7.3f}  HC1 {m.bse[v]:.3f}  cluster {mc.bse[v]:.3f} (p={mc.pvalues[v]:.3f})"
                  f"  Conley50 {se_c[50][v]:.3f}  Conley100 {se_c[100][v]:.3f}  Conley200 {se_c[200][v]:.3f}")

section("2b. STANDARDISED COEFFICIENTS")
z = d19.copy()
for v in ["ltap_pc", "ldens", "coast", "elev"]:
    z[v] = (z[v] - z[v].mean()) / z[v].std()
for name in ["(2) + coast + elevation", "(3) + province FE"]:
    m = smf.ols(specs[name], z).fit()
    print(name, {v: round(m.params[v], 3) for v in ["ldens", "coast", "elev"]})
print("Correlations:\n", d19[["ldens", "coast", "elev"]].corr().round(2))

section("2c. NEIGHBOURHOOD DENSITY AND MARKET POTENTIAL")
pop, area = d19.pop_total.values, d19.commune_area_sqkm.values
for r in (10, 25, 50):
    M = (Dkm <= r).astype(float)
    d19[f"lnd{r}"] = np.log((M @ pop) / (M @ area))
Dm = Dkm.copy(); np.fill_diagonal(Dm, np.inf)
own = pop / (0.66 * np.sqrt(area / np.pi))
d19["lmp"] = np.log((pop[None, :] / np.maximum(Dm, 1)).sum(1) + own)
for f in ["ltap_pc ~ lnd10 + elev + C(wilaya_code)", "ltap_pc ~ lnd25 + elev + C(wilaya_code)",
          "ltap_pc ~ lnd50 + elev + C(wilaya_code)", "ltap_pc ~ ldens + lmp + elev + C(wilaya_code)"]:
    m = cl(f, d19)
    k = [x for x in m.params.index if not x.startswith("C(") and x != "Intercept"]
    print(f"{f:48s}", "  ".join(f"{x}={m.params[x]:.3f}({m.bse[x]:.3f})" for x in k))

# --------------------------------------------------------------------------
# 3. Gradient decomposition and functional form
# --------------------------------------------------------------------------
section("3. COASTAL GRADIENT: ACTIVITY DENSITY = PER-CAPITA x POPULATION DENSITY")
for y in ["ltap_area", "ltap_pc", "ldens"]:
    m = cl(f"{y} ~ coast + elev", d19)
    print(f"{y:10s} coast={m.params['coast']:.3f} ({m.bse['coast']:.3f})  "
          f"elev={m.params['elev']:.3f} ({m.bse['elev']:.3f})  R2={m.rsquared:.3f}")

section("3b. FUNCTIONAL FORM: PER-CAPITA TAP ON LOG DENSITY")
mq = cl("ltap_pc ~ ldens + I(ldens**2)", d19)
tp = -mq.params["ldens"] / (2 * mq.params["I(ldens ** 2)"])
print(mq.params.round(3).to_dict(), f"p(quadratic)={mq.pvalues['I(ldens ** 2)']:.4f}")
print(f"Turning point: {np.exp(tp):.1f} inhabitants/km2; share of communes below: {(d19.ldens < tp).mean():.3f}")
d19["bin"] = pd.qcut(d19.ldens, 25, labels=False)
print(d19.groupby("bin").agg(log_density=("ldens", "mean"), log_tap_pc=("ltap_pc", "mean")).round(2).T.to_string())
low = d19[d19.ldens < tp].assign(tpc=lambda x: x.tax_professional_activity / x.pop_total)
print("Highest per-capita TAP below the turning point:")
print(low.nlargest(8, "tpc")[["commune_name", "pop_total", "tpc", "macro_physical_region"]].round(0).to_string(index=False))

# --------------------------------------------------------------------------
# 4. Rank-size: sensitivity to the upper-tail cutoff (Gabaix-Ibragimov)
# --------------------------------------------------------------------------
section("4. RANK-SIZE EXPONENT BY UPPER-TAIL CUTOFF (Gabaix-Ibragimov, rank-1/2)")


def gi(x, n):
    x = np.sort(np.asarray(x, float))[::-1][:n]
    r = np.arange(1, n + 1)
    a = -np.polyfit(np.log(x), np.log(r - 0.5), 1)[0]
    return a, a * np.sqrt(2.0 / n)


print(f"{'N':>6} {'population':>18} {'TAP 2019':>18} {'own rev 2019':>18}")
for n in (50, 100, 200, 300, 500, 750, 1000):
    a1, a2, a3 = gi(G.pop_total.dropna(), n), gi(d19.tax_professional_activity, n), gi(d19.own_revenue, n)
    print(f"{n:>6} {a1[0]:9.3f} ({a1[1]:.3f}) {a2[0]:9.3f} ({a2[1]:.3f}) {a3[0]:9.3f} ({a3[1]:.3f})")

# --------------------------------------------------------------------------
# 5. Concentration, Theil decomposition (both weightings), persistence
# --------------------------------------------------------------------------
section("5. CONCENTRATION AND THEIL DECOMPOSITION")


def top_share(x, n):
    x = np.sort(np.asarray(x, float))[::-1]
    return x[:n].sum() / x.sum()


print(f"Top 10% (154) share: population {top_share(G.pop_total.dropna(), 154):.3f}, "
      f"TAP {top_share(d19.tax_professional_activity, 154):.3f}")


def theil(df, val, grp, wcol=None):
    """Theil T of `val` across units. wcol=None: each commune weighted equally
    (unit shares 1/N); wcol='pop_total': population-weighted (per-capita values)."""
    p = np.ones(len(df)) if wcol is None else df[wcol].values.astype(float)
    y = df[val].values.astype(float)
    Y, N = y.sum(), p.sum()
    T = np.sum((y / Y) * np.log((y / Y) / (p / N)))
    g = pd.DataFrame({"y": y, "p": p, "g": df[grp].values}).groupby("g").sum()
    Tb = np.sum((g.y / Y) * np.log((g.y / Y) / (g.p / N)))
    return T, Tb, 1 - Tb / T


for yr in sorted(PANEL.YEAR.unique()):
    x = PANEL[(PANEL.YEAR == yr) & (PANEL.tax_professional_activity > 0) & PANEL.pop_total.notna()]
    T0, B0, w0 = theil(x, "tax_professional_activity", W)
    T1, B1, w1 = theil(x, "tax_professional_activity", W, "pop_total")
    print(f"{yr}: equal-weight T={T0:.3f} within={w0:.3f} | population-weighted T={T1:.3f} within={w1:.3f}")

section("5b. PERSISTENCE AND DECILE MOBILITY")
for y0, y1 in [(2010, 2019), (2010, 2020)]:
    a = (PANEL[PANEL.YEAR == y0][["rgph2008_commune_id", "tax_professional_activity"]]
         .merge(PANEL[PANEL.YEAR == y1][["rgph2008_commune_id", "tax_professional_activity"]],
                on="rgph2008_commune_id", suffixes=("0", "1")))
    a = a[(a.tax_professional_activity0 > 0) & (a.tax_professional_activity1 > 0)]
    rho = spearmanr(a.tax_professional_activity0, a.tax_professional_activity1)[0]
    t0 = set(a.nlargest(100, "tax_professional_activity0").rgph2008_commune_id)
    t1 = set(a.nlargest(100, "tax_professional_activity1").rgph2008_commune_id)
    a["d0"] = pd.qcut(a.tax_professional_activity0.rank(method="first"), 10, labels=range(1, 11))
    a["d1"] = pd.qcut(a.tax_professional_activity1.rank(method="first"), 10, labels=range(1, 11))
    T = pd.crosstab(a.d0, a.d1, normalize="index")
    print(f"\n{y0}->{y1}: n={len(a)} Spearman={rho:.3f} top-100 overlap={len(t0 & t1)} "
          f"Shorrocks M={(10 - np.trace(T.values)) / 9:.3f}")
    print("Decile transition matrix (rows: origin decile):")
    print(T.round(2).to_string())

# --------------------------------------------------------------------------
# 6. Independent validation: VIIRS 2019 night lights
# --------------------------------------------------------------------------
section("6. VALIDATION AGAINST VIIRS 2019 NIGHT LIGHTS (flare-masked)")
NL = pd.read_csv(os.path.join(D, "commune_nightlights_2019.csv"), dtype={"rgph2008_commune_id": str})
v = d19.merge(NL[["rgph2008_commune_id", "viirs2019_sum_radiance_flaremasked", "vnf2019_flare_sites"]],
              on="rgph2008_commune_id", how="left")
v = v[v.viirs2019_sum_radiance_flaremasked > 0].copy()
v["lntl"] = np.log(v.viirs2019_sum_radiance_flaremasked)
v["lnpc"] = v.lntl - v.lpop
print(f"N={len(v)}  corr(log TAP, log lights)={np.corrcoef(v.ltap, v.lntl)[0, 1]:.3f}  "
      f"corr(log pop, log lights)={np.corrcoef(v.lpop, v.lntl)[0, 1]:.3f}  "
      f"corr per capita={np.corrcoef(v.ltap_pc, v.lnpc)[0, 1]:.3f}")
samples = {"All": v, "No flare sites": v[v.vnf2019_flare_sites == 0],
           "No Saharan belt": v[v.macro_physical_region != "Saharan belt"]}
for lab, s in samples.items():
    for f in ["ltap ~ lntl", "ltap ~ lntl + lpop", "ltap ~ lntl + lpop + C(wilaya_code)",
              "ltap_pc ~ lnpc + C(wilaya_code)"]:
        m = cl(f, s)
        k = [x for x in ["lntl", "lpop", "lnpc"] if x in m.params]
        print(f"{lab:16s} N={len(s):4d} {f:38s}", "  ".join(f"{x}={m.params[x]:.3f}({m.bse[x]:.3f})" for x in k),
              f"R2={m.rsquared:.3f}")
print(f"Top 10% share: lights {top_share(v.viirs2019_sum_radiance_flaremasked, 154):.3f}, "
      f"TAP {top_share(v.tax_professional_activity, 154):.3f}, population {top_share(v.pop_total, 154):.3f}")
print(f"Theil within-province share (equal weights): lights "
      f"{theil(v, 'viirs2019_sum_radiance_flaremasked', W)[2]:.3f}, TAP {theil(v, 'tax_professional_activity', W)[2]:.3f}")

# Census 2008 count of dwellings used for professional purposes (second independent indicator)
c = PANEL[(PANEL.YEAR == 2010) & (PANEL.tax_professional_activity > 0) & (PANEL.log_professional > 0)].copy()
c["ltap"], c["lprof"], c["lpop"] = np.log(c.tax_professional_activity), np.log(c.log_professional), np.log(c.pop_total)
m = cl("ltap ~ lprof + lpop + C(wilaya_code)", c)
print(f"\nCensus professional premises (2008) vs TAP (2010): N={len(c)} "
      f"corr={np.corrcoef(c.ltap, c.lprof)[0, 1]:.3f}; conditional coef={m.params['lprof']:.3f} ({m.bse['lprof']:.3f})")
print("\nDone.")
