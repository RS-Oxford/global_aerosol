#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_modis_aod.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/03/2023 19:11

from pyproj import Proj, transform
from osgeo import osr
import numpy as np
import glob
import h5py
import os

"/neodc/modis/data/MCD19A2/collection6/2020/06/14/"
CALIOP_path = './aeolus_caliop_sahara2020_extraction_output/'
MCD19A2_base_path = "/neodc/modis/data/MCD19A2/collection6"

def mtile_cal(lat, lon):

    x_step = -463.31271653
    y_step = 463.31271653
    # m_y0, m_x0 = -20015109.354, 10007554.677

    tile_width = 1111950.5196666666
    # m_x0, m_y0 = -20015109.35579742, -10007554.677898709
    m_x0, m_y0 = -20015109.35579742, -10007554.677898709

    outProj = Proj('+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs')
    inProj = Proj(init='epsg:4326')
    ho, vo = transform(inProj, outProj, np.array(lon).ravel(), np.array(lat).ravel())
    h = ((ho - m_x0) / tile_width).astype(int)
    v = 17 - ((vo - m_y0) / tile_width).astype(int)
    print(h[0], v[0])
    return f"{h[0]:02}", f"{v[0]:02}"

for npz_file in os.listdir(CALIOP_path):
    if npz_file.endswith('.npz') & ('caliop_dbd' in npz_file):

        year_i = npz_file[-16:-12]
        month_i = npz_file[-12:-10]
        day_i = npz_file[-10:-8]

        MCD19A2_directory = os.path.join(MCD19A2_base_path, year_i, month_i, day_i)

        lat = np.load(CALIOP_path + npz_file, allow_pickle=True)['lat']
        lon = np.load(CALIOP_path + npz_file, allow_pickle=True)['lon']
        aod = np.load(CALIOP_path + npz_file, allow_pickle=True)['aod']

        tile_h1, tile_v1 = mtile_cal(lat[0], lon[0])
        print("MODIS Tile: ", tile_h1, tile_v1)
        tile_h2, tile_v2 = mtile_cal(lat[-1], lon[-1])
        print("MODIS Tile: ", tile_h1, tile_v1)
        # use glob to find "*h{tile_h}v{tile_v}*.hdf" in MCD19A2_directory
        MCD19A2_file1 = glob.glob(MCD19A2_directory + f"/*h{tile_h1}v{tile_v1}*.hdf")[0]
        MCD19A2_file2 = glob.glob(MCD19A2_directory + f"/*h{tile_h2}v{tile_v2}*.hdf")[0]

        # check if the two files are the same, and delete one of them if they are the same
        if MCD19A2_file1 == MCD19A2_file2:
            os.remove(MCD19A2_file2)
            print("The two files are the same, and the second file is deleted.")

        # check if MCD19A2_file1 exists
        if os.path.exists(MCD19A2_file1):
            print("%s file found." % MCD19A2_file1)
        # check if MCD19A2_file2 exists
        if os.path.exists(MCD19A2_file2):
            print("%s file found." % MCD19A2_file2)

        with h5py.File(MCD19A2_file1, "r") as hdf_file:
            # Read the AOD dataset
            aod_data = hdf_file["/Optical_Depth_055"][:]

        print(aod_data.shape)

        quit()


