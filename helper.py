import pandas as pd
import re

def includes_special(input):

    rule = re.compile("[@_!#$%^&*()<>?/|}{~:]")

    return True if rule.search(input) else False

def exclusive_special(input): 

    special_chars = "[@_!#$%^&*()<>?/|}{~:]"
    for char in input: 
        if char not in special_chars: 
            return False 
    return True

def extract_domain(email):

    if pd.isna(email) or "@" not in str(email):
        return ''
    return str(email).split("@")[-1].lower()

def extract_username(email): 

    if pd.isna(email) or "@" not in str(email):
        return ''
    return str(email).split("@")[0].lower()

def normalize_domain(domain):

    # get the value before the period. 'samsung.com' should return 'samsung'
    domain_arr = domain.split('.')
    return domain_arr[0]

def lookup_df(email, df):
    
    if df is not None: 
        selected_emails = set(df['Email'])
        if email in selected_emails:
            return df[df['Email'] == email].iloc[0]
        return pd.DataFrame()
    return pd.DataFrame()
