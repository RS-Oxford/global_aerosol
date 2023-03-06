#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_SEVIRI_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 16:14

from datetime import datetime

def get_SEVIRI_CLM(dt):

    """Round a time object to the closest 15-minute interval."""
    minutes = dt.minute
    # Calculate the number of minutes to add or subtract to get to the nearest 15-minute interval
    remainder = minutes % 15
    if remainder < 8:
        rounded_minutes = minutes - remainder
    else:
        rounded_minutes = minutes + (15 - remainder)
    # Round the time object to the nearest 15-minute interval
    rounded = datetime(dt.year, dt.month, dt.day, dt.hour, rounded_minutes)
    formatted = datetime.strftime(rounded, '%Y%m%d%H%M%S')
    return formatted


if __name__ == '__main__':

    now = datetime.now()
    formatted = get_SEVIRI_CLM(now)
    print("Original datetime:", now)
    print("Formatted rounded datetime:", formatted)

