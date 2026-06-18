"""
analysis.py
===========
Reproduces every figure, table, and statistic reported in:

  Dahar, T. T. (2025). Uniform Law, Unequal Capacity: Fiscal Heteronomy and
  the Limits of Regional Decentralisation in Algeria's Communes, 2010-2020.
  Public Administration and Development. [under review]

Inputs (both in ../data/processed/):
  - algeria_commune_fiscal_panel_2010_2020.csv
  - rgph2008_communes_master_1541_geo_physical_enriched.csv

Outputs (written to ../figures/):
  - fig_theil.png             Figure 2: Theil decomposition 2010-2020
  - fig_autonomy_dist.png     Figure 1: Distribution of autonomy ratios 2019
  - fig_lorenz.png            Figure 2: Lorenz curve of own revenue 2019
  - fig_autonomy_morph.png    Figure 3: Autonomy by settlement morphology 2019
  - fig_regression.png        Figure 4: Regression coefficient plot

Console output includes all numbers cited in the text, clearly labelled.

Requirements:
  Python >= 3.9
  pandas, numpy, matplotlib, statsmodels, scipy
  Install: pip install pandas numpy matplotlib statsmodels scipy

Author: Tayeb Toufik Dahar
Repository: https://github.com/[author-handle]/algeria-commune-fiscal-panel
License: CC BY 4.0
"""

import os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

# ── paths ──────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data', 'processed')
FIGS = os.path.join(BASE, 'figures')
os.makedirs(FIGS, exist_ok=True)

# ── colour palette (consistent with published figures) ─────────────────────
PRIMARY = '#1F4E79'
ACCENT1 = '#C00000'
ACCENT2 = '#548235'
HP      = '#E8A33D'
TELL    = '#2E75B6'
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.edgecolor': '#444',
    'axes.linewidth': 0.8,
})


# ══════════════════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ══════════════════════════════════════════════════════════════════════════
print("=" * 65)
print("Loading data...")
fiscal = pd.read_csv(
    os.path.join(DATA, 'algeria_commune_fiscal_panel_2010_2020.csv'),
    low_memory=False
)
geo = pd.read_csv(
    os.path.join(DATA, 'rgph2008_communes_master_1541_geo_physical_enriched.csv'),
    low_memory=False
)
print(f"  Fiscal panel: {fiscal.shape[0]:,} rows × {fiscal.shape[1]} cols")
print(f"  Geo master:   {geo.shape[0]:,} rows × {geo.shape[1]} cols")
print(f"  Years in panel: {sorted(fiscal['YEAR'].unique())}")


