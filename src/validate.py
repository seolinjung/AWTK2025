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

        # if the name matches ae bdr or sdr list 
        for order in alt_orders: 
            if order in self.ae_bdr or self.sdr:
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

        # email username is only consisted of digits or special characters 
        for item in [self.title, self.company]: 
            if item.isdigit() or helper.exclusive_special(item): 
                return '비유효', 'decision maker: 숫자 혹은 특수문자' 

        if self.match("company", "freelancer") or self.match("company", "unemployed"): 
            return '비유효', 'decision maker: unemployed/freelancer'
        
        if self.match("company", "unspecified"): 
            return '비유효', 'decision maker: unspecified company'
        
        if self.match("company", "academia"): 
            return '비유효', 'decision maker: academia'

        if self.match("company", "misc") or self.match("title", "misc"): 
            return '비유효', 'decision maker: misc company'

        if self.match("normalized_domain", "free-email", exact=True): 
            return '홀딩', 'decision maker: free e-mail'
        
        return '유효', 'decision maker'
    
    def filter_free_emails(self): 

        # title/company is only consisted of digits or special characters 
        for item in [self.title, self.company]: 
            if item.isdigit() or helper.exclusive_special(item): 
                return '비유효', 'Free email: invalid title/company'
            
        if self.match("title", "unspecified", exact=True) or self.match("company", "unspecified", exact=True): 
            return '비유효', 'Free email: 불분명한 이름, 직급 및 회사명'

        if self.match("email", "unspecified"): 
            return '비유효', "Invalid e-mail: test" 

        # 일반, personal
        if self.match("company", "unspecified") or self.company == 'company': 
            return '비유효', "Unspecified company"

        if self.match("company", "suffix", "valid"): 
            return '유효', 'Free email: valid suffix'

        if self.match("record_owner", ""):
            return '비유효', 'Free email: Invalid Record Owner'

        if not helper.includes_special(self.company):
            return '유효', 'Free email: no special chars'

        return '홀딩', 'Free e-mail'    

    def is_one_letter(self, input): 

        '''
        if item is one letter, but if it's a special character, it shouldn't return True 
        '''

        if len(input) == 1: 
            if helper.exclusive_special(input): 
                return False
            return True
        return False          
    
    # return the classification result 
    def classify(self):
    
        if self.match("title", "academia", "valid") and self.ref_ae_bdr():
            return '유효', '학교 소속 유효 직급'

        if self.match("normalized_domain", "agency"):
            return '비유효', '에이전시'
        
        if self.match("title", "decision-maker", "valid"):
            return self.filter_decision_makers()
        
        if self.match("company", "academia") or self.match("title", "academia"):
            return '비유효', '학교 소속'
        
        if self.match("title", "freelancer") or self.match("company", "freelancer"):
            return '비유효', '프리랜서'
        
        if self.match("title", "unemployed") or self.match("company", "unemployed"):
            if self.match("company", "suffix", "valid"):
                return '유효', ''
            if self.match("title", "misc", "valid"):
                return '유효', ''
            else:
                return '비유효', '무직' 

        if self.match("title", "misc") or self.match("company", "misc") or self.title == "intern": 
            if self.company == "owner": 
                if self.match("title", "misc", "valid"): 
                    return '유효', ''
            return '비유효', '기타 비유효'
        
        # exception in match logic: domain must match exactly 
        if self.match("normalized_domain", "competitor", exact=True) or self.match("company", "competitor"):
            return '비유효', '경쟁사'
        
        if any(char.isdigit() for char in self.name) or any(char.isdigit() for char in self.title) or self.is_one_letter(self.title) or self.is_one_letter(self.company):
            return '홀딩', '불분명한 이름, 직급 및 회사명'
        
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
            return seonhye_row["MKT Review(유효/비유효/홀딩)"], 'Seonhye Review'
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]

    def overwrite_sales(self):

        if not helper.lookup_df(self.sales_invite_df, 'Email', self.email).empty: 
            return '유효', 'Sales Invite' 
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]    