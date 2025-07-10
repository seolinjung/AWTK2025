import re
import os
import pandas as pd

from helper import retrieve_json, normalize_domain

class Classification:

    def __init__(self, args, row):

        self.args = args

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

    def sales_invite(self):
        
        sales_invite_path = os.path.join("raw_db", "org_db", self.args.date, "sales_invite.csv")

        if os.path.exists(sales_invite_path):
            sales_invite_df = pd.read_csv(sales_invite_path)
            sales_invite_emails = set(sales_invite_df['Email'])
            if self.email in sales_invite_emails:
                return True
            return False
        return False

    # algorithm to reference ae bdr list in accordance with Korean name order
    def ref_ae_bdr(self):
        
        # make it into an array for deconstructing
        record_owner_arr = self.record_owner.split()

        alt_order = ""

        # "Hong Gil Dong" or "Gil Dong Hong"
        if len(record_owner_arr) == 3:
            alt_order = " ".join([self.record_owner[2], self.record_owner[0], self.record_owner[1]])

        # "Hong Gildong" or "Gildong Hong"
        if len(record_owner_arr) == 2:
            alt_order = " ".join([self.record_owner[1], self.record_owner[0]])

        # if the name matches ae bdr list 
        if record_owner_arr in self.ae_bdr or alt_order in self.ae_bdr: 
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
    
    def includes_special(self, input):

        rule = re.compile("[@_!#$%^&*()<>?/|}{~:]")

        return True if rule.search(input) else False
    
    # return the classification result 
    def classify(self):

        if self.sales_invite():
            return '유효', 'Sales Invite'
        
        # 필수? 
        if self.title == "학생": 
            return '비유효', '학교 소속'
    
        if self.match("title", "academia", "valid"):
            # 
            if self.record_owner == "Yoon Yeji":
                return '유효', ''

        if self.match("domain", "agency"):
            return '비유효', '에이전시'
        
        if self.match("title", "decision-maker", "valid") and not self.match("company", "misc"):
            return '유효', ''
        
        if self.match("company", "academia") and self.match("title", "academia"):
            return '비유효', '학교 소속'
        
        if self.match("title", "freelancer") and self.match("company", "freelancer"):
            return '비유효', '프리랜서'
        
        if self.match("title", "unemployed") and self.match("company", "unemployed"):
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
            return '유효', ''
        
        if any(char.isdigit() for char in self.name):
            return '홀딩', '불분명한 이름 및 회사명'
        
        if self.match("company", "unspecified", exact=True): 
            return '비유효', '불분명한 이름 및 회사명'
        
        if not self.domain: 
            return '비유효', '불분명한 e-mail'
        
        if self.match("title", "occupation"):
            return '홀딩', '직책'
        
        if self.match("normalized_domain", "free-email"): 
            if self.match("company", "suffix", "valid"):
                return '유효', ''
            if not self.includes_special(self.company):
                return '유효', ''
            return '홀딩', 'Free e-mail' 
                        
        return '유효', ''
    