# ══════════════════════════════════════════════════════════════════════════
# 2. HELPERS
# ══════════════════════════════════════════════════════════════════════════
def gini(x):
    """Gini coefficient of array x (all values >= 0)."""
    x = np.sort(np.asarray(x, float))
    n = len(x)
    if x.sum() == 0:
        return np.nan
    return (2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n


def theil_T_decompose(df, value_col, group_col):
    """
    Decompose Theil T index of `value_col` into within- and between-`group_col`
    components. Returns (T_total, T_within, T_between).
    Only positive values are used.
    """
    d = df[df[value_col] > 0].copy()
    x = d[value_col].values
    N = len(x)
    mu = x.mean()
    T_total = (1 / N) * np.sum((x / mu) * np.log(x / mu))
    T_between = 0.0
    T_within  = 0.0
    for _, gd in d.groupby(group_col):
        xg  = gd[value_col].values
        ng  = len(xg)
        mug = xg.mean()
        s   = ng / N
        if mug > 0:
            T_between += s * (mug / mu) * np.log(mug / mu)
            Tg = (1 / ng) * np.sum((xg / mug) * np.log(xg / mug))
            T_within  += s * (mug / mu) * Tg
    return T_total, T_within, T_between


# ══════════════════════════════════════════════════════════════════════════
# 3. SECTION 5.1 — MORPHOLOGICAL HETEROGENEITY (Table 1 numbers)
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("SECTION 5.1 — MORPHOLOGICAL HETEROGENEITY")
print("=" * 65)

pop_col  = 'pop_total'
area_col = 'commune_area_sqkm'
dens_col = 'population_density_2008_per_sqkm'

print(f"  N communes in geo master: {len(geo):,}")
print(f"  Total population (RGPH 2008): {geo[pop_col].sum():,.0f}")
print(f"  Total area (km²): {geo[area_col].sum():,.0f}")
print(f"  Gini — commune area:       {gini(geo[area_col].dropna()):.3f}")
print(f"  Gini — population density: {gini(geo[dens_col].dropna()):.3f}")
print(f"  Gini — commune population: {gini(geo[pop_col].dropna()):.3f}")

area_sorted = geo[area_col].dropna().sort_values()
ratio = area_sorted.iloc[-1] / area_sorted.iloc[0]
print(f"  Largest/smallest area ratio: {ratio:,.0f} : 1")

# Top-decile area share
top10 = geo.nlargest(int(0.1 * len(geo)), area_col)
print(f"  Top 10% communes: {len(top10)} units")
print(f"    Share of national area:  {top10[area_col].sum() / geo[area_col].sum() * 100:.1f}%")
print(f"    Share of population:     {top10[pop_col].sum() / geo[pop_col].sum() * 100:.1f}%")

# Coastal corridor
coast50 = geo[geo['near_coast_50km'] == 1]
print(f"  Coastal corridor (≤50 km):")
print(f"    % of area:        {coast50[area_col].sum() / geo[area_col].sum() * 100:.1f}%")
print(f"    % of population:  {coast50[pop_col].sum() / geo[pop_col].sum() * 100:.1f}%")


# ══════════════════════════════════════════════════════════════════════════
# 4. SECTION 5.2 — AUTONOMY DEFICIT AND CONCENTRATION (Table 1 fiscal rows)
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("SECTION 5.2 — AUTONOMY DEFICIT AND CONCENTRATION (2019)")
print("=" * 65)

d19 = fiscal[fiscal['YEAR'] == 2019].copy()
print(f"  N communes in 2019 file: {len(d19):,}")
print(f"  Median fiscal autonomy ratio: {d19['autonomy_ratio'].median() * 100:.1f}%")
print(f"  Mean fiscal autonomy ratio:   {d19['autonomy_ratio'].mean() * 100:.1f}%")
print(f"  Communes < 25% autonomy: {(d19['autonomy_ratio'] < 0.25).sum():,} "
      f"({(d19['autonomy_ratio'] < 0.25).mean() * 100:.1f}%)")
print(f"  Communes < 50% autonomy: {(d19['autonomy_ratio'] < 0.50).sum():,} "
      f"({(d19['autonomy_ratio'] < 0.50).mean() * 100:.1f}%)")

g_own = gini(d19['own_revenue'].values)
print(f"  Gini of own revenue (2019): {g_own:.3f}")
d19_sorted = d19.sort_values('own_revenue', ascending=False)
n10 = int(0.1  * len(d19_sorted))
n01 = max(1, int(0.01 * len(d19_sorted)))
n50 = int(0.5  * len(d19_sorted))
tot = d19_sorted['own_revenue'].sum()
print(f"  Top 10% communes ({n10}): {d19_sorted.head(n10)['own_revenue'].sum() / tot * 100:.1f}% of own revenue")
print(f"  Top  1% communes ({n01}): {d19_sorted.head(n01)['own_revenue'].sum() / tot * 100:.1f}% of own revenue")
print(f"  Bottom 50% communes:       {d19_sorted.tail(n50)['own_revenue'].sum() / tot * 100:.1f}% of own revenue")

# Transfer dependency over time
print("\n  Transfer-dependency counts (transfers >= own revenue):")
for y in sorted(fiscal['YEAR'].unique()):
    sub = fiscal[fiscal['YEAR'] == y]
    dep = (sub['transfer_total'] >= sub['own_revenue']).sum()
    print(f"    {y}: {dep:,} / {len(sub):,} ({dep / len(sub) * 100:.1f}%)")

# Own-revenue composition 2019
print("\n  Own-revenue composition 2019 (% of total own revenue):")
own_cols = ['tax_professional_activity','property_tax','vat_share',
            'operating_receipts','domain_receipts','slaughter_tax',
            'single_flat_rate_tax','income_tax_share']
own_cols_present = [c for c in own_cols if c in d19.columns]
total_own = d19[own_cols_present].sum().sum()
for c in own_cols_present:
    pct = d19[c].sum() / total_own * 100
    print(f"    {c}: {pct:.1f}%")


# ══════════════════════════════════════════════════════════════════════════
# 5. SECTION 5.3 — THEIL DECOMPOSITION (Figure 2)
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("SECTION 5.3 — THEIL DECOMPOSITION 2010-2020")
print("=" * 65)
print(f"  {'Year':<6} {'Theil T':>9} {'Within':>9} {'Between':>9} {'Within%':>9}")
years_available = sorted(fiscal['YEAR'].unique())
theil_results = {}
for y in years_available:
    sub = fiscal[fiscal['YEAR'] == y]
    Tt, Tw, Tb = theil_T_decompose(sub, 'own_revenue', 'wilaya_code')
    theil_results[y] = (Tt, Tw, Tb)
    print(f"  {y:<6} {Tt:>9.4f} {Tw:>9.4f} {Tb:>9.4f} {Tw/Tt*100:>8.1f}%")
within_pcts = [v[1] / v[0] * 100 for v in theil_results.values()]
print(f"\n  Within-wilaya share — mean: {np.mean(within_pcts):.1f}%, "
      f"min: {min(within_pcts):.1f}%, max: {max(within_pcts):.1f}%")

# Per-capita decomposition check
print("\n  Per-capita Theil decomposition:")
for y in years_available:
    sub = fiscal[(fiscal['YEAR'] == y) & (fiscal['population_rgph2008'] > 0)].copy()
    sub['own_pc'] = sub['own_revenue'] / sub['population_rgph2008']
    Tt, Tw, Tb = theil_T_decompose(sub, 'own_pc', 'wilaya_code')
    print(f"  {y}: within {Tw/Tt*100:.1f}%,  between {Tb/Tt*100:.1f}%")
    
# Scale-invariance verification
sub19 = fiscal[fiscal['YEAR'] == 2019]
T1, _, _ = theil_T_decompose(sub19, 'own_revenue', 'wilaya_code')
sub19c = sub19.copy(); sub19c['own_rev_deflated'] = sub19c['own_revenue'] * 1.35
T2, _, _ = theil_T_decompose(sub19c, 'own_rev_deflated', 'wilaya_code')
print(f"\n  Scale-invariance check: Theil(nominal) = {T1:.6f}, "
      f"Theil(×1.35 deflator) = {T2:.6f}  → {'IDENTICAL ✓' if abs(T1-T2)<1e-9 else 'DIFFERS'}")

# FIGURE 2: Theil decomposition line chart
print("\n  Generating Figure 2: Theil decomposition...")
fig, ax = plt.subplots(figsize=(8, 4.2))
W = [theil_results[y][1] / theil_results[y][0] * 100 for y in years_available]
B = [100 - w for w in W]
ax.plot(years_available, W, marker='o', color=PRIMARY, lw=2.2, markersize=6,
        label='Within-wilaya share')
ax.plot(years_available, B, marker='s', color=HP, lw=2.2, markersize=6,
        label='Between-wilaya share')
ax.axhline(50, color='#888', ls='--', lw=1)
ax.fill_between(years_available, W, B, color=PRIMARY, alpha=0.05)
for x, yv in zip(years_available, W):
    ax.annotate(f'{yv:.0f}%', (x, yv), textcoords='offset points',
                xytext=(0, 9), ha='center', fontsize=8.5, color=PRIMARY, fontweight='bold')
ax.set_ylabel('Share of total Theil T inequality (%)')
ax.set_xlabel('Year')
ax.set_ylim(20, 80)
ax.set_xticks(years_available)
ax.set_xticklabels(years_available, rotation=45)
ax.legend(frameon=False, loc='center right')
ax.set_title(
    'Where is communal fiscal inequality generated?\n'
    'Theil decomposition of own revenue, 1,541 communes',
    fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGS, 'fig_theil.png'), dpi=200, bbox_inches='tight')
