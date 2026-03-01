# import time
# import requests

# BASE1 = "http://localhost:5001"
# BASE2 = "http://localhost:5002"

# PET_TYPE1 = {"type":"Golden Retriever"}
# PET_TYPE1_VAL = {"type":"Golden Retriever","family":"Canidae","genus":"Canis","attributes":[],"lifespan":12}

# PET_TYPE2 = {"type":"Australian Shepherd"}
# PET_TYPE2_VAL = {"type":"Australian Shepherd","family":"Canidae","genus":"Canis","attributes":["Loyal","outgoing","and","friendly"],"lifespan":15}

# PET_TYPE3 = {"type":"Abyssinian"}
# PET_TYPE3_VAL = {"type":"Abyssinian","family":"Felidae","genus":"Felis","attributes":["Intelligent","and","curious"],"lifespan":13}

# PET_TYPE4 = {"type":"bulldog"}
# PET_TYPE4_VAL = {"type":"bulldog","family":"Canidae","genus":"Canis","attributes":["Gentle","calm","and","affectionate"],"lifespan":None}

# PET1_TYPE1 = {"name":"Lander","birthdate":"14-05-2020"}
# PET2_TYPE1 = {"name":"Lanky"}
# PET3_TYPE1 = {"name":"Shelly","birthdate":"07-07-2019"}
# PET4_TYPE2 = {"name":"Felicity","birthdate":"27-11-2011"}
# PET5_TYPE3 = {"name":"Muscles"}
# PET6_TYPE3 = {"name":"Junior"}
# PET7_TYPE4 = {"name":"Lazy","birthdate":"07-08-2018"}
# PET8_TYPE4 = {"name":"Lemon","birthdate":"27-03-2020"}

# def _wait_ready(base, timeout=60):
#     t0=time.time()
#     while time.time()-t0 < timeout:
#         try:
#             r=requests.get(base + "/pet-types", timeout=2)
#             if r.status_code in (200, 404, 415, 400):
#                 return
#         except Exception:
#             pass
#         time.sleep(1)
#     raise RuntimeError(f"Service not ready on {base}")

# def _post_json(url, payload):
#     return requests.post(url, json=payload, headers={"Content-Type":"application/json"}, timeout=10)

# def _get(url):
#     return requests.get(url, timeout=10)

# def test_assignment4_flow():
#     _wait_ready(BASE1)
#     _wait_ready(BASE2)

#     # 1-2) create pet types
#     r1=_post_json(BASE1 + "/pet-types", PET_TYPE1); assert r1.status_code==201
#     r2=_post_json(BASE1 + "/pet-types", PET_TYPE2); assert r2.status_code==201
#     r3=_post_json(BASE1 + "/pet-types", PET_TYPE3); assert r3.status_code==201

#     r4=_post_json(BASE2 + "/pet-types", PET_TYPE1); assert r4.status_code==201
#     r5=_post_json(BASE2 + "/pet-types", PET_TYPE2); assert r5.status_code==201
#     r6=_post_json(BASE2 + "/pet-types", PET_TYPE4); assert r6.status_code==201

#     js1,js2,js3,js4,js5,js6 = r1.json(), r2.json(), r3.json(), r4.json(), r5.json(), r6.json()

#     ids=[js1["id"], js2["id"], js3["id"], js4["id"], js5["id"], js6["id"]]
#     assert len(set(ids[:3]))==3
#     assert len(set(ids[3:]))==3

#     def _check_val(actual, expected):
#         for k,v in expected.items():
#             assert actual.get(k)==v

#     _check_val(js1, PET_TYPE1_VAL)
#     _check_val(js2, PET_TYPE2_VAL)
#     _check_val(js3, PET_TYPE3_VAL)
#     _check_val(js4, PET_TYPE1_VAL)
#     _check_val(js5, PET_TYPE2_VAL)
#     _check_val(js6, PET_TYPE4_VAL)

#     id1,id2,id3,id4,id5,id6 = ids

