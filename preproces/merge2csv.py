#!/data/leuven/320/vsc32093/miniconda3/envs/science/bin/python

import sys
import glob
import numpy as np
import datetime
import pandas as pd
import csv
import timezones as TZ
import settings

#SETTINGS
datapath=settings.rawdatadir
pathT=datapath+"/temperature/restructured/"
pathR=datapath+"/humidity/restructured/"
pathH=datapath+"/heatindex/restructured/"
topath=settings.datadir

writetype='extended' #'basic' #'extended'

def HeatIndexCompute(T,RH):
    #HUMIDEX
    HI=T+(5/9)*((6.112*10**((7.5*T)/(237.7+T))*(RH/100))-10)
    return HI

def openfile(filepath):
    if True:
        data=[] ; datatim=[]
        if filepath.endswith('.csv'):
            with open(filepath) as csvf:
                csv_reader=csv.reader(csvf,delimiter=',')
                line_count = 0 ; Tminmax=[] ; oldday=0 ; hours=[]
                for row in csv_reader: #ALL MOMENTS WITHIN ONE PERIOD
                    if line_count==9:
                        if "CET" in row[0]:
                            timezon="CET"
                        elif "CEST" in row[0]:
                            timezon="CEST"
                        elif "EAT" in row[0]:
                            timezon="EAT"
                        else:
                            print('timezon unknown')
                            sys.exit()
                    if line_count>=20:
                        if timezon=="CET":
                            dt1=datetime.datetime.strptime(row[0],'%d/%m/%y %H:%M:%S')
                            dt=TZ.CET2EAT(dt1)
                        elif timezon=="CEST":
                            dt1=datetime.datetime.strptime(row[0],'%d/%m/%y %H:%M:%S')
                            dt=TZ.CEST2EAT(dt1)
                        elif timezon=="EAT":
                            dt=datetime.datetime.strptime(row[0],'%m/%d/%y %I:%M:%S %p')
                        if len(row)==3: #decimal is dot
                            x=float(row[2])
                        elif len(row)==4: #decimal is comma
                            x=float(str(row[2])+'.'+str(row[3]))
                        data.append(x)
                        datatim.append(dt)
                    line_count+=1
            data=np.array(data)
            datatim=np.array(datatim)
        return data,datatim

def roundTime(dt=None, roundTo=60):
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

def initiate_df():
    startdate=datetime.datetime.strptime('20180701','%Y%m%d')
    stopdate=datetime.datetime.strptime('20190701','%Y%m%d')
    Nq=int((stopdate-startdate).total_seconds()/900) #number of quarters (15min)
    dat=[] ; period=[]
    for i in range(Nq):
        dat.append(startdate+datetime.timedelta(seconds=i*900))
        if dat[-1]<datetime.datetime.strptime('20181017','%Y%m%d'):
            period.append(1)
        elif dat[-1]<datetime.datetime.strptime('20190201','%Y%m%d'):
            period.append(2)
        else:
            period.append(3)
    df=pd.DataFrame({'datetime':dat})
    df['period']=period
    return df

def fill_df(df,path):
    cols=[]
    for key,val in settings.sensors.items():
        for s in val:
            datapersensor=np.zeros(len(df))*np.nan
            for file in glob.glob(path+'/'+s+'_'+key+'_*.csv'):
                data,tims=openfile(file)
                t=roundTime(tims[0],roundTo=60*15)
                idx=df[df['datetime']==t].index[0]
                datapersensor[int(idx):int(idx)+len(tims)]=data
            df[settings.abbreviations[key]+'_'+s]=datapersensor
            cols.append(settings.abbreviations[key]+'_'+s)
    df=df.dropna(axis=0,how='all',subset=cols)
    df=df.reset_index(drop=True)
    return df

def sensormeans(df):
    datadict={}
    for key,val in settings.sensors.items():
        cols=[]
        for s in val:
            cols.append(settings.abbreviations[key]+'_'+s)
        datadict[settings.abbreviations[key]]=df[cols].mean(axis='columns',skipna=None)
    return pd.DataFrame(datadict)

if __name__=="__main__":
    dfT=initiate_df()
    dfT=fill_df(dfT,pathT)
    if writetype=='extended': dfT=pd.concat([dfT,sensormeans(dfT)],axis='columns')
    dfT.to_csv(topath+'/Kampala_temperature.csv',sep=';')
    print('*** Data written: '+topath+'/Kampala_temperature.csv')
    
    dfR=initiate_df()
    dfR=fill_df(dfR,pathR)
    if writetype=='extended': dfR=pd.concat([dfR,sensormeans(dfR)],axis='columns')
    dfR.to_csv(topath+'/Kampala_humidity.csv',sep=';')
    print('*** Data written: '+topath+'/Kampala_humidity.csv')
    
    dfH=pd.DataFrame({'datetime':dfT['datetime'],'period':dfT['period']})
    for key,val in settings.sensors.items():
        for s in val:
            dfH[settings.abbreviations[key]+'_'+s]=HeatIndexCompute(dfT[settings.abbreviations[key]+'_'+s],dfR[settings.abbreviations[key]+'_'+s])
    if writetype=='extended': dfH=pd.concat([dfH,sensormeans(dfH)],axis='columns')
    dfH.to_csv(topath+'/Kampala_heatindex.csv',sep=';')
    print('*** Data written: '+topath+'/Kampala_heatindex.csv')
