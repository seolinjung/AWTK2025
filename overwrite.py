import pandas as pd

from validate import Validate

import helper as helper 

class Overwrite(Validate): 

    def __init__(self, args, row): 

        super().__init__(args, row)

        self.seonhye_confirm_path = self.retrieve_csv("seonhye_confirm", True)
        self.seonhye_confirm_df = pd.read_csv(self.seonhye_confirm_path) if self.seonhye_confirm_path else False 

        self.sales_invite_path = self.retrieve_csv("sales_invite")
        self.sales_invite_df = pd.read_csv(self.sales_invite_path) if self.sales_invite_path else False  

    def overwrite_seonhye(self): 

        seonhye_row = helper.lookup_df(self.email, self.seonhye_confirm_df)

        if not seonhye_row.empty:
            return seonhye_row["MKT Review(유효/비유효/홀딩)"], ''
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]

    def overwrite_sales(self):

        if not helper.lookup_df(self.email, self.sales_invite_df).empty: 
            return '유효', 'Sales Invite' 
        return self.row["MKT Review(유효/비유효/홀딩)"], self.row["MKT Review(사유)"]       