plt.close()
print("  → Saved fig_theil.png")


# ══════════════════════════════════════════════════════════════════════════
# 6. FIGURE 1 — DISTRIBUTION OF AUTONOMY RATIOS 2019
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("FIGURE 1 — AUTONOMY DISTRIBUTION 2019")
vals = d19['autonomy_ratio'].dropna() * 100
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(vals, bins=40, color=TELL, edgecolor='white', alpha=0.9)
med = vals.median()
ax.axvline(med, color=ACCENT1, lw=2, ls='--', label=f'Median = {med:.1f}%')
ax.axvline(50, color='#444', lw=1, ls=':', label='50% self-financing threshold')
ax.set_xlabel('Fiscal autonomy ratio (%)')
ax.set_ylabel('Number of communes')
ax.legend(frameon=False)
ax.set_title(
    'Distribution of commune fiscal autonomy ratios, 2019\n(n = 1,541 communes)',
    fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGS, 'fig_autonomy_dist.png'), dpi=200, bbox_inches='tight')
plt.close()
print("  → Saved fig_autonomy_dist.png")


# ══════════════════════════════════════════════════════════════════════════
# 7. FIGURE 2b — LORENZ CURVE 2019
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("FIGURE 2 — LORENZ CURVE 2019")
x = np.sort(d19['own_revenue'].values)
cum = np.cumsum(x) / x.sum()
p = np.arange(1, len(x) + 1) / len(x)
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot([0, 1], [0, 1], color='#888', ls='--', lw=1, label='Perfect equality')
ax.plot(np.concatenate([[0], p]), np.concatenate([[0], cum]),
        color=PRIMARY, lw=2.2, label='Own fiscal revenue')
