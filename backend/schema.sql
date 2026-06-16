PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS zones (
    location_id   INTEGER PRIMARY KEY,
    borough       TEXT    NOT NULL,
    zone          TEXT    NOT NULL,
    service_zone  TEXT
);

CREATE TABLE IF NOT EXISTS trips (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    pickup_datetime        TEXT    NOT NULL,
    dropoff_datetime       TEXT    NOT NULL,
    pu_location_id         INTEGER REFERENCES zones(location_id),
    do_location_id         INTEGER REFERENCES zones(location_id),
    passenger_count        INTEGER,
    trip_distance          REAL    NOT NULL,
    fare_amount            REAL    NOT NULL,
    total_amount           REAL    NOT NULL,
    trip_duration_minutes  REAL    NOT NULL,
    speed_mph              REAL    NOT NULL,
    pickup_hour            INTEGER NOT NULL,
    pickup_borough         TEXT,
    pickup_zone            TEXT,
    dropoff_borough        TEXT,
    dropoff_zone           TEXT
);

CREATE INDEX IF NOT EXISTS idx_trips_pickup_hour     ON trips(pickup_hour);
CREATE INDEX IF NOT EXISTS idx_trips_pu_borough      ON trips(pickup_borough);
CREATE INDEX IF NOT EXISTS idx_trips_pu_location     ON trips(pu_location_id);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime ON trips(pickup_datetime);