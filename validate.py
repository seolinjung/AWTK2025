import re 
import json 
import os

# from helper import reverse_dict

class Classification:

    def __init__(self, row):

        # define all the major column values 
        self.title = str(row['Title']).lower()
        self.company = str(row['Company (Custom)']).strip().lower()
        self.email = str(row['Email']).lower()
        self.domain = row['domain']
        self.first_name = str(row.get('First Name', '')).lower()
        self.last_name = str(row.get('Last Name', '')).lower()
        self.name = self.first_name + self.last_name
        self.record_owner = str(row['Related Record Owner']).strip()

        # normalized domain
        self.normalized_domain = self.normalize_domain()

        # path to json folder 
        self.json_path = os.path.join('data', 'exceptions')

        # list of the json arrays, retrieved
        self.invalid_companies = self.retrieve_json("invalid-companies")
        self.invalid_titles = self.retrieve_json("invalid-titles")
        self.invalid_domains = self.retrieve_json("invalid-domains")
        self.valid_titles = self.retrieve_json("valid-titles")
        self.ae_bdr = self.retrieve_json("ae-bdr")

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
    
    # retrive an array format of the request json file
    def retrieve_json(self, input):

        # actual json file name
        name = input + ".json"
        # get path name
        path = os.path.join(self.json_path, name)

        # get the array
        with open(path, 'r') as file: 
            return json.load(file)[input]
    
    # normalize domain 
    def normalize_domain(self):

        # get the value before the period. 'samsung.com' should return 'samsung'
        domain_arr = self.domain.split('.')
        return domain_arr[0]
    
    def match(self, value, category, valid="valid"):

        lookup = [] 

        if value == "title":
            if valid == "valid":
                lookup = self.valid_titles[category]
            lookup = self.invalid_titles[category]

        if value == "company":
            lookup = self.invalid_companies[category]

        if value == "domain":
            lookup = self.invalid_domains[category]

        return any(k in value for k in lookup)

    # return the classification result 
    def classify(self):

        # 필수? 
        if self.title == "학생": 
            return '비유효', '학교 소속'

        if self.match(self.domain, "agency"):
            return '비유효', '에이전시'
        
        # valid - title is one of these && company is NOT in invalid-keywords: '기타 비유효'
        if self.match(self.title, "decision_maker", "valid") and not self.match(self.company, "misc"):
            return '유효', ''
        
        if self.match(self.company, "academia") and self.match(self.title, "academia"):
            return '비유효', '학교 소속'
        
        if self.match(self.title, "freelancer") and self.match(self.company, "freelancer"):
            return '비유효', '프리랜서'
        
        if self.match(self.title, "unemployed") and self.match(self.company, "unemployed"):
            return '비유효', '무직'
        
        # TODO: 기타 비유효 로직 포함해야 함 


        for key in self.invalid_titles["misc"]: 
            if self.title == key: 
                return '비유효', '기타 비유효'
        
        for key in self.invalid_companies["misc"]:
            if self.company == key:
                return '비유효', '기타 비유효'
            
        if self.title == 'personal' or self.company == 'personal':
            return '홀딩', '기타 비유효'
        
        if self.normalized_domain in self.invalid_domains["competitor"] or self.company in self.invalid_companies["competitor"]:
            return '비유효', '경쟁사'

        if self.company == 'company' or self.company == 'startup':
            return '비유효', '불분명한 이름 및 회사명'
        
        for char in list(self.name):
            if char.isdigit(): 
                return '홀딩', '불분명한 이름 및 회사명'

        # valid - record owner in AE & BDR 
        if self.ref_ae_bdr():
            return '유효', ''
        
        if self.normalized_domain in self.invalid_domains["free-email"]:
            if self.company.isalnum() and self.title.isalnum():
                return '유효', ''
            return '홀딩', 'Free email' 
        
        # valid - title is 교수, 연구원 && record owner is Yeji Yoon 
        for key in self.valid_titles["academia"]:
            if key in self.title and self.record_owner == "Yoon Yeji":
                return '유효', ''
                        
        return '유효', ''
    