ax.fill_between(np.concatenate([[0], p]),
                np.concatenate([[0], cum]),
                np.concatenate([[0], p]),
                color=PRIMARY, alpha=0.12)
g = gini(d19['own_revenue'].values)
ax.text(0.05, 0.82, f'Gini = {g:.3f}', fontsize=11, fontweight='bold', color=PRIMARY)
ax.set_xlabel('Cumulative share of communes')
ax.set_ylabel('Cumulative share of own fiscal revenue')
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.legend(loc='upper left', frameon=False)
ax.set_title(
    'Concentration of own fiscal revenue across\n1,541 Algerian communes, 2019',
    fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGS, 'fig_lorenz.png'), dpi=200, bbox_inches='tight')
plt.close()
print(f"  Gini = {g:.3f}")
print("  → Saved fig_lorenz.png")


# ══════════════════════════════════════════════════════════════════════════
# 8. SECTION 5.4 — MORPHOLOGY GRADIENT (Figure 3, Table 2)
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("SECTION 5.4 — MORPHOLOGY GRADIENT (2019)")
print("=" * 65)

# Merge fiscal 2019 with geo
geo['wilaya_code'] = geo['rgph2008_commune_id'].str[:2].astype(int)
geo['commune_seq']  = geo['rgph2008_commune_id'].str[3:].astype(int)

# Ensure matching dtypes in fiscal file
d19['wilaya_code'] = d19['wilaya_code'].astype(int)
d19['commune_seq'] = d19['commune_seq'].astype(int)

