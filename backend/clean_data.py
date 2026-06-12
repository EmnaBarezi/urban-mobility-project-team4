import pandas as pd
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')

print("Loading data files...")
trips = pd.read_csv(os.path.join(DATA_FOLDER, 'yellow_tripdata_2019-01.csv'))
zones = pd.read_csv(os.path.join(DATA_FOLDER, 'taxi_zone_lookup.csv'))
print(f"Trips loaded: {len(trips)} rows")

# Remove rows where important columns are empty
trips = trips.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'passenger_count', 'trip_distance', 'fare_amount', 'total_amount'])
print(f"After removing empty rows: {len(trips)} rows")

# Remove trips that make no sense
# A trip cannot have 0 or negative distance
trips = trips[trips['trip_distance'] > 0]
# A trip cannot have 0 or negative fare
trips = trips[trips['fare_amount'] > 0]
# A trip cannot have more than 6 passengers (max taxi capacity)
trips = trips[trips['passenger_count'] <= 6]
trips = trips[trips['passenger_count'] > 0]
print(f"After removing bad values: {len(trips)} rows")

# Convert pickup and dropoff columns to proper date format
trips['tpep_pickup_datetime'] = pd.to_datetime(trips['tpep_pickup_datetime'])
trips['tpep_dropoff_datetime'] = pd.to_datetime(trips['tpep_dropoff_datetime'])

# Keep only trips from January 2019
trips = trips[trips['tpep_pickup_datetime'].dt.year == 2019]
trips = trips[trips['tpep_pickup_datetime'].dt.month == 1]
print(f"After keeping only January 2019: {len(trips)} rows")

# Add 3 new useful columns (derived features)
# 1. Trip duration in minutes
trips['trip_duration_minutes'] = (trips['tpep_dropoff_datetime'] - trips['tpep_pickup_datetime']).dt.total_seconds() / 60

# 2. Speed in miles per hour
trips['speed_mph'] = trips['trip_distance'] / (trips['trip_duration_minutes'] / 60)

# 3. Hour of the day the trip started
trips['pickup_hour'] = trips['tpep_pickup_datetime'].dt.hour

# Remove trips with impossible duration or speed
trips = trips[trips['trip_duration_minutes'] > 0]
trips = trips[trips['trip_duration_minutes'] < 180]
trips = trips[trips['speed_mph'] < 100]
print(f"After removing impossible trips: {len(trips)} rows")

# Connect trips with zone names using LocationID
trips = trips.merge(zones[['LocationID', 'Borough', 'Zone']], left_on='PULocationID', right_on='LocationID', how='left')
trips = trips.rename(columns={'Borough': 'pickup_borough', 'Zone': 'pickup_zone'})
trips = trips.drop(columns=['LocationID'])

trips = trips.merge(zones[['LocationID', 'Borough', 'Zone']], left_on='DOLocationID', right_on='LocationID', how='left')
trips = trips.rename(columns={'Borough': 'dropoff_borough', 'Zone': 'dropoff_zone'})
trips = trips.drop(columns=['LocationID'])

print(f"Final clean dataset: {len(trips)} rows")

# Save the cleaned data to a new file
OUTPUT_PATH = os.path.join(DATA_FOLDER, 'cleaned_trips.csv')
trips.to_csv(OUTPUT_PATH, index=False)
print(f"Cleaned data saved to: {OUTPUT_PATH}")