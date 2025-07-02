import argparse
import pandas as pd
import openpyxl, xlsxwriter
import re
import os

from manipulate_db import match_db, merge_db
from validate import validate 
    
def main(args):

    # define path to db 
    main_db_path = os.path.join("raw_db", "org_db", args.date, "main.csv")
    
    # read main file 
    main_df = pd.read_csv(main_db_path, usecols=["First Name", "Last Name", "Email", "Company (Custom)", "Title", "Related Record Owner"])

    
    # validate
    print(main_df)
    


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="0615")

    args = parser.parse_args()

    main(args)