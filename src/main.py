import argparse

import helper as helper

from initialize import Initialize
from validate import Validate
from normalize_nametag import NormalizeNametag
from handle_files import HandleFiles 

def apply_validation(row, mode="default"): 

    validate_logic = Validate(args=args, row=row) 

    if mode=="seonhye":
        return validate_logic.overwrite_seonhye()
    
    if mode=="sales":
        return validate_logic.overwrite_sales()

    return validate_logic.classify()

def apply_normalization(row):
    
    normalize_nametag = NormalizeNametag(row=row)

    return normalize_nametag.execute()
    
def main(args):

    handle_files = HandleFiles(args=args)

    '''
    Initialization is run by default in main to prevent any mismatches in code. 
    '''
    
    initialize_logic = Initialize(args=args)
    main_df = initialize_logic.execute()

    if args.validate:  
        steps = ["default"]

        if handle_files.retrieve_csv("seonhye_confirm", True):
            steps.append("seonhye")

        if handle_files.retrieve_csv("sales_invite"):
            steps.append("sales")

        for step in steps: 
            main_df[['MKT Review(유효/비유효/홀딩)', 'MKT Review(사유)']] = main_df.apply(
                lambda row: apply_validation(row, step), axis=1, result_type='expand')
    
        main_df.reset_index(inplace=True, drop=True)

    if args.normalize: 
        print("Normalize operation not implemented yet. Terminating.")
    
    # upload db to excel file 
    handle_files.upload_db(main_df)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str)
    parser.add_argument("--validate", type=bool, default=False)
    parser.add_argument("--normalize", type=bool, default=False)
    parser.add_argument("--check-db", type=bool, default=False)

    args = parser.parse_args()

    main(args)