#     # 3-7) add pets
#     assert _post_json(f"{BASE1}/pet-types/{id1}/pets", PET1_TYPE1).status_code==201
#     assert _post_json(f"{BASE1}/pet-types/{id1}/pets", PET2_TYPE1).status_code==201
#     assert _post_json(f"{BASE1}/pet-types/{id3}/pets", PET5_TYPE3).status_code==201
#     assert _post_json(f"{BASE1}/pet-types/{id3}/pets", PET6_TYPE3).status_code==201

#     assert _post_json(f"{BASE2}/pet-types/{id4}/pets", PET3_TYPE1).status_code==201
#     assert _post_json(f"{BASE2}/pet-types/{id5}/pets", PET4_TYPE2).status_code==201
#     assert _post_json(f"{BASE2}/pet-types/{id6}/pets", PET7_TYPE4).status_code==201
#     assert _post_json(f"{BASE2}/pet-types/{id6}/pets", PET8_TYPE4).status_code==201

#     # 8) GET pet-type id2 from store1
#     g=_get(f"{BASE1}/pet-types/{id2}")
#     assert g.status_code==200
#     _check_val(g.json(), PET_TYPE2_VAL)

#     # 9) GET pets for id6 from store2
#     gp=_get(f"{BASE2}/pet-types/{id6}/pets")
#     assert gp.status_code==200
#     arr=gp.json()
#     # order not guaranteed
#     names={p.get("name").lower():p for p in arr}
#     assert "lazy" in names and "lemon" in names, f'names: {names}'
#     assert names["lazy"]["name"]=="lazy"
#     assert names["lazy"].get("birthdate")=="07-08-2018"
#     assert names["lemon"]["name"]=="lemon"
#     assert names["lemon"].get("birthdate")=="27-03-2020"

# import pytest
# import requests
# import json

# # Test data from Assignment #4 specification
# PET_TYPE1 = {"type": "Golden Retriever"}
# PET_TYPE1_VAL = {
#     "type": "Golden Retriever",
#     "family": "Canidae",
#     "genus": "Canis",
#     "attributes": [],
#     "lifespan": 12
# }

# PET_TYPE2 = {"type": "Australian Shepherd"}
# PET_TYPE2_VAL = {
#     "type": "Australian Shepherd",
#     "family": "Canidae",
#     "genus": "Canis",
#     "attributes": ["Loyal", "outgoing", "and", "friendly"],
#     "lifespan": 15
# }

# PET_TYPE3 = {"type": "Abyssinian"}
# PET_TYPE3_VAL = {
#     "type": "Abyssinian",
#     "family": "Felidae",
#     "genus": "Felis",
#     "attributes": ["Intelligent", "and", "curious"],
#     "lifespan": 13
# }

# PET_TYPE4 = {"type": "bulldog"}
# PET_TYPE4_VAL = {
#     "type": "bulldog",
#     "family": "Canidae",
#     "genus": "Canis",
#     "attributes": ["Gentle", "calm", "and", "affectionate"],
#     "lifespan": None
# }

# PET1_TYPE1 = {"name": "Lander", "birthdate": "14-05-2020"}
# PET2_TYPE1 = {"name": "Lanky"}
# PET3_TYPE1 = {"name": "Shelly", "birthdate": "07-07-2019"}
# PET4_TYPE2 = {"name": "Felicity", "birthdate": "27-11-2011"}
# PET5_TYPE3 = {"name": "Muscles"}
# PET6_TYPE3 = {"name": "Junior"}
# PET7_TYPE4 = {"name": "Lazy", "birthdate": "07-08-2018"}
# PET8_TYPE4 = {"name": "Lemon", "birthdate": "27-03-2020"}

# # Base URLs for the services
# STORE1_URL = "http://localhost:5001"
# STORE2_URL = "http://localhost:5002"

# # Global variables to store IDs
# pet_type_ids = []


# class TestPetStoreAssignment4:
#     """Test suite for Assignment #4 - Pet Store Application"""

#     def test_01_post_pet_types_to_store1(self):
#         """Test 1-2: POST 3 pet-types to pet-store #1"""
#         global pet_type_ids
        
