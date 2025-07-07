import pandas as pd 

def extract_domain(email):
    if pd.isna(email) or "@" not in str(email):
        return ''
    return str(email).split("@")[-1].lower()

'''
def reverse_dict(dict):

    reversed = {}
    # iterate through the dictionary
    for key, values in dict.items():
        for value in values: 
            # map each individual value to the key 
            reversed[value] = key 

    return reversed
'''       

