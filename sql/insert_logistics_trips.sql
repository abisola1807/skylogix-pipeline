INSERT INTO logistics_trips (city, trip_time, delay_minutes)
VALUES
('Lagos', NOW() - INTERVAL '10 minutes', 15),
('Accra', NOW() - INTERVAL '20 minutes', 5),
('Nairobi', NOW() - INTERVAL '30 minutes', 0),
('Johannesburg', NOW() - INTERVAL '25 minutes', 20);
