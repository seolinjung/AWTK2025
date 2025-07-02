import re 
import json 
import os

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

        # path to json folder 
        self.json_path = os.path.join('data', 'exceptions')

        # list of the json arrays, retrieved
        self.invalid_keywords = self.retrieve_json("invalid-keywords")
        self.invalid_domains = self.retrieve_json("invalid_domains")
        self.competitors = self.retrieve_json("competitors")

    # algorithm to reference ae bdr list in accordance with Korean name order
    def ref_ae_bdr(self):

        # define path to ae bdr 
        ae_bdr_path = os.path.join(self.json_path, 'ae-bdr.json')

        # get the json file array
        with open(ae_bdr_path, 'r') as file:
            ae_bdr = json.load(file)['ae-bdr']
        
        # make it into an array for deconstructing
        record_owner_arr = self.record_owner.split()

        # "Hong Gil Dong" or "Gil Dong Hong"
        if len(record_owner_arr) == 3:
            alt_order = " ".join([self.record_owner[2], self.record_owner[0], self.record_owner[1]])

        # "Hong Gildong" or "Gildong Hong"
        if len(record_owner_arr) == 2:
            alt_order = " ".join(self.record_owner[1], self.record_owner[0])

        # if the name matches ae bdr list 
        if record_owner_arr in ae_bdr or alt_order in ae_bdr: 
            return True
        
        return False
    
    # retrive an array format of the request json file
    def retrieve_json(self, input):

        name = input + ".json"
        path = os.path.join(self.json_path, input)

        # get the array
        with open(path, 'r') as file: 
            return json.load(name)[input]
    
    # normalize domain 
    def normalize_domain(self):

        domain_arr = self.domain.split('.')
        return domain_arr[0]
    
    # normalize email 
    def normalize_email(self):

        email_arr = self.email.split('@')
        return email_arr[0]
    
    # return the classification result 
    def classify(self):

        if self.title == '학생': 
            return '학교 소속'
        
        if '학교' in self.company or 'university' in self.company: 
            if self.title in self.invalid_keywords['학교 소속']:
                return '학교 소속'
            
        if self.title == '군인':
            return '군인'
        
        if self.title in ['freelancer', '프리랜서'] or self.company in ['freelancer', '프리랜서']:
            return '프리랜서'
        
        if self.title in self.invalid_keywords['무직'] or self.company in self.invalid_keywords['무직']:
            return '무직'
        
        normalized_domain = self.normalize_domain(self.domain)
        
        if normalized_domain in self.invalid_domains['agencies']:
            return '에이전시'
        
        if normalized_domain in self.invalid_domains['competitors'] or self.company in self.competitors:
            return '경쟁사'
        
        # TODO: 기타 비유효 로직 포함해야 함 

        if self.company == 'company' or self.company == 'startup':
            return '불분명한 이름 및 회사명'
        
        for char in list(self.name):
            if char.isdigit(): 
                return '불분명한 이름 및 회사명'
            
        return ''

    def validate(self):

        # valid - record owner in AE & BDR 
        if self.ref_ae_bdr(self.record_owner):
            return '유효', ''

        # valid - title is 교수, 연구원 && record owner is Yeji Yoon 
        if self.title == '교수' or self.title == '연구원':
            if self.record_owner == 'Yeji Yoon' or 'Yoon Yeji': 
                return '유효', ''
        
        # valid - title is one of these && company is NOT in invalid-keywords: '기타 비유효'
        if self.title in ['대표', '사장', 'ceo', '팀장'] and self.company not in self.invalid_keywords['기타 비유효']:
            return '유효', ''
        
        classification_result = self.classify()

        if classification_result == '':
            return '유효', ''
        
        return '비유효', classification_result
        # unfinished logic 


        '''
        학교 소속 ‘교수', '학생', 'student', '대학생', '대학원생', '석사', '박사 연구원’ - quip
        "학생", "student", "대학생", "대학원생", "석사", "학년" - ik

        - 
        Logic 

        1. must validate if 

            - record owner in AE & BDR 
            - title is 대표, 사장, ceo, 팀장 && company is NOT in invalid-keywords: '기타 비유효'
            - title is 교수, 연구원 && record owner is Yeji Yoon 


        2. must invalidate if 

            - 학교 소속     
                - title is 학생, ALWAYS 
                - company ends with 학교 or university && title is invalid-keywords: '학교 소속' (above title logic does not hold for yeji)

            - 군인 
                - title is 군인 

            - 프리랜서 
                - title or company is 'freelancer' or '프리랜서' 

            - 무직 
                - title or company is in invalid-keywords: '무직' 

            - 에이전시 
                - domain is in invalid-domains: 'agencies' 

            - 경쟁사 
                - domain (normalized) is in invalid-domains: 'competitors' or company is in 'competitors' 

            - 기타 비유효 
                - 
            
            - domain is 
                - invalid-domains: 'agencies', 'competitors'


            - 불분명한 이름 및 회사명 
                - company == 'company' or 'startup'
                - 이름에 숫자 포함, 회사명 키워드 포함 
            

        3. 홀딩 if 

            - 기타 비유효 
                - title or company == personal 
            
            - 불분명한 이름 및 회사명 
                -  name has digits

            - 불분명한 eMail
                - 도메인에 숫자 포함 또는 빈 값 

            - 직책
                - if title in invalid-keywords: 직책 
            
            - Free email
                - email is in invalid-domains: 'free-emails'

        '''
