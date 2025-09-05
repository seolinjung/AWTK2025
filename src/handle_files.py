import os 
import json 
import pandas as pd 

class HandleFiles:

    def __init__(self, *, args, **kwargs): 

        super().__init__(**kwargs)
        
        self.db_root_path = os.path.join("data", "raw_db", "org_db", args.date)
        self.seonhye_path = os.path.join("data", "raw_db", "seonhye", args.date)
        self.json_path = os.path.join("data", "exceptions")
        
        self.modified_main_path = os.path.join("data", "results", args.date)

        self.invalid_companies = self.retrieve_json("invalid-companies")
        self.invalid_titles = self.retrieve_json("invalid-titles")
        self.invalid_record_owners = self.retrieve_json("invalid-record-owners")
        self.invalid_emails = self.retrieve_json("invalid-emails")
        self.invalid_domains = self.retrieve_json("invalid-domains")

        self.valid_companies = self.retrieve_json("valid-companies")
        self.valid_titles = self.retrieve_json("valid-titles")

        self.special_domains = self.retrieve_json("special-domains")

        self.ae_bdr = self.retrieve_json("ae-bdr")
        self.sdr = self.retrieve_json("sdr-record-owners")

    def retrieve_json(self, input):

        name = input + ".json"
        path = os.path.join(self.json_path, name)

        if os.path.exists(path):
            with open(path, 'r') as file: 
                return json.load(file)[input]
            return False
        return False

    def retrieve_csv(self, input, seonhye=False):

        path = self.db_root_path if not seonhye else self.seonhye_path 
        file = os.path.join(path, (input + ".csv"))

        if os.path.exists(file):
            return file
        return False
    
    def upload_db(self, main_df):

        if not os.path.exists(self.modified_main_path):
            os.makedirs(self.modified_main_path, exist_ok=True)

        writer = pd.ExcelWriter(os.path.join(self.modified_main_path, "Sorted_DB.xlsx"))
        main_df.to_excel(writer)

        writer.close()   