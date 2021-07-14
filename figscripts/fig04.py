#!/data/leuven/320/vsc32093/miniconda3/envs/profiles/bin/python

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import settings
import readfromcsv as RD

path=settings.datadir
csvfile=path+settings.HIfile
file_explvar=path+settings.EVfile
figsavefile=settings.savedir+'/fig04.png'

colordict = {'2':'#9a0200','3':'#fd3c06','5':'#e50000','6':'#fd8d49','7':'#ffda03','8':'#d8dcd6'}
colornumb = {'2':0,'3':1,'5':2,'6':3,'7':4,'8':5}
N=len(list(colordict.values()))
cm=LinearSegmentedColormap.from_list('lczclassification',list(colordict.values()),N=N)

LCZcolorscales={\
           'Mk':5,\
           'Bk':6,\
           'Ia':8,\
           'Bw':3,\
           'Nt':7,\
           'Aq':7,\
           'Nk':7,\
           'Kw':6,\
           'Bl':6,\
           'Ng':3,\
           'Nj':3,\
           'Bz':6,\
           'Ns':2 \
          }

def save_explvars(corvar,mmm):
    X=np.zeros((len(settings.abbreviations.keys()),len(corvar)))
    Y=np.zeros(len(settings.abbreviations.keys()))
    Xplus=np.zeros((len(settings.abbreviations.keys()),len(corvar)+1))
    for cv in range(len(corvar)):
        T=RD.readdata_psMMM(csvfile,wanted='heatindex',mmm=mmm)
        df=pd.read_csv(file_explvar,sep=';',index_col='sensorlocations')
        V=df[corvar[cv]].to_dict()
        counter=0
        for key in settings.abbreviations.keys():
            X[counter,cv]=V[key]
            if cv==0: Y[counter]=T[key]
            Xplus[counter,cv+1]=V[key]
            if cv==0: Xplus[counter,cv]=T[key]
            counter+=1
    return Xplus

def regressor(corvar,Xplus,select,printvar=False):
    Y=Xplus[:,0]
    X=Xplus[:,1:]
    X=sm.add_constant(X) ; X=X[:,select]
    corvar1=['const']+corvar
    if printvar: print([corvar1[i] for i in select])
    regressor_OLS = sm.OLS(endog=Y, exog=X).fit()
    return X,regressor_OLS

def regression_with_backward_elimination(explvar,mmm,verbose=False):
    corvar=list(explvar.keys())
    corvar1=['const']+corvar
    select=np.arange(len(corvar1))
    corvarlist=list([corvar1[i] for i in select])
    if verbose: print(['const']+corvar)
    Xplus=save_explvars(corvar,mmm)
    for i in range(len(select)):
        corvar1=['const']+corvar
        Xreduced,regressorOLS=regressor(corvar,Xplus,select,printvar=verbose)
        pvals=np.array(regressorOLS.pvalues)
        pvals[0]=0.0 #never remove constant!
        if np.max(pvals)>0.01:
            a=np.argmax(pvals)
            select=list(select[:a])+list(select[a+1:])
            if verbose:
                print(regressorOLS.summary())
                print('\n\n')
                print([corvar1[i] for i in select])
            corvarlist=list([corvar1[i] for i in select])
        else:
            print(regressorOLS.summary())
            coeff=np.array(regressorOLS.params)
            rsq=float(regressorOLS.rsquared)
            prstd, iv_l, iv_u = wls_prediction_std(regressorOLS)
            Y=regressorOLS.fittedvalues
            break
    return corvarlist,Xreduced,Xplus[:,0],Y,coeff,iv_l,iv_u,rsq

