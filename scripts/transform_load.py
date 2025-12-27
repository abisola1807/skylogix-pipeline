import pymongo
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
POSTGRES_URI = os.getenv('POSTGRES_URI')

def transform_and_load(last_run_time=None):
    mongo_client = pymongo.MongoClient(MONGO_URI)
    mongo_db = mongo_client['skylogix_db']
    collection = mongo_db['weather_raw']

    # Query incremental (if last_run_time provided)
    query = {'updatedAt': {'$gt': last_run_time}} if last_run_time else {}
    docs = collection.find(query)

    pg_conn = psycopg2.connect(POSTGRES_URI)
    cursor = pg_conn.cursor()

    for doc in docs:
        # Transformation logic
        observed_at = datetime.fromtimestamp(doc['dt'])
        weather = doc['weather'][0] if doc['weather'] else {}
        main = doc['main']
        wind = doc['wind']
        clouds = doc['clouds']
        rain = doc.get('rain', {})
        snow = doc.get('snow', {})

        transformed = {
            'city': doc['name'],
            'country': doc['sys']['country'],
            'observed_at': observed_at,
            'lat': doc['coord']['lat'],
            'lon': doc['coord']['lon'],
            'temp_c': main['temp'],
            'feels_like_c': main['feels_like'],
            'pressure_hpa': main['pressure'],
            'humidity_pct': main['humidity'],
            'wind_speed_ms': wind['speed'],
            'wind_deg': wind.get('deg', 0),
            'cloud_pct': clouds['all'],
            'visibility_m': doc.get('visibility', 0),
            'rain_1h_mm': rain.get('1h', 0.0),
            'snow_1h_mm': snow.get('1h', 0.0),
            'condition_main': weather.get('main'),
            'condition_description': weather.get('description')
        }

        # Upsert into PG (on conflict do nothing or update)
        insert_query = """
        INSERT INTO weather_readings (city, country, observed_at, lat, lon, temp_c, feels_like_c, pressure_hpa, humidity_pct, wind_speed_ms, wind_deg, cloud_pct, visibility_m, rain_1h_mm, snow_1h_mm, condition_main, condition_description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (city, observed_at) DO UPDATE SET
            temp_c = EXCLUDED.temp_c,  -- Update all fields if conflict
            -- ... (repeat for all fields except id and ingested_at)
            condition_description = EXCLUDED.condition_description;
        """
        values = list(transformed.values())
        cursor.execute(insert_query, values)
        print(f"Loaded data for {transformed['city']} at {observed_at}")

    pg_conn.commit()
    pg_conn.close()

if __name__ == "__main__":
    # For manual test, pass None for full load
    transform_and_load()