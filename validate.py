import re 
import json 
import os

from helper import retrieve_json, normalize_domain

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
        self.normalized_domain = normalize_domain(self.domain)

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
    
    def match(self, type, value, category, valid="invalid"):

        lookup = [] 

        if value == self.title:
            if valid == "valid":
                lookup = self.valid_titles[category]
            lookup = self.invalid_titles[category]

        if value == self.company:
            lookup = self.invalid_companies[category]

        if value == self.domain or value == self.normalized_domain:
            lookup = self.invalid_domains[category]

        return any(k in value for k in lookup)

    # return the classification result 
    def classify(self):

        # 필수? 
        if self.title == "학생": 
            return '비유효', '학교 소속'

        if self.match(self.domain, "agency"):
            return '비유효', '에이전시'
        
        if self.match(self.title, "decision-maker", "valid") and not self.match(self.company, "misc"):
            return '유효', ''
        
        if self.match(self.company, "academia") and self.match(self.title, "academia"):
            return '비유효', '학교 소속'
        
        if self.match(self.title, "freelancer") and self.match(self.company, "freelancer"):
            return '비유효', '프리랜서'
        
        if self.match(self.title, "unemployed") and self.match(self.company, "unemployed"):
            return '비유효', '무직'
        
        # TODO: 기타 비유효 로직 포함해야 함 
        if self.match(self.title, "misc") or self.match(self.company, "misc") or self.company == "intern": 
            return '비유효', '기타 비유효'
        
        if self.title == "personal" or self.company == "personal": 
            return '홀딩', '기타 비유효'
        
        # exception in match logic: domain must match exactly 
        if self.normalized_domain in self.invalid_domains["competitor"] or self.match(self.company, "competitor"):
            return '비유효', '경쟁사'
        
        # valid - record owner in AE & BDR 
        if self.ref_ae_bdr():
            return '유효', ''
        
        if self.match(self.company, "unspecified"): 
            return '비유효', '불분명한 이름 및 회사명'
        
        if any(char.isdigit() for char in self.name):
            return '홀딩', '불분명한 이름 및 회사명'
        
        if not self.domain: 
            return '비유효', '불분명한 e-mail'
        
        if self.match(self.title, "occupation"):
            return '홀딩', '직책'
        
        if self.match(self.normalized_domain, "free-email"): 
            if self.company.isalnum() and self.title.isalnum():
                return '유효', ''
            return '홀딩', 'Free email' 
        
        # valid - title is 교수, 연구원 && record owner is Yeji Yoon 
        if self.match(self.title, "academia", "valid"):
            if self.record_owner == "Yoon Yeji":
                return '유효', ''
                        
        return '유효', ''
    