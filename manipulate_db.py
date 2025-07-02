import pandas as pd

def match_db(main, sub, column):

    # check if sub matches main based on column value
    sub_vals = set(sub[column])
    main_vals = set(main[column])

    # calculate remaining
    unmatched = sub_vals - main_vals

    # if there are any that don't match main 
    if unmatched:
        print(f"List of emails that exist on {sub} but not {main}:")
        for val in unmatched: 
            print(f"- {val}")
        return False
    else:
        # all emails match, no further step needed
        print(f"All emails exist on both {main} and {sub}.")
        return True
    
def merge_db(main, sub, column):

    # now merge with sub
    main = main.merge(sub, on=column, how="left")

    return main 