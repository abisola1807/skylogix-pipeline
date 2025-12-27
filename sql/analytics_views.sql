CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.v_weather_latest AS
SELECT DISTINCT ON (city)
    city,
    country,
    observed_at,
    temp_c,
    feels_like_c,
    humidity_pct,
    pressure_hpa,
    wind_speed_ms,
    cloud_pct,
    visibility_m,
    rain_1h_mm,
    snow_1h_mm,
    condition_main,
    condition_description,
    lat,
    lon
FROM public.weather_readings
ORDER BY city, observed_at DESC;


CREATE OR REPLACE VIEW analytics.v_weather_hourly AS
SELECT
    city,
    date_trunc('hour', observed_at) AS observed_hour,
    AVG(temp_c) AS avg_temp_c,
    AVG(humidity_pct) AS avg_humidity_pct,
    AVG(wind_speed_ms) AS avg_wind_speed_ms,
    MAX(rain_1h_mm) AS max_rain_1h_mm
FROM public.weather_readings
GROUP BY city, date_trunc('hour', observed_at);
