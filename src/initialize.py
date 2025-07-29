from handle_files import HandleFiles 
import pandas as pd 
import helper as helper 

class Initialize(HandleFiles):

    def __init__(self, *, args): 

        super().__init__(args=args)

        self.main_path = self.retrieve_csv("main")
        self.sdr_confirm_path = self.retrieve_csv("sdr_confirm")
        self.confirm_mail_path = self.retrieve_csv("confirm_mail")

    def execute(self):

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
