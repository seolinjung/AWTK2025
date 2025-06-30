import argparse
import pandas as pd
import openpyxl, xlsxwriter
import re
import os

def match_db(main, sub, column):

    # check if sub matches main based on column value
    sub_vals = set(sub[column])
    main_vals = set(main[column])

    # calculate remaining
    unmatched = sub_vals - main_vals

    # if there are any that don't match main 
    if unmatched:
        print(f"List of emails that exist on {sub} but not {main}:")
        for val in unmatched: 
            print(f"- {val}")
        return False
    else:
        # all emails match, no further step needed
        print(f"All emails exist on both {main} and {sub}.")
        return True
    
def merge_db(main, sub, column):

    # now merge with sub
    main = main.merge(sub, on=column, how="left")

    return main 

def cleanse_duplicate_emails(db):

    '''
    scan file and search for duplicates. 
    currently, the logic is simple, but it is up for modification.
    '''

    return db.drop_duplicates(subset="Email", keep="last")

def extract_domain(email):
    if pd.isna(email) or "@" not in str(email):
        return ''
    return str(email).split("@")[-1].lower()
    
def main(args):

    # define path to db 
    org_db_path = os.path.join("raw_db", "org_db")

    # read main and sdr_confirm files 
    main_df = pd.read_excel(os.path.join(org_db_path, "main.xlsx"), engine="openpyxl")
    sdr_confirm_df = pd.read_excel(os.path.join(org_db_path, "sdr_confirm.xlsx"))

    # make copy of main 
    main_copy_df = main_df.copy()
    # merge with sdr confirm 
    main_copy_df = merge_db(main_copy_df, sdr_confirm_df, "Email")
    # match with sdr confirm
    sdr_equal = match_db(main_copy_df, sdr_confirm_df, "Email")

    # read confirm main file
    confirm_mail_df = pd.read_excel(os.path.join(org_db_path, "confirm_mail.xlsx"))
    main_copy_df = merge_db(main_copy_df, confirm_mail_df, "Email")

    # cleanse duplicate emails 
    main_copy_df = cleanse_duplicate_emails(main_copy_df)

    # match with confirm mail 
    confirm_equal = match_db(main_copy_df, confirm_mail_df, "Email")

    # extract domain and apply to copy of main
    main_copy_df["domain"] = main_copy_df["Email"].apply(extract_domain)

    # create unique column
    email_count = main_copy_df["Email"].value_counts()
    main_copy_df["unique"] = main_copy_df["Email"].map(email_count)

    




    
    





















    '''
    1. organize xlsx into one folder 
    2. inefficient use of lists  
    3. change validation algorithm 
    4. clean up files according to OOP

    file names:
    main - main.xlsx
    sdr_confirm - sdr_confirm.xlsx
    seonhye_confirm.xlsx
    ancillary/drive
    
    '''

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # parser.add_argument("--parser")
    


    # parser.add_argument("--date", type=str, default="0615")
    # parser.add_argument("--file", type=str, default="Main")

    args = parser.parse_args()

    main(args)