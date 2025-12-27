-- Weather trends per city (avg temp last 24h)
SELECT city, AVG(temp_c) AS avg_temp
FROM weather_readings
WHERE observed_at > NOW() - INTERVAL '24 hours'
GROUP BY city;

-- Extreme conditions (high wind or heavy rain)(outcome is no value because its within the threshhold)
SELECT
    city,
    observed_at,
    wind_speed_ms,
    rain_1h_mm,
    CASE
        WHEN wind_speed_ms > 10 AND rain_1h_mm > 5 THEN 'High wind & heavy rain'
        WHEN wind_speed_ms > 10 THEN 'High wind'
        WHEN rain_1h_mm > 5 THEN 'Heavy rain'
    END AS alert_type
FROM weather_readings
WHERE wind_speed_ms > 10
   OR rain_1h_mm > 5
ORDER BY observed_at DESC;


--Joining Weather Data with Logistics Data
SELECT
    w.city,
    w.observed_at,
    w.condition_main,
    w.wind_speed_ms,
    w.rain_1h_mm,
    l.trip_id,
    l.delay_minutes
FROM weather_readings w
JOIN logistics_trips l
  ON w.city = l.city
 AND w.observed_at BETWEEN l.trip_time - INTERVAL '15 minutes'
                       AND l.trip_time + INTERVAL '15 minutes'
WHERE l.delay_minutes > 0
ORDER BY l.delay_minutes DESC;
