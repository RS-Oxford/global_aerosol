#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_aeolus.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        08/01/2023 12:52

# import the necessary modules
from netCDF4 import num2date
from netCDF4 import Dataset
import numpy as np
import logging

def extract_variables_from_aeolus(nc_file, logger):
    """Extract relevant variables from the AEOLUS data"""

    # open the netcdf file
    with Dataset(nc_file, 'r') as nc_data:

        # Extract relevant variables from the AEOLUS data

        L1B_start_time_obs = list(map(int, nc_data['observations']['L1B_start_time_obs'][:]))
        latitude_of_DEM_intersection_obs = nc_data['observations']['latitude_of_DEM_intersection_obs'][:]
        longitude_of_DEM_intersection_obs = nc_data['observations']['longitude_of_DEM_intersection_obs'][:]
        sca_observation_time = list(map(int, nc_data['sca']['SCA_time_obs'][:]))

        sca_middle_bin_altitude_obs = nc_data['sca']['SCA_middle_bin_altitude_obs'][:]
        sca_middle_bin_backscatter = nc_data['sca']['SCA_middle_bin_backscatter'][:]
        sca_middle_bin_extinction = nc_data['sca']['SCA_middle_bin_extinction'][:]

    latitude_of_DEM_intersection_obs[1:] = latitude_of_DEM_intersection_obs[0:len(latitude_of_DEM_intersection_obs) - 1]
    longitude_of_DEM_intersection_obs[1:] = longitude_of_DEM_intersection_obs[0:len(latitude_of_DEM_intersection_obs) - 1]

    # Convert time variables to datetime objects
    sca_observation_time_dt = num2date(sca_observation_time, units="s since 2000-01-01",
                                       only_use_cftime_datetimes=False)
    L1B_start_time_obs_dt = num2date(L1B_start_time_obs, units="s since 2000-01-01",
                                     only_use_cftime_datetimes=False)

    # Initialize lists to store selected AEOLUS data
    sca_observation_time_list = []
    sca_lat_obs_list = []
    sca_lon_obs_list = []
    sca_alt_obs_list = []
    sca_middle_bin_backscatter_list = []
    sca_middle_bin_extinction_list = []

    # Iterate through the AEOLUS data, selecting only data points that have a corresponding L1B_start_time_obs value

    for time, lat, lon, alt, backscatter, extinction in zip(sca_observation_time_dt, latitude_of_DEM_intersection_obs,
                                                            longitude_of_DEM_intersection_obs, sca_middle_bin_altitude_obs,
                                                            sca_middle_bin_backscatter, sca_middle_bin_extinction):
        if time in L1B_start_time_obs_dt:
            sca_observation_time_list.append(time)
            sca_lat_obs_list.append(lat)
            sca_lon_obs_list.append(lon)
            sca_alt_obs_list.append(alt)
            sca_middle_bin_backscatter_list.append(backscatter)
            sca_middle_bin_extinction_list.append(extinction)

    sca_observation_time_array = np.asarray(sca_observation_time_list)
    sca_lat_obs_array = np.asarray(sca_lat_obs_list)
    sca_lon_obs_array = np.asarray(sca_lon_obs_list)
    sca_alt_obs_array = np.asarray(sca_alt_obs_list)
    sca_middle_bin_backscatter_array = np.asarray(sca_middle_bin_backscatter_list)
    sca_middle_bin_extinction_array = np.asarray(sca_middle_bin_extinction_list)

    # Update longitude values
    sca_lon_obs_array[sca_lon_obs_array > 180.] -= 360.

    # Log a message indicating that the data has been extracted
    logger.info("Extracted data from AEOLUS file")

    return sca_lat_obs_array, sca_lon_obs_array, sca_alt_obs_array, sca_observation_time_array, sca_middle_bin_backscatter_array

