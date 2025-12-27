CREATE TABLE IF NOT EXISTS weather_readings (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255),
    country VARCHAR(2),
    observed_at TIMESTAMP,
    lat NUMERIC,
    lon NUMERIC,
    temp_c NUMERIC,
    feels_like_c NUMERIC,
    pressure_hpa INTEGER,
    humidity_pct INTEGER,
    wind_speed_ms NUMERIC,
    wind_deg INTEGER,
    cloud_pct INTEGER,
    visibility_m INTEGER,
    rain_1h_mm NUMERIC DEFAULT 0.0,
    snow_1h_mm NUMERIC DEFAULT 0.0,
    condition_main VARCHAR(255),
    condition_description VARCHAR(255),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_city_observed_at ON weather_readings (city, observed_at);