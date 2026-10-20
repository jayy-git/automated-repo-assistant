import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load environment variables from backend/.env
env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)

# Read the MongoDB connection string
mongodb_uri = os.getenv("MONGODB_URI")

if not mongodb_uri:
    raise RuntimeError("MONGODB_URI is missing from backend/.env")

# Connect to MongoDB Atlas and test the connection
try:
    client = MongoClient(
        mongodb_uri,
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    print("SUCCESS: Connected to MongoDB Atlas!")

except PyMongoError as error:
    print("CONNECTION FAILED:", type(error).__name__)
    print("DETAILS:", str(error).splitlines()[0][:300])

finally:
    if "client" in locals():
        client.close()