#         # POST PET_TYPE1 to store #1
#         response1 = requests.post(f"{STORE1_URL}/pet-types", json=PET_TYPE1)
#         assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
#         data1 = response1.json()
        
#         # Validate returned data
#         assert "id" in data1, "Response should contain 'id' field"
#         assert data1["type"] == PET_TYPE1_VAL["type"], f"Type mismatch"
#         assert data1["family"] == PET_TYPE1_VAL["family"], f"Family mismatch"
#         assert data1["genus"] == PET_TYPE1_VAL["genus"], f"Genus mismatch"
        
#         id_1 = data1["id"]
#         pet_type_ids.append(id_1)
        
#         # POST PET_TYPE2 to store #1
#         response2 = requests.post(f"{STORE1_URL}/pet-types", json=PET_TYPE2)
#         assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"
#         data2 = response2.json()
        
#         assert "id" in data2, "Response should contain 'id' field"
#         assert data2["type"] == PET_TYPE2_VAL["type"], f"Type mismatch"
#         assert data2["family"] == PET_TYPE2_VAL["family"], f"Family mismatch"
#         assert data2["genus"] == PET_TYPE2_VAL["genus"], f"Genus mismatch"
        
#         id_2 = data2["id"]
#         pet_type_ids.append(id_2)
        
#         # POST PET_TYPE3 to store #1
#         response3 = requests.post(f"{STORE1_URL}/pet-types", json=PET_TYPE3)
#         assert response3.status_code == 201, f"Expected 201, got {response3.status_code}"
#         data3 = response3.json()
        
#         assert "id" in data3, "Response should contain 'id' field"
#         assert data3["type"] == PET_TYPE3_VAL["type"], f"Type mismatch"
#         assert data3["family"] == PET_TYPE3_VAL["family"], f"Family mismatch"
#         assert data3["genus"] == PET_TYPE3_VAL["genus"], f"Genus mismatch"
        
#         id_3 = data3["id"]
#         pet_type_ids.append(id_3)
        
#         # Verify all IDs are unique
#         assert len(set([id_1, id_2, id_3])) == 3, "All IDs should be unique"

#     def test_02_post_pet_types_to_store2(self):
#         """Test 1-2: POST 3 pet-types to pet-store #2"""
#         global pet_type_ids
        
#         # POST PET_TYPE1 to store #2
#         response4 = requests.post(f"{STORE2_URL}/pet-types", json=PET_TYPE1)
#         assert response4.status_code == 201, f"Expected 201, got {response4.status_code}"
#         data4 = response4.json()
        
#         assert "id" in data4, "Response should contain 'id' field"
#         assert data4["type"] == PET_TYPE1_VAL["type"], f"Type mismatch"
#         assert data4["family"] == PET_TYPE1_VAL["family"], f"Family mismatch"
#         assert data4["genus"] == PET_TYPE1_VAL["genus"], f"Genus mismatch"
        
#         id_4 = data4["id"]
#         pet_type_ids.append(id_4)
        
#         # POST PET_TYPE2 to store #2
#         response5 = requests.post(f"{STORE2_URL}/pet-types", json=PET_TYPE2)
#         assert response5.status_code == 201, f"Expected 201, got {response5.status_code}"
#         data5 = response5.json()
        
#         assert "id" in data5, "Response should contain 'id' field"
#         assert data5["type"] == PET_TYPE2_VAL["type"], f"Type mismatch"
#         assert data5["family"] == PET_TYPE2_VAL["family"], f"Family mismatch"
#         assert data5["genus"] == PET_TYPE2_VAL["genus"], f"Genus mismatch"
        
#         id_5 = data5["id"]
#         pet_type_ids.append(id_5)
        
#         # POST PET_TYPE4 to store #2
#         response6 = requests.post(f"{STORE2_URL}/pet-types", json=PET_TYPE4)
#         assert response6.status_code == 201, f"Expected 201, got {response6.status_code}"
#         data6 = response6.json()
        
#         assert "id" in data6, "Response should contain 'id' field"
#         assert data6["type"] == PET_TYPE4_VAL["type"], f"Type mismatch"
#         assert data6["family"] == PET_TYPE4_VAL["family"], f"Family mismatch"
#         assert data6["genus"] == PET_TYPE4_VAL["genus"], f"Genus mismatch"
        
