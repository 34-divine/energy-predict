from config import units_collection, db
from bson import ObjectId
import datetime

appliances_collection = db["appliances"]

APPLIANCE_DATABASE = [
    {"name": "Television", "watts": 100, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Standing Fan", "watts": 60, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Ceiling Fan", "watts": 75, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Refrigerator", "watts": 150, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Freezer", "watts": 100, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Air Conditioner", "watts": 1500, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Pressing Iron", "watts": 1000, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Washing Machine", "watts": 500, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Laptop", "watts": 65, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Phone Charger", "watts": 10, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "LED Bulb", "watts": 10, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Microwave", "watts": 800, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Water Pump", "watts": 750, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Electric Kettle", "watts": 1500, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Security Light", "watts": 20, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "DSTV Decoder", "watts": 30, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Generator", "watts": 3000, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Electric Cooker", "watts": 2000, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Blender", "watts": 300, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
    {"name": "Game Console", "watts": 150, "hours": {"Light": 2.5, "Average": 7.5, "Heavy": 17}},
]

def add_unit_log(user_id, log_type, amount, note=""):
    log = {
        "user_id": user_id,
        "type": log_type,
        "amount": float(amount),
        "note": note,
        "date": datetime.datetime.utcnow()
    }
    result = units_collection.insert_one(log)
    return str(result.inserted_id)

def get_user_logs(user_id):
    logs = units_collection.find({"user_id": user_id}).sort("date", -1)
    result = []
    for log in logs:
        log["_id"] = str(log["_id"])
        log["date"] = log["date"].isoformat()
        result.append(log)
    return result

def add_appliance(user_id, name, watts, hours_per_day, quantity, usage_level):
    daily_kwh = round((float(watts) * float(hours_per_day) * int(quantity)) / 1000, 4)
    appliance = {
        "user_id": user_id,
        "name": name,
        "watts": float(watts),
        "hours_per_day": float(hours_per_day),
        "quantity": int(quantity),
        "usage_level": usage_level,
        "daily_kwh": daily_kwh,
        "created_at": datetime.datetime.utcnow()
    }
    result = appliances_collection.insert_one(appliance)
    return str(result.inserted_id), daily_kwh

def get_user_appliances(user_id):
    appliances = appliances_collection.find({"user_id": user_id})
    result = []
    for a in appliances:
        a["_id"] = str(a["_id"])
        result.append(a)
    return result

def delete_appliance(appliance_id, user_id):
    result = appliances_collection.delete_one({
        "_id": ObjectId(appliance_id),
        "user_id": user_id
    })
    return result.deleted_count > 0

def get_total_daily_kwh(user_id):
    appliances = get_user_appliances(user_id)
    return round(sum(a["daily_kwh"] for a in appliances), 4)