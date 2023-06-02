#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_thickness_height_subplots.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/06/2023 00:05

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os

# variable file location
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# create save_location folder if not exist
try:
    os.stat(figure_save_location)
except:
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['thickness', 'ash_height', 'latitude'])

for file in files:

    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['thickness', 'ash_height', 'latitude']:
        if column in ['thickness', 'ash_height']:
            # We first split the column into multiple columns
            modified = data[column].str.split(",", expand=True)

            # Case where there is only one value in the cell
            single_value_mask = modified.count(axis=1) == 1
            data.loc[single_value_mask, column] = modified.loc[single_value_mask, 0]

            # Case where there are multiple values in the cell
            multiple_values_mask = ~single_value_mask
            for i, new_column in enumerate(modified.columns):
                data.loc[multiple_values_mask, f"{column}_{i + 1}"] = modified.loc[multiple_values_mask, new_column]

            # Convert the new columns to numeric
            data[column] = pd.to_numeric(data[column], errors='coerce')
            for i in range(modified.shape[1]):
                data[f"{column}_{i + 1}"] = pd.to_numeric(data[f"{column}_{i + 1}"], errors='coerce')
        elif column == 'latitude':
            # Convert the column to numeric
            data[column] = pd.to_numeric(data[column], errors='coerce')

    # Append thickness and ash_height data to the DataFrame
    all_data = all_data.append(data[['thickness', 'ash_height', 'latitude']], ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Define latitude ranges
latitude_ranges = [[60, 90], [30, 60], [-30, 30], [-60, -30], [-90, -60]]

fig, axs = plt.subplots(len(latitude_ranges), 1, figsize=(22, 50), sharex=True)

# Iterate over latitude ranges and create a subplot for each
for i, lat_range in enumerate(latitude_ranges):
    ax = axs[i]

    # Filter data by latitude range
    filtered_data = all_data[(all_data['latitude'] >= lat_range[0]) & (all_data['latitude'] <= lat_range[1])]

    # Bin the 'ash_height' data into levels of 0.2 km from 8 to 30 km
    bins = np.arange(8, 30.2, 0.2)
    labels = bins[:-1] + 0.2 / 2  # Labels are the mid-point of each bin
    filtered_data['ash_height_bin'] = pd.cut(filtered_data['ash_height'], bins=bins, labels=labels)

    # Group by 'ash_height_bin' and calculate the mean and standard deviation 'thickness' for each group
    mean_grouped = filtered_data.groupby('ash_height_bin').mean()
    std_grouped = filtered_data.groupby('ash_height_bin').std()

    # Calculate the count of values in each bin
    count_grouped = filtered_data.groupby('ash_height_bin').count()

    # Use colormap to color each point based on the count of values
    cmap = plt.cm.get_cmap('rainbow')
    norm = plt.Normalize(count_grouped['thickness'].min(), count_grouped['thickness'].max())
    sc = ax.scatter(mean_grouped.index, mean_grouped['thickness'], marker='o', c=count_grouped['thickness'], cmap=cmap,
                    norm=norm, s=100)

    ax.set_xlim(8, 29.)
    ax.set_ylim(0, 3.)

    # Adding the shaded error region
    lower_bound = mean_grouped['thickness'] - std_grouped['thickness']
    upper_bound = mean_grouped['thickness'] + std_grouped['thickness']
    ax.fill_between(mean_grouped.index, lower_bound, upper_bound, color='gray', alpha=0.5)

    ax.set_title(f'Mean Thickness vs. Ash Height for Latitudes {lat_range[0]} to {lat_range[1]}', fontsize=20)
    ax.set_ylabel('Ash Layer Thickness [km]', fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.grid(True)

# Add a colorbar
cbar = fig.colorbar(sc, ax=axs.ravel().tolist(), extend='both', shrink=0.8)
cbar.set_label('Count of measurements', fontsize=18)
cbar.ax.tick_params(labelsize=18)

fig.text(0.5, 0.04, 'Ash Mean Altitude [km]', ha='center', va='center', fontsize=18)
fig.tight_layout()

plt.savefig(figure_save_location + '/' + 'mean_thickness_vs_ash_height_subplots.png')

