import sqlite3
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DATA_FOLDER, 'mobility.db')

# Step 1: get the pickup zone for every trip from the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT pickup_zone FROM trips WHERE pickup_zone IS NOT NULL')
rows = cursor.fetchall()
conn.close()

zone_list = [row[0] for row in rows]
print(f"Total trips with a zone: {len(zone_list)}")

# Step 2: count how many times each zone appears, without using Counter
# We use a normal dictionary and add 1 each time we see a zone
zone_counts = {}
for zone in zone_list:
    if zone in zone_counts:
        zone_counts[zone] = zone_counts[zone] + 1
    else:
        zone_counts[zone] = 1

print(f"Number of different zones found: {len(zone_counts)}")

# Step 3: find the top 5 busiest zones, without using sort() or sorted()
# We do this manually by finding the highest count, 5 times in a row
top_5 = []
zone_counts_copy = dict(zone_counts)

for i in range(5):
    busiest_zone = None
    busiest_count = -1
    for zone in zone_counts_copy:
        count = zone_counts_copy[zone]
        if count > busiest_count:
            busiest_count = count
            busiest_zone = zone
    top_5.append((busiest_zone, busiest_count))
    del zone_counts_copy[busiest_zone]

print("\nTop 5 busiest pickup zones:")
for rank in range(len(top_5)):
    zone_name = top_5[rank][0]
    trip_count = top_5[rank][1]
    print(f"{rank + 1}. {zone_name}: {trip_count} trips")