from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import calendar
import re

# Inputs -> str: DD/MM/YYYY;  Output -> date format (out.year, out.month, out.day)
def parse_date(date_str:str):
    '''
    Inputs -> str: DD/MM/YYYY 
    Output -> date format (out.year, out.month, out.day)
    '''
    formats = [
        "%d/%m/%Y", "%d/%m/%y",   # 19/05/2025, 19-05-2025, 19.05.2025, 19 05 2025
        "%d-%m-%Y", "%d-%m-%y",   # 19/May/2025, April & Apr, etc
        "%d.%m.%Y", "%d.%m.%y",
        "%d %m %Y", "%d %m %y",
        "%d-%b-%Y", "%d-%b-%y",
        "%d-%B-%Y", "%d-%B-%y",
        "%d %b %Y", "%d %b %y",
        "%d %B %Y", "%d %B %y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.date()
        except ValueError:
            continue
    
    raise ValueError(f"Unrecognized date format: {date_str}")

# From DoB, calculates retirement at the age of 60 years
def get_retirement_date(dob_str:str, retirement_age:int=60):
    '''
    From DoB, calculates retirement at the age of 60 years
    Output -> date format (out.year, out.month, out.day)
    '''
    parsed = parse_date(dob_str)
    # dob = date(parsed.year, parsed.month, parsed.date)
    dob = date(parsed.year, parsed.month, parsed.day)

    # # Add 60 years — retirement is on the day before 60th birthday
    # retirement_date = date(dob.year + retirement_age, dob.month, dob.day)

    # Calculate retirement year and month
    retire_year = dob.year + retirement_age
    retire_month = dob.month

    # Get last day of retirement month
    last_day = calendar.monthrange(retire_year, retire_month)[1]

    # Retirement date is the last day of that month
    retirement_date = date(retire_year, retire_month, last_day)

    return retirement_date

# Used in LumpSum calculation of UPS
def get_six_month_periods(initial_date: date, final_date: date) -> int:
    """Returns number of 6-month periods between two dates (inclusive if exact match)."""
    months_diff = (final_date.year - initial_date.year) * 12 + (final_date.month - initial_date.month)
    six_month_periods = months_diff // 6 + 1  # +1 if you count starting period
    return six_month_periods

# Get months difference among two dates (since less than 25 yr/300 month service reduces pension)
def get_month_difference(start_date, end_date):
    diff = relativedelta(end_date, start_date)
    return abs(int(diff.years * 12 + diff.months))

# Extracts Pay Commission Number from it's csv filename
def extract_cpc_no_from_filename(filename: str) -> int:
    """
    Extracts the CPC number from a filename like '8th_CPC_fitment_factor_2.csv'.
    """
    match = re.match(r"(\d+)(?:st|nd|rd|th)?_CPC", filename)
    if match:
        return int(match.group(1))
    raise ValueError(f"Could not extract CPC number from filename: {filename}")

# Convert percent input like 25 or '25%' to float (0.25)
def normalize_percent(value):
    """Convert percent input like 25 or '25%' to float (0.25)"""
    if isinstance(value, str) and value.endswith('%'):
        value = value.rstrip('%')
    return float(value) / 100 if float(value) > 1 else float(value)

# loads given csv file into pd dataframe
def load_csv_into_df(csv_path : str):
    '''
    In -> .csv file path/name
    Out -> pandas 'dataframe' onbject
    '''
    # Load the pay matrix CSV once and keep in memory
    df_loaded = pd.read_csv(csv_path)
    # Convert column names to string for consistency
    df_loaded.columns = df_loaded.columns.map(str)
    return df_loaded

# Default values for E, C, G and their tapering period
def get_default_interes_rate_tapering_dict():
    interest_rate_tapering_dict = {}
    interest_rate_tapering_dict['E'], interest_rate_tapering_dict['C'], interest_rate_tapering_dict['G'] = {}, {}, {}
    interest_rate_tapering_dict['Taper Period'] = 40
    interest_rate_tapering_dict['E']['initial'] = 12.0
    interest_rate_tapering_dict['E']['final'] = 6.0
    interest_rate_tapering_dict['C']['initial'] = 8.0
    interest_rate_tapering_dict['C']['final'] = 4.0
    interest_rate_tapering_dict['G']['initial'] = 8.0
    interest_rate_tapering_dict['G']['final'] = 4.0
    
    return interest_rate_tapering_dict




# To make parse_date_parts.date, parse_date_parts.month, and parse_date_parts.year directly accessible 
# # as attributes after calling the function, you can wrap the return in a custom class
# class ParsedDate:
#     def __init__(self, day, month, year):
#         self.date = day
#         self.month = month
#         self.year = year

#     def __iter__(self):
#         return iter((self.date, self.month, self.year))

#     def __repr__(self):
#         return f"ParsedDate(date={self.date}, month={self.month}, year={self.year})"

# def parse_date_old(date_str):
#     formats = [
#         "%d/%m/%Y", "%d/%m/%y",   # 19/05/2025, 19-05-2025, 19.05.2025, 19 05 2025
#         "%d-%m-%Y", "%d-%m-%y",   # 19/May/2025, April & Apr, etc
#         "%d.%m.%Y", "%d.%m.%y",
#         "%d %m %Y", "%d %m %y",
#         "%d-%b-%Y", "%d-%b-%y",
#         "%d-%B-%Y", "%d-%B-%y",
#         "%d %b %Y", "%d %b %y",
#         "%d %B %Y", "%d %B %y",
#     ]

#     for fmt in formats:
#         try:
#             dt = datetime.strptime(date_str.strip(), fmt)
#             # return dt.day, dt.month, dt.year
#             return ParsedDate(dt.day, dt.month, dt.year)
#         except ValueError:
#             continue
    
#     raise ValueError(f"Unrecognized date format: {date_str}")