#         id_6 = data6["id"]
#         pet_type_ids.append(id_6)
        
#         # Verify all IDs are unique (within store #2)
#         assert len(set([id_4, id_5, id_6])) == 3, "All IDs should be unique"

#     def test_03_post_pets_to_store1_type1(self):
#         """Test 3: POST 2 pets of type 1 to pet-store #1"""
#         global pet_type_ids
#         id_1 = pet_type_ids[0]
        
#         # POST PET1_TYPE1
#         response1 = requests.post(
#             f"{STORE1_URL}/pet-types/{id_1}/pets",
#             json=PET1_TYPE1
#         )
#         assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
        
#         # POST PET2_TYPE1
#         response2 = requests.post(
#             f"{STORE1_URL}/pet-types/{id_1}/pets",
#             json=PET2_TYPE1
#         )
#         assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"

#     def test_04_post_pets_to_store1_type3(self):
#         """Test 4: POST 2 pets of type 3 to pet-store #1"""
#         global pet_type_ids
#         id_3 = pet_type_ids[2]
        
#         # POST PET5_TYPE3
#         response1 = requests.post(
#             f"{STORE1_URL}/pet-types/{id_3}/pets",
#             json=PET5_TYPE3
#         )
#         assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
        
#         # POST PET6_TYPE3
#         response2 = requests.post(
#             f"{STORE1_URL}/pet-types/{id_3}/pets",
#             json=PET6_TYPE3
#         )
#         assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"

#     def test_05_post_pet_to_store2_type1(self):
#         """Test 5: POST 1 pet of type 1 to pet-store #2"""
#         global pet_type_ids
#         id_4 = pet_type_ids[3]
        
#         # POST PET3_TYPE1
#         response = requests.post(
#             f"{STORE2_URL}/pet-types/{id_4}/pets",
#             json=PET3_TYPE1
#         )
#         assert response.status_code == 201, f"Expected 201, got {response.status_code}"

#     def test_06_post_pet_to_store2_type2(self):
#         """Test 6: POST 1 pet of type 2 to pet-store #2"""
#         global pet_type_ids
#         id_5 = pet_type_ids[4]
        
#         # POST PET4_TYPE2
#         response = requests.post(
#             f"{STORE2_URL}/pet-types/{id_5}/pets",
#             json=PET4_TYPE2
#         )
#         assert response.status_code == 201, f"Expected 201, got {response.status_code}"

#     def test_07_post_pets_to_store2_type4(self):
#         """Test 7: POST 2 pets of type 4 to pet-store #2"""
#         global pet_type_ids
#         id_6 = pet_type_ids[5]
        
#         # POST PET7_TYPE4
#         response1 = requests.post(
#             f"{STORE2_URL}/pet-types/{id_6}/pets",
#             json=PET7_TYPE4
#         )
#         assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
        
#         # POST PET8_TYPE4
#         response2 = requests.post(
#             f"{STORE2_URL}/pet-types/{id_6}/pets",
#             json=PET8_TYPE4
#         )
#         assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"

#     def test_08_get_pet_type2_from_store1(self):
#         """Test 8: GET /pet-types/{id2} from pet-store #1"""
#         global pet_type_ids
#         id_2 = pet_type_ids[1]
        
#         response = requests.get(f"{STORE1_URL}/pet-types/{id_2}")
#         assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
#         data = response.json()
        
#         # Validate all fields match PET_TYPE2_VAL
#         assert data["type"] == PET_TYPE2_VAL["type"], f"Type mismatch"
#         assert data["family"] == PET_TYPE2_VAL["family"], f"Family mismatch"
#         assert data["genus"] == PET_TYPE2_VAL["genus"], f"Genus mismatch"
#         assert data["lifespan"] == PET_TYPE2_VAL["lifespan"], f"Lifespan mismatch"
        
#         # Check attributes (order may vary)
#         assert set(data["attributes"]) == set(PET_TYPE2_VAL["attributes"]), f"Attributes mismatch"

