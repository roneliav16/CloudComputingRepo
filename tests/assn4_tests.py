import time
import requests

BASE1 = "http://localhost:5001"
BASE2 = "http://localhost:5002"

PET_TYPE1 = {"type":"Golden Retriever"}
PET_TYPE1_VAL = {"type":"Golden Retriever","family":"Canidae","genus":"Canis","attributes":[],"lifespan":12}

PET_TYPE2 = {"type":"Australian Shepherd"}
PET_TYPE2_VAL = {"type":"Australian Shepherd","family":"Canidae","genus":"Canis","attributes":["Loyal","outgoing","and","friendly"],"lifespan":15}

PET_TYPE3 = {"type":"Abyssinian"}
PET_TYPE3_VAL = {"type":"Abyssinian","family":"Felidae","genus":"Felis","attributes":["Intelligent","and","curious"],"lifespan":13}

PET_TYPE4 = {"type":"bulldog"}
PET_TYPE4_VAL = {"type":"bulldog","family":"Canidae","genus":"Canis","attributes":["Gentle","calm","and","affectionate"],"lifespan":None}

PET1_TYPE1 = {"name":"Lander","birthdate":"14-05-2020"}
PET2_TYPE1 = {"name":"Lanky"}
PET3_TYPE1 = {"name":"Shelly","birthdate":"07-07-2019"}
PET4_TYPE2 = {"name":"Felicity","birthdate":"27-11-2011"}
PET5_TYPE3 = {"name":"Muscles"}
PET6_TYPE3 = {"name":"Junior"}
PET7_TYPE4 = {"name":"Lazy","birthdate":"07-08-2018"}
PET8_TYPE4 = {"name":"Lemon","birthdate":"27-03-2020"}

def _wait_ready(base, timeout=60):
    t0=time.time()
    while time.time()-t0 < timeout:
        try:
            r=requests.get(base + "/pet-types", timeout=2)
            if r.status_code in (200, 404, 415, 400):
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Service not ready on {base}")

def _post_json(url, payload):
    return requests.post(url, json=payload, headers={"Content-Type":"application/json"}, timeout=10)

def _get(url):
    return requests.get(url, timeout=10)

def test_assignment4_flow():
    _wait_ready(BASE1)
    _wait_ready(BASE2)

    # 1-2) create pet types
    r1=_post_json(BASE1 + "/pet-types", PET_TYPE1); assert r1.status_code==201
    r2=_post_json(BASE1 + "/pet-types", PET_TYPE2); assert r2.status_code==201
    r3=_post_json(BASE1 + "/pet-types", PET_TYPE3); assert r3.status_code==201

    r4=_post_json(BASE2 + "/pet-types", PET_TYPE1); assert r4.status_code==201
    r5=_post_json(BASE2 + "/pet-types", PET_TYPE2); assert r5.status_code==201
    r6=_post_json(BASE2 + "/pet-types", PET_TYPE4); assert r6.status_code==201

    js1,js2,js3,js4,js5,js6 = r1.json(), r2.json(), r3.json(), r4.json(), r5.json(), r6.json()

    ids=[js1["id"], js2["id"], js3["id"], js4["id"], js5["id"], js6["id"]]
    assert len(set(ids[:3]))==3
    assert len(set(ids[3:]))==3

    def _check_val(actual, expected):
        for k,v in expected.items():
            assert actual.get(k)==v

    _check_val(js1, PET_TYPE1_VAL)
    _check_val(js2, PET_TYPE2_VAL)
    _check_val(js3, PET_TYPE3_VAL)
    _check_val(js4, PET_TYPE1_VAL)
    _check_val(js5, PET_TYPE2_VAL)
    _check_val(js6, PET_TYPE4_VAL)

    id1,id2,id3,id4,id5,id6 = ids

    # 3-7) add pets
    assert _post_json(f"{BASE1}/pet-types/{id1}/pets", PET1_TYPE1).status_code==201
    assert _post_json(f"{BASE1}/pet-types/{id1}/pets", PET2_TYPE1).status_code==201
    assert _post_json(f"{BASE1}/pet-types/{id3}/pets", PET5_TYPE3).status_code==201
    assert _post_json(f"{BASE1}/pet-types/{id3}/pets", PET6_TYPE3).status_code==201

    assert _post_json(f"{BASE2}/pet-types/{id4}/pets", PET3_TYPE1).status_code==201
    assert _post_json(f"{BASE2}/pet-types/{id5}/pets", PET4_TYPE2).status_code==201
    assert _post_json(f"{BASE2}/pet-types/{id6}/pets", PET7_TYPE4).status_code==201
    assert _post_json(f"{BASE2}/pet-types/{id6}/pets", PET8_TYPE4).status_code==201

    # 8) GET pet-type id2 from store1
    g=_get(f"{BASE1}/pet-types/{id2}")
    assert g.status_code==200
    _check_val(g.json(), PET_TYPE2_VAL)

    # 9) GET pets for id6 from store2
    gp=_get(f"{BASE2}/pet-types/{id6}/pets")
    assert gp.status_code==200
    arr=gp.json()
    # order not guaranteed
    names={p.get("name").lower():p for p in arr}
    assert "lazy" in names and "lemon" in names, f'names: {names}'
    assert names["lazy"]["name"]=="Lazy"
    assert names["lazy"].get("birthdate")=="07-08-2018"
    assert names["lemon"]["name"]=="Lemon"
    assert names["lemon"].get("birthdate")=="27-03-2020"