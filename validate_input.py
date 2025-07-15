import pandas as pd

from helper import retrieve_json, normalize_domain, retrieve_csv, includes_special

class ValidateInput:

    def __init__(self, args, row):

        self.args = args
        self.row = row 

        # define all the major column values 
        self.title = str(row['Title']).lower()
        self.company = str(row['Company (Custom)']).strip().lower()
        self.email = str(row['Email']).lower()
        self.domain = row['domain']
        self.first_name = str(row.get('First Name', '')).lower()
        self.last_name = str(row.get('Last Name', '')).lower()
        self.name = self.first_name + self.last_name
        self.record_owner = str(row['Related Record Owner']).strip()

        self.normalized_domain = normalize_domain(self.domain)

        self.invalid_companies = retrieve_json("invalid-companies")
        self.invalid_titles = retrieve_json("invalid-titles")
        self.invalid_domains = retrieve_json("invalid-domains")
        self.valid_companies = retrieve_json("valid-companies")
        self.valid_titles = retrieve_json("valid-titles")
        self.ae_bdr = retrieve_json("ae-bdr")

        self.seonhye_confirm_path = retrieve_csv(args, "seonhye_confirm", True)
        self.seonhye_confirm_df = pd.read_csv(self.seonhye_confirm_path) if self.seonhye_confirm_path else False 

        self.sales_invite_path = retrieve_csv(args, "sales_invite")
        self.sales_invite_df = pd.read_csv(self.sales_invite_path) if self.sales_invite_path else False 

    def lookup_email(self, df):
        
        if df is not None: 
            selected_emails = set(df['Email'])
            if self.email in selected_emails:
                return df[df['Email'] == self.email].iloc[0]
            return pd.DataFrame()
        return pd.DataFrame()

    # algorithm to reference ae bdr list in accordance with Korean name order
    def ref_ae_bdr(self):
        
        # make it into an array for deconstructing
        record_owner_arr = self.record_owner.split()

        alt_orders = [self.record_owner]

        # "Hong Gil Dong" or "Gil Dong Hong"
        if len(record_owner_arr) == 3:
            # intl -> korean 
            alt_orders.append(" ".join([record_owner_arr[2], record_owner_arr[0], record_owner_arr[1]]))
            # korean -> intl
            alt_orders.append(" ".join([record_owner_arr[1], record_owner_arr[2], record_owner_arr[0]]))

        # "Hong Gildong" or "Gildong Hong"
        if len(record_owner_arr) == 2:
            alt_orders.append(" ".join([record_owner_arr[1], record_owner_arr[0]]))

        # if the name matches ae bdr list 
        for order in alt_orders: 
            if order in self.ae_bdr:
                return True
        
        return False
    
    def match(self, value, category, valid="invalid", exact=False):

        lookup = [] 
        item = ""

        if not exact:

            if value == "title":
                item = self.title 
                lookup = self.valid_titles[category] if valid == "valid" else self.invalid_titles[category]

            if value == "company":
                item = self.company 
                lookup = self.valid_companies[category] if valid == "valid" else self.invalid_companies[category]

            if "domain" in value:
                item = self.domain if value == "domain" else self.normalized_domain
                lookup = self.invalid_domains[category]

            return any(k in item for k in lookup)
        
        return any(k == item for k in lookup)
    
    # return the classification result 
    def classify(self):
        
        # 필수? 
        if self.title == "학생": 
            return '비유효', '학교 소속'
    
        if self.match("title", "academia", "valid") and self.record_owner == "Yoon Yeji":
            return '유효', ''

        if self.match("domain", "agency"):
            return '비유효', '에이전시'
        
        if self.match("title", "decision-maker", "valid") and not self.match("company", "misc"):
            return '유효', ''
        
        if self.match("company", "academia") or self.match("title", "academia"):
            return '비유효', '학교 소속'
        
        if self.match("title", "freelancer") or self.match("company", "freelancer"):
            return '비유효', '프리랜서'
        
        if self.match("title", "unemployed") or self.match("company", "unemployed"):
            return '비유효', '무직'
        
        # TODO: 기타 비유효 로직 포함해야 함 
        if self.match("title", "misc") or self.match("company", "misc") or self.company == "intern": 
            return '비유효', '기타 비유효'
        
        if self.title == "personal" or self.company == "personal": 
            return '홀딩', '기타 비유효'
        
        # exception in match logic: domain must match exactly 
        if self.match("normalized_domain", "competitor", exact=True) or self.match("company", "competitor"):
            return '비유효', '경쟁사'
        
        if self.ref_ae_bdr():
            return '유효', 'ae-bdr'
        
        if any(char.isdigit() for char in self.name):
            return '홀딩', '불분명한 이름 및 회사명'
        
        if self.match("company", "unspecified", exact=True): 
            return '비유효', '불분명한 이름 및 회사명'
        
        if not self.domain: 
            return '비유효', '불분명한 e-mail'
        
        if self.match("title", "occupation"):
            return '홀딩', '직책'
        
        if self.match("normalized_domain", "free-email"): 
            #TODO: add "related record owner = ae-bdr" 
            #TODO: invalid-record-owners
            if self.match("company", "suffix", "valid"):
                return '유효', ''
            if not includes_special(self.company):
                return '유효', ''
            return '홀딩', 'Free e-mail' 
                        
        return '유효', ''
    
    def overwrite_seonhye(self): 

        seonhye_row = self.lookup_email(self.seonhye_confirm_df)

        if not seonhye_row.empty:
            return seonhye_row["MKT Review(유효/비유효/홀딩)"], ''
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]

    def overwrite_sales(self):

        if not self.lookup_email(self.sales_invite_df).empty: 
            return '유효', 'Sales Invite' 
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]