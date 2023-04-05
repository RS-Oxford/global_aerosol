#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_crs_analysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/04/2023 00:06

import matplotlib.pyplot as plt
from osgeo import gdal
import numpy as np
import glob
import csv
import os
import re

CALIOP_path = './aeolus_caliop_sahara2020_extraction_output/'
specific_filename_1 = 'caliop_dbd_descending_202006180342'
specific_filename_2 = 'caliop_dbd_ascending_202006171527'

sepcific_filename_3 = 'aeolus_descending_202006180757'

caliop_filename = []
caliop_lat_all = []
caliop_lon_all = []
caliop_aod_all = []

for npz_file in os.listdir(CALIOP_path):
    if npz_file.endswith('%s.npz'%specific_filename_1) & ('caliop_dbd_' in npz_file):

        lat_caliop_1 = np.load(CALIOP_path + npz_file, allow_pickle=True)['lat']
        lon_caliop_1 = np.load(CALIOP_path + npz_file, allow_pickle=True)['lon']
        aod_caliop_1 = np.load(CALIOP_path + npz_file, allow_pickle=True)['aod']

    if npz_file.endswith('%s.npz'%specific_filename_2) & ('caliop_dbd_' in npz_file):

        lat_caliop_2 = np.load(CALIOP_path + npz_file, allow_pickle=True)['lat']
        lon_caliop_2 = np.load(CALIOP_path + npz_file, allow_pickle=True)['lon']
        aod_caliop_2 = np.load(CALIOP_path + npz_file, allow_pickle=True)['aod']

    if npz_file.endswith('%s.npz'%sepcific_filename_3) & ('aeolus_' in npz_file):

        lat_aeolus_1 = np.load(CALIOP_path + npz_file, allow_pickle=True)['lat']
        lon_aeolus_1 = np.load(CALIOP_path + npz_file, allow_pickle=True)['lon']
        alt_aeolus_1 = np.load(CALIOP_path + npz_file, allow_pickle=True)['alt']
        alpha_aeolus_1 = np.load(CALIOP_path + npz_file, allow_pickle=True)['alpha']

        print(alt_aeolus_1.shape)
        quit()


# plt aod_caliop
plt.figure(figsize=(16,8))
plt.plot(lat_caliop_1, aod_caliop_1, 'ro-', label='CALIOP Descending')
plt.plot(lat_caliop_2, aod_caliop_2, 'bo-', label='CALIOP Ascending')
plt.xlabel('Latitude')
plt.ylabel('AOD 532 nm')
plt.title('CALIOP AOD 532 nm')
plt.legend(loc='best')
plt.savefig(CALIOP_path + 'caliop_aod_532nm_crs1.png', dpi=300)