#     def test_09_get_pets_of_type6_from_store2(self):
#         """Test 9: GET /pet-types/{id6}/pets from pet-store #2"""
#         global pet_type_ids
#         id_6 = pet_type_ids[5]
        
#         response = requests.get(f"{STORE2_URL}/pet-types/{id_6}/pets")
#         assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
#         data = response.json()
        
#         # Should be an array
#         assert isinstance(data, list), "Response should be a JSON array"
        
#         # Should contain 2 pets
#         assert len(data) == 2, f"Expected 2 pets, got {len(data)}"
        
#         # Extract pet names
#         pet_names = [pet["name"] for pet in data]
        
#         # Should contain both PET7_TYPE4 and PET8_TYPE4
#         assert PET7_TYPE4["name"] in pet_names, f"{PET7_TYPE4['name']} not found in response"
#         assert PET8_TYPE4["name"] in pet_names, f"{PET8_TYPE4['name']} not found in response"
        
#         # Validate each pet has expected fields
#         for pet in data:
#             assert "name" in pet, "Pet should have 'name' field"
#             assert "birthdate" in pet, "Pet should have 'birthdate' field"
            
#             # Validate specific pet data
#             if pet["name"] == PET7_TYPE4["name"]:
#                 assert pet["birthdate"] == PET7_TYPE4["birthdate"], "Birthdate mismatch for Lazy"
#             elif pet["name"] == PET8_TYPE4["name"]:
#                 assert pet["birthdate"] == PET8_TYPE4["birthdate"], "Birthdate mismatch for Lemon"

# - tester pytest file for checking query.txt file -

# import pytest
# import requests
# import json

# # Base URLs for the pet store instances
# PET_STORE_1_URL = "http://localhost:5001"
# PET_STORE_2_URL = "http://localhost:5002"
# PET_ORDER_URL = "http://localhost:5003"

# # Pet Type Payloads
# PET_TYPE1 = {
#     "type": "Golden Retriever"
# }

# PET_TYPE2 = {
#     "type": "Australian Shepherd"
# }

# PET_TYPE3 = {
#     "type": "Abyssinian"
# }

# PET_TYPE4 = {
#     "type": "bulldog"
# }

# # Pet Payloads
# PET1_TYPE1 = {
#     "name": "Lander",
#     "birthdate": "14-05-2020"
# }

# PET2_TYPE1 = {
#     "name": "Lanky"
# }

# PET3_TYPE1 = {
#     "name": "Shelly",
#     "birthdate": "07-07-2019"
# }

# PET4_TYPE2 = {
#     "name": "Felicity",
#     "birthdate": "27-11-2011"
# }

# PET5_TYPE3 = {
#     "name": "Muscles"
# }

# PET6_TYPE3 = {
#     "name": "Junior"
# }

# PET7_TYPE4 = {
#     "name": "Lazy",
#     "birthdate": "07-08-2018"
# }

# PET8_TYPE4 = {
#     "name": "Lemon",
#     "birthdate": "27-03-2020"
# }

# # Global variables to store IDs
# pet_type_ids = {}


# def test_01_post_pet_types_to_store1():
#     """POST 3 pet-types to pet-store #1"""
#     global pet_type_ids
    
#     # POST PET_TYPE1 to store 1
#     response1 = requests.post(f"{PET_STORE_1_URL}/pet-types", json=PET_TYPE1)
#     data1 = response1.json()
#     pet_type_ids['id_1'] = data1["id"]
    
#     # POST PET_TYPE2 to store 1
#     response2 = requests.post(f"{PET_STORE_1_URL}/pet-types", json=PET_TYPE2)
#     data2 = response2.json()
#     pet_type_ids['id_2'] = data2["id"]
    
#     # POST PET_TYPE3 to store 1
#     response3 = requests.post(f"{PET_STORE_1_URL}/pet-types", json=PET_TYPE3)
#     data3 = response3.json()
#     pet_type_ids['id_3'] = data3["id"]


# def test_02_post_pet_types_to_store2():
#     """POST 3 pet-types to pet-store #2"""
#     global pet_type_ids
    
