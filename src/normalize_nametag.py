from handle_files import HandleFiles
from row_operations import RowOperations
import pandas as pd 

class NormalizeNametag(RowOperations, HandleFiles):

    def __init__(self, *, args, row, main_df): 

        super().__init__(args=args, row=row)

        self.nametag_path = self.retrieve_csv("nametag")
        self.main_df = main_df

        # nametag 
        self.email = row['email']
        self.company_raw = row['company_raw']
        self.account = row['account']
        self.account_local = str(row.get('account_local', '')).strip()
        self.company_cleansed = str(row['company_cleansed']).strip()

        self.normalized_domain = self.normalize_domain()
        self.username = self.extract_username() 

    def extract_cleansed_nametags(self): 

        if not self.nametag_path: 
            print("A nametag.csv file has not been provided.")
            return 

        nametag_df = pd.read_csv(
            self.nametag_path,
            usecols=["이메일", "회사명 (미정제 Raw DB 맵핑)", "Account Name", "Account Name (Local)", "회사명 (네임택용 정제 버전)"],
            index_col=False)
        
        nametag_df.columns = ['email', 'company_raw', 'account', 'account_local', 'company_cleansed']

        return nametag_df

    def execute(self): 

        nametag_df = self.extract_cleansed_nametags()
        email, company_raw, account, account_local, company = nametag_df['email'], 
        

        