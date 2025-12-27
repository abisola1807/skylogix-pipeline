import requests
import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')
MONGO_URI = os.getenv('MONGO_URI')
CITIES = ['Nairobi,KE', 'Lagos,NG', 'Accra,GH', 'Johannesburg,ZA']
PROVIDER_NAME = 'OpenWeatherMap'

def fetch_and_upsert():
    client = pymongo.MongoClient(MONGO_URI)
    db = client['skylogix_db']
    collection = db['weather_raw']

    for city in CITIES:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            raw_data = response.json()
            # Create unique key: city + observed_at (dt from API)
            observed_at = datetime.fromtimestamp(raw_data['dt'])
            doc_id = f"{raw_data['name']}_{observed_at.isoformat()}"
            raw_data['_id'] = doc_id  # Stable key
            raw_data['updatedAt'] = datetime.utcnow()
            raw_data['provider'] = PROVIDER_NAME
            # Upsert
            collection.update_one({'_id': doc_id}, {'$set': raw_data}, upsert=True)
            print(f"Upserted data for {city}")
        else:
            print(f"Error fetching {city}: {response.status_code}")

if __name__ == "__main__":
    fetch_and_upsert()