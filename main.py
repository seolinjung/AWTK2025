import argparse
import pandas as pd
import openpyxl, xlsxwriter
import re
    

def main(args):

    main_df = pd.read_excel(f"{args.date}/Main.xlsx", engine="openpyxl")
    main_df_copy = main_df.copy()
    sdr_confirm_df = pd.read_excel("sdr_confirm_df.xlsx")

    '''
    1. organize xlsx into one folder 
    2. inefficient use of lists  
    3. change validation algorithm 
    4. clean up files according to OOP
    '''

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="0615")
    parser.add_argument("--file", type=str, default="Main")

    args = parser.parse_args()

    main(args)