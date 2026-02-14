import json
import os
import time
import requests

BASE1 = "http://localhost:5001"
BASE2 = "http://localhost:5002"
ORDER = "http://localhost:5003"

PET_TYPE1 = {"type":"Golden Retriever"}
PET_TYPE2 = {"type":"Australian Shepherd"}
PET_TYPE3 = {"type":"Abyssinian"}
PET_TYPE4 = {"type":"bulldog"}

PET1_TYPE1 = {"name":"Lander","birthdate":"14-05-2020"}
PET2_TYPE1 = {"name":"Lanky"}
PET3_TYPE1 = {"name":"Shelly","birthdate":"07-07-2019"}
PET4_TYPE2 = {"name":"Felicity","birthdate":"27-11-2011"}
PET5_TYPE3 = {"name":"Muscles"}
PET6_TYPE3 = {"name":"Junior"}
PET7_TYPE4 = {"name":"Lazy","birthdate":"07-08-2018"}
PET8_TYPE4 = {"name":"Lemon","birthdate":"27-03-2020"}

def _wait_ready(url, timeout=60):
    t0=time.time()
    while time.time()-t0 < timeout:
        try:
            r=requests.get(url + "/pet-types", timeout=2)
            if r.status_code in (200, 404, 415, 400):
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Service not ready: {url}")

def _post_json(url, payload, expect=None):
    r=requests.post(url, json=payload, headers={"Content-Type":"application/json"}, timeout=10)
    if expect is not None and r.status_code != expect:
        raise RuntimeError(f"POST {url} expected {expect}, got {r.status_code}: {r.text}")
    return r

def _get(url):
    return requests.get(url, timeout=10)

def seed_data():
    _wait_ready(BASE1)
    _wait_ready(BASE2)
    # create types (store1: 1,2,3; store2: 1,2,4)
    id1=_post_json(BASE1 + "/pet-types", PET_TYPE1, 201).json()["id"]
    id2=_post_json(BASE1 + "/pet-types", PET_TYPE2, 201).json()["id"]
    id3=_post_json(BASE1 + "/pet-types", PET_TYPE3, 201).json()["id"]

    id4=_post_json(BASE2 + "/pet-types", PET_TYPE1, 201).json()["id"]
    id5=_post_json(BASE2 + "/pet-types", PET_TYPE2, 201).json()["id"]
    id6=_post_json(BASE2 + "/pet-types", PET_TYPE4, 201).json()["id"]

    # pets
    _post_json(f"{BASE1}/pet-types/{id1}/pets", PET1_TYPE1, 201)
    _post_json(f"{BASE1}/pet-types/{id1}/pets", PET2_TYPE1, 201)
    _post_json(f"{BASE1}/pet-types/{id3}/pets", PET5_TYPE3, 201)
    _post_json(f"{BASE1}/pet-types/{id3}/pets", PET6_TYPE3, 201)

    _post_json(f"{BASE2}/pet-types/{id4}/pets", PET3_TYPE1, 201)
    _post_json(f"{BASE2}/pet-types/{id5}/pets", PET4_TYPE2, 201)
    _post_json(f"{BASE2}/pet-types/{id6}/pets", PET7_TYPE4, 201)
    _post_json(f"{BASE2}/pet-types/{id6}/pets", PET8_TYPE4, 201)

def run_queries(query_file="query.txt", response_file="response.txt"):
    with open(query_file, "r", encoding="utf-8") as f:
        lines=[ln.strip() for ln in f.readlines() if ln.strip()]

    with open(response_file, "w", encoding="utf-8") as out:
        for entry in lines:
            if not entry.endswith(";"):
                # ignore malformed
                continue
            entry = entry[:-1].strip()

            if entry.startswith("query:"):
                rest=entry[len("query:"):].strip()
                store_num, qstring = rest.split(",", 1)
                base = BASE1 if store_num.strip()=="1" else BASE2
                r=_get(f"{base}/pet-types?{qstring.strip()}")
                out.write(f"{r.status_code}\n")
                if r.status_code==200:
                    out.write(r.text.rstrip()+"\n")
                else:
                    out.write("NONE\n")
                out.write(";\n")

            elif entry.startswith("purchase:"):
                payload_str=entry[len("purchase:"):].strip()
                try:
                    payload=json.loads(payload_str)
                except Exception:
                    out.write("400\nNONE\n;\n")
                    continue
                r=_post_json(f"{ORDER}/purchases", payload)
                out.write(f"{r.status_code}\n")
                if r.status_code==201:
                    out.write(r.text.rstrip()+"\n")
                else:
                    out.write("NONE\n")
                out.write(";\n")

if __name__ == "__main__":
    seed_data()
    if not os.path.exists("query.txt"):
        raise SystemExit("query.txt not found in repo root")
    run_queries("query.txt", "response.txt")
