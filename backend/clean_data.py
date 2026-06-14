import pandas as pd
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')

print("Loading data files...")
trips = pd.read_csv(os.path.join(DATA_FOLDER, 'yellow_tripdata_2019-01.csv'))
zones = pd.read_csv(os.path.join(DATA_FOLDER, 'taxi_zone_lookup.csv'))
print(f"Trips loaded: {len(trips)} rows")

audit_log = []
audit_log.append(f"Starting rows: {len(trips)}")

before = len(trips)
trips = trips.drop_duplicates()
after = len(trips)
audit_log.append(f"Removed {before - after} duplicate rows. Remaining: {after}")

before = len(trips)
trips = trips.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'passenger_count', 'trip_distance', 'fare_amount', 'total_amount'])
after = len(trips)
audit_log.append(f"Removed {before - after} rows with missing values. Remaining: {after}")

before = len(trips)
trips = trips[trips['trip_distance'] > 0]
trips = trips[trips['fare_amount'] > 0]
trips = trips[trips['passenger_count'] <= 6]
trips = trips[trips['passenger_count'] > 0]
after = len(trips)
audit_log.append(f"Removed {before - after} rows with invalid distance, fare or passenger count. Remaining: {after}")

trips['tpep_pickup_datetime'] = pd.to_datetime(trips['tpep_pickup_datetime'])
trips['tpep_dropoff_datetime'] = pd.to_datetime(trips['tpep_dropoff_datetime'])

before = len(trips)
trips = trips[trips['tpep_pickup_datetime'].dt.year == 2019]
trips = trips[trips['tpep_pickup_datetime'].dt.month == 1]
after = len(trips)
audit_log.append(f"Removed {before - after} rows outside January 2019. Remaining: {after}")

trips['trip_duration_minutes'] = (trips['tpep_dropoff_datetime'] - trips['tpep_pickup_datetime']).dt.total_seconds() / 60
trips['speed_mph'] = trips['trip_distance'] / (trips['trip_duration_minutes'] / 60)
trips['pickup_hour'] = trips['tpep_pickup_datetime'].dt.hour

before = len(trips)
trips = trips[trips['trip_duration_minutes'] > 0]
trips = trips[trips['trip_duration_minutes'] < 180]
trips = trips[trips['speed_mph'] < 100]
after = len(trips)
audit_log.append(f"Removed {before - after} rows with impossible duration or speed. Remaining: {after}")

trips = trips.merge(zones[['LocationID', 'Borough', 'Zone']], left_on='PULocationID', right_on='LocationID', how='left')
trips = trips.rename(columns={'Borough': 'pickup_borough', 'Zone': 'pickup_zone'})
trips = trips.drop(columns=['LocationID'])

trips = trips.merge(zones[['LocationID', 'Borough', 'Zone']], left_on='DOLocationID', right_on='LocationID', how='left')
trips = trips.rename(columns={'Borough': 'dropoff_borough', 'Zone': 'dropoff_zone'})
trips = trips.drop(columns=['LocationID'])

audit_log.append(f"Final clean dataset: {len(trips)} rows")
print(f"Final clean dataset: {len(trips)} rows")

OUTPUT_PATH = os.path.join(DATA_FOLDER, 'cleaned_trips.csv')
trips.to_csv(OUTPUT_PATH, index=False)
print(f"Cleaned data saved to: {OUTPUT_PATH}")

LOG_PATH = os.path.join(DATA_FOLDER, 'cleaning_log.txt')
with open(LOG_PATH, 'w') as f:
    for line in audit_log:
        f.write(line + "\n")
print(f"Cleaning log saved to: {LOG_PATH}")