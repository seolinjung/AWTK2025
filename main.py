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
    sdr_confirm_path = os.path.join(db_root_path, "sdr_confirm.csv")
    confirm_mail_path = os.path.join(db_root_path, "confirm_mail.csv")

    # read main file 
    main_df = pd.read_csv(main_path, usecols=["First Name", "Last Name", "Email", "Company (Custom)", "Title", "Related Record Owner"])
    # and make a copy of main
    main_df_copy = main_df.copy()

    # temporary - sdr confirm to csv
    # sdr_confirm_xlsx = pd.read_excel(sdr_confirm_path)
    # sdr_confirm_xlsx.to_csv("sdr_confirm.csv", index=None, header=True)
    sdr_confirm_df = pd.read_csv(sdr_confirm_path)

    # merge with sdr confirm 
    main_df = merge_db(main_df_copy, sdr_confirm_df, "Email")

    # temporary - confirm mail to csv
    # confirm_mail_xlsx = pd.read_excel(confirm_mail_path)
    # confirm_mail_xlsx.to_csv("confirm_mail.csv", index=None, header=True)
    confirm_mail_df = pd.read_csv(confirm_mail_path)

    # merge with confirm mail 
    main_df_copy = merge_db(main_df_copy, confirm_mail_df, "Email")

    # cleanse duplicate emails 
    main_df_copy = cleanse_duplicate_emails(main_df_copy)

    # extract domain and apply to copy of main
    main_df_copy["domain"] = main_df_copy["Email"].apply(extract_domain)

    # create unique column
    email_count = main_df_copy["Email"].value_counts()
    main_df_copy["unique"] = main_df_copy["Email"].map(email_count)

    # apply classification
    main_df_copy[['MKT Review(유효/비유효/홀딩)', 'MKT Review(사유)']] = main_df_copy.apply(apply_classification, axis=1, result_type='expand')

    print(main_df_copy.head())

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="0615")

    args = parser.parse_args()

    main(args)