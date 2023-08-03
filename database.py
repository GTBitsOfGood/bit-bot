import os
import pymongo
from dotenv import load_dotenv
load_dotenv()

mongo_client = pymongo.MongoClient(os.environ["MONGO_DB_URL"])
db_client = mongo_client[os.environ["MONGO_DB_DATABASE"]]
users_collection = db_client['users']

def give_bits_to_user(user_id, amount):
    if db_client is None:
        raise Exception("Failed to connect to database")
    
    users_collection = db_client['users']
    user_query = { "userId": user_id }
    insert_query = { "userId": user_id, "bits": amount}
    update_query = {"$inc": {"bits": amount}}

    pre_existing_user = users_collection.find_one(user_query)

    if not pre_existing_user:
        users_collection.insert_one(insert_query)
    else:
        users_collection.update_one(user_query, update_query)
    
def remove_bits_from_user(user_id, amount):
    if db_client is None:
        raise Exception("Failed to connect to database")
    
    users_collection = db_client['users']
    
    user_query = { "userId": user_id }
    update_query = {"$inc": {"bits": -amount}}

    pre_existing_user = users_collection.find_one(user_query)

    if not pre_existing_user:
        raise Exception("Cannot remove bits from a user that has no bits")
    
    if pre_existing_user['bits'] < amount:
        raise Exception("Cannot remove more bits than what the user has")

    users_collection.update_one(user_query, update_query)

def get_leaderboard_documents(limit=10):
    query = {}
    sort_by_field_query = [("bits", pymongo.DESCENDING)]

    return users_collection.find(query).sort(sort_by_field_query).limit(limit)