#     # POST PET_TYPE1 to store 2
#     response4 = requests.post(f"{PET_STORE_2_URL}/pet-types", json=PET_TYPE1)
#     data4 = response4.json()
#     pet_type_ids['id_4'] = data4["id"]
    
#     # POST PET_TYPE2 to store 2
#     response5 = requests.post(f"{PET_STORE_2_URL}/pet-types", json=PET_TYPE2)
#     data5 = response5.json()
#     pet_type_ids['id_5'] = data5["id"]
    
#     # POST PET_TYPE4 to store 2
#     response6 = requests.post(f"{PET_STORE_2_URL}/pet-types", json=PET_TYPE4)
#     data6 = response6.json()
#     pet_type_ids['id_6'] = data6["id"]


# def test_03_post_pets_to_store1_type1():
#     """POST 2 pets to pet-store #1 pet-type id_1"""
#     id_1 = pet_type_ids['id_1']
    
#     # POST PET1_TYPE1
#     requests.post(f"{PET_STORE_1_URL}/pet-types/{id_1}/pets", json=PET1_TYPE1)
    
#     # POST PET2_TYPE1
#     requests.post(f"{PET_STORE_1_URL}/pet-types/{id_1}/pets", json=PET2_TYPE1)


# def test_04_post_pets_to_store1_type3():
#     """POST 2 pets to pet-store #1 pet-type id_3"""
#     id_3 = pet_type_ids['id_3']
    
#     # POST PET5_TYPE3
#     requests.post(f"{PET_STORE_1_URL}/pet-types/{id_3}/pets", json=PET5_TYPE3)
    
#     # POST PET6_TYPE3
#     requests.post(f"{PET_STORE_1_URL}/pet-types/{id_3}/pets", json=PET6_TYPE3)


# def test_05_post_pet_to_store2_type1():
#     """POST 1 pet to pet-store #2 pet-type id_4"""
#     id_4 = pet_type_ids['id_4']
    
#     # POST PET3_TYPE1
#     requests.post(f"{PET_STORE_2_URL}/pet-types/{id_4}/pets", json=PET3_TYPE1)


# def test_06_post_pet_to_store2_type2():
#     """POST 1 pet to pet-store #2 pet-type id_5"""
#     id_5 = pet_type_ids['id_5']
    
#     # POST PET4_TYPE2
#     requests.post(f"{PET_STORE_2_URL}/pet-types/{id_5}/pets", json=PET4_TYPE2)


# def test_07_post_pets_to_store2_type4():
#     """POST 2 pets to pet-store #2 pet-type id_6"""
#     id_6 = pet_type_ids['id_6']
    
#     # POST PET7_TYPE4
#     requests.post(f"{PET_STORE_2_URL}/pet-types/{id_6}/pets", json=PET7_TYPE4)
    
#     # POST PET8_TYPE4
#     requests.post(f"{PET_STORE_2_URL}/pet-types/{id_6}/pets", json=PET8_TYPE4)



# - tester pytest file for checking query.txt file -

import pytest
import requests
import json

# Base URLs for the pet store instances
PET_STORE_1_URL = "http://localhost:5001"
PET_STORE_2_URL = "http://localhost:5002"
PET_ORDER_URL = "http://localhost:5003"

# Pet Type Payloads
PET_TYPE1 = {
    "type": "Golden Retriever"
}

PET_TYPE2 = {
    "type": "Australian Shepherd"
}

PET_TYPE3 = {
    "type": "Abyssinian"
}

PET_TYPE4 = {
    "type": "bulldog"
}

# Pet Payloads
PET1_TYPE1 = {
    "name": "Lander",
    "birthdate": "14-05-2020"
}

PET2_TYPE1 = {
    "name": "Lanky"
}

PET3_TYPE1 = {
    "name": "Shelly",
    "birthdate": "07-07-2019"
}

PET4_TYPE2 = {
    "name": "Felicity",
    "birthdate": "27-11-2011"
}

PET5_TYPE3 = {
    "name": "Muscles"
}

PET6_TYPE3 = {
    "name": "Junior"
}

