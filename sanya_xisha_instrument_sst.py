# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 15:07:09 2021

@author: DSH
"""

import numpy as np
import xarray as xr
f_sst = xr.open_dataset('E:/interpolate_paper/data_calculation/hadISST_sst.nc')
print(f_sst)
sst = f_sst['sst']
lat = f_sst['latitude']
lon = f_sst['longitude']
lat = lat.values
lon = lon.values

sanya = sst.loc['1980-01-01':'1989-12-31',18.5,109.5]
sanya = sanya.values
sanya = (sanya.reshape(120,1)).reshape(10,12)
sanya_monthly_mean = sanya.mean(axis = 0)
sanya = sanya.reshape(120,1)

sanya_100a = sst.loc['1911-01-01':'2010-12-31',18.5,109.5]
sanya_100a = sanya_100a.values
sanya_100a = (sanya_100a.reshape(len(sanya_100a),1)).reshape(100,12)
sanya_100a_plateau = sanya_100a[:,5:9]

index_sanya_100a_plateau_max_sst_month = np.empty(shape=(100))
for i in range(100):
    index_sanya_100a_plateau_max_sst_month[i] = (np.array(np.where(sanya_100a_plateau[i,:] == sanya_100a_plateau.max(axis = 1)[i]),dtype = None))+6

index_sanya_100a_plateau_min_sst_month = np.empty(shape=(100))
for i in range(100):
    index_sanya_100a_plateau_min_sst_month[i] = (np.array(np.where(sanya_100a_plateau[i,:] == sanya_100a_plateau.min(axis = 1)[i]),dtype = None))+6
       



sanya_100a_monthly_mean = sanya_100a.mean(axis = 0)
sanya_100a = sanya_100a.reshape(1200,1)
sanya_100a_monthly = sanya_100a.reshape(100,12)
sanya_100a_monthly_std = sanya_100a_monthly.std(axis = 0)

index_sanya_max_sst_month = np.empty(shape=(100))
for i in range(100):
    index_sanya_max_sst_month[i] = (np.array(np.where(sanya_100a_monthly[i,:] == sanya_100a_monthly.max(axis = 1)[i]),dtype = None))+1

index_sanya_min_sst_month = np.empty(shape=(100))
for i in range(100):
    index_sanya_min_sst_month[i] = (np.array(np.where(sanya_100a_monthly[i,:] == sanya_100a_monthly.min(axis = 1)[i]),dtype = None))+1
       


xisha_28a = sst.loc['1980-01-01':'2007-12-31',16.5,112.5]
xisha_28a = xisha_28a.values
xisha_28a = (xisha_28a.reshape(336,1).reshape(28,12))
xisha_28a_monthly_mean = xisha_28a.mean(axis = 0)
xisha_28a = xisha_28a.reshape(336,1)

xisha_100a = sst.loc['1911-01-01':'2010-12-31',16.5,112.5]
xisha_100a = xisha_100a.values
xisha_100a = (xisha_100a.reshape(1200,1).reshape(100,12))
xisha_100a_monthly_mean = xisha_100a.mean(axis = 0)

xisha_100a_plateau = xisha_100a[:,4:9]
index_xisha_100a_plateau_max_sst_month = np.empty(shape=(100))
for i in range(100):
    index_xisha_100a_plateau_max_sst_month[i] = (np.array(np.where(xisha_100a_plateau[i,:] == xisha_100a_plateau.max(axis = 1)[i]),dtype = None))+5

index_xisha_100a_plateau_min_sst_month = np.empty(shape=(100))
for i in range(100):
    index_xisha_100a_plateau_min_sst_month[i] = (np.array(np.where(xisha_100a_plateau[i,:] == xisha_100a_plateau.min(axis = 1)[i]),dtype = None))+5
       

xisha_100a = xisha_100a.reshape(1200,1)
xisha_100a_monthly = xisha_100a.reshape(100,12)
xisha_100a_monthly_std = xisha_100a_monthly.std(axis = 0)


index_xisha_max_sst_month = np.empty(shape=(100))
for i in range(100):
    index_xisha_max_sst_month[i] = (np.array(np.where(xisha_100a_monthly[i,:] == xisha_100a_monthly.max(axis = 1)[i]),dtype = None))+1

index_xisha_min_sst_month = np.empty(shape=(100))
for i in range(100):
    index_xisha_min_sst_month[i] = (np.array(np.where(xisha_100a_monthly[i,:] == xisha_100a_monthly.min(axis = 1)[i]),dtype = None))+1
   

time_sanya_1991 = np.delete((np.linspace(1981,1991,121)),120,axis = 0)
time_sanya_1991 = time_sanya_1991.reshape(120,1)


time_xisha_2008 = np.delete((np.linspace(1980,2008,337)),336,axis = 0)
time_xisha_2008 = time_xisha_2008.reshape(336,1)


sanya_time_sst = np.concatenate((time_sanya_1991,sanya),axis = 1)
xisha_1980_sst = np.concatenate((time_xisha_2008,xisha_28a),axis = 1)
