#!/data/leuven/320/vsc32093/miniconda3/envs/science/bin/python

#IMPORTS
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.ndimage import gaussian_filter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.basemap import Basemap
import settings
import readfromcsv as RD


figurelayout=np.array([['Tmin','Tmean','Tmax'],\
                       ['RHmin','RHmean','RHmax'],\
                       ['HImin','HImean','HImax']])

path=settings.datadir
csvfile=path+settings.HIfile
GMISfile=settings.GMISfile
figsavefile=settings.savedir+'fig02.png'
plotKb=False  # plot Kampala boundaries if GMIS file is available

figureinformation={\
                   'Tmin'  : ['a','$T$'  ,'$^\\circ$C','RdYlBu_r'],\
                   'Tmean' : ['b','$T_{\\rm mean}$' ,'$^\\circ$C','RdYlBu_r'],\
                   'Tmax'  : ['c','$T$'  ,'$^\\circ$C','RdYlBu_r'],\
                   'RHmin' : ['d','$RH$' ,'%'         ,'PuBuGn'  ],\
                   'RHmean': ['e','$RH_{\\rm mean}$','%'         ,'PuBuGn'  ],\
                   'RHmax' : ['f','$RH$' ,'%'         ,'PuBuGn'  ],\
                   'HImin' : ['g','$H_{\\rm min}$' ,'$^\\circ$C','RdYlBu_r'],\
                   'HImean': ['h','$H_{\\rm mean}$','$^\\circ$C','RdYlBu_r'],\
                   'HImax' : ['i','$H_{\\rm max}$' ,'$^\\circ$C','RdYlBu_r']\
                  }

def plot_SP():
    Nrows,Ncols=np.shape(figurelayout)
    fig = plt.figure(figsize=(15,11))
    gs = gridspec.GridSpec(Nrows,Ncols,wspace=0.0,hspace=0.15)
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
    #Actual figure:
    for ir in range(Nrows):
        for ic in range(Ncols):
            mmm=figurelayout[ir,ic]
            index,title,unit,cmap=figureinformation[mmm]
            Z=RD.readdata_psMMM(csvfile,wanted=('temperature','humidity','heatindex')[ir],mmm=('min','mean','max')[ic])
            ax[ir,ic] = fig.add_subplot(gs[ir,ic])
            ax[ir,ic].text(0.075,0.925,index+')',fontsize=12,horizontalalignment='center',verticalalignment='center',transform=ax[ir,ic].transAxes)
            m = Basemap(llcrnrlon=32.399,llcrnrlat=0.099,urcrnrlon=32.801,urcrnrlat=0.501,\
                        resolution='f',projection='merc',\
                        lat_0=0.3,lon_0=32.6,lat_ts=0.0,ax=ax[ir,ic])
            m.drawcoastlines(color='b',linewidth=0.5)
            if ic==0 and ir==Nrows-1:
                m.drawparallels([0.1,0.5],labels=[1,0,0,0],linewidth=0)
                m.drawmeridians([32.4,32.8],labels=[0,0,0,1],linewidth=0)
            else:
                m.drawparallels([0.1,0.5],labels=[0,0,0,0],linewidth=0)
                m.drawmeridians([32.4,32.8],labels=[0,0,0,0],linewidth=0)
            # indicate sensor locations
            x=[]  ; y=[] ; T=[] ; txt=[]
            for key,value in settings.locations.items():
                x1,y1=m(value[0],value[1])
                x.append(x1) ; y.append(y1)
                T.append(Z[key])
                txt.append(settings.abbreviations[key])
                print(mmm,key,Z[key])
            im=m.scatter(x,y,c=T,s=150,cmap=cmap)
            avg=np.nanmean(np.array(T)) ; d=max(abs(avg-np.nanmin(np.array(T))),abs(avg-np.nanmax(np.array(T))))
            im.set_clim(round((avg-d)*2.0)*0.5,round((avg+d)*2.0)*0.5)
            for i,t in enumerate(txt):
                ax[ir,ic].annotate(t, (x[i],y[i]),va='center',ha='center',fontsize=8)
            axins = inset_axes(ax[ir,ic], width=0.1,height="100%",bbox_to_anchor=(1.01, 0., 1, 1),bbox_transform=ax[ir,ic].transAxes,loc='center left')
            cb=fig.colorbar(im,cax=axins) ; cb.ax.tick_params(labelsize=7)
            cb.set_label(title+' ('+str(unit)+')')
            # plot K boundaries
            if plotKb:
                gmislon,gmislat=m(gmisLON,gmisLAT)
                m.contour(gmislon,gmislat,kamboundary,levels=[0.1],colors='grey',linewidths=0.5,ax=ax[ir,ic])
            if ic==0:
                name=['temperature','relative humidity','humidex']
                ax[ir,ic].text(-0.2,0.5,name[ir],fontsize=12,horizontalalignment='center',verticalalignment='center',transform=ax[ir,ic].transAxes,rotation=90)
            if ir==0:
                name=['condition at $H_{\\rm min}$', 'daily mean', 'condition at $H_{\\rm max}$']
                ax[ir,ic].text(0.5,1.1,name[ic],fontsize=12,horizontalalignment='center',verticalalignment='center',transform=ax[ir,ic].transAxes)
    plt.savefig(figsavefile,bbox_inches='tight')
    plt.close()
    print('*** FIG SAVED : '+figsavefile)
    #plt.show()

if __name__=="__main__":
    plot_SP()
