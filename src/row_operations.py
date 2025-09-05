import pandas as pd 

class RowOperations: 

    def __init__(self, *, row, **kwargs): 

        super().__init__(**kwargs)

        # define all the major column values 
        self.campaign = str(row.get('Campaign Name'))
        self.title = str(row.get('Title')).lower()
        self.company = str(row.get('Company (Custom)')).strip().lower()
        self.email = str(row.get('Email')).lower()
        self.domain = row.get('domain')
        self.first_name = str(row.get('First Name', '')).lower()
        self.last_name = str(row.get('Last Name', '')).lower()
        self.name = self.first_name + self.last_name
        self.record_owner = (
            str(row.get('Related Record Owner') or row.get('Lead Owner') or "").strip()
        )

        self.normalized_domain = self.normalize_domain()
        self.username = self.extract_username()

    def extract_username(self): 

        if pd.isna(self.email) or "@" not in str(self.email):
            return ''
        return str(self.email).split("@")[0].lower()

    def normalize_domain(self):

        # get the value before the period. 'samsung.com' should return 'samsung'
        domain_arr = self.domain.split('.')
        return domain_arr[0]