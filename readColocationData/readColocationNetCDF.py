#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    readColocationNetCDF.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        29/01/2023 13:24

from netCDF4 import Dataset
import geopy.distance
import numpy as np

def extractColocationParameters(inputNetCDF):

    with Dataset(inputNetCDF, 'r') as nc_data:
        lat_colocation = nc_data['colocation_info']['latitude'][:]
        lon_colocation = nc_data['colocation_info']['longitude'][:]

        lat_aeolus = nc_data['aeolus_data']['aeolus_latitude'][:]
        lon_aeolus = nc_data['aeolus_data']['aeolus_longitude'][:]
        alt_aeolus = nc_data['aeolus_data']['aeolus_altitude'][:]
        beta_aeolus = nc_data['aeolus_data']['aeolus_beta'][:]
        alpha_aeolus = nc_data['aeolus_data']['aeolus_alpha'][:]

        lat_caliop = nc_data['caliop_data']['caliop_latitude'][:]
        lon_caliop = nc_data['caliop_data']['caliop_longitude'][:]
        alt_caliop = nc_data['caliop_data']['caliop_altitude'][:]
        beta_caliop = nc_data['caliop_data']['caliop_beta'][:]

    aeolus_index_x = np.argmin(abs(lat_aeolus - lat_colocation))

    # calculate and find the closest distance point

    colocation_distance_list = [
        geopy.distance.geodesic((lat_colocation, lon_colocation), (lat_caliop[s], lon_caliop[s])).km for s in
        range(len(lat_caliop))]
    colocation_distance_array = np.asarray(colocation_distance_list)
    caliop_index_x = np.argmin(colocation_distance_array)

    caliop_index_x_min = caliop_index_x - 50
    caliop_index_x_max = caliop_index_x + 50

    # If the start index is negative, set it to 0
    if caliop_index_x_min < 0:
        caliop_index_x_min = 0
    # If the end index is greater than the length of the lat_aeolus array, set it to the length of the array
    if caliop_index_x_max > len(colocation_distance_array):
        caliop_index_x_max = len(colocation_distance_array)

    alt_aeolus_centre = alt_aeolus[:, aeolus_index_x]
    alt_aeolus_centre = alt_aeolus_centre * 1e-3

    beta_aeolus_centre = beta_aeolus[:, aeolus_index_x]

    beta_aeolus_stats = []

    for k in range(np.size(alt_aeolus_centre)):
        if alt_aeolus_centre[k] > 0:
            if (k + 1) < len(alt_aeolus_centre):

                beta_aeolus_stats.append(beta_aeolus_centre[k] * 1.e-6 * 1.e3) # scaling factor, and unit conversion
                print(beta_aeolus_centre[k] * 1.e-6 * 1.e3)
                print(caliop_index_x_min, caliop_index_x_max)
                beta_caliop_filter = beta_caliop[(alt_caliop < alt_aeolus_centre[k]) & (alt_caliop > alt_aeolus_centre[k+1]), caliop_index_x_min : caliop_index_x_max]
                print(beta_caliop)
                print(beta_caliop_filter)
                beta_caliop_stats = np.nanmean(beta_caliop_filter)
                print(beta_caliop_stats)

    quit()
    # print(alt_caliop)
    # quit()