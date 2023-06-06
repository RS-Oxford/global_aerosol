#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    box_caulle.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/06/2023 13:56

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib import gridspec
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np
import os

# variable file location
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# Define time and latitude range
name = 'Puyehue-Cordón Caulle'
start_time = '2011-06-15'
end_time = '2011-06-20'
lat_top = 0
lat_bottom = -80

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'ash_height'])

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['utc_time', 'thickness', 'latitude', 'ash_height']:
        if column == 'utc_time':
            # Convert utc_time to datetime format
            data[column] = pd.to_datetime(data[column], format='%Y-%m-%dT%H-%M-%S')
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'ash_height']], ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Filter data based on defined start_time, end_time, lat_top, and lat_bottom
all_data = all_data[(all_data['utc_time'] >= start_time) & (all_data['utc_time'] <= end_time) &
                    (all_data['latitude'] >= lat_bottom) & (all_data['latitude'] <= lat_top)]

# Iterate over the rows to check for latitude criterion
all_data['count'] = np.nan
for i, row in all_data.iterrows():
    nearby_records = all_data[(np.abs(all_data['latitude'] - row['latitude']) <= 1) &
                              (all_data['utc_time'] == row['utc_time'])]
    if nearby_records.shape[0] < 5:
        all_data.drop(i, inplace=True)
    else:
        all_data.loc[i, 'count'] = nearby_records.shape[0]
    if i % 1000 == 0:  # Print progress for every 1000 rows
        print(f"Processed {i} rows")


grouped_data_day = all_data.groupby([all_data['utc_time'].dt.date]).agg({'thickness': list, 'ash_height': list}).dropna()

# Prepare boxplot data
box_plot_data = {}
for day, data in grouped_data_day.iterrows():
    box_plot_data[day] = {
        'thickness': data['thickness'],
        'ash_height': data['ash_height']
    }

fig, ax = plt.subplots(2, 1, figsize=(8, 16))

# First subplot for thickness
positions = range(len(box_plot_data))  # Generate numeric positions for the x-axis
thickness_data = [data['thickness'] for data in box_plot_data.values()]
ax[0].boxplot(thickness_data, positions=positions, widths=0.6)
ax[0].set_ylabel('Ash layer thickness [km]', fontsize=18)
ax[0].grid(True)
ax[0].set_title(f"{name}", fontsize=20)
ax[0].tick_params(axis='both', labelsize=18)
ax[0].set_xticklabels([])  # Hide ax0 xticklabels
# ax[0].set_xlim(0, 100)

# Second subplot for ash_height
ax[1].boxplot([data['ash_height'] for data in box_plot_data.values()], positions=positions, widths=0.6)
ax[1].set_ylabel('Ash height [km]', fontsize=18)
ax[1].grid(True)
ax[1].tick_params(axis='both', labelsize=18)
# ax[1].set_xlim(0, 100)
start_time_dt = datetime.strptime(start_time, '%Y-%m-%d')
formatted_start_time = start_time_dt.strftime('%d/%m/%Y')
ax[1].set_xlabel('Days Since T0 (' + formatted_start_time + ')', fontsize=18)

plt.savefig(figure_save_location + '/' + name + '_box.png')
