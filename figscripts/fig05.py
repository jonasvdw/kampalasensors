#!/data/leuven/320/vsc32093/miniconda3/envs/science/bin/python

#IMPORTS
import sys
import numpy as np
from PIL import Image
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.ndimage import gaussian_filter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.basemap import Basemap
import settings

VFfile='/scratch/leuven/320/vsc32093/projects/iButtons/explainingvars/NDVI_MODIS_006_MYD13Q1_01082018-01052019.nc'
GMISfile='/scratch/leuven/320/vsc32093/projects/iButtons/explainingvars/36N_gmis_impervious_surface_percentage_utm_30m.tif'
figsavefile='/scratch/leuven/320/vsc32093/projects/iButtons/figs/fig05.png'
plotKb=True # plot Kampala boundaries if GMIS file is available

def HI_from_VF(VF,mmm):
    if mmm=='min':
        return 29.25-7.95*VF
    elif mmm=='mean':
        return 34.58-8.17*VF
    elif mmm=='max':
        return 44.17-13.19*VF
    else:
        print('choose min/mean/max')
        sys.exit()

def removelakebounds(x):
    x[x<1000]=np.nan
    neigh=np.copy(x); neigh=neigh/neigh
    for i in range(10):
        neigh=np.roll(neigh,1,axis=0)*np.roll(neigh,-1,axis=0)*np.roll(neigh,1,axis=1)*np.roll(neigh,-1,axis=1)
    x[np.isnan(neigh)]=np.nan
    return x

#LOAD DATA
def load_vf(f,smoother=0):
    with xr.open_dataset(f) as ds:
        var=ds.get('Band1')
        lons=var.lon ; lats=var.lat
    LON,LAT=np.meshgrid(lons,lats)
    ima=removelakebounds(np.array(var))
    ima=(ima-np.nanmin(ima))/(np.nanmax(ima)-np.nanmin(ima))
    ima=gaussian_filter(ima,sigma=smoother)
    return LON,LAT,ima

def plot_variables(LON,LAT,imarray):
    Nrows,Ncols=(1,3)
    fig = plt.figure(figsize=(15,4))
    gs = gridspec.GridSpec(Nrows,Ncols,wspace=0.2,hspace=0.15)
    ax=np.empty(gs.get_geometry(),dtype=object)
    #Kampala boundaries for each plot:
    if plotKb:
        lon1=32.32864
        lon2=32.84385
        lat1=0.0001361111
        lat2=0.5603056
        dlon=1911
        dlat =2064
        lons=np.linspace(lon1,lon2,dlon,endpoint=True)
        lats=np.linspace(lat1,lat2,dlat,endpoint=True)
        gmisLON,gmisLAT=np.meshgrid(lons,lats)
        kamboundary=np.array(Image.open(GMISfile))[::-1,:]
        kamboundary[kamboundary>100]=0.0 ; kamboundary=kamboundary/100
        kamboundary=gaussian_filter(kamboundary,sigma=5)
    #Actual figure
    ir=0
    for ic in range(Ncols):
        ax[ir,ic] = fig.add_subplot(gs[ir,ic])
        m = Basemap(llcrnrlon=32.399,llcrnrlat=0.099,urcrnrlon=32.801,urcrnrlat=0.501,\
                    resolution='f',projection='merc',lat_0=0.3,lon_0=32.6,lat_ts=0.0,ax=ax[ir,ic])
        if ic==0 and ir==Nrows-1:
            m.drawparallels([0.1,0.5],labels=[1,0,0,0],linewidth=0)
            m.drawmeridians([32.4,32.8],labels=[0,0,0,1],linewidth=0)
        else:
            m.drawparallels([0.1,0.5],labels=[0,0,0,0],linewidth=0)
            m.drawmeridians([32.4,32.8],labels=[0,0,0,0],linewidth=0)
        mlon,mlat=m(LON,LAT)
        im=m.pcolormesh(mlon,mlat,imarray[('min','mean','max')[ic]],cmap='RdYlBu_r',ax=ax[ir,ic])
        axins = inset_axes(ax[ir,ic], width=0.1,height="100%",bbox_to_anchor=(1.01, 0., 1, 1),bbox_transform=ax[ir,ic].transAxes,loc='center left')
        cb=fig.colorbar(im,cax=axins) ; cb.ax.tick_params(labelsize=7)
        cb.set_label('Daily {} Humidex ($^\\circ$C)'.format(('min','mean','max')[ic]))
        # indicate sensor locations
        x=[]  ; y=[] ; txt=[]
        for key,value in settings.locations.items():
            x1,y1=m(value[0],value[1])
            x.append(x1) ; y.append(y1)
            txt.append(settings.abbreviations[key])
        for i,t in enumerate(txt):
            ax[ir,ic].annotate(t, (x[i],y[i]),va='center',ha='center',fontsize=8)
        # plot K boundaries
        if plotKb:
            gmislon,gmislat=m(gmisLON,gmisLAT)
            m.contour(gmislon,gmislat,kamboundary,levels=[0.1],colors='grey',linewidths=0.5,ax=ax[ir,ic])
        ax[ir,ic].text(0.1,1.05,('a)','b)','c)')[ic],fontsize=12,horizontalalignment='center',verticalalignment='center',transform=ax[ir,ic].transAxes)
    plt.savefig(figsavefile,bbox_inches='tight')
    plt.close()
    print('*** FIG SAVED : '+figsavefile)
    #plt.show()
    

if __name__=="__main__":
    LO,LA,VF=load_vf(VFfile)
    HI={}
    for i in ['min','mean','max']:
        HI[i]=HI_from_VF(VF,i)
    plot_variables(LO,LA,HI)


