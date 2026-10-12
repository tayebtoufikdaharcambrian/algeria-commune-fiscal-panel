"""
make_figures.py
===============
Produces the five figures of the paper in figures/:
  Figure1_validation.png, Figure2_ranksize.png, Figure3_gradient.png,
  Figure4_density.png, Figure5_theil.png
Run:  python code/make_figures.py      Requires: pandas numpy statsmodels matplotlib
"""
import os
import numpy as np, pandas as pd, statsmodels.formula.api as smf, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
_here = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'revision_analysis.py')
_src = open(_here).read().split('# 1. Sample accounting')[0]
__file__ = _here
exec(_src)
ROOT = os.path.dirname(os.path.dirname(_here))
NL = pd.read_csv(os.path.join(D, 'commune_nightlights_2019.csv'), dtype={'rgph2008_commune_id': str})
d = d19.merge(NL[['rgph2008_commune_id', 'viirs2019_sum_radiance_flaremasked', 'vnf2019_flare_sites']], on='rgph2008_commune_id')

OUT=os.path.join(ROOT,'figures','')
BLUE,ORANGE,AQUA='#2a78d6','#eb6834','#1baf7a'; INK='#222222'; MUTED='#6b6b6b'; GRID='#e6e6e6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':'#888','axes.linewidth':0.6,
 'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,'axes.spines.top':False,'axes.spines.right':False,
 'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.5,'legend.frameon':False,'savefig.dpi':300})
L=d.viirs2019_sum_radiance_flaremasked
series=[('Population (2008)',d.pop_total.values,BLUE,'-'),('Night lights (2019)',L.values,AQUA,'--'),('TAP receipts (2019)',d.tax_professional_activity.values,ORANGE,'-')]
def gi(x,n):
    x=np.sort(np.asarray(x,float))[::-1][:n]; r=np.arange(1,n+1); a=-np.polyfit(np.log(x),np.log(r-0.5),1)[0]; return a,a*np.sqrt(2/n)
# ---- Figure 1
fig,ax=plt.subplots(1,2,figsize=(7.2,3.2))
for lab,x,c,ls in series:
    x=np.sort(x[x>0])[::-1]; ax[0].plot(np.log(x/x[0]),np.log(np.arange(1,len(x)+1)),color=c,ls=ls,lw=1.6,label=lab)
ax[0].set_xlabel('log(size / largest commune)'); ax[0].set_ylabel('log rank'); ax[0].set_title('(a) Rank–size plots',loc='left',fontsize=9,color=INK)
ax[0].legend(loc='lower left',fontsize=8); ax[0].set_xlim(-8.5,0.3)
Ns=np.array([50,100,150,200,300,400,500,750,1000])
for lab,x,c,ls in series:
    est=np.array([gi(x[x>0],n) for n in Ns]); ax[1].plot(Ns,est[:,0],color=c,ls=ls,lw=1.6,marker='o',ms=3.5,label=lab)
    ax[1].fill_between(Ns,est[:,0]-1.96*est[:,1],est[:,0]+1.96*est[:,1],color=c,alpha=0.12,lw=0)
ax[1].axhline(1,color=MUTED,lw=0.8,ls=':'); ax[1].text(1010,1.02,'Zipf (α = 1)',color=MUTED,fontsize=7.5,ha='right',va='bottom')
ax[1].set_xlabel('Number of largest communes in the fit (N)'); ax[1].set_ylabel('Estimated exponent α'); ax[1].set_title('(b) Exponent by tail cutoff',loc='left',fontsize=9,color=INK)
fig.tight_layout(); fig.savefig(OUT+'Figure2_ranksize.png'); plt.close()
# ---- Figure 2
v=d[L>0].copy(); v['lntl']=np.log(v.viirs2019_sum_radiance_flaremasked)
ry=smf.ols('ltap ~ lpop + C(wilaya_code)',v).fit().resid; rx=smf.ols('lntl ~ lpop + C(wilaya_code)',v).fit().resid
fig,ax=plt.subplots(1,2,figsize=(7.2,3.2))
ax[0].scatter(rx,ry,s=5,color='#bdbdbd',lw=0,alpha=0.7)
b=pd.DataFrame({'x':rx,'y':ry}); b['q']=pd.qcut(b.x,25,labels=False); bm=b.groupby('q').mean()
ax[0].scatter(bm.x,bm.y,s=22,color=ORANGE,edgecolor='white',lw=0.8,zorder=3)
k=np.polyfit(rx,ry,1); xx=np.linspace(rx.min(),rx.max(),10); ax[0].plot(xx,np.polyval(k,xx),color=INK,lw=1)
ax[0].text(0.03,0.96,f'slope = {k[0]:.2f}',transform=ax[0].transAxes,va='top',fontsize=8,color=INK)
ax[0].set_xlabel('log night lights (residual)'); ax[0].set_ylabel('log TAP receipts (residual)')
ax[0].set_title('(a) TAP vs lights, net of population\n     and province effects',loc='left',fontsize=9,color=INK)
for lab,x,c,ls in series:
    x=np.sort(x); cum=np.concatenate([[0],np.cumsum(x)/x.sum()]); p=np.linspace(0,1,len(cum))
    ax[1].plot(p,cum,color=c,ls=ls,lw=1.6,label=lab)