def plot_bigfig(mmms,corvar,names):
    Nrows=1 ; Ncols=len(mmms)
    fig = plt.figure(figsize=(12,3))
    gs = gridspec.GridSpec(Nrows,Ncols,wspace=0.30,hspace=0.10)
    ax=np.empty(gs.get_geometry(),dtype=object)
    ir=0
    for ic in range(Ncols):
        corvarlist,X,Yobs,Ymod,coeff,low,up,rsq=regression_with_backward_elimination(corvar,mmms[ic],verbose=False)
        if len(corvarlist)>2:
            print('!!!!! more than one explaining variable comes out of statistical model, change the code. Now I will only plot for '+str(corvarlist[-1]))
        var=str(corvarlist[-1])
        X=X[:,-1]
        
        ax[ir,ic] = fig.add_subplot(gs[ir,ic])
        data1=[] ; data2=[] ; lczcol=[] ; counter=0
        for key,val in settings.abbreviations.items():
            ax[ir,ic].annotate(val, (X[counter],Yobs[counter]),ha='center',va='center')
            data1.append(X[counter]) ; data2.append(Yobs[counter])
            lczcol.append(colornumb[str(LCZcolorscales[val])])
            counter+=1
        im=ax[ir,ic].scatter(data1,data2,s=150,c=lczcol,cmap=cm)
        ax[ir,ic].set_xlim(np.nanmin(data1)-0.1*(np.nanmax(data1)-np.nanmin(data1)),np.nanmax(data1)+0.1*(np.nanmax(data1)-np.nanmin(data1)))
        ax[ir,ic].set_ylabel(names[mmms[ic]]+' (°C)')
        ax[ir,ic].set_xlabel(var+' '+str(corvar[var]))
        plotmatrix=np.array([X,Ymod,low,up]).T
        pms=plotmatrix[np.argsort(plotmatrix[:,0])]
        ax[ir,ic].plot(pms[:,0],pms[:,1],c='C0',ls='-',lw=1.0)
        ax[ir,ic].plot(pms[:,0],pms[:,2],c='C0',ls='--',lw=0.5)
        ax[ir,ic].plot(pms[:,0],pms[:,3],c='C0',ls='--',lw=0.5)
        ax[ir,ic].text(0.44,0.92,names[mmms[ic]]+' $\\approx$ '+str(round(float(coeff[0]),2))+str(np.sign(coeff[1]))[0]+str(round(float(abs(coeff[1])),2))+'$\,$'+str(var),fontsize=8,horizontalalignment='left',verticalalignment='center',transform=ax[ir,ic].transAxes)
        ax[ir,ic].text((0.50,0.53,0.515)[ic],0.84,'$\\rm R^2$='+str(round(float(rsq),3)),fontsize=8,horizontalalignment='left',verticalalignment='center',transform=ax[ir,ic].transAxes)
        if ic==Ncols-1:
            axins = inset_axes(ax[ir,ic], width=0.1,height="100%",bbox_to_anchor=(1.01, 0., 1, 1),bbox_transform=ax[ir,ic].transAxes,loc='center left')
            cb=fig.colorbar(im,cax=axins,ticks=np.linspace(0,N-1,N+1)+((N-1)/(2*N))) ; cb.ax.set_yticklabels(list(colordict.keys())) ; cb.ax.tick_params(labelsize=7)
            cb.set_label('LCZ class')
        ax[ir,ic].text(0.1,1.05,('a)','b)','c)')[ic],fontsize=12,horizontalalignment='center',verticalalignment='center',transform=ax[ir,ic].transAxes)
    plt.savefig(figsavefile,bbox_inches='tight')
    plt.savefig(figsavefile.replace('.png','.pdf'),bbox_inches='tight')
    plt.close()
    print('*** FIG SAVED : '+figsavefile)

if __name__=="__main__":
    mmms=['min','mean','max']
    names={\
           'min' : '$H_{\\rm min}$',
           'mean' : '$H_{\\rm mean}$',
           'max' : '$H_{\\rm max}$'
          }
    explvar={\
             'D2L' : '(km)',
             'DEM' : '(m)',
             'VF'  : '()',
             'GMIS': '(%)',
             'POP' : '(km-2)',
             'ALB' : '(-)'
            }
    plot_bigfig(mmms,explvar,names)
