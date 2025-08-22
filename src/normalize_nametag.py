import argparse
import os
import pandas as pd
import json

from handle_files import HandleFiles


class NormalizeNametag(HandleFiles):

    def __init__(self, args):
        super().__init__(args=args)
        self.date = args.date
        self.raw_db_dir = os.path.join("data", "raw_db", "org_db", self.date)
        self.results_dir = os.path.join("data", "results", self.date)

        os.makedirs(self.results_dir, exist_ok=True)

        # Load special domains
        with open("data/config/special-domains.json", "r", encoding="utf-8") as f:
            self.special_domains = json.load(f)

        # Load nametag_records.csv
        self.nametag_records = pd.read_csv("data/config/nametag_records.csv")

    def clean_company_name(self, name: str) -> str:
        """주식회사, (주), Co., Ltd, INC 등 불필요한 suffix 제거 + 괄호 안 텍스트 제거"""
        if pd.isna(name):
            return ""
        cleaned = str(name)

        # 제거할 패턴들 (대소문자 무시)
        patterns = [
            r"주식회사",
            r"\(주\)",
            r"co\.?\s*ltd\.?",   # co ltd, co. ltd, co.,ltd 등 변형
            r"inc\.?",           # inc, inc.
            r"ltd\.?",           # ltd, ltd.
            r"corp\.?",          # corp, corp.
        ]

        import re
        for p in patterns:
            cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)

        # 괄호 안 텍스트 제거
        cleaned = re.sub(r"\(.*?\)", "", cleaned)

        # 양쪽 공백 정리
        return cleaned.strip()

    def map_special_domain(self, email: str) -> str:
        """special-domains.json 매핑"""
        if not isinstance(email, str) or "@" not in email:
            return ""
        domain = email.split("@")[-1].lower()
        return self.special_domains.get(domain, "")

    def map_nametag_records(self, email: str) -> str:
        """nametag_records.csv 매핑"""
        if not isinstance(email, str):
            return ""
        match = self.nametag_records[self.nametag_records["이메일"] == email]
        if not match.empty:
            return match.iloc[0]["네임택용 회사명"]
        return ""

    def run(self):
        # original_nametags.csv 불러오기
        input_path = os.path.join(self.raw_db_dir, "original_nametags.csv")
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"{input_path} not found")

        df = pd.read_csv(input_path)

        # 필요한 열만 가져오기
        df = df[["Email", "Account Name", "Account Name (Local)"]].copy()

        # 네임택용 회사명 생성
        company_names = []
        for _, row in df.iterrows():
            email = row["Email"]
            account_name = row["Account Name"]
            account_name_local = row["Account Name (Local)"]

            name = self.map_special_domain(email)  # 1. special-domains.json
            if not name:
                name = self.map_nametag_records(email)  # 2. nametag_records.csv
            if not name:
                if isinstance(account_name_local, str) and account_name_local.strip():
                    name = self.clean_company_name(account_name_local)  # 3. Local 우선
                else:
                    name = self.clean_company_name(account_name)  # 4. Local 없으면 Account Name

            company_names.append(name)

        df["네임택용 회사명"] = company_names

        # 최종 3개 열만 저장
        output_df = df[["Email", "Account Name", "네임택용 회사명"]]

        output_path = os.path.join(self.results_dir, "nametag_normalized.xlsx")
        output_df.to_excel(output_path, index=False)
        print(f"✅ Saved normalized nametag file: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, required=True, help="Date in MMDD format.")

    args = parser.parse_args()
    NormalizeNametag(args).run()