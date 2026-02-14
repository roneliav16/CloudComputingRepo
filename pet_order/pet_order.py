from flask import Flask, request, jsonify
import os
import random
import requests
from pymongo import MongoClient

app = Flask(__name__)
global_purchase_id = 0

# --------- Config from env ---------
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://mongo:27017")
DB_NAME = os.environ.get("DB_NAME", "petshop")
TRANSACTIONS_COLLECTION = "transactions"

STORE1_URL = os.environ.get("STORE1_URL", "http://pet-store1:5001")
STORE2_URL = os.environ.get("STORE2_URL", "http://pet-store2:5001")

OWNER_HEADER_KEY = "OwnerPC"
OWNER_HEADER_VAL = "LovesPetsL2M3n4"

# --------- Mongo connection ---------
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
transactions = db[TRANSACTIONS_COLLECTION]


# ------------------ helpers ------------------

def error_400(msg="Bad request"):
    return jsonify({"error": msg}), 400

def error_401():
    return jsonify({"error": "unauthorized"}), 401

def error_415():
    return jsonify({"error": "Expected application/json media type"}), 415

def get_stores():
    return [
        (1, STORE1_URL),
        (2, STORE2_URL),
    ]


def find_type_id(base_url, pet_type):
    """
    Calls GET /pet-types?type=<pet_type> on the appropriate store
    and returns the id of the type if found, otherwise None
    """
    try:
        resp = requests.get(
            f"{base_url}/pet-types",
            params={"type": pet_type},
            timeout=5,
        )
    except Exception:
        return None

    if resp.status_code != 200:
        return None

    data = resp.json()
    if not data:
        return None

    # If there are several - assume the first one
    return data[0].get("id")


def list_pets_for_type(base_url, type_id):
    """
    Returns list of pets for this store and this type_id
    """
    try:
        resp = requests.get(
            f"{base_url}/pet-types/{type_id}/pets",
            timeout=5,
        )
    except Exception:
        return []

    if resp.status_code != 200:
        return []
    return resp.json()


def get_pet_by_name(base_url, type_id, pet_name):
    """
    Returns specific pet named pet_name if exists, otherwise None
    """
    try:
        resp = requests.get(
            f"{base_url}/pet-types/{type_id}/pets/{pet_name}",
            timeout=5,
        )
    except Exception:
        return None

    if resp.status_code != 200:
        return None
    return resp.json()


def delete_pet(base_url, type_id, pet_name):
    """
    Deletes specific pet in store. Returns True if successful.
    """
    try:
        resp = requests.delete(
            f"{base_url}/pet-types/{type_id}/pets/{pet_name}",
            timeout=5,
        )
    except Exception:
        return False

    return resp.status_code == 204


# --------------- /purchases (customers) ----------------

@app.route("/purchases", methods=["POST"])
def create_purchase():
    # Content-Type must be application/json
    if request.headers.get("Content-Type") != "application/json":
        return error_415()

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_400()

    purchaser = data.get("purchaser")
    pet_type = data.get("pet-type")
    store = data.get("store")
    pet_name = data.get("pet-name")

    # Required fields
    if not isinstance(purchaser, str) or not purchaser.strip():
        return error_400("missing/invalid purchaser")
    if not isinstance(pet_type, str) or not pet_type.strip():
        return error_400("missing/invalid pet-type")

    # store if exists - 1 or 2
    if store is not None:
        if not isinstance(store, int) or store not in (1, 2):
            return error_400("invalid store")

    # pet-name is allowed only if there is a store
    if pet_name is not None and store is None:
        return error_400("pet-name requires store")

    # Determine which stores to check
    candidate_stores = []
    for sid, url in get_stores():
        if (store is None) or (sid == store):
            candidate_stores.append((sid, url))

    chosen = None  # (store_id, base_url, type_id, pet_obj)

    # Iterate over stores according to the rules
    for sid, base_url in candidate_stores:
        type_id = find_type_id(base_url, pet_type)
        if not type_id:
            continue

        if pet_name:
            # Need pet with this name
            pet_obj = get_pet_by_name(base_url, type_id, pet_name)
            if pet_obj:
                chosen = (sid, base_url, type_id, pet_obj)
                break
        else:
            # Choose randomly from all pets of this type in the store
            pets = list_pets_for_type(base_url, type_id)
            if pets:
                pet_obj = random.choice(pets)
                chosen = (sid, base_url, type_id, pet_obj)
                break

    if not chosen:
        # No suitable pet in any store
        return error_400("No pet of this type is available")

    chosen_store, base_url, type_id, pet_obj = chosen
    chosen_name = pet_obj.get("name")

    # Delete the pet from the store
    if not chosen_name or not delete_pet(base_url, type_id, chosen_name):
        # If we couldn't delete - can return 500 or 400, at your discretion
        return error_400("could not delete pet")

    # Build purchase-id
    global global_purchase_id
    global_purchase_id += 1
    purchase_id = str(global_purchase_id)

    # Build the purchase JSON for return and saving to DB
    purchase_doc = {
        "purchaser": purchaser,
        "pet-type": pet_type,
        "store": chosen_store,
        "pet-name": chosen_name,
        "purchase-id": purchase_id,
    }

    # Save to Mongo as transaction
    transactions.insert_one(purchase_doc.copy())

    return jsonify(purchase_doc), 201


# --------------- /transactions (owner) ----------------

@app.route("/transactions", methods=["GET"])
def get_transactions():
    # Check owner Header
    header_val = request.headers.get(OWNER_HEADER_KEY)
    if header_val != OWNER_HEADER_VAL:
        return error_401()

    # query string - <field>=<value> on one of the fields
    query = {}
    for field in ("purchaser", "pet-type", "store", "pet-name", "purchase-id"):
        if field in request.args:
            value = request.args[field]
            if field == "store":
                try:
                    value = int(value)
                except ValueError:
                    return error_400("invalid store filter")
            query[field] = value

    # Retrieve from DB
    docs = list(transactions.find(query, {"_id": 0}))  # Don't return Mongo's _id

    return jsonify(docs), 200

@app.route("/kill", methods=["GET"])
def kill_container():
    os._exit(1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
