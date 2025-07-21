import pandas as pd

from validate_default import ValidateInput
import helper

class ValidateEmail(ValidateInput): 

    def __init__(self, row): 

        super().__init__(row)
        self.normalized_domain = helper.normalize_domain(self.domain)
        self.username = helper.extract_username(self.email) 

    def is_free(self): 
        
        return self.match("normalized_domain", "free-email")
    
    def is_special(self): 

        special_chars = "[@_!#$%^&*()<>?/\|}{~:]"
        for char in self.username: 
            if char not in special_chars: 
                return False 

        return True

    def filter_free_email(self): 

        # email username is only consisted of digits or special characters 
        if self.username.isdigit() or self.is_special(): 
            return '비유효', 'Invalid e-mail: username'
        
        if "test" in self.username or "test" in self.domain: 
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


    def lookup_df(self, df):
        
        if df is not None: 
            selected_emails = set(df['Email'])
            if self.email in selected_emails:
                return df[df['Email'] == self.email].iloc[0]
            return pd.DataFrame()
        return pd.DataFrame()
    