import os
import pymongo
from dotenv import load_dotenv

load_dotenv("./api/.env")

mongo_client = pymongo.MongoClient(os.environ["MONGO_DB_URL"])
db_client = mongo_client[os.environ["MONGO_DB_DATABASE"]]
users_collection = db_client["users"]
messages_collection = db_client["messages"]
bit_history_collection = db_client["bit_history"]


def get_bits_by_user_id(user_id):
    if db_client is None:
        raise Exception("Failed to connect to database")

    users_collection = db_client["users"]
    bit_query = {"userId": user_id}

    user = users_collection.find_one(bit_query)
    if user:
        return user.get("bits", 0)
    else:
        return 0


def get_bits_by_user_id_from_history(user_id, tag):
    if db_client is None:
        raise Exception("Failed to connect to database")

    bit_query = {"userId": user_id, "tag": tag}

    user = bit_history_collection.find_one(bit_query)
    if user:
        return user.get("bits", 0)
    else:
        return 0


def give_bits_to_user(user_id, amount):
    if db_client is None:
        raise Exception("Failed to connect to database")

    users_collection = db_client["users"]
    user_query = {"userId": user_id}
    insert_query = {"userId": user_id, "bits": amount, "team": "No Team"}
    update_query = {"$inc": {"bits": amount}}

    pre_existing_user = users_collection.find_one(user_query)

    if not pre_existing_user:
        users_collection.insert_one(insert_query)
    else:
        users_collection.update_one(user_query, update_query)


def record_bit_history(tag):
    if db_client is None:
        raise Exception("Failed to connect to database")

    users_collection = db_client["users"]

    users = users_collection.find({})

    for user in users:
        user_id = user["userId"]
        bits = user["bits"]
        team = user["team"]

        bit_history_entry = {"bits": bits, "userId": user_id, "tag": tag, "team": team}

        bit_history_collection.insert_one(bit_history_entry)


def remove_bit_history_by_tag(tag):
    if db_client is None:
        raise Exception("Failed to connect to database")

    bit_history_collection.delete_many({"tag": tag})


def remove_bits_from_user(user_id, amount):
    if db_client is None:
        raise Exception("Failed to connect to database")

    users_collection = db_client["users"]

    user_query = {"userId": user_id}
    update_query = {"$inc": {"bits": -amount}}

    pre_existing_user = users_collection.find_one(user_query)

    if not pre_existing_user:
        raise Exception("Cannot remove bits from a user that has no bits")

    if pre_existing_user["bits"] < amount:
        raise Exception("Cannot remove more bits than what the user has")

    users_collection.update_one(user_query, update_query)


def get_leaderboard_documents(limit=10):
    if db_client is None:
        raise Exception("Failed to connect to database")

    query = {}
    sort_by_field_query = [("bits", pymongo.DESCENDING)]

    return users_collection.find(query).sort(sort_by_field_query).limit(limit)


def get_leaderboard_documents_from_history(tag, limit=10):
    if db_client is None:
        raise Exception("Failed to connect to database")

    sort_by_field_query = [("bits", pymongo.DESCENDING)]

    return (
        bit_history_collection.find({"tag": tag}).sort(sort_by_field_query).limit(limit)
    )


def get_team_leaderboard_from_history(tag):
    if db_client is None:
        raise Exception("Failed to connect to database")

    bit_history_collection = db_client["bit_history"]

    pipeline = [
        {"$match": {"tag": tag}},
        {"$group": {"_id": "$team", "total_bits": {"$sum": "$bits"}}},
        {"$sort": {"total_bits": -1}},
    ]

    result = bit_history_collection.aggregate(pipeline)
    aggregated_data = list(result)
    return aggregated_data


def user_is_admin(user_id):
    user_query = {"userId": user_id}
    pre_existing_user = users_collection.find_one(user_query)

    return pre_existing_user and pre_existing_user["role"] == "admin"


def set_user_bits_to_zero():
    if db_client is None:
        raise Exception("Failed to connect to database")

    users_collection = db_client["users"]
    users_collection.update_many({}, {"$set": {"bits": 0}})


def set_team_by_user_id(user_id, team):
    user_query = {"userId": user_id}

    pre_existing_user = users_collection.find_one(user_query)
    insert_query = {"userId": user_id, "bits": 0, "team": team}
    update_query = {"$set": {"team": team}}

    if not pre_existing_user:
        users_collection.insert_one(insert_query)
    else:
        users_collection.update_one(user_query, update_query)


def get_team_leaderboard():
    pipeline = [{"$group": {"_id": "$team", "total_bits": {"$sum": "$bits"}}}]

    result = users_collection.aggregate(pipeline)
    aggregated_data = list(result)
    return aggregated_data


def change_user_role(user_id, role):
    user_query = {"userId": user_id}

    pre_existing_user = users_collection.find_one(user_query)
    insert_query = {"userId": user_id, "bits": 0, "team": "No Team", "role": role}
    update_query = {"$set": {"role": role}}

    if not pre_existing_user:
        users_collection.insert_one(insert_query)
    else:
        users_collection.update_one(user_query, update_query)


def create_message_id(message_id):
    message_query = {"messageId": message_id}
    messages_collection.insert_one(message_query)


def get_message_by_id(message_id):
    message_query = {"messageId": message_id}
    pre_existing_message = messages_collection.find_one(message_query)
    return pre_existing_message


def set_teams_to_no_team():
    update_query = {"$set": {"team": "No Team"}}
    users_collection.update_many({}, update_query)
