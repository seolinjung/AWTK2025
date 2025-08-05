import pandas as pd
import re

def includes_special(input):

    rule = re.compile("[@_!#$%^&*()<>?/|}{~:]")

    return True if rule.search(input) else False

def exclusive_special(input): 

    special_chars = "[@_!#$%^&*()<>?/|}{~:]-"
    for char in input: 
        if char not in special_chars: 
            return False 
    return True

def extract_domain(email):

    if pd.isna(email) or "@" not in str(email):
        return ''
    return str(email).split("@")[-1].lower()

def lookup_df(df, category, value):
    
    if df is not None: 
        selected_values = set(df[category])
        if value in selected_values:
            return df[df[category] == value].iloc[0]
        return pd.DataFrame()
    return pd.DataFrame()
