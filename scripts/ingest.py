from fitparse import FitFile
import pandas as pd
import os, io, gpxpy

############### Functions for Data Ingestion ###################

## 1) Ingestion from .gpx file

# def gpx_to_dataframe(gpx_file_path: str) -> pd.core.frame.DataFrame:

#     '''
#     Ingest data from .gpx filetype

#     Inputs:
#         - gpx_file_path (str): string containing relative filepath to .gpx file

#     Returns:
#         - df (pd.core.frame.DataFrame): pandas dataframe containing parsed activity data

#     '''

#     # Open and parse the GPX file storing data in "gpxpy.gpx.GPX" object
#     with open(gpx_file_path, 'r') as gpx_file:
#         gpx = gpxpy.parse(gpx_file)
#     # Extract track point data
#     track_data = []

#     for track in gpx.tracks:
#         for segment in track.segments:
#             for point in segment.points:
#                 # Basic GPX metrics
#                 point_dict = {
#                     'time': point.time,
#                     'latitude': point.latitude,
#                     'longitude': point.longitude,
#                     'elevation_meters': point.elevation
#                 }
                
#                 # Extract Garmin extensions (Heart Rate, Cadence, etc.) if available
#                 if point.extensions:
#                     for extension in point.extensions:
#                         # Common Garmin TrackpointExtension namespaces
#                         if 'TrackpointExtension' in extension.tag:
#                             for child in extension:
#                                 # Cleans tag name from XML namespace (e.g., '{...}hr' -> 'hr')
#                                 clean_tag = child.tag.split('}')[-1]
#                                 point_dict[clean_tag] = float(child.text) if child.text else None

#                 track_data.append(point_dict)
                
#     # Convert list of dicts to Pandas DataFrame
#     df = pd.DataFrame(track_data)
    
#     # Optional: Clean up timestamp formatting
#     if 'time' in df.columns:
#         df['time'] = pd.to_datetime(df['time'])
        
#     return df

# Example usage:
# df = gpx_to_dataframe('your_activity.gpx')
# print(df.head())

## 2) Ingestion from ".fit" file

def fit_to_dataframe(fit_file_path: str) -> tuple[pd.core.frame.DataFrame, dict]:
    """
    Parses a Garmin binary .fit file and extracts individual record data points.
    
    '''
    Inputs:
        - fit_file_path (str): string containing relative filepath to .fit file

    Returns:
        - tuple: (pd.DataFrame of activity data, dict of {column_name: unit})
    '''
    
    """
    fitfile = FitFile(fit_file_path)
    records = []
    units = {}
    
    # Iterate through all data messages in the file
    for record in fitfile.get_messages('record'):
        record_data = {}
        for data in record:
            record_data[data.name] = data.value
            if data.units and data.name not in units:
                units[data.name] = data.units
        records.append(record_data)
    df = pd.DataFrame(records)
    df.attrs['units'] = units
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df, units

# Usage: df_fit = fit_to_dataframe('activity.fit')

## 3) Ingestion from .CSV file
# def csv_to_dataframe(csv_file_path: str) -> tuple[pd.core.frame.DataFrame, dict]:
#     """
#     Parses a Garmin web-exported .csv file, automatically removing top metadata layers.
    
#     '''
#     Inputs:
#         - csv_file_path (str): string containing relative filepath to .csv file

#     Returns:
#         - tuple: (pd.DataFrame of activity data, dict of {column_name: unit})
#     '''
    
#     """

#     metadata_lines = []
#     data_lines = []
#     is_data_block = False
    
#     # 1. Read file to dynamically isolate metadata from tabular fields
#     with open(csv_file_path, 'r', encoding='utf-8') as file:
#         for line in file:
#             cleaned_line = line.strip()
#             if not cleaned_line:
#                 continue
                
#             # Detect where the actual tabular column grid begins
#             if any(marker in cleaned_line for marker in ['Activity Type', 'Time', 'Date', 'Title']):
#                 is_data_block = True
            
#             if is_data_block:
#                 data_lines.append(line)
#             else:
#                 metadata_lines.append(cleaned_line)
                
#     # 2. Ingest isolated data lines directly into Pandas
#     data_string_io = io.StringIO(''.join(data_lines))
#     df = pd.read_csv(data_string_io)
#     df = df.dropna(how='all') # Wipe blank trailing artifact lines
    
#     # 3. Parse Metadata block to map column names to units
#     # (Garmin lists these as raw text rows above the data block, e.g., "Distance,Kilometers")
#     units_dict = {}
#     for meta_line in metadata_lines:
#         parts = [p.strip() for p in meta_line.split(',')]
#         if len(parts) >= 2:
#             key, unit = parts[0], parts[1]
#             # Match metadata keys to parsed dataframe column headers safely
#             for col in df.columns:
#                 if key.lower() in col.lower() and unit:
#                     units_dict[col] = unit
#                     break
                    
#     # Fill in fallback structural defaults for core columns that lack a metadata flag
#     for col in df.columns:
#         if col not in units_dict:
#             if 'time' in col.lower() or 'duration' in col.lower():
#                 units_dict[col] = 'hh:mm:ss'
#             elif 'date' in col.lower():
#                 units_dict[col] = 'YYYY-MM-DD'
#             else:
#                 units_dict[col] = 'Raw Count / String'

#     return df, units_dict

# Usage: df_csv = parse_garmin_csv_to_dataframe('activity.csv')


############ Test Parsing on Sample Activity Files ###############

#df = gpx_to_dataframe("../activities/sample/activity_23102315093.gpx")
#df, units = csv_to_dataframe("../activities/sample/activity_23102315093.csv")
df, units = fit_to_dataframe("../activities/sample/23102315093_ACTIVITY.fit")
# df.to_csv("test.csv")
# print(df.head())
# print("Units: ", units)