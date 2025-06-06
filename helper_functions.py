from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from babel.numbers import format_currency, format_compact_currency
import streamlit as st
import pandas as pd
import calendar
import inspect
import re

from default_constants import *

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
# @st.cache_data
def load_csv_into_df(csv_name:str, data_path:str = DATA_FOLDER_PATH):
    '''
    In -> .csv file path/name
    Out -> pandas 'dataframe' onbject
    '''
    # Load the pay matrix CSV once and keep in memory
    # df_loaded = pd.read_csv(csv_path)
    df_loaded = pd.read_csv(data_path + csv_name)
    # Convert column names to string for consistency
    df_loaded.columns = df_loaded.columns.map(str)
    # df_loaded.set_index(df_loaded.columns[0])
    return df_loaded

# NPV (Net Present Value): value of future amount in present term -> basically inflation adjusted value
def get_npv(amount:int, discount_rate:float):
    return int(amount / discount_rate)

# Default values for E, C, G and their tapering period
def get_interest_rate_tapering_dict(E_initial:float = DEFAULT_E_INITIAL, E_final:float = DEFAULT_E_FINAL,
                                    C_initial:float = DEFAULT_C_INITIAL, C_final:float = DEFAULT_C_FINAL,
                                    G_initial:float = DEFAULT_G_INITIAL, G_final:float = DEFAULT_G_FINAL,
                                    taper_period_yrs:int = DEFAULT_TAPER_PERIOD):
    interest_rate_tapering_dict = {}
    interest_rate_tapering_dict['E'], interest_rate_tapering_dict['C'], interest_rate_tapering_dict['G'] = {}, {}, {}
    interest_rate_tapering_dict['Taper Period'] = taper_period_yrs
    interest_rate_tapering_dict['E']['initial'] = E_initial
    interest_rate_tapering_dict['E']['final'] = E_final
    interest_rate_tapering_dict['C']['initial'] = C_initial
    interest_rate_tapering_dict['C']['final'] = C_final
    interest_rate_tapering_dict['G']['initial'] = G_initial
    interest_rate_tapering_dict['G']['final'] = G_final
    
    return interest_rate_tapering_dict

# To automatically filter only the required arguments for a function, you can use
def auto_pass_arguments_to_function(sub_function, **kwargs):
    sig = inspect.signature(sub_function)
    accepted_args = {
        k: v for k, v in kwargs.items() if k in sig.parameters
    }
    return sub_function(**accepted_args)

def convert_dt_to_string(dt:date):
    return dt.strftime('%d/%m/%y')

def get_compact_currency(x:int):
    return format_compact_currency(x, 'INR', locale='en_IN', fraction_digits=4)

def get_currency(x:int):
    currency = format_currency(x, 'INR', locale='en_IN')
    currency = currency.replace('.00', '')
    return currency


def format_inr(amount):
    return format_currency(amount, 'INR', locale='en_IN', format=u'¤#,##,##0',currency_digits=False)





# def format_inr(amount):
#     s = f"{amount:,.2f}"
#     parts = s.split(".")
#     rupees = parts[0]
#     decimal = parts[1]

#     # Convert to Indian number system
#     if len(rupees) > 3:
#         rupees = rupees[:-3][::-1]
#         rupees = ",".join([rupees[i:i+2] for i in range(0, len(rupees), 2)])[::-1] + "," + s[-6:-3]
#     return f"₹{rupees}.{decimal}"

# def format_inr_no_paise(amount):
#     return format_inr(round(amount)).split('.')[0]