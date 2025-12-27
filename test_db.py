import pymongo
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
mongo_uri = os.getenv('MONGO_URI')
postgres_uri = os.getenv('POSTGRES_URI')

# Test MongoDB
mongo_client = pymongo.MongoClient(mongo_uri)
mongo_db = mongo_client['skylogix_db']
print("MongoDB connected:", mongo_db.list_collection_names())

# Test PostgreSQL
pg_conn = psycopg2.connect(postgres_uri)
print("PostgreSQL connected.")
pg_conn.close()