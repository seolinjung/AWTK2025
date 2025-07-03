import argparse
import pandas as pd
import openpyxl, xlsxwriter
import re
import os

from manipulate_db import match_db, merge_db, cleanse_duplicate_emails
from helper import extract_domain

from validate import Classification

def apply_classification(row): 

    classification = Classification(row)
    return classification.classify()
    
def main(args):

    # define path to db root
    db_root_path = os.path.join("raw_db", "org_db", args.date)
    # to main and sdr confirm, confirm mail 
    main_path = os.path.join(db_root_path, "main.csv")
    sdr_confirm_path = os.path.join(db_root_path, "sdr_confirm.xlsx")
    confirm_mail_path = os.path.join(db_root_path, "confirm_mail.xlsx")

    # read main file 
    main_df = pd.read_csv(main_path, usecols=["First Name", "Last Name", "Email", "Company (Custom)", "Title", "Related Record Owner"])
    # and make a copy of main
    main_df_copy = main_df.copy()

    # temporary - sdr confirm to csv
    sdr_confirm_df = pd.read_excel(sdr_confirm_path).to_csv("sdr_confirm.csv", index=None, header=True)
    # merge with sdr confirm 
    main_df = merge_db(main_df_copy, sdr_confirm_df, "Email")

    # temporary - confirm mail to csv
    confirm_mail_df = pd.read_excel(confirm_mail_path).to_csv("confirm_mail.csv", index=None, header=True)
    # merge with confirm mail 
    main_copy_df = merge_db(main_copy_df, confirm_mail_df, "Email")

    # cleanse duplicate emails 
    main_copy_df = cleanse_duplicate_emails(main_copy_df)

    # extract domain and apply to copy of main
    main_copy_df["domain"] = main_copy_df["Email"].apply(extract_domain)

    # create unique column
    email_count = main_copy_df["Email"].value_counts()
    main_copy_df["unique"] = main_copy_df["Email"].map(email_count)

    # apply classification
    main_copy_df[['MKT Review(유효/비유효/홀딩)', 'MKT Review(사유)']] = main_copy_df.apply(apply_classification, axis=1, result_type='expand')

    print(main_copy_df.head())

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="0615")

    args = parser.parse_args()

    main(args)