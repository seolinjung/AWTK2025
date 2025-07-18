# AWTK2025

AWTK2025 is a database cleansing automation project initiated by two interns at Salesforce Korea. It aims to reduce the manual work of previous years to validate and normalize submitted inputs of at least 8,000+ attendees of Agentforce World Tour Korea from 2025 onwards. 

## Environment Setup

AWTK2025 runs on Python 3.13. Please find the most recent versions on Python's [official site](https://www.python.org/downloads/).  

You must have `pip` in order to download the required packages. 

```bash
python3 -m ensure pip --upgrade
```

If you have multiple versions of Python on your operating system, it helps to run `python3.13` in place of `python`. 

In order to ensure an isolated environment for clean installation, we must set up our virtual environment. Make sure you are in the correct directory. 

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Success! Now you are inside a virtual environment. Please find the list of required packages alongside their specific versions in `requirements.txt.` 

```bash
pip3 install -r requirements.txt
```

## File Structure

Make sure that you have all folders and files necessary to run your code. The complete tree looks like this: 

```
.
├── cleanse_test.py
├── config.yaml
├── data (internally provided)
│   ├── exceptions
│   │   ├── ae-bdr.json
│   │   ├── invalid-companies.json
│   │   ├── invalid-domains.json
│   │   ├── invalid-record-owners.json
│   │   ├── invalid-titles.json
│   │   ├── sdr-record-owners.json
│   │   ├── special-domains.json
│   │   ├── valid-companies.json
│   │   └── valid-titles.json
│   └── results (created upon running the code)
│       └── 0615 (or other date)
│           └── Sorted_DB.xlsx
├── helper.py
├── main.py
├── omitted_db_check.py
├── raw_db (internally provided)
│   ├── org_db
│   │   ├── 0615 (or other date)
│   │   │   ├── confirm_mail.csv (optional)
│   │   │   ├── main.csv (internally provided, must exist)
│   │   │   ├── sales_invite.csv (optional)
│   │   └── └── sdr_confirm.csv (optional)
│   └── seonhye
│       └── seonhye_confirm.csv (optional)
├── README.md
├── requirements.txt
└── validate_input.py
```

The `data` and `raw_db` folders are internally provided within Salesforce for security purposes. Once you gain access to those two folders, you've activated your virtual environment, and you know you are in the right root folder, AWTK2025 should be ready to run. 

## Code Execution

```bash
python3 main.py --date {insert preferred date}
```

Date is an optional parameter. By providing the date, you can specify which input files you want to run the code on. The code expects a date format of MMDD. The resulting Excel file will be created under `data/results/{date}` as `Sorted_DB.xlsx`. 

## Authors 
[Jeeho Kim](https://github.com/kimjooooo)  
[Seolin Jung](https://github.com/seolinjung)
