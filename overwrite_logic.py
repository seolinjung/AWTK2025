import pandas as pd

from validate_default import ValidateInput

import helper 

class Overwrite(ValidateInput): 

    def __init__(self, row): 

        super().__init__(row)

        self.seonhye_confirm_path = helper.retrieve_csv(self.args, "seonhye_confirm", True)
        self.seonhye_confirm_df = pd.read_csv(self.seonhye_confirm_path) if self.seonhye_confirm_path else False 

        self.sales_invite_path = helper.retrieve_csv(self.args, "sales_invite")
        self.sales_invite_df = pd.read_csv(self.sales_invite_path) if self.sales_invite_path else False  

    def overwrite_seonhye(self): 

        seonhye_row = self.email_logic.lookup_email(self.seonhye_confirm_df)

        if not seonhye_row.empty:
            return seonhye_row["MKT Review(유효/비유효/홀딩)"], ''
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]

    def overwrite_sales(self):

        if not self.email_logic.lookup_email(self.sales_invite_df).empty: 
            return '유효', 'Sales Invite' 
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]       

