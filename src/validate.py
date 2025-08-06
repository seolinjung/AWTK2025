import pandas as pd 

from handle_files import HandleFiles 
from row_operations import RowOperations
import helper as helper 

class Validate(RowOperations, HandleFiles):

    def __init__(self, *, args, row):

        super().__init__(args=args, row=row)

        self.row = row 

        self.seonhye_confirm_path = self.retrieve_csv("seonhye_confirm", seonhye=True)
        self.seonhye_confirm_df = pd.read_csv(self.seonhye_confirm_path) if self.seonhye_confirm_path else False 

        self.sales_invite_path = self.retrieve_csv("sales_invite")
        self.sales_invite_df = pd.read_csv(self.sales_invite_path) if self.sales_invite_path else False 

    # algorithm to reference ae bdr list in accordance with Korean name order
    def ref_ae_bdr(self):
        
        # make it into an array for deconstructing
        record_owner_arr = self.record_owner.split()

        alt_orders = [self.record_owner]

        # "Hong Gil Dong" or "Gil Dong Hong"
        if len(record_owner_arr) == 3:
            # intl -> korean or korean -> intl
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

        if value == "title":
            item = self.title 
            lookup = self.valid_titles[category] if valid == "valid" else self.invalid_titles[category]

        if value == "company":
            item = self.company 
            lookup = self.valid_companies[category] if valid == "valid" else self.invalid_companies[category]

        if value == "record_owner":
            item = self.record_owner
            lookup = self.invalid_record_owners

        if value == "email": 
            item = self.email
            lookup = self.invalid_emails

        if "domain" in value:
            item = self.domain if value == "domain" else self.normalized_domain
            lookup = self.invalid_domains[category]

        if not exact: 
            return any(k in item for k in lookup)
        
        return any(k == item for k in lookup)
    
    def filter_decision_makers(self): 

        if self.match("normalized_domain", "free-email", exact=True): 
            return '홀딩', 'decision maker: free e-mail'
        
        if self.match("company", "misc"): 
            return '홀딩', 'decision maker: misc company'
        
        if self.match("company", "freelancer") or self.match("company", "unemployed"): 
            return '비유효', 'decision maker: unemployed/freelancer'
        
        return '유효', 'decision maker'
    
    def filter_free_emails(self): 

        # email username is only consisted of digits or special characters 
        for item in [self.username, self.company]: 
            if item.isdigit() or helper.exclusive_special(item): 
                return '비유효', 'Invalid e-mail: company/username'

        if self.match("email", "unspecified"): 
            return '비유효', "Invalid e-mail: test" 

        # 일반, personal         
        if self.match("company", "unspecified"): 
            return '비유효', "Unspecified company"

        if self.match("record_owner", ""):
            return '비유효', 'Invalid Record Owner'

        if self.match("company", "suffix", "valid"): 
            return '유효', 'valid suffix'

        if not helper.includes_special(self.company):
            return '유효', 'no special chars'

        return '홀딩', 'Free e-mail'    

    def is_one_letter(self): 

        if len(self.title) == 1 or len(self.company) == 1: 
            return True         
    
    # return the classification result 
    def classify(self):
    
        if self.match("title", "academia", "valid") and self.ref_ae_bdr():
            return '유효', 'ae-bdr'

        if self.match("domain", "agency", exact=True):
            return '비유효', '에이전시'
        
        if self.match("title", "decision-maker", "valid"):
            return self.filter_decision_makers()
        
        if self.match("company", "academia") or self.match("title", "academia"):
            return '비유효', '학교 소속'
        
        if self.match("title", "freelancer") or self.match("company", "freelancer"):
            return '비유효', '프리랜서'
        
        if self.match("title", "unemployed") or self.match("company", "unemployed"):
            if self.match("title", "misc", "valid"):
                return '유효', '실무직'
            else:
                return '비유효', '무직' 
        
        # TODO: 기타 비유효 로직 포함해야 함 
        if self.match("title", "misc") or self.match("company", "misc") or self.company == "intern": 
            return '비유효', '기타 비유효'
        
        # exception in match logic: domain must match exactly 
        if self.match("normalized_domain", "competitor", exact=True) or self.match("company", "competitor"):
            return '비유효', '경쟁사'
        
        if any(char.isdigit() for char in self.name) or any(char.isdigit() for char in self.title) or self.is_one_letter():
            return '홀딩', '불분명한 이름, 직급 및 회사명'
        
        if self.match("title", "unspecified", exact=True) or self.match("company", "unspecified", exact=True): 
            return '비유효', '불분명한 이름, 직급 및 회사명'
        
        if not self.domain: 
            return '비유효', '불분명한 e-mail'
        
        if self.match("title", "occupation"):
            return '홀딩', '직책'
        
        if self.match("normalized_domain", "free-email", exact=True): 
            return self.filter_free_emails()

        return '유효', ''
    
    def overwrite_seonhye(self): 

        seonhye_row = helper.lookup_df(self.seonhye_confirm_df, 'Email', self.email)

        if not seonhye_row.empty:
            return seonhye_row["MKT Review(유효/비유효/홀딩)"], ''
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]

    def overwrite_sales(self):

        if not helper.lookup_df(self.sales_invite_df, 'Email', self.email).empty: 
            return '유효', 'Sales Invite' 
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]    