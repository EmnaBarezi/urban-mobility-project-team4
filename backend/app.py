from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import json

app = Flask(__name__)
CORS(app)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DATA_FOLDER, 'mobility.db')

# This function opens a connection to the database
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# ─────────────────────────────────────────────────────────────────────────────────────────────────────────
# Shared helper: reads borough from the URL and turns them into a SQL WHERE clause + params list. 
# ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def build_filters():
    borough = request.args.get('borough')
    start = request.args.get('start')  
    end = request.args.get('end')

    clauses = []
    params = []

    if borough:
        clauses.append("pickup_borough = ?")
        params.append(borough)
    if start:
        clauses.append("pickup_datetime >= ?")
        params.append(start)
    if end:
        clauses.append("pickup_datetime <= ?")
        params.append(end + " 23:59:59")

    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where_sql, params

# Endpoint 1: KPI numbers for the top cards
@app.route('/api/kpis')
def get_kpis():
    where_sql, params = build_filters()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT
            COUNT(*),
            AVG(fare_amount),
            AVG(trip_distance),
            AVG(speed_mph)
        FROM trips
        {where_sql}
    ''', params)
    row = cursor.fetchone()
    conn.close()
    if row[0] == 0 or row[1] is None:
        return jsonify({'totalTrips': 0, 'avgFare': 0, 'avgDistance': 0, 'avgSpeed': 0})

    result = {
        'totalTrips': row[0],
        'avgFare': round(row[1], 2),
        'avgDistance': round(row[2], 2),
        'avgSpeed': round(row[3], 2)
    }
    return jsonify(result)


# Endpoint 2: number of trips for each hour of the day
@app.route('/api/hourly-demand')
def get_hourly_demand():
    where_sql, params = build_filters()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT pickup_hour, COUNT(*)
        FROM trips
        {where_sql} 
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    ''', params)
    rows = cursor.fetchall()
    conn.close()

    labels = [str(row[0]) for row in rows]
    data = [row[1] for row in rows]
    return jsonify({'labels': labels, 'data': data})

# Endpoint 3: total revenue grouped by pickup borough
@app.route('/api/revenue-by-borough')
def get_revenue_by_borough():
    where_sql, params = build_filters()
    extra = "pickup_borough IS NOT NULL"
    where_sql = (where_sql + " AND " + extra) if where_sql else ("WHERE " + extra)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT pickup_borough, SUM(total_amount)
        FROM trips
        {where_sql}
        GROUP BY pickup_borough
        ORDER BY SUM(total_amount) DESC
    ''', params)
    rows = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in rows]
    data = [round(row[1], 2) for row in rows]
    return jsonify({'labels': labels, 'data': data})

# Endpoint 4: average speed for each hour of the day
@app.route('/api/speed-by-hour')
def get_speed_by_hour():
    where_sql, params = build_filters()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT pickup_hour, AVG(speed_mph)
        FROM trips
        {where_sql}
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    ''', params)
    rows = cursor.fetchall()
    conn.close()

    labels = [str(row[0]) for row in rows]
    data = [round(row[1], 2) for row in rows]
    return jsonify({'labels': labels, 'data': data})

# Endpoint 5: most common pickup to dropoff borough routes
@app.route('/api/top-routes')
def get_top_routes():
    where_sql, params = build_filters()
    extra = "pickup_borough IS NOT NULL AND dropoff_borough IS NOT NULL"
    where_sql = (where_sql + " AND " + extra) if where_sql else ("WHERE " + extra)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT pickup_borough, dropoff_borough, COUNT(*) as trip_count
        FROM trips
        {where_sql}
        GROUP BY pickup_borough, dropoff_borough
        ORDER BY trip_count DESC
        LIMIT 5
    ''', params)
    rows = cursor.fetchall()
    conn.close()

    labels = [f"{row[0]} -> {row[1]}" for row in rows]
    data = [row[2] for row in rows]
    return jsonify({'labels': labels, 'data': data})

# Endpoint 6: distinct boroughs, to populate the filter dropdown
@app.route('/api/boroughs')
def get_boroughs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT pickup_borough
        FROM trips
        WHERE pickup_borough IS NOT NULL
        ORDER BY pickup_borough
    ''')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([row[0] for row in rows])


# Endpoint 7: trip counts per pickup zone, for the map
@app.route('/api/zone-stats')
def get_zone_stats():
    where_sql, params = build_filters()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT pu_location_id, pickup_zone, pickup_borough, COUNT(*) as trip_count
        FROM trips
        {where_sql}
        GROUP BY pu_location_id
        ORDER BY trip_count DESC
    ''', params)
    rows = cursor.fetchall()
    conn.close()

    result = [
        {
            'locationId': row[0],
            'zone': row[1],
            'borough': row[2],
            'tripCount': row[3]
        }
        for row in rows
    ]
    return jsonify(result)


# Endpoint 8: Draw real zone boundaries from taxi-zones-geojson
@app.route('/api/taxi-zones-geojson')
def get_taxi_zones_geojson():
    geojson_path = os.path.join(DATA_FOLDER, 'taxi_zones.geojson')
    if not os.path.exists(geojson_path):
        return jsonify({'error': 'taxi_zones.geojson not found. Run data/convert_zones.py first.'}), 404
    with open(geojson_path, encoding='utf-8') as f:
        return jsonify(json.load(f))


# Endpoint 9:
@app.route('/api/top-zones-manual')
def get_top_zones_manual():
    limit = int(request.args.get('limit', 5))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT pickup_zone FROM trips WHERE pickup_zone IS NOT NULL')
    rows = cursor.fetchall()
    conn.close()

    zone_list = [row[0] for row in rows]

    # Manual counting 
    zone_counts = {}
    for zone in zone_list:
        if zone in zone_counts:
            zone_counts[zone] = zone_counts[zone] + 1
        else:
            zone_counts[zone] = 1

    # Manual top-N selection — no sort() or sorted()
    top_n = []
    zone_counts_copy = dict(zone_counts)
    for _ in range(min(limit, len(zone_counts_copy))):
        busiest_zone = None
        busiest_count = -1
        for zone in zone_counts_copy:
            count = zone_counts_copy[zone]
            if count > busiest_count:
                busiest_count = count
                busiest_zone = zone
        top_n.append({'zone': busiest_zone, 'tripCount': busiest_count})
        del zone_counts_copy[busiest_zone]

    return jsonify(top_n)


if __name__ == '__main__':
    app.run(debug=True, port=5000)