CREATE TABLE IF NOT EXISTS logistics_trips (
    trip_id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    trip_time TIMESTAMP NOT NULL,
    delay_minutes INTEGER
);
