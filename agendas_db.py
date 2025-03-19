from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Initialize connection when module is imported
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    reminder_db = client["reminder_database"]
    reminders_collection = reminder_db["reminders"]

    # Ensure collection exists by creating an index for uniqueness
    reminders_collection.create_index([("time", 1), ("task", 1), ("date", 1)], unique=True)
    print("✅ MongoDB connection established")

except ConnectionFailure as e:
    print(f"❌ Database connection failed: {e}")
    raise

def save_reminder(reminder_data):
    """
    Save reminder to MongoDB with proper error handling.
    
    Args:
        reminder_data (dict): A dictionary containing 'time', 'task', and 'date'.
    
    Returns:
        tuple: (success: bool, inserted_id: str|None)
    """
    try:
        # Validate data format
        if not isinstance(reminder_data, dict):
            raise ValueError("Reminder data must be a dictionary")
        
        # Ensure required fields exist
        required_keys = {"time", "task", "date"}
        if not required_keys.issubset(reminder_data.keys()):
            raise ValueError("Missing required fields: 'time', 'task', or 'date'")

        # Remove '_id' if present to prevent duplication errors
        reminder_data.pop("_id", None)

        # Check if the reminder already exists
        existing_reminder = reminders_collection.find_one({
            "time": reminder_data["time"],
            "task": reminder_data["task"],
            "date": reminder_data["date"]
        })

        if existing_reminder:
            print(f"⚠️ Reminder already exists: {existing_reminder['_id']}")
            return (False, str(existing_reminder['_id']))  # Return existing reminder ID

        # Insert document if no duplicate is found
        insert_result = reminders_collection.insert_one(reminder_data)
        print(f"✅ Reminder stored in MongoDB with ID: {insert_result.inserted_id}")
        return (True, str(insert_result.inserted_id))

    except OperationFailure as e:
        print(f"❌ Database operation failed: {e.code} - {e.details}")
        return (False, None)
    except ValueError as e:
        print(f"❌ Validation error: {e}")
        return (False, None)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return (False, None)
