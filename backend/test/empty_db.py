from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

uri = os.getenv("MONGODB_URI")

client = MongoClient(uri)
db = client["GlobalLaunchAI"]  # or whatever your database is called

# Wipe all data from both collections
db["country_reports"].delete_many({})