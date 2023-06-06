#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    box_calbuco.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/06/2023 16:29

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
variable_file_location = './thickness_data_extraction_extinction'
figure_save_location = './figures'

# Define time and latitude range
name = 'Calbuco'
start_time = '2015-04-22'
end_time = '2015-07-25'
lat_top = 0
lat_bottom = -50

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'ash_height', 'extinction'])

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['utc_time', 'thickness', 'latitude', 'ash_height', 'extinction']:  # include 'extinction'
        if column == 'utc_time':
            # Convert utc_time to datetime format
            data[column] = pd.to_datetime(data[column], format='%Y-%m-%dT%H-%M-%S')
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'ash_height', 'extinction']], ignore_index=True)  # include 'extinction'


# Remove rows with any NaN values
all_data = all_data.dropna()

# Filter data based on defined start_time, end_time, lat_top, and lat_bottom
all_data = all_data[(all_data['utc_time'] >= start_time) & (all_data['utc_time'] <= end_time) &
                    (all_data['latitude'] >= lat_bottom) & (all_data['latitude'] <= lat_top)]

# Set utc_time as the index for resampling
all_data.set_index('utc_time', inplace=True)

# Resample to daily frequency, fill missing values with NaN
all_data_daily = all_data.resample('D').mean().fillna(np.nan)

# Iterate over the rows to check for latitude criterion
all_data_daily['count'] = np.nan

for i, row in all_data_daily.iterrows():
    print(all_data_daily.index , row.name)
    nearby_records = all_data_daily[(np.abs(all_data_daily['latitude'] - row['latitude']) <= 1) &
                                    (all_data_daily.index == row.name)]
    if nearby_records.shape[0] < 5:
        all_data_daily.loc[i, 'count'] = np.nan
    else:
        all_data_daily.loc[i, 'count'] = nearby_records.shape[0]
    if i.day % 10 == 0:  # Print progress for every 10 days
        print(f"Processed till {i}")

grouped_data_time = all_data_daily.groupby(['utc_time']).agg({'thickness': np.mean, 'ash_height': np.mean, 'extinction': np.mean})  # include 'extinction'
# Now group these means by day
grouped_data_day = grouped_data_time.groupby([grouped_data_time.index.date]).agg({'thickness': list, 'ash_height': list, 'extinction': list}).dropna()  # include 'extinction'

# Prepare boxplot data
box_plot_data = {}
for day, data in grouped_data_day.iterrows():
    box_plot_data[day] = {
        'thickness': data['thickness'],
        'ash_height': data['ash_height'],
        'extinction': data['extinction']  # include 'extinction'
    }

fig, ax = plt.subplots(1, 3, figsize=(24, 8))

start_date = min(box_plot_data.keys())
x_labels = [(day - start_date).days for day in box_plot_data.keys()]
start_time_dt = datetime.strptime(start_time, '%Y-%m-%d')
formatted_start_time = start_time_dt.strftime('%d/%m/%Y')

# First subplot for thickness
positions = range(len(box_plot_data))  # Generate numeric positions for the x-axis
thickness_data = [data['thickness'] for data in box_plot_data.values()]
bp0 = ax[0].boxplot(thickness_data, positions=positions, widths=0.6)
for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
    plt.setp(bp0[element], color='#FF851B')
ax[0].set_ylabel('Ash layer thickness [km]', fontsize=18)
ax[0].set_xlim(0., 50)
ax[0].set_ylim(0, 4.)
ax[0].set_title(f"{name}", fontsize=20)
ax[0].tick_params(axis='both', labelsize=18)

ax[0].set_xticks(positions[::5])  # add this
ax[0].set_xticklabels(x_labels[::5])  # add this
ax[0].set_xlabel('Days Since T0 (' + formatted_start_time + ')', fontsize=18)


# Second subplot for ash_height
bp1 = ax[1].boxplot([data['ash_height'] for data in box_plot_data.values()], positions=positions, widths=0.6)
for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
    plt.setp(bp1[element], color='#FF4136')
ax[1].set_xlim(0., 50)
ax[1].set_ylabel('Ash height [km]', fontsize=18)
# ax[1].grid(True)
ax[1].tick_params(axis='both', labelsize=18)
ax[1].set_ylim(15, 22.)
ax[1].set_title(f"{name}", fontsize=20)
ax[1].set_xticklabels([])
# ax[1].set_xlim(0, 100)
ax[1].set_xticks(positions[::5])  # add this
ax[1].set_xticklabels(x_labels[::5])  # add this
ax[1].set_xlabel('Days Since T0 (' + formatted_start_time + ')', fontsize=18)

bp2 = ax[2].boxplot([data['extinction'] for data in box_plot_data.values()], positions=positions, widths=0.6)  # add this
for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
    plt.setp(bp2[element], color='#3D9970')
ax[2].set_xlim(0., 50)
ax[2].set_ylabel('Extinction [km$^{-1}$]', fontsize=18)  # you might want to adjust this label
ax[2].tick_params(axis='both', labelsize=18)
ax[2].set_ylim(0, 0.3)  # Set the appropriate y limits for your extinction data
ax[2].set_title(f"{name}", fontsize=20)
ax[2].set_xticks(positions[::5])  # add this
ax[2].set_xticklabels(x_labels[::5])  # add this
ax[2].set_xlabel('Days Since T0 (' + formatted_start_time + ')', fontsize=18)

plt.savefig(figure_save_location + '/' + name + '_box.png')
