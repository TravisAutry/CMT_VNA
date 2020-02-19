#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 11:25:09 2020

@author: tma
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from CM_VNA import VNA


A = VNA()


#%%
direc1 = '/home/tma/Documents/Python Scripts/device1/'

A.Rec_Sav_Res(direc = direc1)

