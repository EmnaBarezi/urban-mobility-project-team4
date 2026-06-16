from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DATA_FOLDER, 'mobility.db')

# This function opens a connection to the database
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Endpoint 1: KPI numbers for the top cards
@app.route('/api/kpis')
def get_kpis():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            COUNT(*),
            AVG(fare_amount),
            AVG(trip_distance),
            AVG(speed_mph)
        FROM trips
    ''')
    row = cursor.fetchone()
    conn.close()

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