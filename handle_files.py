import os 
import json 

class HandleFiles:

    def __init__(self, args): 

        self.db_root_path = os.path.join("data", "raw_db", "org_db", args.date)
        self.seonhye_path = os.path.join("data", "raw_db", "seonhye")
        self.json_path = os.path.join("data", "exceptions")

        self.invalid_companies = self.retrieve_json("invalid-companies")
        self.invalid_titles = self.retrieve_json("invalid-titles")
        self.invalid_record_owners = self.retrieve_json("invalid-record-owners")
        self.invalid_emails = self.retrieve_json("invalid-emails")
        self.invalid_domains = self.retrieve_json("invalid-domains")
        self.valid_companies = self.retrieve_json("valid-companies")
        self.valid_titles = self.retrieve_json("valid-titles")
        self.ae_bdr = self.retrieve_json("ae-bdr")

    def retrieve_json(self, input):

        name = input + ".json"
        path = os.path.join(self.json_path, name)

        if os.path.exists(path):
            with open(path, 'r') as file: 
                return json.load(file)[input]
            return False
        return False

    def retrieve_csv(self, input, seonhye=False):

        root_path = self.seonhye_path if seonhye else self.db_root_path
        final_path = os.path.join(root_path, input + ".csv")

        if os.path.exists(final_path):
            return final_path
        
        return False