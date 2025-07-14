import argparse
import os

import pandas as pd

from helper import extract_domain, retrieve_csv

from validate_input import ValidateInput

def default_classify(row): 

    validation = ValidateInput(args, row)

    return validation.classify()
    
def seonhye_classify(row):

    validation = ValidateInput(args, row)

    return validation.overwrite_seonhye()

def sales_classify(row):
    
    validation = ValidateInput(args, row)
    return validation.overwrite_sales()

def upload_db(args, db):

    dest_path = os.path.join("raw_db", "org_db", args.date, "Integrated_DB.xlsx")

    writer = pd.ExcelWriter(dest_path)
    db.to_excel(writer)

    writer.close()    

def main(args):

    sdr_confirm_path = retrieve_csv(args, "sdr_confirm")
    confirm_mail_path = retrieve_csv(args, "confirm_mail")

    # read main file 
    main_df = pd.read_csv(retrieve_csv(args, "main"), usecols=["First Name", "Last Name", "Email", "Company (Custom)", "Title", "Related Record Owner"])
    # and make a copy of main
    main_df_copy = main_df.copy()

    if sdr_confirm_path: # if exists
        sdr_confirm_df = pd.read_csv(sdr_confirm_path)
        # merge based on commonality of emails 
        main_df_copy = main_df_copy.merge(sdr_confirm_df, on="Email", how="left")

        sdr_confirm_emails = set(sdr_confirm_df['Email'])

        # for each row, does the email column value exist in the email list? 
        main_df_copy["SDR 컨펌 여부"] = main_df_copy.apply(
            lambda row: '예' if row["Email"] in sdr_confirm_emails else '', axis=1)

    if confirm_mail_path: 
        confirm_mail_df = pd.read_csv(confirm_mail_path)
        main_df_copy = main_df_copy.merge(confirm_mail_df, on="Email", how="left")

    # keep last updated version of email, drop rest 
    main_df_copy = main_df_copy.drop_duplicates(subset="Email", keep="last")

    # apply extracted domain and add to created column 
    main_df_copy["domain"] = main_df_copy["Email"].apply(extract_domain)

    # add unique column 
    email_count = main_df_copy["Email"].value_counts()
    main_df_copy["unique"] = main_df_copy["Email"].map(email_count)

    main_df_copy[['MKT Review(유효/비유효/홀딩)', 'MKT Review(사유)']] = main_df_copy.apply(default_classify, axis=1, result_type='expand')
    main_df_copy[['MKT Review(유효/비유효/홀딩)', 'MKT Review(사유)']] = main_df_copy.apply(seonhye_classify, axis=1, result_type='expand')
    main_df_copy[['MKT Review(유효/비유효/홀딩)', 'MKT Review(사유)']] = main_df_copy.apply(sales_classify, axis=1, result_type='expand')

    # 파일 review - get value of MKT 

    main_df_copy.reset_index(inplace=True, drop=True)
    
    # upload db to excel file 
    upload_db(args, main_df_copy)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="0615")

    args = parser.parse_args()

    main(args)