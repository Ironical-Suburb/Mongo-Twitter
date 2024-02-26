import sys
import json
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

def load_json(file_name, port):
    # Connect to MongoDB
    client = MongoClient('localhost', int(port))
    db = client['291db']

    # Create or reset the 'tweets' collection
    if 'tweets' in db.list_collection_names():
        db['tweets'].drop()
    tweets_collection = db['tweets']

    # Process the JSON file
    try:
        with open(file_name, 'r') as file:
            batch = []
            batch_size = 100

            for line in file:
                tweet = json.loads(line)
                batch.append(tweet)

                if len(batch) >= batch_size:
                    tweets_collection.insert_many(batch)
                    batch.clear()

            # Insert any remaining tweets
            if batch:
                tweets_collection.insert_many(batch)

    except BulkWriteError as bwe:
        print("Error in bulk write:", bwe.details)
    except Exception as e:
        print("An error occurred:", e)

    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: load-json.py <json_file> <port>")
        sys.exit(1)

    json_file = sys.argv[1]
    port = sys.argv[2]
    load_json(json_file, port)

