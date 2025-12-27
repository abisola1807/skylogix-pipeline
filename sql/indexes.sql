CREATE INDEX IF NOT EXISTS idx_weather_city_observed_at
ON public.weather_readings (city, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_weather_observed_at
ON public.weather_readings (observed_at DESC);
