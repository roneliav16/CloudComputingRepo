import os
import re
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError

import requests
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Create pictures directory within the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURES_DIR = os.path.join(BASE_DIR, "pictures")
os.makedirs(PICTURES_DIR, exist_ok=True)

NINJA_API_KEY = os.environ.get("NINJA_API_KEY")

# pet_types = {} 
# id = 0
# image_number = 0
# -------------------------
# MongoDB setup
# -------------------------

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "petshop")
STORE_ID = os.environ.get("STORE_ID", "1")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# 2 Collection for pet types - one per store
PET_TYPES_COL = db[f"pet_store{STORE_ID}"]

# Retrieve existing pet types ID from the DB
last = PET_TYPES_COL.find_one(sort=[("id", -1)])
id = int(last["id"]) if last and "id" in last else 0

image_number = 0

# -------------------------
# Helper functions for errors
# -------------------------

# Returns 400 Bad Request error
def error_400():
    return jsonify({"error": "Malformed data"}), 400

# Returns 404 Not Found error
def error_404():
    return jsonify({"error": "Not found"}), 404

# Returns 415 Unsupported Media Type error
def error_415():
    return jsonify({"error": "Expected application/json media type"}), 415

# Returns 500 Internal Server Error
def error_500(status_code=None):
    msg = "API response code " + str(status_code) if status_code is not None else "internal error"
    return jsonify({"server error": msg}), 500

# -------------------------
# Helper functions for parsing
# -------------------------

# Parse dates to DD-MM-YYYY format (for comparison services)
def parse_date(date_str):
    return datetime.strptime(date_str, "%d-%m-%Y")

# Converts lifespan text to number – always takes the smallest number.
def parse_lifespan(text):
    if not text:
        return None
    nums = [int(n) for n in re.findall(r"\d+", text)]
    return min(nums) if nums else None

# Converts temperament / group_behavior sentence to array of words in attributes field, each word separated, without punctuation.
def extract_attributes(text):
    if not text:
        return []
    # Replace punctuation with space
    text = re.sub(r"[.,;:!?]", " ", text)
    words = [w for w in text.split() if w]
    return words

# -------------------------
# API Ninjas call
# -------------------------

# Calls Animals API at api-ninjas, returns dict with: family, genus, attributes (list), lifespan (int or None) 
def fetch_animal_data(type_name):
    if not NINJA_API_KEY:
        # use generic Exception to signal internal error
        raise Exception(500)

    url = "https://api.api-ninjas.com/v1/animals"
    headers = {"X-Api-Key": NINJA_API_KEY}
    params = {"name": type_name}

    resp = requests.get(url, headers=headers, params=params, timeout=5)

    # If code is not 200 – external server error
    if resp.status_code != 200:
        # raise generic exception with status code
        raise Exception(resp.status_code)

    data = resp.json()
    if not data:   # Animal not found
        return None

    # Select entry with identical name (case-insensitive)
    chosen = None
    lower_name = type_name.lower()
    for item in data:
        if item.get("name", "").lower() == lower_name:
            chosen = item
            break
    if chosen is None:  
        chosen = data[0]

    taxonomy = chosen.get("taxonomy", {}) or {}
    characteristics = chosen.get("characteristics", {}) or {}

    # attributes from temperament or group_behavior
    temperament = characteristics.get("temperament")
    group_behavior = characteristics.get("group_behavior")
    source = temperament or group_behavior or ""
    attributes = extract_attributes(source)

    # lifespan – take the text and extract the lower number
    lifespan_text = characteristics.get("lifespan") or chosen.get("lifespan")
    lifespan = parse_lifespan(lifespan_text)

    return {
        "family": taxonomy.get("family", ""),
        "genus": taxonomy.get("genus", ""),
        "attributes": attributes,
        "lifespan": lifespan,
    }

# -------------------------
# Helper functions for pet-types
# -------------------------

# Unique identifier as a number
def generate_id():
    global id
    id += 1
    return id

# Creates dict to send to client without internal fields.
def serialize_pet_type(pet):
    result = {
        "id": pet["id"],
        "type": pet["type"],
        "family": pet["family"],
        "genus": pet["genus"],
        "attributes": pet["attributes"],
        "lifespan": pet["lifespan"],
        "pets": sorted(pet["pets"]),
    }

    return result


# Retrieves pet type by ID or returns 404 error
def get_pet_type_or_404(pet_type_id):
    pet = PET_TYPES_COL.find_one({"id": pet_type_id})
    if pet is None:
        return None, error_404()
    return pet, None

# -------------------------
# Helper functions for pictures
# -------------------------

