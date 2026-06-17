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

# Endpoint 2: number of trips for each hour of the day
@app.route('/api/hourly-demand')
def get_hourly_demand():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pickup_hour, COUNT(*)
        FROM trips
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    ''')
    rows = cursor.fetchall()
    conn.close()

    labels = [str(row[0]) for row in rows]
    data = [row[1] for row in rows]
    return jsonify({'labels': labels, 'data': data})

# Endpoint 3: total revenue grouped by pickup borough
@app.route('/api/revenue-by-borough')
def get_revenue_by_borough():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pickup_borough, SUM(total_amount)
        FROM trips
        WHERE pickup_borough IS NOT NULL
        GROUP BY pickup_borough
        ORDER BY SUM(total_amount) DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in rows]
    data = [round(row[1], 2) for row in rows]
    return jsonify({'labels': labels, 'data': data})

# Endpoint 4: average speed for each hour of the day
@app.route('/api/speed-by-hour')
def get_speed_by_hour():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pickup_hour, AVG(speed_mph)
        FROM trips
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    ''')
    rows = cursor.fetchall()
    conn.close()

    labels = [str(row[0]) for row in rows]
    data = [round(row[1], 2) for row in rows]
    return jsonify({'labels': labels, 'data': data})

# Endpoint 5: most common pickup to dropoff borough routes
@app.route('/api/top-routes')
def get_top_routes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pickup_borough, dropoff_borough, COUNT(*) as trip_count
        FROM trips
        WHERE pickup_borough IS NOT NULL AND dropoff_borough IS NOT NULL
        GROUP BY pickup_borough, dropoff_borough
        ORDER BY trip_count DESC
        LIMIT 5
    ''')
    rows = cursor.fetchall()
    conn.close()

    labels = [f"{row[0]} -> {row[1]}" for row in rows]
    data = [row[2] for row in rows]
    return jsonify({'labels': labels, 'data': data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)