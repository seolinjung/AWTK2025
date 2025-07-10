import pandas as pd 
import os
import json

def extract_domain(email):
    if pd.isna(email) or "@" not in str(email):
        return ''
    return str(email).split("@")[-1].lower()

def normalize_domain(domain):

    # get the value before the period. 'samsung.com' should return 'samsung'
    domain_arr = domain.split('.')
    return domain_arr[0]

def retrieve_json(input):

    json_path = os.path.join('data', 'exceptions')

    name = input + ".json"
    path = os.path.join(json_path, name)

    if os.path.exists(path):
        with open(path, 'r') as file: 
            return json.load(file)[input]
        return False
    return False

def retrieve_csv(args, input, seonhye=False):

    db_root_path = ""

    db_root_path = os.path.join("raw_db", "org_db", "seonhye") if seonhye else os.path.join("raw_db", "org_db", args.date)
    
    if os.path.exists(db_root_path): 
        return os.path.join(db_root_path, input + ".csv")
    
    return False