#!/data/leuven/320/vsc32093/miniconda3/envs/science/bin/python

import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd
import matplotlib.patches as patches
import settings
import readfromcsv as RD

path=settings.datadir
csvfile=path+settings.HIfile
figsavefile=savedir+'/fig03.png'

locs=['makerere','bukerere','kawanda','buloba','buziga','industrialarea','nakasero','namungoona','bwaise','najjanankumbi','nateete','nkeere','acholiq']
THs=np.arange(30,50+1,1)

def exceedancepercentage():
    exceedchance={}
    for key in locs:
        exceedchance[key]=[]
        TS=RD.openfile(csvfile,wanted='heatindex',sensor=settings.abbreviations[key],mmm='max')[settings.abbreviations[key]].dropna() #daily max Humidex
        hist,edges=np.histogram(np.array(TS),bins=np.arange(0,60+0.1,0.1),density=True)
        dbin=(edges[1]-edges[0])
        bincenters=(edges[1:]+edges[:-1])*0.5
        for TH in THs:
            exceedchance[key].append(np.sum(hist[edges[:-1]>TH])*dbin)
    M=np.zeros((len(list(settings.sensors.keys())),len(THs)))
    for i,key in enumerate(locs):
        for j in range(len(THs)):
            M[i,j]=exceedchance[key][j]
    M=np.array(M)*100 #percentage
    return M

def metricmatrix(array):
    fig=plt.figure(figsize=(16,6)) ; ax=plt.gca()
    dfcm=pd.DataFrame(array,columns=[str(i) for i in THs],index=[settings.abbreviations[i] for i in locs])
    annots=np.array(array).astype(int) ; annotlabs=annots.astype(str) ; annotlabs[annots==0]=''
    sn.heatmap(dfcm,vmin=0,vmax=100,annot=annotlabs,linewidth=0.2,fmt="",cmap='afmhot_r',cbar_kws={'label':'days with $H_{\\rm max}$ exceeding threshold (%)'},ax=ax)
    ax.set_xlabel('$H_{\\rm max}$ threshold ($^\\circ C$)')
    rect1=patches.Rectangle(((30-THs[0])/len(THs),0.0),1.0/len(THs)/20,1.0,linewidth=2,edgecolor='c',facecolor='none',transform=ax.transAxes)
    rect2=patches.Rectangle(((40-THs[0])/len(THs),0.0),1.0/len(THs)/20,1.0,linewidth=2,edgecolor='c',facecolor='none',transform=ax.transAxes)
    rect3=patches.Rectangle(((45-THs[0])/len(THs),0.0),1.0/len(THs)/20,1.0,linewidth=2,edgecolor='c',facecolor='none',transform=ax.transAxes)
    ax.add_patch(rect1) ; ax.add_patch(rect2) ;ax.add_patch(rect3)
    ax.text((30.0-THs[0])/len(THs),1.05,'Some discomfort',color='c',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='left',verticalalignment='center')
    ax.text((40.0-THs[0])/len(THs),1.05,'Great discomfort',color='c',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='left',verticalalignment='center')
    ax.text((45.0-THs[0])/len(THs),1.05,'Dangerous',color='c',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='left',verticalalignment='center')
    lczticks=(np.arange(len(locs))+0.5)/len(locs)
    ax.text(-0.05,lczticks[1],'---LCZ 7---',color='k',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='center',verticalalignment='center',rotation=90)
    ax.text(-0.05,lczticks[4],'---LCZ 3---',color='k',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='center',verticalalignment='center',rotation=90)
    ax.text(-0.05,lczticks[6],'2',color='k',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='center',verticalalignment='center',rotation=90)
    ax.text(-0.05,lczticks[7],'8',color='k',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='center',verticalalignment='center',rotation=90)
    ax.text(-0.05,lczticks[9]+0.5/len(locs),'------LCZ 6------',color='k',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='center',verticalalignment='center',rotation=90)
    ax.text(-0.05,lczticks[12],'5',color='k',transform=ax.transAxes,weight="bold",fontsize=12,horizontalalignment='center',verticalalignment='center',rotation=90)
    plt.savefig(figsavefile,bbox_inches='tight')
    plt.savefig(figsavefile.replace('.png','.pdf'),bbox_inches='tight')
    plt.close()
    print('*** FIG SAVED : '+figsavefile)

if __name__=='__main__':
    matrix=exceedancepercentage()
    metricmatrix(matrix)
