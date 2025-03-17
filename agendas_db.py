from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Initialize connection when module is imported
try:
    client = MongoClient("mongodb://localhost:27017/", 
                       serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    reminder_db = client["reminder_database"]
    reminders_collection = reminder_db["reminders"]
    print("✅ MongoDB connection established")
except ConnectionFailure as e:
    print(f"❌ Database connection failed: {e}")
    raise

def save_reminder(reminder_data):
    """
    Save reminder to MongoDB with proper error handling
    Returns tuple: (success: bool, inserted_id: str|None)
    """
    try:
        # Validate data format
        if not isinstance(reminder_data, dict):
            raise ValueError("Reminder data must be a dictionary")
            
        # Insert document
        insert_result = reminders_collection.insert_one(reminder_data)
        print(f"Inserted reminder with id: {insert_result.inserted_id}")
        return (True, str(insert_result.inserted_id))
        
    except OperationFailure as e:
        print(f"Database operation failed: {e.code} - {e.details}")
        return (False, None)
    except ValueError as e:
        print(f"Validation error: {e}")
        return (False, None)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return (False, None)