merge = d19.merge(
    geo[['wilaya_code', 'commune_seq', 'settlement_character_2008',
         'macro_physical_region', 'population_density_2008_per_sqkm',
         'distance_to_coast_km', 'commune_area_sqkm', 'pop_total',
         'near_coast_50km']],
    on=['wilaya_code', 'commune_seq'],
    how='inner'
)
print(f"  Matched: {len(merge):,} / {len(d19):,} communes")

morph_order = [
    'Predominantly dispersed/rural (ZE >= 50%)',
    'Mixed, low-density / rural-influenced',
    'Mixed, urban-influenced',
    'Predominantly agglomerated (ACL+AS >= 75%)',
    'Predominantly urban core (ACL >= 75%)',
]
morph_labels = ['Dispersed/rural', 'Mixed low-density', 'Mixed urban-infl.',
                'Agglomerated', 'Urban core']
print("\n  Table 2 — Median fiscal autonomy by settlement morphology:")
medians = []
for o, l in zip(morph_order, morph_labels):
    sub = merge[merge['settlement_character_2008'] == o]
    med = sub['autonomy_ratio'].median() * 100
    medians.append(med)
    print(f"    {l:<25}: {med:.1f}%  (n={len(sub):,})")
print(f"\n  Urban-core / dispersed-rural ratio: {medians[-1] / medians[0]:.1f}×")

# Spearman correlation
sp = stats.spearmanr(
    merge['autonomy_ratio'].dropna(),
    np.log(merge.loc[merge['autonomy_ratio'].notna(), 'population_density_2008_per_sqkm'] + 1)
)
print(f"  Spearman corr(autonomy, log density): r = {sp.statistic:.3f}, p = {sp.pvalue:.4f}")

# FIGURE 3: morphology bar chart
fig, ax = plt.subplots(figsize=(8, 3.8))
colors = [ACCENT2, '#5B9279', HP, '#B07A22', ACCENT1]
bars = ax.barh(morph_labels, medians, color=colors, height=0.6)
for b, v in zip(bars, medians):
    ax.text(v + 0.35, b.get_y() + b.get_height() / 2,
            f'{v:.1f}%', va='center', fontsize=9, fontweight='bold')
ax.set_xlabel('Median fiscal autonomy ratio, 2019 (%)')
ax.set_xlim(0, 26)
ax.invert_yaxis()
ax.set_title(
    'Same law, different capacity: median fiscal autonomy\nby settlement morphology, 2019',
    fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGS, 'fig_autonomy_morph.png'), dpi=200, bbox_inches='tight')
plt.close()
print("  → Saved fig_autonomy_morph.png")


# ══════════════════════════════════════════════════════════════════════════
# 9. SECTION 5.6 — REGRESSION MODELS (Table 3, Figure 4)
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("SECTION 5.6 — REGRESSION MODELS (Table 3)")
print("=" * 65)

reg = merge[merge['autonomy_ratio'].notna()].copy()
reg = reg[(reg['population_density_2008_per_sqkm'] > 0) &
          (reg['pop_total'] > 0) &
          (reg['commune_area_sqkm'] > 0)]
reg['aut_pct']         = reg['autonomy_ratio'] * 100
reg['log_density']     = np.log(reg['population_density_2008_per_sqkm'])
reg['log_pop']         = np.log(reg['pop_total'])
reg['coast_dist_100km'] = reg['distance_to_coast_km'] / 100
reg['region'] = reg['macro_physical_region'].map({
    'Tell / northern coastal-mountain belt': 'Tell',
    'High Plateaus / steppe belt': 'High Plateaus',
    'Saharan belt': 'Sahara',
})
print(f"  Regression N = {len(reg):,}")

m1 = smf.ols('aut_pct ~ log_density', data=reg).fit(cov_type='HC1')
m2 = smf.ols('aut_pct ~ log_density + log_pop + coast_dist_100km', data=reg).fit(cov_type='HC1')
m3 = smf.ols('aut_pct ~ log_density + log_pop + coast_dist_100km + C(region)', data=reg).fit(cov_type='HC1')
m4 = smf.ols('aut_pct ~ log_density + log_pop + coast_dist_100km + C(wilaya_code)', data=reg).fit(cov_type='HC1')

