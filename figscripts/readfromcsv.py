#!/data/leuven/320/vsc32093/miniconda3/envs/science/bin/python

#IMPORTS
import sys
import os.path
import numpy as np
import pandas as pd
from scipy.stats import circmean
import matplotlib.pyplot as plt
import datetime
import timezones as TZ
import csv
import glob
import settings

def openfile(csvfile,wanted='heatindex',sensor='Mk_s01',mmm='max'):
    if mmm=='mean': 
        df1=pd.read_csv(csvfile.replace('temperature',wanted).replace('humidity',wanted).replace('heatindex',wanted),sep=';',index_col=0)
        df1['datetime'] = pd.to_datetime(df1['datetime'])
        return df1.groupby(pd.Grouper(key='datetime', freq='D')).mean().reset_index(level=0)[['datetime','period',sensor]]
    else:
        df1=pd.read_csv(csvfile,sep=';',index_col=0)
        df1['datetime'] = pd.to_datetime(df1['datetime'])
        s = df1.groupby(pd.Grouper(key='datetime', freq='D'))[sensor].transform(mmm)
        #s = df1.resample('D', on='datetime')['Mk_s01'].transform('max')
        df2=pd.DataFrame({'datetime':df1[df1[sensor] == s]['datetime'],'period':df1[df1[sensor] == s]['period'],sensor:df1[df1[sensor] == s][sensor]})
        q=df2.groupby(pd.Grouper(key='datetime', freq='D'))['datetime'].transform(lambda x: x.quantile(0.5,interpolation='lower')) #.transform('first')
        df=df2[df2['datetime']==q]
        #DATA OF WANTED QUANTITY
        filew=csvfile.replace('temperature',wanted).replace('humidity',wanted).replace('heatindex',wanted)
        if filew!=csvfile:
            dfw=pd.read_csv(filew,sep=';',index_col=0)
            dfw['datetime'] = pd.to_datetime(dfw['datetime'])
            dfw=dfw[dfw.datetime.isin(df.datetime)]
            return dfw[['datetime','period',sensor]]
        else:
            return df

def readdata_psMMM(csvfile,wanted='heatindex',mmm='max'):
    HI={}
    for key,val in settings.abbreviations.items():
        per1=[] ; per2=[] ; per3=[]
        df=openfile(csvfile,wanted=wanted,sensor=val,mmm=mmm)
        HI[key]=np.nanmean([df[df['period']==1][val].mean(),df[df['period']==2][val].mean(),df[df['period']==3][val].mean()])
    return HI

if __name__=='__main__':
    file='/data/leuven/320/vsc32093/SCRIPTS/iButtons/kampalasensors/data/Kampala_temperature.csv'
    print(readdata_psMMM(file,wanted='temperature',mmm='max'))
