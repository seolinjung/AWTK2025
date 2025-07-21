import pandas as pd
import helper
from validate_email import ValidateEmail

class Validate:

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

        self.invalid_companies = helper.retrieve_json("invalid-companies")
        self.invalid_titles = helper.retrieve_json("invalid-titles")
        self.invalid_record_owners = helper.retrieve_json("invalid-record-owners")
        self.invalid_domains = helper.retrieve_json("invalid-domains")
        self.valid_companies = helper.retrieve_json("valid-companies")
        self.valid_titles = helper.retrieve_json("valid-titles")
        self.ae_bdr = helper.retrieve_json("ae-bdr")

        self.email_logic = ValidateEmail(row)

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

            if value == "record_owner":
                item = self.record_owner
                lookup = self.invalid_record_owners

            if "domain" in value:
                item = self.domain if value == "domain" else self.email_logic.normalized_domain
                lookup = self.invalid_domains[category]

            return any(k in item for k in lookup)
        
        return any(k == item for k in lookup)
    
    def filter_decision_maker(self): 

        if self.email_logic.is_free(self.email): 
            return '홀딩', 'decision maker: free e-mail'
        
        if self.match("company", "misc"): 
            return '홀딩', 'decision maker: misc company'
        
        return '유효', 'deciison maker'
    
    # return the classification result 
    def classify(self):

        # 필수? 
        if self.title == "학생": 
            return '비유효', '학교 소속'
    
        if self.match("title", "academia", "valid") and self.record_owner == "Yoon Yeji":
            return '유효', 'academia'

        if self.match("domain", "agency"):
            return '비유효', '에이전시'
        
        self.filter_decision_maker()
        
        if self.match("company", "academia") or self.match("title", "academia"):
            return '비유효', '학교 소속'
        
        if self.match("title", "freelancer") or self.match("company", "freelancer"):
            return '비유효', '프리랜서'
        
        if self.match("title", "unemployed") or self.match("company", "unemployed"):
            return '비유효', '무직'
        
        # TODO: 기타 비유효 로직 포함해야 함 
        if self.match("title", "misc") or self.match("company", "misc") or self.company == "intern": 
            return '비유효', '기타 비유효'
        
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
        
        self.email_logic.filter_free_email()
                        
        return '유효', ''
    