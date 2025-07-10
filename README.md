# AWTK2025

AWTK2025 is a database cleansing automation project initiated by two interns at Salesforce Korea. It aims to reduce the manual work of previous years to validate and normalize submitted inputs of at least 8,000+ attendees of Agentforce World Tour Korea from 2025 onwards. 

## Installation

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

AWTK2025 should now be ready to run. 

## Authors 
[Jeeho Kim](https://github.com/kimjooooo)  
[Seolin Jung](https://github.com/seolinjung)
