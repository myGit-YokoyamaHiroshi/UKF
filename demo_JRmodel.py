#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 14:53:08 2021

@author: Hiroshi Yokoyama
"""
from IPython import get_ipython
from copy import deepcopy, copy
get_ipython().magic('reset -sf')
#get_ipython().magic('cls')

import os
current_path = os.path.dirname(__file__)
os.chdir(current_path)

fig_save_dir = current_path + '/figures/ukf/' 
if os.path.exists(fig_save_dir)==False:  # Make the directory for figures
    os.makedirs(fig_save_dir)

current_path = os.getcwd()
param_path   = current_path + '/save_data/' 
if os.path.exists(param_path)==False:  # Make the directory for figures
    os.makedirs(param_path)

    
import matplotlib.pylab as plt
plt.rcParams['font.family']      = 'Arial'#
plt.rcParams['mathtext.fontset'] = 'stix' # math font setting
plt.rcParams["font.size"]        = 26 # Font size


#%%
import sys
sys.path.append(current_path)

from my_modules.my_jansen_rit import *
from scipy import signal as sig
import numpy as np
import joblib
import random

np.random.seed(0)
#%%
def sigmoid(A, k,x,x0,b):
    return (A / (1 + np.exp(-k*(x-x0)))) + b
#%%
# paramter settings for beta oscillation (Jansen & Rit, 1995)

# alpha oscillation
# A    = 3.25 # Amplitude of exitatory neuron
# a    = 100  # time constant of exitatory neuron
# B    = 22   # Amplitude of inhibitory neuron
# b    = 50   # time constant of inhibitory neuron
# 

# #     # beta oscillation
# A    = 3.25 # Amplitude of exitatory neuron
# a    = 100  # time constant of exitatory neuron
# B    = 44   # Amplitude of inhibitory neuron
# b    = 80 # time constant of inhibitory neuron

# theta oscillation
# A    = 3.25
# a    = 20
# B    = 22
# b    = 17

C    = 135  # Num of interneurons
SD   = 22;
MEAN = 220;
P_in = np.random.normal(loc = MEAN, scale = SD, size = 1)
#%%
fs          = 1000
dt          = 1/fs
Nt          = int(6*fs)# + 100
noise_scale = 0.01
t           = np.arange(0,Nt,1)/fs



y           = np.zeros((Nt, 6))
y_init      = y[0,:]
dy          = np.zeros((Nt, 6))
param       = np.zeros((Nt, 4))

A           = 3.25* np.ones(Nt)#sigmoid(4.25-3.25, 2, t, 1.5, 3.25) #+ np.random.normal(loc= 0, scale= .1, size=Nt)
A[t>2.0]    = 4.00
a           = 100  * np.ones(Nt)
B           = 22* np.ones(Nt)#sigmoid(22-20, -2, t, 2.5, 20) #+ np.random.normal(loc= 0, scale= .1, size=Nt)
B[t>2.0]    = 21.5
b           = 50   * np.ones(Nt)
p           = np.random.normal(loc=  220, scale= 22, size=Nt)



dy[0, :]    = func_JR_model(y_init, A[0], a[0], B[0], b[0], p[0])

for i in range(1, Nt):        
    y_now      = y[i-1, :]
    # y_next     = euler_maruyama(dt, func_JR_model, y_now, A[i], a[i], B[i], b[i], p[i], noise_scale)
    y_next     = runge_kutta(dt, func_JR_model, y_now, A[i], a[i], B[i], b[i], p[i])
    dy[i, :]   = func_JR_model(y_now, A[i], a[i], B[i], b[i], p[i])
    y[i, :]    = y_next
    
eeg   = y[:,1]-y[:,2]
param = np.concatenate((A[:,np.newaxis], a[:,np.newaxis], B[:,np.newaxis], b[:,np.newaxis], p[:,np.newaxis]), axis=1)
#%%
############# save_data
param_dict          = {} 
param_dict['fs']    = fs
param_dict['dt']    = dt
param_dict['Nt']    = Nt#-100
param_dict['param'] = param#[100:,:]
param_dict['eeg']   = eeg#[100:]
param_dict['t']     = t#[100:]
param_dict['dy']    = dy
param_dict['y']     = y

save_name   = 'synthetic_data'
fullpath_save   = param_path + save_name 
np.save(fullpath_save, param_dict)
#%%
plt.plot(t, eeg)
plt.xlabel('time (s)')
plt.ylabel('simulated amp. (a.u.)')
# plt.xlim(0, 2)
plt.show()
#%%
frqs, p_welch = sig.welch(eeg, fs, nperseg = Nt/2)
plt.plot(frqs, 10*np.log10(p_welch));
plt.xlim(0, 60)
plt.xlabel('frequency (Hz)')
plt.ylabel('power (dB)')
plt.show()