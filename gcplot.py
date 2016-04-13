import csv
import pandas as pd
import logging
import numpy as np
import matplotlib.pyplot as plt
import datetime
import tempfile
import shutil

activity_header_human = ['Activity ID','Activity Name','Description','Begin Timestamp','Begin Timestamp (Raw Milliseconds)','End Timestamp',
'End Timestamp (Raw Milliseconds)','Device','Activity Parent','Activity Type','Event Type','Activity Time Zone','Max. Elevation','Max. Elevation (Raw)',
'Begin Latitude (Decimal Degrees Raw)','Begin Longitude (Decimal Degrees Raw)','End Latitude (Decimal Degrees Raw)','End Longitude (Decimal Degrees Raw)',
'Average Moving Speed','Average Moving Speed (Raw)','Max. Heart Rate (bpm)','Average Heart Rate (bpm)','Max. Speed','Max. Speed (Raw)','Calories',
'Calories (Raw)','Duration (h:m:s)','Duration (Raw Seconds)','Moving Duration (h:m:s)','Moving Duration (Raw Seconds)','Average Speed','Average Speed (Raw)',
'Distance','Distance (Raw)','Min. Heart Rate (bpm)','Min. Elevation','Min. Elevation (Raw)','Elevation Gain','Elevation Gain (Raw)','Elevation Loss','Elevation Loss (Raw)']

activity_header_computer = ['activity_id','activity_name','description','begin_timestamp','begin_timestamp_ms','end_timestamp','end_timestamp_ms','device',
'activity_parent','activity_type','event_type','activity_time_zone','max_elevation','max_elevation_raw','begin_latitude_deg_raw','begin_longitude_deg_raw',
'end_latitude_deg_raw','end_longitude_deg_raw','average_moving_speed','average_moving_speed_raw','max_heart_rate_bpm','average_heart_rate_bpm','max_speed',
'max_speed_raw','calories','calories_raw','duration','duration_seconds','moving_duration','moving_duration_seconds','average_speed','average_speed_raw',
'distance','distance_raw','min_heart_rate_bpm','min_elevation','min_elevation_raw','elevation_gain','elevation_gain_raw','elevation_loss','elevation_loss_raw']


def get_human_readable_name(serie_name):
    if serie_name not in activity_header_computer:
        return ''
    else:
        return activity_header_human[activity_header_computer.index(serie_name)]

def get_numeric_data_list(csv_file):
    activities = get_activities(csv_file)

    # only keep the numeric columns
    activities_numeric = activities.select_dtypes(include=[np.number])
    return activities_numeric.columns.values


def convert_ms_ts_to_date(ts):
    return datetime.datetime.fromtimestamp(ts/1000)

def clean_csv_file(orig):
    fd, clean = tempfile.mkstemp()
    with open(clean, 'w') as csv_out:
        writer = csv.writer(csv_out, delimiter=',', quotechar='"')
        with open(orig, 'r') as csv_in:
            reader = csv.reader(csv_in, delimiter=',', quotechar='"')

            # Get the length of the row with the titles : this will be the standard
            header_len = len (next(reader))

            # Get back
            csv_in.seek(0)

            for row in reader:

                # Add empty fields to lines too short - this should not happen
                for i in range(header_len - len(row)):
                    logging.debug("adding padding to an incomplete row")
                    row.extend([''])

                # Clamp lines too long : this is pretty common
                writer.writerow(row[0:header_len])

    shutil.move(clean, orig)

def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


def get_activities(csv_file):
    
    # Create a clean copy of the csv file
    #clean_csv_file(csv_file)

    # Load with pandas
    activities = pd.read_csv(csv_file, delimiter=',', quotechar='"', )

    # Reformat the header for computer use
    activities.columns = activity_header_computer

    # Format the dates properly
    activities['begin_timestamp'] = activities['begin_timestamp_ms'].apply(convert_ms_ts_to_date)

    # Sort by date
    activities = activities.sort_values(by='begin_timestamp_ms')

    # Use date as index
    activities.index = activities.begin_timestamp

    return activities
    

def get_label_from_field(data_field):

    if 'begin_timestamp' in data_field:
        return 'Date'
    elif 'elevation' in data_field:
        return 'Elevation [m]'
    elif 'speed' in data_field:
        return 'Speed [min/km]'
    elif 'duration' in data_field:
        return 'Duration [seconds]'
    else:
        return ''
