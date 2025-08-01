from handle_files import HandleFiles
import helper 
import pandas as pd 
import csv 
import os 

class NormalizeNametag(HandleFiles):

    def __init__(self, *, args, row): 

        super().__init__(args=args)

        self.email = str(row.get('email'))
        self.company_raw = str(row.get('company_raw'))
        self.account = str(row.get('account'))
        self.account_local = str(row.get('account_local'))
        self.company_cleansed = str(row.get('company_cleansed'))

        self.domain = helper.extract_domain(self.email)

        self.nametag_records = self.read_past_records()

        # issue - kr.kpmg.com -> kr, music.yamaha.com -> music
        self.company_email = helper.extract_domain(self.email).split(".")[0]
        self.normalized_account = self.normalize_account()

        self.special_companies = ["samsung", "lg", "hyundai"]

    def read_past_records(self): 
        
        nametag_records_path = os.path.join("data", "nametag_records.csv")

        if os.path.exists(nametag_records_path):
            with open(nametag_records_path, "r") as file: 
                nametag_records = list(csv.DictReader(file))
                return nametag_records

        print("Nametag records does not exist on file.")
        return {}
    
    def identify_records(self): 

        if self.domain in self.nametag_records: 
            return True
        return False 

    def normalize_account(self): 

        normalized_account = []
        conjoined_account = "".join(self.account.split()).lower()
        for char in conjoined_account: 
            if char.isalnum(): 
                normalized_account.append(char)
        return "".join(normalized_account)

    def company_from_email(self): 
        # kr.kpmg.com -> kpmg, music.yamaha.com -> yamaha, posco.com -> posco 

        return "Hello"

    def detect_special(self): 

        for company in self.special_companies: 
            if any(k == self.account for k in self.special_domains[company]): 
                return company
            
        return ''         

    def normalize(self): 

        '''
        with open("cleansed_accounts.txt", "a") as file: 
            file.write(self.normalize_account())
            file.write("\n")
        '''
             
        # if email and company are different, return email first 
        


        return self.company_cleansed