def stars(p):
    return '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.10 else ''

for name, m in [('M1', m1), ('M2', m2), ('M3', m3), ('M4 (Wilaya FE)', m4)]:
    print(f"\n  {name}: N={int(m.nobs)}, R²={m.rsquared:.3f}, adj.R²={m.rsquared_adj:.3f}")
    for v in ['log_density', 'log_pop', 'coast_dist_100km']:
        if v in m.params.index:
            p = m.pvalues[v]
            print(f"    {v}: b={m.params[v]:.3f} (SE={m.bse[v]:.3f}) {stars(p)}")
    for k in m.params.index:
        if 'region' in k.lower():
            p = m.pvalues[k]
            label = k.replace('C(region)[T.', '').rstrip(']')
            print(f"    {label}: b={m.params[k]:.3f} (SE={m.bse[k]:.3f}) {stars(p)}")

# FIGURE 4: coefficient plot from M4
fig, ax = plt.subplots(figsize=(8, 3.4))
labels_r = ['Log population', 'Log density', 'Coastal distance\n(per 100 km)']
vars_r   = ['log_pop', 'log_density', 'coast_dist_100km']
b_vals   = [m4.params[v] for v in vars_r]
se_vals  = [m4.bse[v] for v in vars_r]
ci_vals  = [1.96 * s for s in se_vals]
y = np.arange(len(labels_r))
ax.errorbar(b_vals, y, xerr=ci_vals, fmt='o', color=PRIMARY,
            ecolor='#888', capsize=4, markersize=7, lw=1.5)
for i, (bb, _) in enumerate(zip(b_vals, ci_vals)):
    ax.annotate(f'{bb:+.2f}', (bb, y[i]),
                textcoords='offset points', xytext=(0, 10),
                ha='center', fontsize=9, fontweight='bold', color=PRIMARY)
ax.axvline(0, color='#444', lw=1, ls='--')
ax.set_yticks(y); ax.set_yticklabels(labels_r)
ax.invert_yaxis()
ax.set_xlabel(
    'Marginal effect on fiscal autonomy (pp), Model 4 with wilaya fixed effects')
ax.set_title(
    'Predictors of commune fiscal autonomy, within wilayas (2019)\n'
    'OLS with wilaya fixed effects, 95% confidence intervals (HC1)',
    fontsize=10.5, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGS, 'fig_regression.png'), dpi=200, bbox_inches='tight')
plt.close()
print("\n  → Saved fig_regression.png")


# ══════════════════════════════════════════════════════════════════════════
# 10. APPENDIX DATA-QUALITY CHECKS
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("APPENDIX — DATA QUALITY CHECKS")
print("=" * 65)

# Matched vs unmatched
geo['comm_key'] = geo['wilaya_code'].astype(str).str.zfill(2) + geo['commune_seq'].astype(str).str.zfill(4)
fis19_keys = set(d19['wilaya_code'].astype(str).str.zfill(2) + d19['commune_seq'].astype(str).str.zfill(4))
geo['matched'] = geo['comm_key'].isin(fis19_keys)
unmatched = geo[~geo['matched']]
matched_g  = geo[geo['matched']]
print(f"  Unmatched communes: {len(unmatched)} / {len(geo)}")
print(f"  Unmatched by region: {unmatched['macro_physical_region'].value_counts().to_dict()}")
print("\n  Matched vs full sample comparison:")
for col, label in [(pop_col, 'Pop. median'), (area_col, 'Area median (km²)'),
                   (dens_col, 'Density median'), ('distance_to_coast_km', 'Coastal dist. median')]:
    if col in geo.columns:
        print(f"    {label}: full={geo[col].median():.1f}, matched={matched_g[col].median():.1f}")

print("\n" + "=" * 65)
print("ALL COMPUTATIONS COMPLETE")
print("Figures saved to:", FIGS)
print("=" * 65)
