from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    # Single connection setup
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    
    reminder_db = client["reminder_database"]
    reminders_collection = reminder_db["reminders"]
    
    # Your insert operation
    insert_result = reminders_collection.insert_one(parsed_data)
    print("Inserted reminder with id:", insert_result.inserted_id)

except ConnectionFailure as e:
    print(f"Database connection failed: {e}")
except Exception as e:
    print(f"Error storing reminder: {e}")
