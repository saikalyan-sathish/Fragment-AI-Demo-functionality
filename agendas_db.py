from pymongo import MongoClient

# Connect to the MongoDB server (default is localhost on port 27017)
client = MongoClient("mongodb://localhost:27017/")

# Create or use an existing database named "sample_database"
db = client["sample_database"]

# Create or use an existing collection named "users"
collection = db["users"]

# Document to be inserted
document = {"name": "saikalyan"}

# Insert the document into the collection
result = collection.insert_one(document)

print("Inserted document id:", result.inserted_id)
