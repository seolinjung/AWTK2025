def main(): 

    english_ver = [
        "Kyobo Digital Technology Service Co.,Ltd.",
        "Cheil Worldwide Inc.",
        "Samsung SDS Co.,Ltd.(CRM)",
        "Vieworks Co.,Ltd.",
        "I2MAX"
    ]

    local_ver = [
        "교보디티에스 주식회사", 
        "주식회사 제일기획",
        "삼성에스디에스 주식회사",
        "주식회사 뷰웍스",
        "주식회사 제일기획",
        "I2MAX(Partner Main)"
    ]

    print("~~ testing ~~\n")
    print(f"Original, in English:\n")
    print(english_ver)

    english_ver_cleansed = []

    for company in english_ver:
        english_ver_cleansed.append(english_cleanse(company))

    print("\nCleansed!\n")
    print(english_ver_cleansed)

    print(f"\nOriginal, in Korean:\n")
    print(local_ver)

    local_ver_cleansed = []

    for company in local_ver:
        local_ver_cleansed.append(local_cleanse(company))

    print("\nCleansed!\n")
    print(local_ver_cleansed)

def english_cleanse(name):
    
    split_name = name.split()
    
    for i, word in enumerate(split_name):
        if "," in word or "." in word:
            split_name.pop(i)
    
    return " ".join(split_name)

def local_cleanse(name):

    filters = [
        "주식회사"
    ]

    # also a problem if parentheses exist - special characters
    
    new_name = []

    split_name = name.split()

    for i, word in enumerate(split_name):
        if word in filters:
            continue
        if '(' in word: 
            # but it doesn't start with parenthesis
            # which means that we have to replace the word with substring omitting (
            para_idx = word.index('(')
            replacement = word[:para_idx]
            new_name.append(replacement)
            continue
        if ')' in word:
            # just delete it all 
            continue
        new_name.append(word)

    return " ".join(new_name)


if __name__ == "__main__":

    # python3 -m venv venv
    # source ./venv/bin/activate

    main()