PET7_TYPE4 = {
    "name": "Lazy",
    "birthdate": "07-08-2018"
}

PET8_TYPE4 = {
    "name": "Lemon",
    "birthdate": "27-03-2020"
}

# Global variables to store IDs
pet_type_ids = {}


def test_01_post_pet_types_to_store1():
    """POST 3 pet-types to pet-store #1"""
    global pet_type_ids
    
    # POST PET_TYPE1 to store 1
    response1 = requests.post(f"{PET_STORE_1_URL}/pet-types", json=PET_TYPE1)
    data1 = response1.json()
    pet_type_ids['id_1'] = data1["id"]
    
    # POST PET_TYPE2 to store 1
    response2 = requests.post(f"{PET_STORE_1_URL}/pet-types", json=PET_TYPE2)
    data2 = response2.json()
    pet_type_ids['id_2'] = data2["id"]
    
    # POST PET_TYPE3 to store 1
    response3 = requests.post(f"{PET_STORE_1_URL}/pet-types", json=PET_TYPE3)
    data3 = response3.json()
    pet_type_ids['id_3'] = data3["id"]


def test_02_post_pet_types_to_store2():
    """POST 3 pet-types to pet-store #2"""
    global pet_type_ids
    
    # POST PET_TYPE1 to store 2
    response4 = requests.post(f"{PET_STORE_2_URL}/pet-types", json=PET_TYPE1)
    data4 = response4.json()
    pet_type_ids['id_4'] = data4["id"]
    
    # POST PET_TYPE2 to store 2
    response5 = requests.post(f"{PET_STORE_2_URL}/pet-types", json=PET_TYPE2)
    data5 = response5.json()
    pet_type_ids['id_5'] = data5["id"]
    
    # POST PET_TYPE4 to store 2
    response6 = requests.post(f"{PET_STORE_2_URL}/pet-types", json=PET_TYPE4)
    data6 = response6.json()
    pet_type_ids['id_6'] = data6["id"]


def test_03_post_pets_to_store1_type1():
    """POST 2 pets to pet-store #1 pet-type id_1"""
    id_1 = pet_type_ids['id_1']
    
    # POST PET1_TYPE1
    requests.post(f"{PET_STORE_1_URL}/pet-types/{id_1}/pets", json=PET1_TYPE1)
    
    # POST PET2_TYPE1
    requests.post(f"{PET_STORE_1_URL}/pet-types/{id_1}/pets", json=PET2_TYPE1)


def test_04_post_pets_to_store1_type3():
    """POST 2 pets to pet-store #1 pet-type id_3"""
    id_3 = pet_type_ids['id_3']
    
    # POST PET5_TYPE3
    requests.post(f"{PET_STORE_1_URL}/pet-types/{id_3}/pets", json=PET5_TYPE3)
    
    # POST PET6_TYPE3
    requests.post(f"{PET_STORE_1_URL}/pet-types/{id_3}/pets", json=PET6_TYPE3)


def test_05_post_pet_to_store2_type1():
    """POST 1 pet to pet-store #2 pet-type id_4"""
    id_4 = pet_type_ids['id_4']
    
    # POST PET3_TYPE1
    requests.post(f"{PET_STORE_2_URL}/pet-types/{id_4}/pets", json=PET3_TYPE1)


def test_06_post_pet_to_store2_type2():
    """POST 1 pet to pet-store #2 pet-type id_5"""
    id_5 = pet_type_ids['id_5']
    
    # POST PET4_TYPE2
    requests.post(f"{PET_STORE_2_URL}/pet-types/{id_5}/pets", json=PET4_TYPE2)


def test_07_post_pets_to_store2_type4():
    """POST 2 pets to pet-store #2 pet-type id_6"""
    id_6 = pet_type_ids['id_6']
    
    # POST PET7_TYPE4
    requests.post(f"{PET_STORE_2_URL}/pet-types/{id_6}/pets", json=PET7_TYPE4)
    
    # POST PET8_TYPE4
    requests.post(f"{PET_STORE_2_URL}/pet-types/{id_6}/pets", json=PET8_TYPE4)
