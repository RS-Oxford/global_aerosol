#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    Layer_subplots_June18_AOD.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        19/04/2023 00:54

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

aeolus_lat_shift= 0.

lat1_caliop = 8.25
lat2_caliop = 19.
lat1_aeolus = 11. + aeolus_lat_shift
lat2_aeolus = 18.7 + aeolus_lat_shift

layer1_index = -7
layer1 = [4.42, 5.43]

layer2_index = -6
layer2 = [3.42, 4.42]

layer3_index = -5
layer3 = [2.42, 3.42]

input_path = './aeolus_caliop_sahara2020_extraction_output/'
script_name = os.path.splitext(os.path.abspath(__file__))[0]
save_path = f'{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

# convert qc_aeolus to bits and check the quality of the data
def qc_to_bits(qc_array):
    qc_uint8 = qc_array.astype(np.uint8)
    qc_bits = np.unpackbits(qc_uint8, axis=1)
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)
    return qc_bits

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_ascending_202006181612' in npz_file):
        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']

        cols_to_keep_caliop = []
        for k in range(len(lat_caliop)):
            if lat_caliop[k] > lat1_caliop and lat_caliop[k] < lat2_caliop:
                cols_to_keep_caliop.append(k)

        beta_caliop = beta_caliop[:, cols_to_keep_caliop]
        alpha_caliop = alpha_caliop[:, cols_to_keep_caliop]
        lat_caliop = lat_caliop[cols_to_keep_caliop]

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('aeolus_qc_ascending_202006242042' in npz_file):
        # print the file name and variables in the file
        lat_aeolus = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_aeolus = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        qc_aeolus = np.load(input_path + npz_file, allow_pickle=True)['qc']

        qc_bits = qc_to_bits(qc_aeolus)
        first_bit = qc_bits[:, :, -1]
        second_bit = qc_bits[:, :, -2]

        # Create a boolean mask where the second bit equals 1 (valid data)
        valid_mask_extinction = first_bit == 1
        valid_mask_backscatter = second_bit == 1
        # set invalid data to nan
        alpha_aeolus_qc = np.where(valid_mask_extinction, alpha_aeolus, np.nan)
        beta_aeolus_qc = np.where(valid_mask_backscatter, beta_aeolus, np.nan)

        rows_to_keep_aeolus = []
        for k in range(len(lat_aeolus)):
            if lat_aeolus[k] > lat1_aeolus and lat_aeolus[k] < lat2_aeolus:
                rows_to_keep_aeolus.append(k)
                print(lat_aeolus[k])
                print(alpha_aeolus_qc[k, :])

        beta_aeolus_qc = beta_aeolus_qc[rows_to_keep_aeolus, :]
        alpha_aeolus_qc = alpha_aeolus_qc[rows_to_keep_aeolus, :]
        lat_aeolus = lat_aeolus[rows_to_keep_aeolus]

fontsize = 22

def plot_aerosol_layer(ax, layer, layer_index):
    alpha_caliop_layer = np.zeros(len(lat_caliop))

    for k in range(len(lat_caliop)):
        alt_k = alt_caliop[::-1]
        alpha_k = alpha_caliop[::-1, k]
        alpha_k[np.isnan(alpha_k)] = 0
        mask = (alt_k >= layer[0]) & (alt_k <= layer[1])
        alpha_caliop_layer[k] = np.trapz(alpha_k[mask], alt_k[mask]) / (layer[1] - layer[0])

    alpha_caliop_layer[alpha_caliop_layer <= 0] = np.nan

    ax.plot(lat_aeolus, alpha_aeolus_qc[:, layer_index], 'ro-', label='AEOLUS layer')
    ax.plot(lat_caliop, alpha_caliop_layer, 'bo-', label='CALIOP layer')
    ax.set_xlabel('Latitude', fontsize=fontsize)
    ax.set_ylabel('Extinction [km$^{-1}$]', fontsize=fontsize)
    ax.set_xlim(8., 19.)
    ax.set_ylim(1e-2, 3e0)
    ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.legend(loc='best', fontsize=fontsize)
    ax.set_yscale('log')

layers = [layer1, layer2, layer3]
layer_indices = [layer1_index, layer2_index, layer3_index]

fig, axs = plt.subplots(len(layers), 1, figsize=(16, 8 * len(layers)))

for i, (layer, layer_index) in enumerate(zip(layers, layer_indices)):
    plot_aerosol_layer(axs[i], layer, layer_index)

fig.suptitle('Comparison of AEOLUS and CALIOP Aerosol Extinction at Different Layers', fontsize=fontsize * 1.2, y=1.05)
plt.savefig(save_path + 'aeolus_caliop_alpha_layers.png', dpi=300)


