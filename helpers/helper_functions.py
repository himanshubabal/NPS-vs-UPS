"""
NPS vs UPS Pension Calculator - Helper Functions Module

This module provides utility functions used throughout the pension calculator
application. It includes date parsing, retirement calculations, CSV loading,
currency formatting, and other helper functions.

Key Functions:
- Date utilities: parse_date(), get_retirement_date(), convert_dt_to_string()
- Financial helpers: get_npv(), get_interest_rate_tapering_dict()
- Data loading: load_csv_into_df()
- Currency formatting: get_currency(), format_inr(), get_compact_currency()
- Utility functions: auto_pass_arguments_to_function(), normalize_percent()

Author: Pension Calculator Team
Version: 1.0
"""

from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from babel.numbers import format_currency, format_compact_currency
import streamlit as st
import pandas as pd
import calendar
import inspect
import re
from typing import Union, Dict, Any, List, Tuple

from default_constants import *


def parse_date(date_str: str) -> date:
    """
    Parse date string in multiple formats to date object.
    
    This function handles various date input formats commonly used in India:
    - DD/MM/YYYY, DD/MM/YY
    - DD-MM-YYYY, DD-MM-YY
    - DD.MM.YYYY, DD.MM.YY
    - DD MM YYYY, DD MM YY
    - DD-MMM-YYYY, DD-MMM-YY (abbreviated month names)
    - DD-MMMM-YYYY, DD-MMMM-YY (full month names)
    
    Args:
        date_str (str): Date string in any supported format
        
    Returns:
        date: Parsed date object
        
    Raises:
        ValueError: If date string cannot be parsed in any supported format
        
    Example:
        >>> parse_date('15/06/1995')
        datetime.date(1995, 6, 15)
        >>> parse_date('15-Jun-1995')
        datetime.date(1995, 6, 15)
        >>> parse_date('15 06 95')
        datetime.date(1995, 6, 15)
    """
    formats = [
        "%d/%m/%Y", "%d/%m/%y",   # 19/05/2025, 19-05-2025, 19.05.2025, 19 05 2025
        "%d-%m-%Y", "%d-%m-%y",   # 19/May/2025, April & Apr, etc
        "%d.%m.%Y", "%d.%m.%y",
        "%d %m %Y", "%d %m %y",
        "%d-%b-%Y", "%d-%b-%y",
        "%d-%B-%Y", "%d-%B-%y",
        "%d %b %Y", "%d %b %Y",
        "%d %B %Y", "%d %B %Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.date()
        except ValueError:
            continue
    
    raise ValueError(f"Unrecognized date format: {date_str}")


def get_retirement_date(dob_str: str, retirement_age: int = 60) -> date:
    """
    Calculate retirement date based on date of birth.
    
    Retirement is calculated as the last day of the month in which
    the employee turns the specified retirement age. This follows
    government service rules where retirement occurs at month-end.
    
    Args:
        dob_str (str): Date of birth in DD/MM/YYYY format
        retirement_age (int): Age at retirement (default: 60 years)
        
    Returns:
        date: Retirement date (last day of retirement month)
        
    Example:
        >>> get_retirement_date('15/06/1995')
        datetime.date(2055, 6, 30)  # June 30, 2055 (last day of June)
        >>> get_retirement_date('01/01/1990', 58)
        datetime.date(2048, 1, 31)  # January 31, 2048 (last day of January)
    """
    parsed = parse_date(dob_str)
    dob = date(parsed.year, parsed.month, parsed.day)

    # Calculate retirement year and month
    retire_year = dob.year + retirement_age
    retire_month = dob.month

    # Get last day of retirement month
    last_day = calendar.monthrange(retire_year, retire_month)[1]

    # Retirement date is the last day of that month
    retirement_date = date(retire_year, retire_month, last_day)

    return retirement_date


def get_six_month_periods(initial_date: date, final_date: date) -> int:
    """
    Calculate number of 6-month periods between two dates.
    
    This function is used for UPS lumpsum calculations where
    lumpsum = (Last month salary / 10) × Number of 6-month periods served.
    
    Args:
        initial_date (date): Starting date (usually date of joining)
        final_date (date): Ending date (usually date of retirement)
        
    Returns:
        int: Number of 6-month periods (inclusive if exact match)
        
    Example:
        >>> get_six_month_periods(date(2024, 1, 1), date(2026, 1, 1))
        5  # 2 years = 4 six-month periods + 1 (inclusive)
        >>> get_six_month_periods(date(2024, 7, 1), date(2025, 1, 1))
        2  # 6 months = 1 six-month period + 1 (inclusive)
    """
    months_diff = (final_date.year - initial_date.year) * 12 + (final_date.month - initial_date.month)
    six_month_periods = months_diff // 6 + 1  # +1 if you count starting period
    return six_month_periods


def get_month_difference(start_date: date, end_date: date) -> int:
    """
    Calculate months difference between two dates.
    
    This is used for pension calculations where service less than
    25 years (300 months) reduces pension proportionally.
    
    Args:
        start_date (date): Starting date
        end_date (date): Ending date
        
    Returns:
        int: Absolute difference in months
        
    Example:
        >>> get_month_difference(date(2024, 1, 1), date(2026, 1, 1))
        24
        >>> get_month_difference(date(2024, 7, 1), date(2025, 1, 1))
        6
    """
    diff = relativedelta(end_date, start_date)
    return abs(int(diff.years * 12 + diff.months))


def extract_cpc_no_from_filename(filename: str) -> int:
    """
    Extract CPC (Central Pay Commission) number from filename.
    
    This function parses filenames like '8th_CPC_fitment_factor_2.csv'
    to extract the CPC number for pay matrix generation.
    
    Args:
        filename (str): Filename containing CPC information
        
    Returns:
        int: CPC number extracted from filename
        
    Raises:
        ValueError: If CPC number cannot be extracted
        
    Example:
        >>> extract_cpc_no_from_filename('8th_CPC_fitment_factor_2.csv')
        8
        >>> extract_cpc_no_from_filename('7th_CPC.csv')
        7
        >>> extract_cpc_no_from_filename('10th_CPC_fitment_factor_1.71.csv')
        10
    """
    match = re.match(r"(\d+)(?:st|nd|rd|th)?_CPC", filename)
    if match:
        return int(match.group(1))
    raise ValueError(f"Could not extract CPC number from filename: {filename}")


def normalize_percent(value: Union[str, float, int]) -> float:
    """
    Convert percentage input to decimal format.
    
    This function handles various percentage input formats:
    - 25 → 0.25
    - '25%' → 0.25
    - 0.25 → 0.25 (already decimal)
    
    Args:
        value: Percentage value in any supported format
        
    Returns:
        float: Normalized decimal value (0.0 to 1.0)
        
    Example:
        >>> normalize_percent(25)
        0.25
        >>> normalize_percent('25%')
        0.25
        >>> normalize_percent(0.25)
        0.25
    """
    if isinstance(value, str) and value.endswith('%'):
        value = value.rstrip('%')
    return float(value) / 100 if float(value) > 1 else float(value)


def load_csv_into_df(csv_name: str, data_path: str = DATA_FOLDER_PATH) -> pd.DataFrame:
    """
    Load CSV file into pandas DataFrame.
    
    This function loads pay matrix and DA data CSV files, ensuring
    consistent column handling and data types. It's used throughout
    the application for loading various data sources.
    
    Args:
        csv_name (str): Name of the CSV file to load
        data_path (str): Path to the data directory (default: 'data/')
        
    Returns:
        pd.DataFrame: Loaded CSV data with string column names
        
    Example:
        >>> df = load_csv_into_df('7th_CPC.csv')
        >>> df = load_csv_into_df('6th_CPC_DA.csv', 'custom_data/')
    """
    # Load the pay matrix CSV once and keep in memory
    df_loaded = pd.read_csv(data_path + csv_name)
    
    # Convert column names to string for consistency
    df_loaded.columns = df_loaded.columns.map(str)
    
    return df_loaded


def get_npv(amount: int, discount_rate: float) -> int:
    """
    Calculate Net Present Value (NPV) of a future amount.
    
    NPV = Future Amount / Discount Rate
    This is used to determine the present value of the final corpus
    considering inflation over the career period.
    
    Args:
        amount (int): Future amount (usually final corpus)
        discount_rate (float): Cumulative inflation factor
        
    Returns:
        int: Present value of the future amount
        
    Example:
        >>> get_npv(1000000, 2.5)
        400000  # ₹10L in future = ₹4L in present terms
    """
    return int(amount / discount_rate)


def get_interest_rate_tapering_dict(E_initial: float = DEFAULT_E_INITIAL, 
                                   E_final: float = DEFAULT_E_FINAL,
                                   C_initial: float = DEFAULT_C_INITIAL, 
                                   C_final: float = DEFAULT_C_FINAL,
                                   G_initial: float = DEFAULT_G_INITIAL, 
                                   G_final: float = DEFAULT_G_FINAL,
                                   taper_period_yrs: int = DEFAULT_TAPER_PERIOD) -> Dict[str, Any]:
    """
    Build interest rate tapering configuration dictionary.
    
    This function creates a structured dictionary that defines how
    investment returns change over time for different asset classes:
    - E (Equity): Usually tapers from high to low returns
    - C (Corporate Bonds): Moderate tapering
    - G (Government Bonds): Minimal tapering
    
    Args:
        E_initial (float): Initial equity return rate
        E_final (float): Final equity return rate
        C_initial (float): Initial corporate bond return rate
        C_final (float): Final corporate bond return rate
        G_initial (float): Initial government bond return rate
        G_final (float): Final government bond return rate
        taper_period_yrs (int): Years over which rates taper
        
    Returns:
        Dict[str, Any]: Configuration dictionary with structure:
            {
                'E': {'initial': float, 'final': float},
                'C': {'initial': float, 'final': float},
                'G': {'initial': float, 'final': float},
                'Taper Period': int
            }
            
    Example:
        >>> config = get_interest_rate_tapering_dict(
        ...     E_initial=12.0, E_final=6.0,
        ...     C_initial=8.0, C_final=4.0,
        ...     G_initial=8.0, G_final=4.0,
        ...     taper_period_yrs=40
        ... )
        >>> print(config['E']['initial'])
        12.0
    """
    interest_rate_tapering_dict = {}
    interest_rate_tapering_dict['E'] = {'initial': E_initial, 'final': E_final}
    interest_rate_tapering_dict['C'] = {'initial': C_initial, 'final': C_final}
    interest_rate_tapering_dict['G'] = {'initial': G_initial, 'final': G_final}
    interest_rate_tapering_dict['Taper Period'] = taper_period_yrs
    
    return interest_rate_tapering_dict


def auto_pass_arguments_to_function(sub_function: callable, **kwargs) -> Any:
    """
    Automatically filter and pass only relevant arguments to a function.
    
    This utility function inspects the target function's signature
    and only passes parameters that the function actually accepts.
    This prevents "unexpected keyword argument" errors when calling
    functions with different parameter sets.
    
    Args:
        sub_function (callable): Function to call with filtered arguments
        **kwargs: All available keyword arguments
        
    Returns:
        Any: Result of calling sub_function with filtered arguments
        
    Example:
        >>> def test_func(a, b, c):
        ...     return a + b + c
        >>> result = auto_pass_arguments_to_function(
        ...     test_func, a=1, b=2, c=3, d=4, e=5
        ... )
        >>> print(result)  # Only a, b, c are passed, d and e are ignored
        6
    """
    sig = inspect.signature(sub_function)
    accepted_args = {
        k: v for k, v in kwargs.items() if k in sig.parameters
    }
    return sub_function(**accepted_args)


def convert_dt_to_string(dt: date) -> str:
    """
    Convert date object to DD/MM/YY string format.
    
    This function is used for displaying dates in the UI and
    passing date information between functions.
    
    Args:
        dt (date): Date object to convert
        
    Returns:
        str: Date string in DD/MM/YY format
        
    Example:
        >>> convert_dt_to_string(date(2024, 12, 9))
        '09/12/24'
    """
    return dt.strftime('%d/%m/%y')


def get_compact_currency(x: int) -> str:
    """
    Format large amounts in compact currency format.
    
    This function uses Babel to format Indian Rupee amounts
    in a compact, readable format (e.g., ₹1.00Cr for ₹1 crore).
    
    Args:
        x (int): Amount in rupees
        
    Returns:
        str: Formatted currency string
        
    Example:
        >>> get_compact_currency(10000000)
        '₹1.00Cr'
        >>> get_compact_currency(1500000)
        '₹15.00L'
    """
    return format_compact_currency(x, 'INR', locale='en_IN', fraction_digits=4)


def get_currency(x: int) -> str:
    """
    Format amounts in standard currency format.
    
    This function formats Indian Rupee amounts with proper
    formatting and removes unnecessary decimal places.
    
    Args:
        x (int): Amount in rupees
        
    Returns:
        str: Formatted currency string
        
    Example:
        >>> get_currency(1000000)
        '₹10,00,000'
        >>> get_currency(1500)
        '₹1,500'
    """
    currency = format_currency(x, 'INR', locale='en_IN')
    currency = currency.replace('.00', '')  # Remove unnecessary decimals
    return currency


def format_inr(amount: Union[int, float]) -> str:
    """
    Format amounts in Indian Rupee format with proper separators.
    
    This function provides Indian number system formatting
    with lakhs and crores separators.
    
    Args:
        amount (Union[int, float]): Amount to format
        
    Returns:
        str: Formatted amount in Indian Rupee format
        
    Example:
        >>> format_inr(1000000)
        '₹10,00,000'
        >>> format_inr(15000000)
        '₹1,50,00,000'
    """
    return format_currency(amount, 'INR', locale='en_IN', format=u'¤#,##,##0', currency_digits=False)


# Legacy formatting functions (commented out but available for reference)
# def format_inr_legacy(amount):
#     """
#     Legacy Indian Rupee formatting function.
#     
#     This function manually implements Indian number system formatting.
#     It's kept for reference but the Babel-based format_inr() is preferred.
#     """
#     s = f"{amount:,.2f}"
#     parts = s.split(".")
#     rupees = parts[0]
#     decimal = parts[1]
# 
#     # Convert to Indian number system
#     if len(rupees) > 3:
#         rupees = rupees[:-3][::-1]
#         rupees = ",".join([rupees[i:i+2] for i in range(0, len(rupees), 2)])[::-1] + "," + s[-6:-3]
#     return f"₹{rupees}.{decimal}"
# 
# def format_inr_no_paise(amount):
#     """Format amount without decimal places."""
#     return format_inr(round(amount)).split('.')[0]


def format_indian_currency(amount):
    """
    Format amount in Indian currency style (₹xx,xx,xx,xxx)
    
    Args:
        amount (float/int): Amount to format
        
    Returns:
        str: Formatted amount in Indian style
        
    Example:
        >>> format_indian_currency(1234567)
        '₹12,34,567'
        >>> format_indian_currency(1234567890)
        '₹1,23,45,67,890'
    """
    if amount is None:
        return "₹0"
    
    # Convert to integer if it's a whole number
    if isinstance(amount, float) and amount.is_integer():
        amount = int(amount)
    
    # Handle negative numbers
    is_negative = amount < 0
    amount = abs(amount)
    
    # Convert to string and split by decimal point
    amount_str = str(amount)
    if '.' in amount_str:
        integer_part, decimal_part = amount_str.split('.')
    else:
        integer_part, decimal_part = amount_str, ""
    
    # Add commas in Indian style (every 2 digits from right, except first 3)
    if len(integer_part) <= 3:
        formatted_integer = integer_part
    else:
        # First group of 3 digits from right
        first_group = integer_part[-3:]
        # Remaining digits
        remaining = integer_part[:-3]
        
        # Handle remaining digits in groups of 2 from right to left
        if len(remaining) == 1:
            formatted_remaining = remaining
        elif len(remaining) == 2:
            formatted_remaining = remaining
        else:
            # For more than 2 digits, group them properly
            formatted_remaining = ""
            for i in range(len(remaining)):
                if i > 0 and (len(remaining) - i) % 2 == 0:
                    formatted_remaining += ","
                formatted_remaining += remaining[i]
        
        if formatted_remaining:
            formatted_integer = formatted_remaining + "," + first_group
        else:
            formatted_integer = first_group
    
    # Add decimal part if exists
    if decimal_part:
        result = f"₹{formatted_integer}.{decimal_part}"
    else:
        result = f"₹{formatted_integer}"
    
    # Add negative sign if needed
    if is_negative:
        result = "-" + result
    
    return result


def test_indian_formatting():
    """Test function to verify Indian currency formatting"""
    test_cases = [
        (1234567, "₹12,34,567"),
        (1234567890, "₹1,23,45,67,890"),
        (123456789, "₹12,34,56,789"),
        (12345678, "₹1,23,45,678"),
        (1234567.89, "₹12,34,567.89"),
        (1234567890.12, "₹1,23,45,67,890.12"),
        (1000, "₹1,000"),
        (100, "₹100"),
        (10, "₹10"),
        (1, "₹1"),
        (0, "₹0"),
        (None, "₹0")
    ]
    
    print("Testing Indian Currency Formatting:")
    for amount, expected in test_cases:
        result = format_indian_currency(amount)
        status = "✅" if result == expected else "❌"
        print(f"{status} {amount} -> {result} (expected: {expected})")

if __name__ == "__main__":
    test_indian_formatting()