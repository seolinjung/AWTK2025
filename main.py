import argparse
import os

import pandas as pd

from manipulate_db import merge_db, cleanse_duplicate_emails
from helper import extract_domain, retrieve_csv

from validate import Classification

def apply_classification(row): 

    classification = Classification(args, row)
    return classification.classify()

def upload_db(args, db):

    dest_path = os.path.join("raw_db", "org_db", args.date, "Integrated_DB.xlsx")

    writer = pd.ExcelWriter(dest_path)
    db.to_excel(writer)

    writer.close()

def main(args):

    # read main file 
    main_df = pd.read_csv(retrieve_csv(args, "main"), usecols=["First Name", "Last Name", "Email", "Company (Custom)", "Title", "Related Record Owner"])
    # and make a copy of main
    main_df_copy = main_df.copy()

    sdr_confirm_df = pd.read_csv(retrieve_csv(args, "sdr_confirm"))
    main_df_copy = merge_db(main_df_copy, sdr_confirm_df, "Email")

    sdr_confirm_emails = set(sdr_confirm_df['Email'])

    main_df_copy["SDR 컨펌 여부"] = main_df_copy.apply(
        lambda row: '예' if row["Email"] in sdr_confirm_emails else '', axis=1)

    confirm_mail_df = pd.read_csv(retrieve_csv(args, "confirm_mail"))
    main_df_copy = merge_db(main_df_copy, confirm_mail_df, "Email")

    # TODO: 로직 다시 생각 
    main_df_copy = cleanse_duplicate_emails(main_df_copy)

    # extract domain and apply to copy of main
    main_df_copy["domain"] = main_df_copy["Email"].apply(extract_domain)

    # TODO: depends on how we handle cleansing duplicate emails from top 
    email_count = main_df_copy["Email"].value_counts()
    main_df_copy["unique"] = main_df_copy["Email"].map(email_count)

    # apply classification
    main_df_copy[['MKT Review(유효/비유효/홀딩)', 'MKT Review(사유)']] = main_df_copy.apply(apply_classification, axis=1, result_type='expand')

    # 선혜님 덮어씌우는 단계 
    seonhye_confirm_df = pd.read_csv(retrieve_csv(args, "seonhye_confirm", True))

    main_df_copy.set_index('Email', inplace=True)
    seonhye_confirm_df.set_index('Email', inplace=True)

    main_df_copy.update(seonhye_confirm_df[['MKT Review(유효/비유효/홀딩)']])
    main_df_copy.reset_index(inplace=True)

    upload_db(args, main_df_copy)

    # 4-c logic - sales
    print(main_df_copy.head())

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="0615")

    args = parser.parse_args()

    main(args)