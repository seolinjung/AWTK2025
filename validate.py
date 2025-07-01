import re 
import json 

def extract_values(row):

    title = str(row['Title']).lower()
    company = str(row['Company (Custom)']).strip().lower()
    email = str(row['Email']).lower()
    domain = row['domain']
    first_name = str(row.get('First Name', '')).lower()
    last_name = str(row.get('Last Name', '')).lower()
    record_owner = str(row['Related Record Owner']).strip()

    return [title, company, email, domain, first_name, last_name, record_owner]

def ref_ae_bdr(record_owner):

    # get the json file array
    with open('ae-bdr.json', 'r') as file:
        ae_bdr_list = json.load(file)["ae-bdr"]
    
    # make it into an array for deconstructing
    record_owner_arr = record_owner.split()

    # "Hong Gil Dong" or "Gil Dong Hong"
    if len(record_owner_arr) == 3:
        alt_order = " ".join([record_owner[2], record_owner[0], record_owner[1]])

    # "Hong Gildong" or "Gildong Hong"
    if len(record_owner_arr) == 2:
        alt_order = " ".join(record_owner[1], record_owner[0])

    # if the name matches ae bdr list 
    if record_owner_arr in ae_bdr_list or alt_order in ae_bdr_list: 
        return True
    
    return False

def ref_title(title):

    # get the json file array
    
    
    return True

def ref_domain(domain):

    '''
    domain - 
    1. 비유효 
        - no domain 
        - competitor: 경쟁사 
        - agency: 에이전시 
        - 기타 비유효: misc
    '''




def validate(row):

    # extract array of values from the single row 
    values = extract_values(row)
    # define the names
    title, company, email, domain, first_name, last_name, record_owner = values[0], values[1], values[2], values[3], values[4], values[5], values[6]

    # no exception validation first: check ae bdr
    if ref_ae_bdr(record_owner):
        return "유효", ""


    return True


'''
Logic 

1. must validate if 
    - AE & BDR 
    - title is 대표, 사장, ceo, 팀장 
        - unless company is 자영업 

2. invalid if 
    - company ends with 학교 or university AND title is 학교 소속 ‘교수', '학생', 'student', '대학생', '대학원생', '석사', '박사 연구원’
        - unless record owner is Yeji Yoon and title is '교수', '연구원' 
        - if 학생 & 군인, always invalid regardless of record owner 

    - title includes '프리랜서' or 'freelancer'
    - title or company is '무직', '없음', '취준', '준비중'
    - domain is 에이전시 or 경쟁사 
    - company is 'company', 'startup'
    

3. 홀딩 if 
    - name has digits
    - free email


    title -
    1. if 대표, 사장, ceo, 팀장 
        - if company is NOT in ik:'기타 비유효'
            --> 유효 
    2. if
        - invalid-keywords: '프리랜서'
        - invalid-keywords: '무직' 
        - invalid-keywords: '학교 소속' 
            --> 비유효 

    3. if 
        - 기자, 
            --> 비유효 

    company - 
    1. 유효
    2. 비유효 
        - company ends with 학교 or university  

    email - 
        - free 
'''