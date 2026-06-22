# MobilityIQ: Urban Mobility Intelligence Platform

## Project Overview

MobilityIQ is a full-stack urban mobility analytics platform developed using the New York City Taxi & Limousine Commission (TLC) trip dataset.

The system processes raw taxi trip records, cleans and enriches the data, stores it in a relational database, and provides an interactive dashboard for exploring mobility patterns, revenue trends, congestion indicators, and spatial movement across New York City.

---

### Project Name
Urban Mobility Team 4

### Team Members

| Name | Role |
|--------|--------|
| Emna Barezi | Backend Development |
| Moreen Muthoni | Frontend Development |

---

## Important Note

The API server must be running before opening the dashboard. Keep the terminal open while using the app.

---

## Project Structure
urban-mobility-project-team4/

├── backend/

│   ├── clean_data.py          cleans the raw trip data

│   ├── convert_zones.py       converts taxi zone shapefile to geojson

│   ├── database.py            creates the database tables

│   ├── load_trips.py          loads cleaned data into the database

│   ├── top_zones_algorithm.py manual algorithm, finds top 5 busiest zones

│   ├── app.py                 Flask API server

│   └── schema.sql             database schema

├── front_end/

│   ├── index.html

│   ├── script.js

│   └── style.css

├── data/

│   (dataset files go here, see Setup section below)

└── README.md

---

## Setup Instructions

### 1. Requirements

- Python 3.10 or higher
- A web browser (Chrome recommended)

### 2. Install Python libraries
python -m pip install flask flask-cors pandas geopandas

### 3. Download the dataset

The dataset files are too large for GitHub, so they must be downloaded manually:

1. Download `yellow_tripdata_2019-01.csv` from the NYC TLC website
2. Download `taxi_zone_lookup.csv`
3. Download `taxi_zones.zip`
4. Place all 3 files inside the `data/` folder

### 4. Run the backend setup (in order)
python backend/clean_data.py

python backend/convert_zones.py

python backend/database.py

python backend/load_trips.py

This will clean the data, convert the spatial files, create the database, and load all the trips. This step can take a few minutes since there are over 7 million trip records.

### 5. Start the API server
python backend/app.py

The server will start at `http://127.0.0.1:5000`

**Keep this terminal open while using the dashboard.**

### 6. Open the dashboard

Open `front_end/index.html` in your browser. The dashboard will automatically connect to the API and load real data.

---

## Video Walkthrough

https://drive.google.com/file/d/1xqB1v7qRAvzoDWKuqkw5wAvMVLvmVUjx/view?usp=sharing