ax[1].plot([0,1],[0,1],color=MUTED,lw=0.7,ls=':')
ax[1].set_xlabel('Cumulative share of communes'); ax[1].set_ylabel('Cumulative share of total'); ax[1].legend(loc='upper left',fontsize=8)
ax[1].set_title('(b) Lorenz curves, 2019',loc='left',fontsize=9,color=INK)
fig.tight_layout(); fig.savefig(OUT+'Figure1_validation.png'); plt.close()
# ---- Figure 3 gradient decomposition
g=d19.copy(); g['bin']=(g.distance_to_coast_km//50).clip(upper=20)*50
bm=g.groupby('bin')[['ltap_area','ldens','ltap_pc']].mean(); bm=bm-bm.iloc[0]
fig,ax=plt.subplots(figsize=(5.2,3.3))
for col,lab,c,ls in [('ltap_area','TAP per km² (activity density)',ORANGE,'-'),('ldens','Population per km²',BLUE,'-'),('ltap_pc','TAP per inhabitant',INK,'--')]:
    ax.plot(bm.index+25,bm[col],color=c,ls=ls,lw=1.6,marker='o',ms=3.5,label=lab)
ax.axhline(0,color=MUTED,lw=0.7)
ax.set_xlabel('Distance from the coast (km), 50-km bins'); ax.set_ylabel('Mean log value, relative to 0–50 km bin')
ax.legend(loc='lower left',fontsize=8); fig.tight_layout(); fig.savefig(OUT+'Figure3_gradient.png'); plt.close()
# ---- Figure 4 U-shape
fig,ax=plt.subplots(figsize=(5.2,3.4))
ax.scatter(d19.ldens,d19.ltap_pc,s=5,color='#c8c8c8',lw=0)
d19['q']=pd.qcut(d19.ldens,25,labels=False); bm=d19.groupby('q')[['ldens','ltap_pc']].mean()
ax.scatter(bm.ldens,bm.ltap_pc,s=24,color=ORANGE,edgecolor='white',lw=0.8,zorder=3,label='25 quantile-bin means')
m=smf.ols('ltap_pc ~ ldens + I(ldens**2)',d19).fit(); xx=np.linspace(d19.ldens.min(),d19.ldens.max(),100)
ax.plot(xx,m.params['Intercept']+m.params['ldens']*xx+m.params['I(ldens ** 2)']*xx**2,color=INK,lw=1.1,label='Quadratic fit')
for nm,off in [('HASSI MESSAOUD',(8,6)),('IN AMENAS',(8,-6)),('EL BORMA',(8,0)),("HASSI R'MEL",(8,0))]:
    r=d19[d19.commune_name==nm].iloc[0]; ax.annotate(nm.title(),(r.ldens,r.ltap_pc),xytext=off,textcoords='offset points',fontsize=7,color=MUTED,va='center')
ax.set_xlabel('log population density, 2008 (inhabitants per km²)'); ax.set_ylabel('log TAP receipts per inhabitant, 2019'); ax.legend(loc='lower right',fontsize=8)
fig.tight_layout(); fig.savefig(OUT+'Figure4_density.png'); plt.close()
# ---- Figure 5 Theil
def theil(df,val,grp,wcol=None):
    p=np.ones(len(df)) if wcol is None else df[wcol].values.astype(float); y=df[val].values.astype(float); Y,N=y.sum(),p.sum()
    T=np.sum((y/Y)*np.log((y/Y)/(p/N))); gg=pd.DataFrame({'y':y,'p':p,'g':df[grp].values}).groupby('g').sum(); Tb=np.sum((gg.y/Y)*np.log((gg.y/Y)/(gg.p/N))); return 1-Tb/T
yrs=sorted(PANEL.YEAR.unique()); e=[];w=[]
for yr in yrs:
    x=PANEL[(PANEL.YEAR==yr)&(PANEL.tax_professional_activity>0)&PANEL.pop_total.notna()]
    e.append(theil(x,'tax_professional_activity','wilaya_code')); w.append(theil(x,'tax_professional_activity','wilaya_code','pop_total'))
fig,ax=plt.subplots(figsize=(5.2,3.0))
ax.plot(yrs,np.array(e)*100,color=ORANGE,lw=1.6,marker='o',ms=4,label='TAP, communes weighted equally')
ax.plot(yrs,np.array(w)*100,color=ORANGE,lw=1.6,ls='--',marker='s',ms=3.5,label='TAP, population-weighted')
lw_=theil(v,'viirs2019_sum_radiance_flaremasked','wilaya_code')
ax.scatter([2019],[lw_*100],color=AQUA,marker='D',s=36,zorder=4,edgecolor='white',label='Night lights 2019, equal weights')
lwp=theil(v,'viirs2019_sum_radiance_flaremasked','wilaya_code','pop_total')
ax.scatter([2019],[lwp*100],color='white',marker='D',s=36,zorder=4,edgecolor=AQUA,linewidth=1.4,label='Night lights 2019, population-weighted')
ax.set_ylim(40,80); ax.legend(loc='lower left',fontsize=7.5); ax.set_ylabel('Within-province share of Theil T (%)'); ax.set_xticks(yrs); ax.legend(loc='lower left',fontsize=8)
fig.tight_layout(); fig.savefig(OUT+'Figure5_theil.png'); plt.close()
print('ok', [round(x,3) for x in e], [round(x,3) for x in w], round(lw_,3), 'slope',k[0])
