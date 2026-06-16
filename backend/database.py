import sqlite3
import pandas as pd
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DATA_FOLDER, 'mobility.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Read the schema file and run all the SQL commands inside it
with open(SCHEMA_PATH, 'r') as f:
    schema_sql = f.read()
cursor.executescript(schema_sql)

print("Tables and indexes created from schema.sql")

# Load the zones data
zones_df = pd.read_csv(os.path.join(DATA_FOLDER, 'taxi_zone_lookup.csv'))
zones_df = zones_df.rename(columns={
    'LocationID': 'location_id',
    'Borough': 'borough',
    'Zone': 'zone'
})
zones_df = zones_df[['location_id', 'borough', 'zone', 'service_zone']]
zones_df.to_sql('zones', conn, if_exists='replace', index=False)
print(f"Loaded {len(zones_df)} zones into the database")

conn.commit()
conn.close()