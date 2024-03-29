
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 10 16:11:10 2022

@author: dsh19
"""
import pycwt
import math
import numpy as np 
import xlrd
import sys
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
import scipy.stats as st
from scipy import interpolate
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error  
import pyleoclim as pyleo
plt.style.use('ggplot')
sys.path.append('E:/interpolate_paper/data_calculation/bandpass.py') 
import bandpass





#####Sanya#####





#Read Excel file of Sanya coral data
ctl_depth_sanya = xlrd.open_workbook('E:/interpolate_paper/data_calculation/YXN-1 and SY-1 srca data.xlsx')
sheet_sanya = ctl_depth_sanya.sheets()[0]
coral_data_sanya = np.array(((sheet_sanya.col_values(0))[1:]),dtype = np.float64)   #Sanya cora Sr/Ca data
instrument_sanya = np.array(((sheet_sanya.col_values(1))[1:121]),dtype = np.float64)  #Sanya instrumental SST (HadiSST)
depth_sanya_endpoint = np.array(((sheet_sanya.col_values(3))[1:13]),dtype = np.float64) # depth of the endpoind method
depth_sanya_extreme = np.array(((sheet_sanya.col_values(9))[1:23]),dtype = np.float64) # depth of the extreme method
depth_sanya_plateau = np.array(((sheet_sanya.col_values(15))[1:33]),dtype = np.float64) # depth of the plateau method

#Define coral interpolated function
def coral_chronology_model(depth,depth_ctlpoints,ctl_points_age,data,interpolate_rate): #depth:length of the data; depth_ctlpoints:tie points`depth; ctl_points_age: age(month) of the tie points; data:coral data;  interpolate_rate:target resolution;
    f_depth_ctlpoints_age = interpolate.interp1d(depth_ctlpoints, ctl_points_age)
    depth_age = f_depth_ctlpoints_age(depth) #calculated the age of raw srca data`s depth according to tie points
    depth_age_even = [] #make an array to stock interpolated series including age and srca 
    npts = len(depth_age)
    depth_age_even = np.arange(depth_age[0],depth_age[npts-1] + 0.01,interpolate_rate) # if the steps is 1/12, the length should be longer than 17 or 18 to ensure the length of the data.
    age = depth_age_even # interpolated age
    dataeven = interpolate.interp1d(depth_age,data)
    interpolate_result = dataeven(age) # interpolated result
    return age,interpolate_result


###Montel Carlo sensitivity test###


##the entpoint method## 
ctl_points_sanya_endpoint = np.empty((12,4)) # make an array to reposit potential tie points
for i in range(4):
    ctl_points_sanya_endpoint[:,i] = np.array(((sheet_sanya.col_values(i+4))[1:13]),dtype = np.float64)  
# selecting the tie points randomly at particular depth
sanya_endpoint_mont_ctlpoints = np.empty((12,2000))#make an array to reposit age of tie points using bootstrap method
for j in range(2000): #set the iterated number
        for k in range(0,12,2): # selecting the tie points based on minimum sst month occrurrences
            sanya_endpoint_mont_ctlpoints[k,j] = np.random.choice(ctl_points_sanya_endpoint[k,:],1,[0.01,0.2,0.7,0.09]) 
        for l in range(1,12,2):
            sanya_endpoint_mont_ctlpoints[l,j] = np.random.choice(ctl_points_sanya_endpoint[l,:],1,[0.01,0.2,0.7,0.09])
# do the interpolated work for these simulated results;       
srca_sanya_endpoint = np.empty((120,2000))
for i in range(2000):
    age, srca_sanya_endpoint[:,i] = coral_chronology_model(np.arange(1,170,1),depth_sanya_endpoint,sanya_endpoint_mont_ctlpoints[:,i],coral_data_sanya,1/12)
# Sr/Ca-SST paleotherometer
sst_sanya_endpoint = np.empty(shape=(120,2000))
for i in range(2000):
    sst_sanya_endpoint[:,i] = (9.824 - srca_sanya_endpoint[:,i])/0.04306
    
#the extreme method
ctl_points_sanya_extreme = np.empty((22,4)) # make an array to reposit potential tie points
for i in range(4):
    ctl_points_sanya_extreme[:,i] = np.array(((sheet_sanya.col_values(i+10))[1:23]),dtype = np.float64) 
# selecting the tie points randomly at particular depth
sanya_extreme_mont_ctlpoints = np.empty((22,2000))#make an array to reposit age of tie points using bootstrap method
for j in range(2000): #set the iterated number
        for k in range(0,1): # selecting the tie points based on minimum sst month occrurrences
            sanya_extreme_mont_ctlpoints[k,j] = np.random.choice(ctl_points_sanya_extreme[k,:],1) 
        for l in range(1,22,2):
            sanya_extreme_mont_ctlpoints[l,j] = np.random.choice(ctl_points_sanya_extreme[l,:],1,[0.01,0.2,0.7,0.09])
        for m in range(2,22,2):
            sanya_extreme_mont_ctlpoints[m,j] = np.random.choice(ctl_points_sanya_extreme[m,:],1,[0.35,0.17,0.28,0.2])
#do the interpolated work         
srca_sanya_extreme = np.empty((120,2000))
for i in range(2000):
    age, srca_sanya_extreme[:,i] = coral_chronology_model(np.arange(1,170,1),depth_sanya_extreme,sanya_extreme_mont_ctlpoints[:,i],coral_data_sanya,1/12)
sst_sanya_extreme = np.empty(shape=(120,2000))
for i in range(2000):
    sst_sanya_extreme[:,i] = (9.824 - srca_sanya_extreme[:,i])/0.04306   
    
# the plateau method
ctl_points_sanya_plateau = np.empty((32,4)) # make an array to reposit potential tie points
for i in range(4):
    ctl_points_sanya_plateau[:,i] = np.array(((sheet_sanya.col_values(i+16))[1:33]),dtype = np.float64) 
# selecting the tie points randomly at particular depth
sanya_plateau_mont_ctlpoints = np.empty((32,2000))#make an array to reposit age of tie points using bootstrap method
for j in range(2000): #set the iterated number
        for k in range(0,1): # selecting the tie points based on minimum sst month occrurrences
            sanya_plateau_mont_ctlpoints[k,j] = np.random.choice(ctl_points_sanya_plateau[k,:],1) 
        for l in range(1,32,3):
            sanya_plateau_mont_ctlpoints[l,j] = np.random.choice(ctl_points_sanya_plateau[l,:],1,[0.01,0.2,0.7,0.09])
        for m in range(2,32,3):
            sanya_plateau_mont_ctlpoints[m,j] = np.random.choice(ctl_points_sanya_plateau[m,:],1)
        for n in range(3,32,3):
            sanya_plateau_mont_ctlpoints[n,j] = np.random.choice(ctl_points_sanya_plateau[n,:],1)
# do the interpolated work   
srca_sanya_plateau = np.empty((120,2000))
for i in range(2000):
    age, srca_sanya_plateau[:,i] = coral_chronology_model(np.arange(1,170,1),depth_sanya_plateau,sanya_plateau_mont_ctlpoints[:,i],coral_data_sanya,1/12)
sst_sanya_plateau = np.empty(shape=(120,2000))
for i in range(2000):
    sst_sanya_plateau[:,i] = (9.824 - srca_sanya_plateau[:,i])/0.04306  
    
# make a function of linear regression to obtain the coffecient of determination 
def linear_output(X,Y):
    lm = LinearRegression()
    lm.fit(X.reshape(len(X),1),Y.reshape(len(Y),1)) #the input parameter,X, must be an array of two dimensiona 
    k = lm.coef_ #obtain K
    b = lm.intercept_ #obtain b
    r_2 = (lm.score(X.reshape(len(X),1),Y.reshape(len(Y),1))).reshape(1,1)
    p = (st.linregress(X,Y))[3] # obtain p-value
    p = np.array([p],dtype = np.float64) 
    return (np.concatenate([r_2,k, b.reshape(len(b),1),p.reshape(len(p),1)],axis = 1))

# define a function to obtain median absolute deviation
def mad(data1,data2):
    value = np.median(abs(abs(data1-data2) - np.median(abs(abs(data1 - data2)))))
    return value

#define a function to obtain phase angle
def phase_angle_wavelet(x,y,dt): #一般默认dt=1 
    phase_angle = 180 * ( (((pycwt.wct(x,y,dt))[1]).mean(axis = 1)[31]) /math.pi)
    return phase_angle


###statistical parameter of the endpoint method###


#obtain the coefficient of determination(R2)
linear_r2_k_b_endpoint_sanya = []   
for i in range(2000):
    result_r2_k_b = linear_output(instrument_sanya, sst_sanya_endpoint[:,i])
    linear_r2_k_b_endpoint_sanya.append(result_r2_k_b)    
r2_endpoint_sanya = np.empty(shape = (2000)) 
for i in range(2000):
    r2_endpoint_sanya[i] = (linear_r2_k_b_endpoint_sanya[i])[:,0]

#obtain the envelope interval for all perturabed values for fig.3a
sst_sanya_endpoint_value_up = np.max(sst_sanya_endpoint,axis = 1)# 
sst_sanya_endpoint_value_down = np.min(sst_sanya_endpoint,axis = 1)

#obtain the Mean Square Value(MSE),MAD,phase angle
mse_endpoint_sanya = np.empty(shape=(2000))
for i in range(2000):
    mse_endpoint_sanya[i] = mean_squared_error(instrument_sanya,sst_sanya_endpoint[:,i])
mad_sanya_endpoint = np.empty(shape = (2000))
for i in range(2000):
    mad_sanya_endpoint[i] = mad(instrument_sanya,sst_sanya_endpoint[:,i])
pa_sanya_endpoint = np.empty(shape = (2000))
for i in range(2000):
    pa_sanya_endpoint[i] = phase_angle_wavelet(instrument_sanya,sst_sanya_endpoint[:,i],1)
#obtain the seasonality 
sst_sanya_endpoint_winter = np.amin(sst_sanya_endpoint.reshape(10,12,2000),axis = 1)
sst_sanya_endpoint_summer = np.amax(sst_sanya_endpoint.reshape(10,12,2000),axis = 1)
sst_sanya_endpoint_seasonality = sst_sanya_endpoint_summer - sst_sanya_endpoint_winter 
sst_sanya_endpoint_seasonality_mean = sst_sanya_endpoint_seasonality.mean(axis = 0)
#obtain the 95th percentile values for phase angles, R2, MSE,MAD and seasonality 
condition_95_pa_endpoint_sanya = pa_sanya_endpoint [(pa_sanya_endpoint >= np.percentile(pa_sanya_endpoint , 2.5)) & (pa_sanya_endpoint  <= np.percentile(pa_sanya_endpoint , 97.5))]
condition_95_r2_endpoint_sanya = r2_endpoint_sanya [(r2_endpoint_sanya >= np.percentile(r2_endpoint_sanya , 2.5)) & (r2_endpoint_sanya  <= np.percentile(r2_endpoint_sanya , 97.5))]
condition_95_mse_endpoint_sanya = mse_endpoint_sanya [(mse_endpoint_sanya >= np.percentile(mse_endpoint_sanya , 2.5)) & (mse_endpoint_sanya  <= np.percentile(mse_endpoint_sanya , 97.5))]
condition_95_mad_endpoint_sanya = mad_sanya_endpoint [(mad_sanya_endpoint >= np.percentile(mad_sanya_endpoint , 2.5)) & (mad_sanya_endpoint  <= np.percentile(mad_sanya_endpoint , 97.5))]
condition_95_seasonality_endpoint_sanya = sst_sanya_endpoint_seasonality_mean [(sst_sanya_endpoint_seasonality_mean >= np.percentile(sst_sanya_endpoint_seasonality_mean , 2.5)) & (sst_sanya_endpoint_seasonality_mean  <= np.percentile(sst_sanya_endpoint_seasonality_mean , 97.5))]


###statistical parameter of the extremet method###


#obtain the coefficient of determination(R2)
linear_r2_k_b_extreme_sanya = []  
for i in range(2000):
    result_r2_k_b = linear_output(instrument_sanya, sst_sanya_extreme[:,i])
    linear_r2_k_b_extreme_sanya.append(result_r2_k_b)    
r2_extreme_sanya = np.empty(shape = (2000))
for i in range(2000):
    r2_extreme_sanya[i] = (linear_r2_k_b_extreme_sanya[i])[:,0]
    
#obtain the envelope interval for all perturabed values for fig.3a
sst_sanya_extreme_value_up = np.max(sst_sanya_extreme,axis = 1)
sst_sanya_extreme_value_down = np.min(sst_sanya_extreme,axis = 1)

#obtain the Mean Square Value(MSE),MAD,phase angle
mse_extreme_sanya = np.empty(shape=(2000))
for i in range(2000):
    mse_extreme_sanya[i] = mean_squared_error(instrument_sanya,sst_sanya_extreme[:,i])
mad_sanya_extreme = np.empty(shape = (2000))
for i in range(2000):
    mad_sanya_extreme[i] = mad(instrument_sanya,sst_sanya_extreme[:,i])
pa_sanya_extreme = np.empty(shape = (2000))
for i in range(2000):
    pa_sanya_extreme[i] = phase_angle_wavelet(instrument_sanya,sst_sanya_extreme[:,i],1)
        
#obtain the seasonality 
sst_sanya_extreme_winter = np.amin(sst_sanya_extreme.reshape(10,12,2000),axis = 1)
sst_sanya_extreme_summer = np.amax(sst_sanya_extreme.reshape(10,12,2000),axis = 1)
sst_sanya_extreme_seasonality = sst_sanya_extreme_summer - sst_sanya_extreme_winter 
sst_sanya_extreme_seasonality_mean = sst_sanya_extreme_seasonality.mean(axis = 0)
#obtain the 95th percentile values for phase angles, R2, MSE,MAD and seasonality 
condition_95_pa_extreme_sanya = pa_sanya_extreme [(pa_sanya_extreme >= np.percentile(pa_sanya_extreme , 2.5)) & (pa_sanya_extreme  <= np.percentile(pa_sanya_extreme , 97.5))]
condition_95_r2_extreme_sanya = r2_extreme_sanya [(r2_extreme_sanya >= np.percentile(r2_extreme_sanya , 2.5)) & (r2_extreme_sanya  <= np.percentile(r2_extreme_sanya , 97.5))]
condition_95_mad_extreme_sanya = mad_sanya_extreme [(mad_sanya_extreme >= np.percentile(mad_sanya_extreme , 2.5)) & (mad_sanya_extreme  <= np.percentile(mad_sanya_extreme , 97.5))]
condition_95_mse_extreme_sanya = mse_extreme_sanya [(mse_extreme_sanya >= np.percentile(mse_extreme_sanya , 2.5)) & (mse_extreme_sanya  <= np.percentile(mse_extreme_sanya , 97.5))]
condition_95_seasonality_extreme_sanya = sst_sanya_extreme_seasonality_mean [(sst_sanya_extreme_seasonality_mean >= np.percentile(sst_sanya_extreme_seasonality_mean , 2.5)) & (sst_sanya_extreme_seasonality_mean  <= np.percentile(sst_sanya_extreme_seasonality_mean , 97.5))]


###statistical parameter of the extremet method###


#obtain the coefficient of determination(R2)
linear_r2_k_b_plateau_sanya = []   
for i in range(2000):
    result_r2_k_b = linear_output(instrument_sanya, sst_sanya_plateau[:,i])
    linear_r2_k_b_plateau_sanya.append(result_r2_k_b)    
r2_plateau_sanya = np.empty(shape = (2000)) #将输出的r2值转换为数组方便计算
for i in range(2000):
    r2_plateau_sanya[i] = (linear_r2_k_b_plateau_sanya[i])[:,0]
#obtain the envelope interval for all perturabed values for fig.3a
sst_sanya_plateau_value_up = np.max(sst_sanya_plateau,axis = 1)# 基于每个时间点的最大值、最小值求包络区间
sst_sanya_plateau_value_down = np.min(sst_sanya_plateau,axis = 1)

#obtain the Mean Square Value(MSE),MAD,phase angle
mse_plateau_sanya = np.empty(shape=(2000))
for i in range(2000):
    mse_plateau_sanya[i] = mean_squared_error(instrument_sanya,sst_sanya_plateau[:,i])
mad_sanya_plateau = np.empty(shape = (2000))
for i in range(2000):
    mad_sanya_plateau[i] = mad(instrument_sanya,sst_sanya_plateau[:,i])
pa_sanya_plateau = np.empty(shape = (2000))
for i in range(2000):
    pa_sanya_plateau[i] = phase_angle_wavelet(instrument_sanya,sst_sanya_plateau[:,i],1)

#obtain the seasonality 
sst_sanya_plateau_winter = np.amin(sst_sanya_plateau.reshape(10,12,2000),axis = 1)
sst_sanya_plateau_summer = np.amax(sst_sanya_plateau.reshape(10,12,2000),axis = 1)
sst_sanya_plateau_seasonality = sst_sanya_plateau_summer - sst_sanya_plateau_winter 
sst_sanya_plateau_seasonality_mean = sst_sanya_plateau_seasonality.mean(axis = 0)
#obtain the 95th percentile values for phase angles, R2, MSE,MAD and seasonality
condition_95_pa_plateau_sanya = pa_sanya_plateau [(pa_sanya_plateau >= np.percentile(pa_sanya_plateau , 2.5)) & (pa_sanya_plateau  <= np.percentile(pa_sanya_plateau , 97.5))]
condition_95_r2_plateau_sanya = r2_plateau_sanya [(r2_plateau_sanya >= np.percentile(r2_plateau_sanya , 2.5)) & (r2_plateau_sanya  <= np.percentile(r2_plateau_sanya , 97.5))]
condition_95_mse_plateau_sanya = mse_plateau_sanya [(mse_plateau_sanya >= np.percentile(mse_plateau_sanya , 2.5)) & (mse_plateau_sanya  <= np.percentile(mse_plateau_sanya , 97.5))]
condition_95_mad_plateau_sanya = mad_sanya_plateau [(mad_sanya_plateau >= np.percentile(mad_sanya_plateau , 2.5)) & (mad_sanya_plateau  <= np.percentile(mad_sanya_plateau , 97.5))]
condition_95_seasonality_plateau_sanya = sst_sanya_plateau_seasonality_mean [(sst_sanya_plateau_seasonality_mean >= np.percentile(sst_sanya_plateau_seasonality_mean , 2.5)) & (sst_sanya_plateau_seasonality_mean  <= np.percentile(sst_sanya_plateau_seasonality_mean , 97.5))]





#####Xisha#####





#Read Excel file of Xisha coral data
ctl_depth = xlrd.open_workbook('E:/interpolate_paper/data_calculation/YXN-1 and SY-1 srca data.xlsx')
sheet_xisha = ctl_depth.sheets()[1]
coral_data_xisha = np.array(((sheet_xisha.col_values(0))[1:]),dtype = np.float64) #Xisha cora Sr/Ca data
instrument_xisha = np.array(((sheet_xisha.col_values(1))[1:337]),dtype = np.float64) #Xisha instrumental SST(hadi)
nino34_1980_2007 = np.array(((sheet_xisha.col_values(2))[1:337]),dtype = np.float64) #Nino3.4 SST(hadi)
depth_xisha_endpoint = np.array(((sheet_xisha.col_values(4))[1:30]),dtype = np.float64) # depth of the endpoind method
depth_xisha_extreme = np.array(((sheet_xisha.col_values(11))[1:58]),dtype = np.float64) # depth of the extreme method
depth_xisha_plateau = np.array(((sheet_xisha.col_values(18))[1:86]),dtype = np.float64) # depth of the plateau method



###Montel Carlo sensitivity test###


##the entpoint method## 
ctl_points_xisha_endpoint = np.empty((29,5)) #make an array to reposit potential tie points
for i in range(5):
    ctl_points_xisha_endpoint[:,i] = np.array(((sheet_xisha.col_values(i+5))[1:30]),dtype = np.float64)  
# selecting the tie points randomly at particular depth
xisha_endpoint_mont_ctlpoints = np.empty((29,2000))#make an array to reposit age of tie points using bootstrap method
for i in range(2000): #set the iterated numbers
        for k in range(29): ## selecting the tie points based on minimum sst month occrurrences
            xisha_endpoint_mont_ctlpoints[k,i] = np.random.choice(ctl_points_xisha_endpoint[k,:],1,[0.05,0.59,0.59,0.36,0.36]) # 
#do the interpolated work and translate sr/ca to SST          
srca_xisha_endpoint = np.empty((336,2000))
for i in range(2000):
    age, srca_xisha_endpoint[:,i] = coral_chronology_model(np.arange(1,719,1),depth_xisha_endpoint,xisha_endpoint_mont_ctlpoints[:,i],coral_data_xisha,1/12)
sst_xisha_endpoint = np.empty(shape=(336,2000))
for i in range(2000):
    sst_xisha_endpoint[:,i] = (10.144 - srca_xisha_endpoint[:,i])/0.0497
    

##the extreme  method## 
ctl_points_xisha_extreme = np.empty((57,5)) #make an array to reposit potential tie points
for i in range(5):
    ctl_points_xisha_extreme[:,i] = np.array(((sheet_xisha.col_values(i+12))[1:58]),dtype = np.float64) 
#selecting the tie points randomly at particular depth
xisha_extreme_mont_ctlpoints = np.empty((57,2000))#make an array to reposit age of tie points using bootstrap method
for j in range(2000): #set the iterated number
        for k in range(0,57,2): #
            xisha_extreme_mont_ctlpoints[k,j] = np.random.choice(ctl_points_xisha_extreme[k,:],1,[0.05,0.59,0.59,0.36,0.36]) # 
        for l in range(1,57,2):
            xisha_extreme_mont_ctlpoints[l,j] = np.random.choice(ctl_points_xisha_extreme[l,:],1,[0.21,0.45,0.09,0.15,0.1])
       
#do the interpolated work and translate sr/ca to SST       
srca_xisha_extreme = np.empty((336,2000))
for i in range(2000):
    age, srca_xisha_extreme[:,i] = coral_chronology_model(np.arange(1,719,1),depth_xisha_extreme,xisha_extreme_mont_ctlpoints[:,i],coral_data_xisha,1/12)
sst_xisha_extreme = np.empty(shape=(336,2000))
for i in range(2000):
    sst_xisha_extreme[:,i] = (10.144 - srca_xisha_extreme[:,i])/0.0497  
    
    
#the plateau method
ctl_points_xisha_plateau = np.empty((85,5)) #make an array to reposit potential tie points
for i in range(5):
    ctl_points_xisha_plateau[:,i] = np.array(((sheet_xisha.col_values(i+19))[1:86]),dtype = np.float64) 
#selecting the tie points randomly at particular depth
xisha_plateau_mont_ctlpoints = np.empty((85,2000))#make an array to reposit age of tie points using bootstrap method
for j in range(2000): #set the iterated number
        for k in range(0,85,2): 
            xisha_plateau_mont_ctlpoints[k,j] = np.random.choice(ctl_points_xisha_plateau[k,:],1,[0.05,0.59,0.59,0.36,0.36]) # 执行控制点随意选取 ctl_points是我们控制点矩阵 每个年龄深度对应一些年龄控制点
        for l in range(1,85,2):
            xisha_plateau_mont_ctlpoints[l,j] = np.random.choice(ctl_points_xisha_plateau[l,:],1)
        for m in range(2,85,2):
            xisha_plateau_mont_ctlpoints[m,j] = np.random.choice(ctl_points_xisha_plateau[m,:],1)    
#do the interpolated work and translate sr/ca to SST     
srca_xisha_plateau = np.empty((336,2000))
for i in range(2000):
    age, srca_xisha_plateau[:,i] = coral_chronology_model(np.arange(1,719,1),depth_xisha_plateau,xisha_plateau_mont_ctlpoints[:,i],coral_data_xisha,1/12)
sst_xisha_plateau = np.empty(shape=(336,2000))
for i in range(2000):
    sst_xisha_plateau[:,i] = (10.144 - srca_xisha_plateau[:,i])/0.0497 

#make a 3-7yr bandpass filter for instrumental SST in Yongxing 
instrument_monthly_xisha = instrument_xisha.reshape(28,12)
instrument_monthly_mean_xisha = (instrument_monthly_xisha.mean(axis = 0)).reshape(1,12)
instrument_monthly_anomaly_xisha = (instrument_monthly_xisha - instrument_monthly_mean_xisha).reshape(336,1) #get anomaly
instrument_enso_xisha = bandpass.butter_bandpass_filter(instrument_monthly_anomaly_xisha.flatten(),1/84,1/36,1) #get filter series

#make a 3-7yr bandpass filter for nino3.4SST
nino34_anomaly = (nino34_1980_2007.reshape(28,12) - nino34_1980_2007.reshape(28,12).mean(axis = 0).reshape(1,12)).reshape(336,1) # get anomaly
nino34_enso = bandpass.butter_bandpass_filter(nino34_anomaly.flatten(),1/84,1/36,1) #get filter series

#get anomaly on the endpoint method
sst_xisha_endpoint = sst_xisha_endpoint.T
sst_xisha_endpoint = sst_xisha_endpoint.reshape(2000,28,12)
sst_xisha_endpoint_monthly_mean = (sst_xisha_endpoint.mean(axis = 1)).reshape(2000,1,12)
sst_xisha_endpoint_monthly_anomaly = sst_xisha_endpoint - sst_xisha_endpoint_monthly_mean
sst_xisha_endpoint_anomaly = (sst_xisha_endpoint_monthly_anomaly.reshape(2000,336)).T
sst_xisha_endpoint = (sst_xisha_endpoint.reshape(2000,336)).T
    
#get anomaly on the extreme method
sst_xisha_extreme = sst_xisha_extreme.T
sst_xisha_extreme = sst_xisha_extreme.reshape(2000,28,12)
sst_xisha_extreme_monthly_mean = (sst_xisha_extreme.mean(axis = 1)).reshape(2000,1,12)
sst_xisha_extreme_monthly_anomaly = sst_xisha_extreme - sst_xisha_extreme_monthly_mean
sst_xisha_extreme_anomaly = (sst_xisha_extreme_monthly_anomaly.reshape(2000,336)).T
sst_xisha_extreme = (sst_xisha_extreme.reshape(2000,336)).T

#get anomaly on the plateau method
sst_xisha_plateau = sst_xisha_plateau.T
sst_xisha_plateau = sst_xisha_plateau.reshape(2000,28,12)
sst_xisha_plateau_monthly_mean = (sst_xisha_plateau.mean(axis = 1)).reshape(2000,1,12)
sst_xisha_plateau_monthly_anomaly = sst_xisha_plateau - sst_xisha_plateau_monthly_mean
sst_xisha_plateau_anomaly = (sst_xisha_plateau_monthly_anomaly.reshape(2000,336)).T
sst_xisha_plateau = (sst_xisha_plateau.reshape(2000,336)).T


#define a function to calculate the spectral power using multitaper method based on pyleoclim packge; quantiles indicate the confidence level
def mtm_mc(time,value,quantiles,numbers):  
    psd_mtm = pyleo.Series(time = time, value = value).standardize().interp().spectral(method = 'mtm',settings = {'NW':1})
    psd_mtm_signif = psd_mtm.signif_test(number = numbers, method='ar1sim',qs = [quantiles])
    frequency = psd_mtm_signif.frequency #X-axis
    amplitude = psd_mtm_signif.amplitude #Y-axis
    significance = psd_mtm_signif.signif_qs.psd_list[0].amplitude #
    return frequency,amplitude,significance #

#define a function to calculate the crosscorrelation; n indicate the window of the lead-lag time.
def leadlagcor_r(data1,data2,n):
    a=-n
    b=-a
    c=b*2+1
    x=np.arange(-n,n+1,1)
    r=np.zeros((c,1))
    p=np.zeros((c,1))
    for i in range(c):
        if i<(b):
            r[n-i],p[n-i]=pearsonr(data1[:(len(data1)-i)], data2[i:])
        else:
            r[i],p[i]=pearsonr(data1[x[i]:], data2[:len(data1)-x[i]])        
        p = np.squeeze(p)
        max_value = max(abs(r))
        index_correl_value = np.where((r == max_value) | (r == max_value * -1))
        index_correl_value = index_correl_value[0]
        r_value = r[index_correl_value]
    return r_value;

# make a fuction to calculate the effective number
def effective_freedom(x,y):
    r_value = pearsonr(x,y)
    r = r_value[0]
    acf_value_x = sm.tsa.acf(x, nlags = math.floor((len(x))/2))
    acf_value_x = acf_value_x[1:]
    acf_value_y = sm.tsa.acf(y, nlags = math.floor((len(y))/2))
    acf_value_y = acf_value_y[1:]
    sigma = np.empty(shape = (math.floor((len(x))/2)))
    for m in range(math.floor((len(x))/2)):
        sigma[m] = (1- m/len(x)) * acf_value_y[m] * acf_value_x[m]
    tao = 1 + 2 * np.sum(sigma[:m-1])
    neff = (len(x))/tao
    t = (abs(r) * math.sqrt(neff -2 ))/math.sqrt(1 - r**2)
    p = stats.t.sf(t,neff)
    return neff,t,p

#Detect the spectral power of instrumental SST;运用定义函数输出并计算西沙器测数据MTM数据Mtm, Fig6a
mtm_x_ins_xisha,mtm_y_ins_xisha,mtm_sig_ins_xisha = mtm_mc(age,instrument_monthly_anomaly_xisha.flatten(),0.95,2000)
mtm_x_ins_xisha = 1/mtm_x_ins_xisha

r_nino34_ins_enso = leadlagcor_r(nino34_enso,instrument_enso_xisha,9)
neff_nino34_ins,t_nino34_nis,p_nino34_ins = effective_freedom(nino34_enso,instrument_enso_xisha)

###statistical parameter of the endpoint method###


#obtain the R2 value 
linear_r2_k_b_endpoint_xisha = []   
for i in range(2000):
    result_r2_k_b = linear_output(instrument_xisha, sst_xisha_endpoint[:,i])
    linear_r2_k_b_endpoint_xisha.append(result_r2_k_b)    
r2_endpoint_xisha = np.empty(shape = (2000)) 
for i in range(2000):
    r2_endpoint_xisha[i] = (linear_r2_k_b_endpoint_xisha[i])[:,0] 

#obtain the envelope interval for all perturabed values for fig.3c
sst_xisha_endpoint_value_up = np.max(sst_xisha_endpoint,axis = 1)# 基于每个时间点的最大值、最小值求包络区间
sst_xisha_endpoint_value_down = np.min(sst_xisha_endpoint,axis = 1)
#obtain the spectral of the endpoint method
mtm_y_endpoint_xisha = np.empty(shape = (168,2000))
mtm_sig_endpoint_xisha = np.empty(shape = (168,2000)) 
for i in range(2000):
    mtm_x_endpoint_xisha,mtm_y_endpoint_xisha[:,i],mtm_sig_endpoint_xisha[:,i] = mtm_mc(age,sst_xisha_endpoint_anomaly[:,i],0.95,100)

#obtain the Mean Square Value(MSE),MAD,phase angle,ENSO signal,R(filtered srca and filtered nino3.4 SST),neff,t,p
mse_endpoint_xisha = np.empty(shape=(2000))
for i in range(2000):
    mse_endpoint_xisha[i] = mean_squared_error(instrument_xisha,sst_xisha_endpoint[:,i])
mad_endpoint_xisha = np.empty(shape = (2000))
for i in range(2000):
    mad_endpoint_xisha[i] = mad(instrument_xisha,sst_xisha_endpoint[:,i])
pa_endpoint_xisha = np.empty(shape = (2000))
for i in range(2000):
    pa_endpoint_xisha[i] = phase_angle_wavelet(instrument_xisha,sst_xisha_endpoint[:,i],1)
endpoint_enso_xisha = np.empty(shape = (336,2000))
for i in range (2000):
    endpoint_enso_xisha[:,i] = bandpass.butter_bandpass_filter(sst_xisha_endpoint_anomaly[:,i].flatten(),1/84,1/36,1)
correl_value_nino34_endpoint_enso_xisha = np.empty(shape = (2000))
for i in range(2000):
    correl_value_nino34_endpoint_enso_xisha[i] = leadlagcor_r(nino34_enso,endpoint_enso_xisha[:,i],6)
    
neff_endpoint_xisha = np.empty(shape = (2000))
t_endpoint_xisha = np.empty(shape = (2000))
p_endpoint_xisha = np.empty(shape = (2000))
for i in range(2000):
    neff_endpoint_xisha[i], t_endpoint_xisha[i], p_endpoint_xisha[i] = effective_freedom(nino34_enso,endpoint_enso_xisha[:,i])

#obtain the seasonality(including winter,summer and mean)
sst_xisha_endpoint_winter = np.amin(sst_xisha_endpoint.reshape(28,12,2000),axis = 1)
sst_xisha_endpoint_summer = np.amax(sst_xisha_endpoint.reshape(28,12,2000),axis = 1)
sst_xisha_endpoint_seasonality = sst_xisha_endpoint_summer - sst_xisha_endpoint_winter 
sst_xisha_endpoint_seasonality_mean = sst_xisha_endpoint_seasonality.mean(axis = 0)
#obtain the 95thpercentile of phase angle,R2,MAD,MSE,R(filtered srca and filtered nino3.4 SST),P,neff,seasonality
condition_95_pa_endpoint_xisha = pa_endpoint_xisha [(pa_endpoint_xisha >= np.percentile(pa_endpoint_xisha , 2.5)) & (pa_endpoint_xisha  <= np.percentile(pa_endpoint_xisha , 97.5))]
condition_95_r2_endpoint_xisha = r2_endpoint_xisha [(r2_endpoint_xisha >= np.percentile(r2_endpoint_xisha , 2.5)) & (r2_endpoint_xisha  <= np.percentile(r2_endpoint_xisha , 97.5))]
condition_95_mad_endpoint_xisha = mad_endpoint_xisha [(mad_endpoint_xisha >= np.percentile(mad_endpoint_xisha , 2.5)) & (mad_endpoint_xisha  <= np.percentile(mad_endpoint_xisha , 97.5))]
condition_95_mse_endpoint_xisha = mse_endpoint_xisha [(mse_endpoint_xisha >= np.percentile(mse_endpoint_xisha , 2.5)) & (mse_endpoint_xisha  <= np.percentile(mse_endpoint_xisha , 97.5))]
condition_95_correl_value_nino34_endpoint_enso_xisha = correl_value_nino34_endpoint_enso_xisha[(correl_value_nino34_endpoint_enso_xisha >= np.percentile(correl_value_nino34_endpoint_enso_xisha, 2.5)) & (correl_value_nino34_endpoint_enso_xisha <= np.percentile(correl_value_nino34_endpoint_enso_xisha, 97.5))]
condition_95_p_endpoint_xisha = p_endpoint_xisha[(p_endpoint_xisha > np.percentile(p_endpoint_xisha, 2.5)) & (p_endpoint_xisha < np.percentile(p_endpoint_xisha, 97.5))]
condition_95_neff_endpoint_xisha = neff_endpoint_xisha[(neff_endpoint_xisha > np.percentile(neff_endpoint_xisha, 2.5)) & (neff_endpoint_xisha < np.percentile(neff_endpoint_xisha, 97.5))]
condition_95_seasonality_endpoint_xisha = sst_xisha_endpoint_seasonality_mean[(sst_xisha_endpoint_seasonality_mean > np.percentile(sst_xisha_endpoint_seasonality_mean, 2.5)) & (sst_xisha_endpoint_seasonality_mean < np.percentile(sst_xisha_endpoint_seasonality_mean, 97.5))]

###figure 6###
mtm_x_endpoint_xisha = 1/mtm_x_endpoint_xisha
mtm_y_2_endpoint_xisha = np.percentile(mtm_y_endpoint_xisha,2.5,axis = 1)
mtm_y_98_endpoint_xisha = np.percentile(mtm_y_endpoint_xisha,97.5,axis = 1)
mtm_y_median_endpoint_xisha = np.percentile(mtm_y_endpoint_xisha,50,axis = 1)
mtm_y_mean_endpoint_xisha = mtm_y_endpoint_xisha.mean(axis = 1)
mtm_sig_2_endpoint_xisha = np.percentile(mtm_sig_endpoint_xisha,2.5,axis = 1)
mtm_sig_98_endpoint_xisha = np.percentile(mtm_sig_endpoint_xisha,97.5,axis = 1)
mtm_sig_mean_endpoint_xisha = mtm_sig_endpoint_xisha.mean(axis = 1)
mtm_sig_50_endpoint_xisha = np.percentile(mtm_sig_endpoint_xisha,50,axis = 1)



###statistical parameter of the extreme method###


#obtain the R2 value 
linear_r2_k_b_extreme_xisha = []
for i in range(2000):
    result_r2_k_b = linear_output(instrument_xisha, sst_xisha_extreme[:,i])
    linear_r2_k_b_extreme_xisha.append(result_r2_k_b)    
r2_extreme_xisha = np.empty(shape = (2000)) #将输出的r2值转换为数组方便计算
for i in range(2000):
    r2_extreme_xisha[i] = (linear_r2_k_b_extreme_xisha[i])[:,0]

#obtain the envelope interval for all perturabed values for fig.3c
sst_xisha_extreme_value_up = np.max(sst_xisha_extreme,axis = 1)# 基于每个时间点的最大值、最小值求包络区间
sst_xisha_extreme_value_down = np.min(sst_xisha_extreme,axis = 1)
#obtain the spectral of the extreme method
mtm_y_extreme_xisha = np.empty(shape = (168,2000))
mtm_sig_extreme_xisha = np.empty(shape = (168,2000)) 
for i in range(2000):
    mtm_x_extreme_xisha,mtm_y_extreme_xisha[:,i],mtm_sig_extreme_xisha[:,i] = mtm_mc(age,sst_xisha_extreme_anomaly[:,i],0.95,100)

#obtain the Mean Square Value(MSE),MAD,phase angle,ENSO signal,R(filtered srca and filtered nino3.4 SST),neff,t,p
mse_extreme_xisha = np.empty(shape=(2000))
for i in range(2000):
    mse_extreme_xisha[i] = mean_squared_error(instrument_xisha,sst_xisha_extreme[:,i])
mad_extreme_xisha = np.empty(shape = (2000))
for i in range(2000):
    mad_extreme_xisha[i] = mad(instrument_xisha,sst_xisha_extreme[:,i])
extreme_enso_xisha = np.empty(shape = (336,2000))
for i in range (2000):
    extreme_enso_xisha[:,i] = bandpass.butter_bandpass_filter(sst_xisha_extreme_anomaly[:,i].flatten(),1/84,1/36,1)
correl_value_nino34_extreme_enso_xisha = np.empty(shape = (2000))
for i in range(2000):
    correl_value_nino34_extreme_enso_xisha[i] = leadlagcor_r(nino34_enso,extreme_enso_xisha[:,i],6) #极值法和nino34海温的相关性
pa_extreme_xisha = np.empty(shape = (2000))
for i in range(2000):
    pa_extreme_xisha[i] = phase_angle_wavelet(instrument_xisha,sst_xisha_extreme[:,i],1)

neff_extreme_xisha = np.empty(shape = (2000))
t_extreme_xisha = np.empty(shape = (2000))
p_extreme_xisha = np.empty(shape = (2000))
for i in range(2000):
    neff_extreme_xisha[i], t_extreme_xisha[i], p_extreme_xisha[i] = effective_freedom(nino34_enso,extreme_enso_xisha[:,i])

#obtain the seasonality(including winter,summer and mean)
sst_xisha_extreme_winter = np.amin(sst_xisha_extreme.reshape(28,12,2000),axis = 1)
sst_xisha_extreme_summer = np.amax(sst_xisha_extreme.reshape(28,12,2000),axis = 1)
sst_xisha_extreme_seasonality = sst_xisha_extreme_summer - sst_xisha_extreme_winter 
sst_xisha_extreme_seasonality_mean = sst_xisha_extreme_seasonality.mean(axis = 0)
#obtain the 95thpercentile of phase angle,R2,MAD,MSE,R(filtered srca and filtered nino3.4 SST),P,neff,seasonality
condition_95_pa_extreme_xisha = pa_extreme_xisha [(pa_extreme_xisha >= np.percentile(pa_extreme_xisha , 2.5)) & (pa_extreme_xisha  <= np.percentile(pa_extreme_xisha , 97.5))]
condition_95_r2_extreme_xisha = r2_extreme_xisha [(r2_extreme_xisha >= np.percentile(r2_extreme_xisha , 2.5)) & (r2_extreme_xisha  <= np.percentile(r2_extreme_xisha , 97.5))]
condition_95_mad_extreme_xisha = mad_extreme_xisha [(mad_extreme_xisha >= np.percentile(mad_extreme_xisha , 2.5)) & (mad_extreme_xisha  <= np.percentile(mad_extreme_xisha , 97.5))]
condition_95_mse_extreme_xisha = mse_extreme_xisha [(mse_extreme_xisha >= np.percentile(mse_extreme_xisha , 2.5)) & (mse_extreme_xisha  <= np.percentile(mse_extreme_xisha , 97.5))]
condition_95_correl_value_nino34_extreme_enso_xisha = correl_value_nino34_extreme_enso_xisha[(correl_value_nino34_extreme_enso_xisha >= np.percentile(correl_value_nino34_extreme_enso_xisha, 2.5)) & (correl_value_nino34_extreme_enso_xisha <= np.percentile(correl_value_nino34_extreme_enso_xisha, 97.5))]
condition_95_p_extreme_xisha = p_extreme_xisha[(p_extreme_xisha > np.percentile(p_extreme_xisha, 2.5)) & (p_extreme_xisha < np.percentile(p_extreme_xisha, 97.5))]
condition_95_neff_extreme_xisha = neff_extreme_xisha[(neff_extreme_xisha > np.percentile(neff_extreme_xisha, 2.5)) & (neff_extreme_xisha < np.percentile(neff_extreme_xisha, 97.5))]
condition_95_seasonality_extreme_xisha = sst_xisha_extreme_seasonality_mean[(sst_xisha_extreme_seasonality_mean > np.percentile(sst_xisha_extreme_seasonality_mean, 2.5)) & (sst_xisha_extreme_seasonality_mean < np.percentile(sst_xisha_extreme_seasonality_mean, 97.5))]

###figure 6###
mtm_x_extreme_xisha = 1/mtm_x_extreme_xisha
mtm_y_2_exreme_xisha = np.percentile(mtm_y_extreme_xisha,2.5,axis = 1)
mtm_y_98_extreme_xisha = np.percentile(mtm_y_extreme_xisha,97.5,axis = 1)
mtm_y_median_extreme_xisha = np.percentile(mtm_y_extreme_xisha,50,axis = 1)
mtm_y_mean_extreme_xisha = mtm_y_extreme_xisha.mean(axis = 1)
mtm_sig_2_extreme_xisha = np.percentile(mtm_sig_extreme_xisha,2.5,axis = 1)
mtm_sig_98_extreme_xisha = np.percentile(mtm_sig_extreme_xisha,97.5,axis = 1)
mtm_sig_mean_extreme_xisha = mtm_sig_extreme_xisha.mean(axis = 1)
mtm_sig_50_extreme_xisha = np.percentile(mtm_sig_extreme_xisha,50,axis = 1)





###statistical parameter of the plateau method###


linear_r2_k_b_plateau_xisha = []   #循环获得2000个斜率和截距值
for i in range(2000):
    result_r2_k_b = linear_output(instrument_xisha, sst_xisha_plateau[:,i])
    linear_r2_k_b_plateau_xisha.append(result_r2_k_b)    
r2_plateau_xisha = np.empty(shape = (2000)) #将输出的r2值转换为数组方便计算
for i in range(2000):
    r2_plateau_xisha[i] = (linear_r2_k_b_plateau_xisha[i])[:,0]

#obtain the envelope interval for all perturabed values for fig.3c
sst_xisha_plateau_value_up = np.max(sst_xisha_plateau,axis = 1)# 基于每个时间点的最大值、最小值求包络区间
sst_xisha_plateau_value_down = np.min(sst_xisha_plateau,axis = 1)

#obtain the spectral of the plateau method
mtm_y_plateau_xisha = np.empty(shape = (168,2000))
mtm_sig_plateau_xisha = np.empty(shape = (168,2000)) 
for i in range(2000):
    mtm_x_plateau_xisha,mtm_y_plateau_xisha[:,i],mtm_sig_plateau_xisha[:,i] = mtm_mc(age,sst_xisha_plateau_anomaly[:,i],0.95,100)

#obtain the Mean Square Value(MSE),MAD,phase angle,ENSO signal,R(filtered srca and filtered nino3.4 SST),neff,t,p
mse_plateau_xisha = np.empty(shape=(2000))
for i in range(2000):
    mse_plateau_xisha[i] = mean_squared_error(instrument_xisha,sst_xisha_plateau[:,i])
mad_plateau_xisha = np.empty(shape = (2000))
for i in range(2000):
    mad_plateau_xisha[i] = mad(instrument_xisha,sst_xisha_plateau[:,i])
plateau_enso_xisha = np.empty(shape = (336,2000))
for i in range (2000):
    plateau_enso_xisha[:,i] = bandpass.butter_bandpass_filter(sst_xisha_plateau_anomaly[:,i].flatten(),1/84,1/36,1)
correl_value_nino34_plateau_enso_xisha = np.empty(shape = (2000))
for i in range(2000):
    correl_value_nino34_plateau_enso_xisha[i] = leadlagcor_r(nino34_enso,plateau_enso_xisha[:,i],6) #极值法和nino34海温的相关性
pa_plateau_xisha = np.empty(shape = (2000))
for i in range(2000):
    pa_plateau_xisha[i] = phase_angle_wavelet(instrument_xisha,sst_xisha_plateau[:,i],1)

neff_plateau_xisha = np.empty(shape = (2000))
t_plateau_xisha = np.empty(shape = (2000))
p_plateau_xisha = np.empty(shape = (2000))
for i in range(2000):
    neff_plateau_xisha[i], t_plateau_xisha[i], p_plateau_xisha[i] = effective_freedom(nino34_enso,plateau_enso_xisha[:,i])

#obtain the seasonality(including winter,summer and mean)
sst_xisha_plateau_winter = np.amin(sst_xisha_plateau.reshape(28,12,2000),axis = 1)
sst_xisha_plateau_summer = np.amax(sst_xisha_plateau.reshape(28,12,2000),axis = 1)
sst_xisha_plateau_seasonality = sst_xisha_plateau_summer - sst_xisha_plateau_winter 
sst_xisha_plateau_seasonality_mean = sst_xisha_plateau_seasonality.mean(axis = 0)
#obtain the 95thpercentile of phase angle,R2,MAD,MSE,R(filtered srca and filtered nino3.4 SST),P,neff,seasonality
condition_95_pa_plateau_xisha = pa_plateau_xisha [(pa_plateau_xisha >= np.percentile(pa_plateau_xisha , 2.5)) & (pa_plateau_xisha  <= np.percentile(pa_plateau_xisha , 97.5))]
condition_95_r2_plateau_xisha = r2_plateau_xisha [(r2_plateau_xisha >= np.percentile(r2_plateau_xisha , 2.5)) & (r2_plateau_xisha  <= np.percentile(r2_plateau_xisha , 97.5))]
condition_95_mad_plateau_xisha = mad_plateau_xisha [(mad_plateau_xisha >= np.percentile(mad_plateau_xisha , 2.5)) & (mad_plateau_xisha  <= np.percentile(mad_plateau_xisha , 97.5))]
condition_95_mse_plateau_xisha = mse_plateau_xisha [(mse_plateau_xisha >= np.percentile(mse_plateau_xisha , 2.5)) & (mse_plateau_xisha  <= np.percentile(mse_plateau_xisha , 97.5))]
condition_95_correl_value_nino34_plateau_enso_xisha = correl_value_nino34_plateau_enso_xisha[(correl_value_nino34_plateau_enso_xisha >= np.percentile(correl_value_nino34_plateau_enso_xisha, 2.5)) & (correl_value_nino34_plateau_enso_xisha <= np.percentile(correl_value_nino34_plateau_enso_xisha, 97.5))]
condition_95_p_plateau_xisha = p_plateau_xisha[(p_plateau_xisha > np.percentile(p_plateau_xisha, 2.5)) & (p_plateau_xisha < np.percentile(p_plateau_xisha, 97.5))]
condition_95_neff_plateau_xisha = neff_plateau_xisha[(neff_plateau_xisha > np.percentile(neff_plateau_xisha, 2.5)) & (neff_plateau_xisha < np.percentile(neff_plateau_xisha, 97.5))]
condition_95_seasonality_plateau_xisha = sst_xisha_plateau_seasonality_mean[(sst_xisha_plateau_seasonality_mean > np.percentile(sst_xisha_plateau_seasonality_mean, 2.5)) & (sst_xisha_plateau_seasonality_mean < np.percentile(sst_xisha_plateau_seasonality_mean, 97.5))]
###figure6###
mtm_x_plateau_xisha = 1/mtm_x_plateau_xisha
mtm_y_2_plateau_xisha = np.percentile(mtm_y_plateau_xisha,2.5,axis = 1)
mtm_y_98_plateau_xisha = np.percentile(mtm_y_plateau_xisha,97.5,axis = 1)
mtm_y_median_plateau_xisha = np.percentile(mtm_y_plateau_xisha,50,axis = 1)
mtm_y_mean_plateau_xisha = mtm_y_plateau_xisha.mean(axis = 1)
mtm_sig_2_plateau_xisha = np.percentile(mtm_sig_plateau_xisha,2.5,axis = 1)
mtm_sig_98_plateau_xisha = np.percentile(mtm_sig_plateau_xisha,97.5,axis = 1)
mtm_sig_mean_plateau_xisha = mtm_sig_plateau_xisha.mean(axis = 1)
mtm_sig_50_plateau_xisha = np.percentile(mtm_sig_plateau_xisha,50,axis = 1)

std_extreme_enso_variance = extreme_enso_xisha.std(axis = 0)
std_endpoint_enso_variance = endpoint_enso_xisha.std(axis = 0)
std_plateau_enso_variance = plateau_enso_xisha.std(axis = 0)
std_ins_enso_variance = instrument_enso_xisha.std()

###ENSO变率分布###
import seaborn as sns
plt.figure(dpi = 600,figsize = (22,20))
f, axes = plt.subplots(1, 1, figsize=(22,20), sharex=True, sharey = True)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus']=False
plt.suptitle('ENSO variance distribution (1980-2008a C.E.)', y=0.95, fontsize = 56)
plt.subplots_adjust(left=None, bottom=0.1, right=None, top=None, wspace=0.18, hspace=0.2)#wspace 子图横向间距， hspace 代表子图间的纵向距离，left 代表位于图像不同位置
font1 = {'family':'Times New Roman','weight':'normal','axes.size':'18','color':'black'} #
font2 = {'weight':'normal','size':'16'}
font3 = {'weight':'normal','size':'14'}

sns.distplot(std_endpoint_enso_variance,hist = False, rug = False, kde_kws = {'color':'grey', 'linestyle':'--','linewidth':6},norm_hist = True, label = 'endpoint',ax = axes)
sns.distplot(std_extreme_enso_variance, hist = False, rug = False, kde_kws = {'color':'blue', 'linestyle':'--','linewidth':6},norm_hist = True, label = 'extreme',ax = axes)
sns.distplot(std_plateau_enso_variance, hist = False, rug = False, kde_kws = {'color':'red', 'linestyle':'--','linewidth':6},norm_hist = True, label = 'plateau',ax = axes)
#sns.distplot(nino34_20_40_ssta_enso_zscore, hist = False, rug = False, kde_kws = {'color':'black', 'linestyle':'--','linewidth':3},norm_hist = True, label = 'Nino3.4 1920-1940',ax = axes[1,1])
#sns.distplot(nino34_80_00_ssta_enso_zscore, hist = False, rug = False, kde_kws = {'color':'grey', 'linestyle':'--','linewidth':3},norm_hist = True, label = '1980-2000',ax = axes[1,1])


#axes.set_title('Kernel value Comparison ', y=1,fontsize = 24,)
axes.set_xlabel('Variance',fontsize = 48,y = 0.1)
axes.set_ylabel('Probability Density',fontsize = 48,x = 0.1)
axes.legend(loc = 2, fontsize = 44)
axes.tick_params(labelsize = 48)
axes.set_xlim([0.2,0.55])
axes.set_ylim([0.1,25])
#plt.savefig('./plteps.eps', format='eps', dpi=2000)
plt.show()
