import sqlite3
import pandas as pd
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DATA_FOLDER, 'mobility.db')

conn = sqlite3.connect(DB_PATH)

print("Reading cleaned trips file...")
trips = pd.read_csv(os.path.join(DATA_FOLDER, 'cleaned_trips.csv'))
print(f"Loaded {len(trips)} rows from csv")

# Rename columns to match the new schema
trips = trips.rename(columns={
    'tpep_pickup_datetime': 'pickup_datetime',
    'tpep_dropoff_datetime': 'dropoff_datetime',
    'PULocationID': 'pu_location_id',
    'DOLocationID': 'do_location_id',
    'passenger_count': 'passenger_count',
    'trip_distance': 'trip_distance',
    'fare_amount': 'fare_amount',
    'total_amount': 'total_amount',
    'trip_duration_minutes': 'trip_duration_minutes',
    'speed_mph': 'speed_mph',
    'pickup_hour': 'pickup_hour',
    'pickup_borough': 'pickup_borough',
    'pickup_zone': 'pickup_zone',
    'dropoff_borough': 'dropoff_borough',
    'dropoff_zone': 'dropoff_zone'
})

columns_we_need = [
    'pickup_datetime', 'dropoff_datetime', 'pu_location_id', 'do_location_id',
    'passenger_count', 'trip_distance', 'fare_amount', 'total_amount',
    'trip_duration_minutes', 'speed_mph', 'pickup_hour',
    'pickup_borough', 'pickup_zone', 'dropoff_borough', 'dropoff_zone'
]
trips = trips[columns_we_need]

# Insert data in chunks so it does not use too much memory at once
chunk_size = 100000
total_rows = len(trips)

for start in range(0, total_rows, chunk_size):
    end = start + chunk_size
    chunk = trips.iloc[start:end]
    chunk.to_sql('trips', conn, if_exists='append', index=False)
    print(f"Inserted rows {start} to {min(end, total_rows)}")

conn.commit()
conn.close()
print("Done loading trips into database")