import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil import parser

client = MongoClient(os.environ.get("MONGO_URI"))
db = client["ecommerce"]
idempotency_collection = db["idempotency_records"]

def create_order(order_data):
    return "12345678"

def process_payment(order_data):
    return "completed"

def process_checkout(idempotency_key, order_data, timestamp):
    request_time = parser.isoparse(timestamp)
    current_time = datetime.now()

    idempotency_window = timedelta(minutes=5)

    existing_record = idempotency_collection.find_one({"idempotency_key":idempotency_key}, {"_id":0})

    if existing_record:
        record_time = existing_record.get("created_at")

        if current_time - record_time <= idempotency_window:
            return existing_record["response_data"]
        else:
            print(f"Idempotency key {idempotency_key} has expired. Creating new order.")
    
    order_id = create_order(order_data)
    payment_status = process_payment(order_data)

    response_data = {
        "order_id": order_id,
        "payment_status": payment_status
        }
    
    idempotency_collection.insert_one({
        "idempotency_key": idempotency_key,
        "response_data": response_data,
        "created_at": request_time,
        "expires_at": request_time + timedelta(hours=24)
    })
    
    return response_data

print(process_checkout("afaotnnooau", "oaghoaugohu8uh", datetime.now().isoformat() + 'Z'))