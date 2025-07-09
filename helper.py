import pandas as pd 
import os
import json

def extract_domain(email):
    if pd.isna(email) or "@" not in str(email):
        return ''
    return str(email).split("@")[-1].lower()

# normalize domain 
def normalize_domain(domain):

    # get the value before the period. 'samsung.com' should return 'samsung'
    domain_arr = domain.split('.')
    return domain_arr[0]

# retrive an array format of the request json file
def retrieve_json(input):

    json_path = os.path.join('data', 'exceptions')

    name = input + ".json"
    path = os.path.join(json_path, name)

    with open(path, 'r') as file: 
        return json.load(file)[input]

def retrieve_csv(args, input, seonhye=False):

    db_root_path = ""

    # define path to db root
    db_root_path = os.path.join("raw_db", "org_db", "seonhye") if seonhye else os.path.join("raw_db", "org_db", args.date)
        
    return os.path.join(db_root_path, input + ".csv")

def reverse_dict(dict):

    reversed = {}

    for key, values in dict.items():
        for value in values: 
            # map each individual value to the key 
            reversed[value] = key 

    return reversed  

