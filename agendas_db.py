from pymongo import MongoClient

# Connect to the MongoDB server running on localhost at the default port 27017
client = MongoClient('mongodb://localhost:27017/')

# Access (or create) a new database called "my_database"
db = client['my_database']

# Access (or create) a new collection within that database called "my_collection"
collection = db['my_collection']

# Insert a sample document into the collection. This action creates the database and collection if they don't exist.
result = collection.insert_one({'name': 'Alice', 'age': 30})
print('Document inserted with id:', result.inserted_id)
