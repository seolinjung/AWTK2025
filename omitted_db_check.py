import pandas as pd
import os
import argparse

def load_file(folder_date, file_stem):
    file_name = f"{file_stem}.csv"
    path = os.path.join("raw_db", "org_db", folder_date, file_name)

    if not os.path.exists(path):
        print(f"❌ 파일을 찾을 수 없습니다: {path}")
        return None
    try:
        df = pd.read_csv(path)
        if 'Email' not in df.columns:
            print("⚠️ 'Email' 컬럼이 존재하지 않습니다. 파일 형식을 확인해주세요.")
            return None
        df['Email'] = df['Email'].str.lower().str.strip()
        return df
    except Exception as e:
        print(f"⚠️ 파일 로딩 중 오류가 발생했습니다: {e}")
        return None

def compare_emails(folder_date, file1_stem, file2_stem):
    df1 = load_file(folder_date, file1_stem)
    df2 = load_file(folder_date, file2_stem)
    
    if df1 is None or df2 is None:
        return

    only_in_first = df1[~df1['Email'].isin(df2['Email'])]

    if only_in_first.empty:
        print(f"\n✅ 모든 email이 '{file1_stem}.csv'와 '{file2_stem}.csv' 양쪽에 존재합니다.\n")
    else:
        print("\n3. 📋 비교 결과:")
        print(f"👉 '{file1_stem}.csv'에만 있고, '{file2_stem}.csv'에는 없는 Email 목록:")
        print("-" * 60)
        print(only_in_first['Email'].to_string(index=False))
        print(f"\n총 {len(only_in_first)}개의 이메일이 '{file1_stem}.csv'에만 존재합니다.\n")

def main(default_date=None):
    while True:
        print("\n📌 이메일 비교를 시작합니다.")
        if default_date:
            use_default = input(f"0. 날짜는 기본값({default_date})을 사용하시겠습니까? (yes/no)\n> ").strip().lower()
            if use_default == 'yes':
                folder_date = default_date
            else:
                folder_date = input("  ➕ 직접 입력해주세요 (예: 0701)\n> ").strip()
        else:
            folder_date = input("0. 어느 날짜의 폴더를 확인하시겠습니까? (예: 0701)\n> ").strip()

        file1_input = input("1. 어떤 파일에만 있는 email 목록을 확인하고 싶나요? (확장자 제외)\n예시: file1\n> ").strip()
        file2_input = input("2. 어떤 파일과 비교할까요? (확장자 제외)\n예시: file2\n> ").strip()

        compare_emails(folder_date, file1_input, file2_input)

        again = input("4. 다른 파일을 확인하시겠습니까? (yes/no)\n> ").strip().lower()
        if again != 'yes':
            print("👋 이메일 비교를 종료합니다.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="기본 폴더 날짜 (예: 20240709)")
    args = parser.parse_args()

    main(default_date=args.date)