# Downloads image from URL to local file and returns filename.
def download_picture(url):
    global image_number
    resp = requests.get(url, stream=True, timeout=10)
    if resp.status_code != 200:
        # Error downloading image
        raise Exception(resp.status_code)

    content_type = resp.headers.get("Content-Type", "").lower()
    if "image/jpeg" == content_type or "image/jpg" == content_type:
        ext = ".jpg"
    elif "png" in content_type:
        ext = ".png"
    else:
        # Not a jpg/png image 
        raise Exception(400)

    image_number += 1  
    filename = "image" + str(image_number) + ext
    full_path = os.path.join(PICTURES_DIR, filename)
    with open(full_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            if chunk:
                f.write(chunk)
    return filename


# -------------------------
# /pet-types – collection of pet types
# -------------------------

# Creates a new pet type
@app.route("/pet-types", methods=["POST"])
def create_pet_type():
    # Must be application/json
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':        
        return error_415()

    data = request.get_json(silent=True) # Return None if not exist
    if not isinstance(data, dict) or "type" not in data: # Check for "type" field and dict type
        return error_400()

    type_name = data["type"]
    if not isinstance(type_name, str) or not type_name.strip(): # Check non-empty string
        return error_400()

    # Check if pet-type with same type already exists (case-insensitive)
# Check if pet-type with same type already exists (case-insensitive)
    lower_type = type_name.lower()
    existing = PET_TYPES_COL.find_one(
        {"type": {"$regex": f"^{re.escape(type_name)}$", "$options": "i"}}
    )
    if existing is not None:
        return error_400()

    try:
        ninja_data = fetch_animal_data(type_name)
    except Exception as e:
        # If Ninja doesn't find animal – 400. Otherwise 500.
        status = e.args[0] if e.args else None
        return error_500(status)

    if ninja_data is None:
        # "type" not recognized by Ninja – 400
        return error_400()

    pet_id = str(generate_id())
    pet = {
        "id": pet_id,
        "type": type_name,
        "family": ninja_data["family"],
        "genus": ninja_data["genus"],
        "attributes": ninja_data["attributes"],
        "lifespan": ninja_data["lifespan"],  # Can be None
        "pets": [],           # list of names
        "_pets": {},          # internal: name -> pet object
    }

    PET_TYPES_COL.insert_one(pet)
    return jsonify(serialize_pet_type(pet)), 201



# Retrieves all pet types with optional filtering
@app.route("/pet-types", methods=["GET"])
def get_pet_types():
    all_docs = list(PET_TYPES_COL.find({}))
    results = [serialize_pet_type(pet) for pet in all_docs]
    args = request.args
    if not args:
        return jsonify(results), 200

    filtered = []
    # hasAttribute
    if "hasAttribute" in args:
        attr = args.get("hasAttribute", "").lower()
        for pet in results:
            if any(a.lower() == attr for a in pet["attributes"]):
                filtered.append(pet)
        # return jsonify(filtered), 200

    # field filter
    allowed_fields = {"id", "type", "family", "genus", "lifespan"}
    if any(field in args for field in allowed_fields):
        filtered = filtered or results 
        for field in allowed_fields:
            if field in args:
                value = args[field]
                if field == "lifespan":
                    try:
                        value_int = int(value)
                    except ValueError:
                        return error_400()
                    filtered = [pet for pet in filtered if pet["lifespan"] == value_int]
                else:
                    filtered = [pet for pet in filtered if isinstance(pet.get(field), str) and pet[field].lower() == value.lower()]

    return jsonify(filtered), 200


# -------------------------
# /pet-types/{id}
# -------------------------

# Retrieves a specific pet type by ID
@app.route("/pet-types/<pet_type_id>", methods=["GET"])
def get_pet_type(pet_type_id):
    pet, err = get_pet_type_or_404(pet_type_id)
    if err:
        return err
    return jsonify(serialize_pet_type(pet)), 200


# Deletes a pet type by ID
@app.route("/pet-types/<pet_type_id>", methods=["DELETE"])
def delete_pet_type(pet_type_id):
    pet = PET_TYPES_COL.find_one({"id": pet_type_id})
    if pet is None:
        return error_404()
    if pet["pets"]:
        return error_400()

    PET_TYPES_COL.delete_one({"id": pet_type_id})
    return "", 204



# -------------------------
# /pet-types/{id}/pets
# -------------------------

# Creates a new pet for a specific pet type
@app.route("/pet-types/<pet_type_id>/pets", methods=["POST"])
def create_pet(pet_type_id):
    pt, err = get_pet_type_or_404(pet_type_id)
    if err:
        return err

    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':
        return error_415()
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "name" not in data:
        return error_400()

    name = data["name"]
    
    if not isinstance(name, str) or not name.strip():
        return error_400()

    name = name.lower()

    # Ensure same pet doesn't exist in same type
    if name in pt["_pets"]:
        return error_400()

    birthdate = data.get("birthdate", "NA")
    if birthdate != "NA":
        try:
            parse_date(birthdate)
        except Exception:
            return error_400()

    picture_url = data.get("picture-url", None)
    if picture_url:
        try:
            picture_filename = download_picture(picture_url)
        except Exception:
            # Picture download failed – treat as 400 error
            return error_400()
    else:
        picture_filename = "NA"

    pet = {
        "name": name,
        "birthdate": birthdate,
        "picture": picture_filename,
    }

    pt["_pets"][name] = pet
    pt["pets"].append(name)

    PET_TYPES_COL.update_one(
        {"id": pet_type_id},
        {
            "$set": {f"_pets.{name}": pet},
            "$push": {"pets": name}
        }
    )

    return jsonify(pet), 201


# Retrieves all pets for a specific pet type with optional date filtering
@app.route("/pet-types/<pet_type_id>/pets", methods=["GET"])
def get_pets_for_type(pet_type_id):
    pet, err = get_pet_type_or_404(pet_type_id)
    if err:
        return err

    pets = list(pet["_pets"].values())

    gt = request.args.get("birthdateGT")
    lt = request.args.get("birthdateLT")

    # Checks if pet's birthdate matches the filter criteria
    def date_ok(pet_obj):
        if pet_obj["birthdate"] == "NA":
            return False
        try:
            d = parse_date(pet_obj["birthdate"])
        except Exception:
            return False
        if gt:
            try:
                d_gt = parse_date(gt)
            except Exception:
                raise ValueError
            if not d > d_gt:
                return False
        if lt:
            try:
                d_lt = parse_date(lt)
            except Exception:
                raise ValueError
            if not d < d_lt:
                return False
        return True

    if gt or lt:
        try:
            pets = [p for p in pets if date_ok(p)]
        except ValueError:
            return error_400()

    return jsonify(pets), 200

# ------------------------------------------------------------------------------------------------------------------

# /pet-types/{id}/pets/{name}
# Retrieves a specific pet by name
@app.route("/pet-types/<pet_type_id>/pets/<name>", methods=["GET"])
def get_pet(pet_type_id, name):
    pet, err = get_pet_type_or_404(pet_type_id)
    if err:
        return err

    pet = pet["_pets"].get(name.lower())
    if not pet:
        return error_404()
    return jsonify(pet), 200


# Deletes a specific pet by name
@app.route("/pet-types/<pet_type_id>/pets/<name>", methods=["DELETE"])
def delete_pet(pet_type_id, name):
    pt, err = get_pet_type_or_404(pet_type_id)
    if err:
        return err

    pet = pt["_pets"].get(name.lower())
    if not pet:
        return error_404()

    # Delete picture file if exists
    picture = pet.get("picture")
    if picture and picture != "NA":
        full_path = os.path.join(PICTURES_DIR, picture)
        if os.path.exists(full_path):
            os.remove(full_path)

    del pt["_pets"][name.lower()]
    pt["pets"] = [n for n in pt["pets"] if n.lower() != name.lower()]

    PET_TYPES_COL.update_one({"id": pet_type_id}, {"$set": {
    "_pets": pt["_pets"],
    "pets": pt["pets"],
}})

    return "", 204


# Updates a specific pet's information
@app.route("/pet-types/<pet_type_id>/pets/<name>", methods=["PUT"])
def update_pet(pet_type_id, name):
    pt, err = get_pet_type_or_404(pet_type_id)
    if err:
        return err

    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':
        return error_415()
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "name" not in data:
        return error_400()

    new_name = data["name"]
    if not isinstance(new_name, str) or not new_name.strip():
        return error_400()

    old_key = name.lower()
    new_key = new_name.lower()

    # If pet doesn't exist – 404
    pet = pt["_pets"].get(old_key)
    if not pet:
        return error_404()

    birthdate = data.get("birthdate", "NA")
    if birthdate != "NA":
        try:
            parse_date(birthdate)
        except Exception:
            return error_400()

    old_picture = pet.get("picture", "NA")

    picture_url = data.get("picture-url", None)
    if picture_url:
        try:
            picture_filename = download_picture(picture_url)
        except Exception:
            return error_400()
    else:
        picture_filename = "NA"

    if picture_filename != "NA" and old_picture and old_picture != "NA":
        full_path = os.path.join(PICTURES_DIR, old_picture)
        if os.path.exists(full_path):
            os.remove(full_path)

    # Update map according to new name (keys in dictionary + list of names)
    if new_key != old_key:
        if new_key in pt["_pets"]:
            return error_400()  # Pet with this name already exists
        del pt["_pets"][old_key]
        pt["_pets"][new_key] = pet
        pt["pets"] = [
            new_name if n.lower() == old_key else n
            for n in pt["pets"]
        ]

    # Here we save the name as it came from the client (with uppercase letter)
    pet["name"] = new_name
    pet["birthdate"] = birthdate
    pet["picture"] = picture_filename

    PET_TYPES_COL.update_one({"id": pet_type_id}, {"$set": pt})

    return jsonify(pet), 200


# -------------------------
# /pictures/{file-name}
# -------------------------

# Returns the picture file itself. the Content-Type of the response should be image/jpeg or image/png.
@app.route("/pictures/<file_name>", methods=["GET"])
def get_picture(file_name):
    full_path = os.path.join(PICTURES_DIR, file_name)
    if not os.path.exists(full_path):
        return error_404()

    if file_name.lower().endswith(".jpeg")or file_name.lower().endswith(".jpg"):
        mimetype = "image/jpeg"
    else:
        mimetype = "image/png"

    return send_file(full_path, mimetype=mimetype), 200

@app.route("/kill", methods=["GET"])
def kill_container():
    os._exit(1)

if __name__ == "__main__":
    # Server must run on port 5001 
    print("running server on host 0.0.0.0 and port 5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
