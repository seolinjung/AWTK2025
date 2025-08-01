from handle_files import HandleFiles 
import pandas as pd 
import helper as helper 
import csv 
import os 

class Initialize(HandleFiles):

    def __init__(self, *, args): 

        super().__init__(args=args)

        self.main_path = self.retrieve_csv("main")
        self.sdr_confirm_path = self.retrieve_csv("sdr_confirm")
        self.confirm_mail_path = self.retrieve_csv("confirm_mail")
        self.nametag_path = os.path.join("data", "nametag.csv")

    def create_nametag_records(self, nametag_df): 

        nametag_records_path = os.path.join("data", "nametag_records.csv")

        nametag_records = []

        if not self.nametag_path: 
            print("We could not find matching records for a nametag database. Terminating.")
            return 
        
        nametag_emails = list(nametag_df['email'])
        nametag_cleansed = list(nametag_df['company_cleansed'])

        unique_domains = []

        record_length = len(nametag_emails)

        for i in range(record_length):
            temporary_dict = {}
            domain = helper.extract_domain(nametag_emails[i])
            if domain in unique_domains: 
                continue
            unique_domains.append(domain)
            temporary_dict['domain'] = domain
            temporary_dict['company_cleansed'] = nametag_cleansed[i]
            nametag_records.append(temporary_dict)

        print("Success: Nametag records stored as list.\nTotal length of unique records:", len(nametag_records))

        with open(nametag_records_path, mode='w', newline='') as file: 
            fieldnames = ['domain', 'company_cleansed']
            writer = csv.DictWriter(file, fieldnames)
            writer.writeheader()
            writer.writerows(nametag_records)

        print("Success: Nametag records uploaded to file.")

        return nametag_records

    def prepare_nametag(self): 
        
        nametag_df = pd.read_csv(
            self.nametag_path,
            usecols=["이메일", "회사명 (미정제 Raw DB 맵핑)", "Account Name", "Account Name (Local)", "회사명 (네임택용 정제 버전)"],
            index_col=False)
        
        nametag_df.columns = ['email', 'company_raw', 'account', 'account_local', 'company_cleansed']

        nametag_df['company_normalized'] = ""

        return nametag_df

    def prepare_main(self):

        main_df = pd.read_csv(
            self.main_path,
            usecols=["First Name", "Last Name", "Email", "Company (Custom)", "Title", "Related Record Owner"],
            index_col=False)
    
        # and make a copy of main
        main_df_copy = main_df.copy()

        if self.sdr_confirm_path: 
            sdr_confirm_df = pd.read_csv(self.sdr_confirm_path)
            # merge based on commonality of emails 
            main_df_copy = main_df_copy.merge(sdr_confirm_df, on="Email", how="left")
            sdr_confirm_emails = set(sdr_confirm_df['Email'])
            
            # for each row, does the email column value exist in the email list? 
            main_df_copy["SDR 컨펌 여부"] = main_df_copy.apply(
                lambda row: '예' if row["Email"] in sdr_confirm_emails else '', axis=1)

        if self.confirm_mail_path: 
            confirm_mail_df = pd.read_csv(self.confirm_mail_path)
            main_df_copy = main_df_copy.merge(confirm_mail_df, on="Email", how="left")

        # keep last updated version of email, drop rest 
        main_df_copy = main_df_copy.drop_duplicates(subset="Email", keep="last")

        # apply extracted domain and add to created column 
        main_df_copy["domain"] = main_df_copy["Email"].apply(helper.extract_domain)

        # add unique column 
        email_count = main_df_copy["Email"].value_counts()
        main_df_copy["unique"] = main_df_copy["Email"].map(email_count)

        return main_df_copy 
