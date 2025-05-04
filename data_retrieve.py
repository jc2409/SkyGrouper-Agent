from pymongo import MongoClient, DESCENDING
import os
from dotenv import load_dotenv

def get_data():
    load_dotenv()
    client = MongoClient(os.getenv("MONGO_URI"))
    collection = client["grouptripAdmin"]["groupTrips"]

    latest = collection.find_one({}, sort=[("createdAt", DESCENDING)])
    res = {}
    res["group_profiles"] = []
    res["departures"] = []
    
    for user in range(len(latest['users'])):
        res["departures"].append({"airport": latest['users'][user]['from'], "budget": int(latest['users'][user]['budget']['max'])})
        res["start_date"] = latest['users'][user]['dates']['start']
        res["end_date"] = latest['users'][user]['dates']['end']    
        res["group_profiles"].append({"interests": latest['users'][user]['interests']})
    print(res)
    return res
    
if __name__ == "__main__":
    get_data()