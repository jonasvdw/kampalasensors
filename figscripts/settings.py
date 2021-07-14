#!/data/leuven/320/vsc32093/miniconda3/envs/science/bin/python

#SETTINGS
sensors={\
           'makerere':       ['s01','s02','s03'],\
           'bukerere':       ['s04','s05','s08'],\
           'industrialarea': ['s09','s10','s11'] ,\
           'bwaise':         ['s12','s13','s16'],\
           'nateete':        ['s17','s18','s19'],\
           'acholiq':        ['s20','s21','s22'],\
           'nkeere':         ['s26','s27','s29'],\
           'kawanda':        ['s33','s34','s35'],\
           'buloba':         ['s36','s37','s38'],\
           'namungoona':     ['s39','s40','s41'],\
           'najjanankumbi':  ['s42','s43','s44'],\
           'buziga':         ['s45','s46','s48'],\
           'nakasero':       ['s49','s50','s51'] \
          }

locations={\
           'makerere':       [32.56868971 ,0.33345329],\
           'bukerere':       [32.6988337  ,0.41116408],\
           'industrialarea': [32.60268803 ,0.3210462] ,\
           'bwaise':         [32.56241631 ,0.35201249],\
           'nateete':        [32.53986146 ,0.29172497],\
           'acholiq':        [32.63944912 ,0.33501852],\
           'nkeere':         [32.5799099  ,0.29538847],\
           'kawanda':        [32.5292712  ,0.42605757],\
           'buloba':         [32.47247892 ,0.32615841],\
           'namungoona':     [32.54262452 ,0.34300468],\
           'najjanankumbi':  [32.56650669 ,0.27506658],\
           'buziga':         [32.61788962 ,0.25952766],\
           'nakasero':       [32.57969113 ,0.31192789] \
          }

abbreviations={\
           'makerere':       'Mk',\
           'bukerere':       'Bk',\
           'industrialarea': 'Ia',\
           'bwaise':         'Bw',\
           'nateete':        'Nt',\
           'acholiq':        'Aq',\
           'nkeere':         'Nk',\
           'kawanda':        'Kw',\
           'buloba':         'Bl',\
           'namungoona':     'Ng',\
           'najjanankumbi':  'Nj',\
           'buziga':         'Bz',\
           'nakasero':       'Ns' \
          }

datadir='/data/leuven/320/vsc32093/SCRIPTS/iButtons/kampalasensors/data/'
savedir='/scratch/leuven/320/vsc32093/projects/iButtons/figs/'
Tfile='Kampala_temperature.csv'
RHfile='Kampala_humidity.csv'
HIfile='Kampala_heatindex.csv'
EVfile='Kampala_explvars.csv'

GMISfile='/scratch/leuven/320/vsc32093/projects/iButtons/explainingvars/36N_gmis_impervious_surface_percentage_utm_30m.tif'
