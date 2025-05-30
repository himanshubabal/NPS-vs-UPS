import pandas as pd
import numpy as np
import re
import os

import pprint

from itertools import accumulate
from helper_functions import *


def get_basic_pay(level, year, pay_matrix_df):
    """
    Fetch basic pay for given pay level and year (0-based index).
    Uses PAY_MATRIX from 7th_CPC_filled.csv.
    
    :param level: int or str (e.g., 13, '13A')
    :param year: int (starts from 1)
    :return: int (basic pay)
    """
    level_str = str(level)
    
    # Validation
    if level_str not in pay_matrix_df.columns:
        raise ValueError(f"Level {level} not found in pay matrix.")

    if not (1 <= year <= len(pay_matrix_df)):
        raise ValueError(f"Year {year} is out of range (must be 1 to {len(pay_matrix_df)}).")
    
    # If at the last basic pay of a given level
    max_steps = pay_matrix_df[level_str].last_valid_index() + 1  # since .iloc is 0-based
    max_basic_pay = pay_matrix_df[level_str].iloc[max_steps - 1]

    # At the last step? No pay change, but year can increment
    if year >= max_steps:
        return max_basic_pay

    # else, return the value reading it from given pay commission df
    return int(pay_matrix_df[level_str].iloc[year - 1])


def get_level_year_from_basic_pay(basic_pay, pay_matrix_df):
    """
    Given a basic pay, find the highest level and least year it appears at.

    :param basic_pay: int
    :return: (level, year) tuple
    """
    # Storing found matches here
    found_matches = []

    for level in pay_matrix_df.columns:
        for i, value in enumerate(pay_matrix_df[level]):
            if value == basic_pay:
                year = i + 1  # convert 0-based index to 1-based year
                found_matches.append((str(level), year))

    if not found_matches:
        # raise ValueError(f"Basic pay ₹{basic_pay} not found in any level.")
        return (0, 0)

    # Sort: highest level first, then lowest year
    found_matches.sort(key=lambda x: (float(x[0].replace('A', '.5')) if 'A' in x[0] else float(x[0]), -x[1]), reverse=True)

    best_match = found_matches[0]
    return best_match


def annual_increment(current_level, year, pay_matrix_df):
    """
    Increment pay by one row within the same level. If already at max pay, stay at same amount,
    but increase year by 1.

    :param current_level: int or str
    :param year: int (1-based)
    :param basic_pay: int
    :return: (level, new_year, new_basic_pay)
    """
    level_str = str(current_level)

    if level_str not in pay_matrix_df.columns:
        raise ValueError(f"Invalid level: {current_level}")
    
    # Since some levels have fewer steps (e.g., Level 13A might have only 18 stages, while Level 1 might have 40).
    #   Thus using 'max_steps', instead of using len(_PAY_MATRIX_DF) (which gives total number of rows in the DataFrame, 
    #   regardless of whether that level column has values)
    max_steps = pay_matrix_df[level_str].last_valid_index() + 1  # since .iloc is 0-based
    max_basic_pay = pay_matrix_df[level_str].iloc[max_steps - 1]

    # print('Level: ' + level_str + ', Max Steps: ' + str(max_steps))

    # VALIDATION --> check that given basic pay corrensponds to the given pay_level & year
    # If given basic pay is the max_basic_pay, do not validate
    # if basic_pay != max_basic_pay:
    #     expected_basic = _PAY_MATRIX_DF[level_str].iloc[year - 1]
    #     if basic_pay != expected_basic:
    #         raise ValueError(
    #             f"Mismatch: expected ₹{expected_basic} at Level {level_str}, Year {year}, not ₹{basic_pay}"
    #         )

    # At the last step? No pay change, but year can increment
    if year >= max_steps:
        return (level_str, year + 1, int(max_basic_pay))

    next_basic = int(pay_matrix_df[level_str].iloc[year])  # year is 1-based, so index = year
    return (level_str, year + 1, next_basic)


def promote_employee(current_level, year, pay_matrix_df, is_ias=False):
    """
    Promote employee based on rules:
    - Validate current position.
    - Step down in same level.
    - Move to next level (skip 13A and 16 if IAS).
    - Find pay ≥ stepped_pay, then:
        * if IAS and level 10–12, go 2 rows further down.
    
    :param current_level: int or str
    :param year: int (1-based)
    :param basic_pay: int
    :param is_ias: bool
    :return: tuple (new_level, new_year, new_basic)
    """
    levels = list(pay_matrix_df.columns)
    current_level_str = str(current_level)

    # Validating -> if 'Level' is valid
    if current_level_str not in levels:
        raise ValueError(f"Level {current_level} not found.")
    # Validating -> if 'Year' is valid
    if not (1 <= year < len(pay_matrix_df)):
        raise ValueError(f"Year {year} must be between 1 and {len(pay_matrix_df) - 1}.")

    # Step 1: Move one cell down in same level
    stepped_pay = pay_matrix_df[current_level_str].iloc[year]  # year is 1-based, so year = index
    # For cases when current basic is the maximum basic pay in that column, keep basic same, just inc year
    max_basic_pay = pay_matrix_df[current_level_str].dropna().max()
    if pd.isna(stepped_pay):
        stepped_pay = max_basic_pay

    # Step 2: identify next level
    curr_index = levels.index(current_level_str)
    
    # IAS case: skip certain levels, and directly go to next-next level
    levels_to_skip = ['13A', '16']
    # Checking if we are already on last level, if not than only move forward
    if curr_index + 1 < len(levels):
        # If IAS, and If next level is to be skipped
        if is_ias and levels[curr_index + 1] in levels_to_skip:
            next_level_index = curr_index + 2
        # If next level need not be skipped
        else:
            next_level_index = curr_index + 1
    else:
        next_level_index = curr_index + 1
    
    # Validating -> whether higher level even exists
    # If not, keep in the same (highest) level
    if next_level_index >= len(levels):
        next_level_index = len(levels) - 1

    # Step 2: Move to next level
    next_level = str(levels[next_level_index])
    next_column = pay_matrix_df[next_level]

    # Step 3: find first cell ≥ stepped pay
    match_index = None
    for i, val in enumerate(next_column):
        if val >= stepped_pay:
            match_index = i
            break

    # IAS Rule: if current level 10–12, go two steps further down (maxing out if needed)
    if is_ias and current_level_str in {'10', '11', '12'}:
        match_index = min(match_index + 2, len(next_column) - 1)

    # Fallback if none found
    if match_index is None:
        return (next_level, len(next_column), int(next_column.iloc[-1]))
    
    return (next_level, match_index + 1, int(next_column.iloc[match_index]))


def generate_next_pay_commission(present_pay_matrix_csv='7th_CPC.csv', 
                                 fitment_factor=None, percent_inc_salary=None, percent_last_DA=None, 
                                 default_fitment_factor=2):
    """
    Generate the next CPC Pay Matrix based on fitment factor or salary increment % and DA %.

    You must provide either:
      - fitment_factor
      - or both percent_inc_salary and percent_last_DA (as 0.25 or 25 or '25%')
      - If none of the three provided --> assume fitment_factor=2

    :param present_pay_matrix_csv: str — input CSV file name (e.g., '7th_CPC.csv')
    :param fitment_factor: float, optional
    :param percent_inc_salary: float, optional (e.g., 0.15 for 15%)
    :param percent_last_DA: float, optional (e.g., 0.50 for 50%)
    :return: DataFrame of next CPC Pay Matrix (also saved to CSV)
    """
    # def normalize_percent(value):
    #     """Convert percent input like 25 or '25%' to float (0.25)"""
    #     if isinstance(value, str) and value.endswith('%'):
    #         value = value.rstrip('%')
    #     return float(value) / 100 if float(value) > 1 else float(value)

    # Validation
    if fitment_factor is None:
        if percent_inc_salary is not None and percent_last_DA is not None:
            inc = normalize_percent(percent_inc_salary)
            da = normalize_percent(percent_last_DA)
            fitment_factor = round((1 + da) * (1 + inc), 2)
        else:
            fitment_factor = default_fitment_factor  # One of the inputs missing — fallback to default
            
    # Extract current CPC number from source filename
    match = re.search(r"(\d+)(?:st|nd|rd|th)_CPC", present_pay_matrix_csv)
    if not match:
        raise ValueError("Source filename must contain CPC name like '7th_CPC'")
    current_cpc = int(match.group(1))
    next_cpc = f"{current_cpc + 1}th_CPC"

    # Copy the input DataFrame to avoid modifying original
    present_pay_matrix_df = pd.read_csv(present_pay_matrix_csv)
    new_df = present_pay_matrix_df.copy()

    # Skip Headers (First Row & First Column)
    # FIRST ROW SKIP:
        # In a proper pandas.read_csv() call, the first row is already treated as headers by default.
        # So df.columns is already set from the first row. Therefore:
        # First row is not part of the data, it's already the column headers.
        # There's no need to skip it again in code.
    # FIRST COLUMN SKIP: 
    #   apply fitment only to numeric columns except first column
    value_columns = new_df.columns[1:]  # Skip first column (e.g., "Year")

    # Apply transformation to all numeric cells (excluding row labels/indices)
    for col in value_columns:
        # Skip non-numeric columns if any
        if not np.issubdtype(new_df[col].dtype, np.number):
            continue
        new_df[col] = new_df[col].apply(
            lambda x: int(round(x * fitment_factor / 100.0) * 100) if not pd.isna(x) else np.nan
        ).astype("Int64")  # Ensures proper nullable integer type

    # Save to CSV
    output_filename = f"{next_cpc}_fitment_factor_{fitment_factor}.csv"
    new_df.to_csv(output_filename, index=False)

    return new_df


# Career journey -> defined through given promotions (level/which prom, year of prom)
def career_progression(starting_level=10, starting_year_row_in_level=1, promotion_duration_array=[4, 5, 4, 1, 4, 7, 5, 3], 
                       present_pay_matrix_csv='7th_CPC.csv', early_retirement:bool = False,
                       dob='20/07/1999', doj='9/10/24', dor:str = None, is_ias=False,
                       pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066], fitment_factors=[2, 2, 2, 2, 2]):
    """
    Simulates career progression with annual increments and level promotions
    based on fixed number of years spent per level.

    :return: list of dicts for each service year with level, year-in-level, and pay
    """
    current_pay_matrix = load_csv_into_df(present_pay_matrix_csv)
    
    # -------- V A L I D A T I O N S --------
    # Validation -- #fitment factors == #pay commissions
    if fitment_factors is None:
        # Use default fitment factor = 2 if none provided
        fitment_factors = [2] * len(pay_commission_implement_years)
    else:
        if len(fitment_factors) != len(pay_commission_implement_years):
            raise ValueError("Number of fitment factors must match number of pay commission implementation years.")
    
    # Validate Present Level
    levels = list(current_pay_matrix.columns)
    if str(starting_level) not in levels:
        raise ValueError(f"Invalid pay level: {str(starting_level)}")
    
    # Calculate max number of possible promotions
    current_index = levels.index(str(starting_level))
    if is_ias and '13A' in levels and str(starting_level) == '13':
        max_promotions = len(levels) - current_index - 2
    else:
        max_promotions = len(levels) - current_index - 1
    
    # Validate if promotion_years_array has more no of promotions than possible
    if len(promotion_duration_array) > max_promotions:
        raise ValueError(
            f"Too many promotions requested: only {max_promotions} promotions possible from Level {str(starting_level)}, "
            f"but got {len(promotion_duration_array)} promotion steps."
        )
    if early_retirement and dor is None:
        raise ValueError('If retiring early, must provide Date of Retirement')

    # ----------- M A I N ---- L O G I C -----------
    # Extracting Year in which joined service from Date of Joining of Service, and year of retirement
    service_joining_year, service_joining_month = parse_date(doj).year, parse_date(doj).month
    if early_retirement:
        retirement_year, retirement_month = parse_date(dor).year, parse_date(dor).month
    else:
        retirement_year, retirement_month = get_retirement_date(dob).year, get_retirement_date(dob).month
    # Years in which next promotion is due - cumulatively add promotion durations to service joining year
    promotion_due_years_array = list(accumulate(promotion_duration_array, initial=service_joining_year))[1:]
    # If joined after 1st July, start counting from next year onwards, else count half year
    service_joining_year += 0.5 if service_joining_month > 6 else 0
    # If retirement after 1st July, additional increment applicable, thus count additional half year
    retirement_year += 0.5 if retirement_month > 6 else 0
    # Max years to serve --> loop will run for this many years
    max_service_years = retirement_year - service_joining_year
    
    # Starting pay level, etc  --> updated after each loop
    pay_level = str(starting_level)
    year_row_in_current_pay_level = starting_year_row_in_level
    basic_pay = current_pay_matrix[pay_level].iloc[year_row_in_current_pay_level - 1]       # since 1st row is taken as label (in 'df') 

    # Data to be updated in each loop
    promotion_yr_array_index, pay_commission_index = 0, 0                                   # Tracks index of arrays
    current_service_duration = 0                                                            # Tracks years spent in service
    present_pay_comm_no = extract_cpc_no_from_filename(present_pay_matrix_csv)
    
    # The main object, returned at the end
    progression = []
    # so that these variables can be used in the loop, and changing key name can be done in one place
    key_level, key_yr_row_in_level, key_basic_pay = 'Level', 'Year Row in Level', 'Basic Pay'
    key_year, key_years_of_service = 'Year', 'Years of Service'

    # -------------- L O O P --------------
    while current_service_duration <= max_service_years:
        # Initialise dictionary with default values 
        half_year_service_details = {}
        # auto updated by functions, no need to manually update (used in case where service duration < 6 months)
        half_year_service_details[key_level] = pay_level
        half_year_service_details[key_yr_row_in_level] = year_row_in_current_pay_level
        half_year_service_details[key_basic_pay] = int(basic_pay)

        # Tracks current year (such as 2024, 2024.5, 2025, 2025.5, etc)
        year = service_joining_year + current_service_duration

        # LOGIC:
        # Increment -- only in middle of year -- ie. year ends with x.5
        # Promotion -- only when year ends -- ie. year ends with x.0
        # Pay Comm -- only when year ends -- only in those years applicable

        # Increment --> only during year mid [1st July -> year ending with x.5]
        if year % 1 == 0.5 and current_service_duration >=0.5:
            # Increment function applies
            pay_level, year_row_in_current_pay_level, basic_pay = annual_increment(pay_level, year_row_in_current_pay_level, pay_matrix_df=current_pay_matrix)
            # Add variables in dictionary after increment
            half_year_service_details[key_level] = pay_level
            half_year_service_details[key_yr_row_in_level] = year_row_in_current_pay_level
            half_year_service_details[key_basic_pay] = int(basic_pay)

        # Promotion and Pay Commission --> only during year end [1st Jan -> year ending with x.0]
        if year % 1 != 0.5:
            # Pay Commission --> only in the years it is implemented [given in pay_commission_implement_years]
            # Applied before Promotion, so that updated pay commission is used in the promotion
            if year == pay_commission_implement_years[pay_commission_index] and pay_commission_index < len(pay_commission_implement_years):
                # Variables to be used here
                fit_factor = fitment_factors[pay_commission_index]
                next_pay_comm_no = present_pay_comm_no + 1
                next_pay_comm_fileName = f"{next_pay_comm_no}th_CPC_fitment_factor_{fit_factor}.csv"

                # If csv exists, load it, if not, prepare it & load
                if os.path.exists(next_pay_comm_fileName):
                    current_pay_matrix = load_csv_into_df(next_pay_comm_fileName)
                else:
                    current_pay_matrix = generate_next_pay_commission(present_pay_matrix_csv=present_pay_matrix_csv, fitment_factor=fit_factor)
                
                # Updating new basic pay according to the new pay commission
                basic_pay = get_basic_pay(pay_level, year_row_in_current_pay_level, current_pay_matrix)
                # Udating loop variables for when the next time pay commission is applicable
                present_pay_matrix_csv = next_pay_comm_fileName
                pay_commission_index += 1
                present_pay_comm_no += 1    
            
            # Promotion --> apply only if further promotions exisis AND only in those years it is due [calc in promotion_due_years_array]
            if promotion_yr_array_index < len(promotion_duration_array):                # Checking if further promotions are available
                if year == promotion_due_years_array[promotion_yr_array_index]:         # Only in the years promotion is due
                    # Promotion function applies
                    pay_level, year_row_in_current_pay_level, basic_pay = promote_employee(pay_level, year_row_in_current_pay_level, pay_matrix_df=current_pay_matrix, is_ias=is_ias)
                    # Udating loop variables for when the next time promotion is due
                    promotion_yr_array_index += 1
            
            # since the variables (pay_level, year_row, basic_pay) can be updated by both Pay Comn and Promotion, keeping it after those blocks
            half_year_service_details[key_level] = pay_level
            half_year_service_details[key_yr_row_in_level] = year_row_in_current_pay_level
            half_year_service_details[key_basic_pay] = int(basic_pay)
        
        # since the variables (year, service duration) are independent of increment, promotion & pay comm, keeping these outside those blocks
        half_year_service_details[key_years_of_service] = current_service_duration
        half_year_service_details[key_year] = year
        progression.append(half_year_service_details)
        # since loop is for six months, add 0.5 to service duration years
        current_service_duration += 0.5
    
    return progression


# --- Example Usage ---
if __name__ == "__main__":
    # progression = career_progression(starting_level=10, starting_year_in_level=1, promotion_duration_array=[4, 5, 4, 1, 4, 7, 5], 
    #                    present_pay_matrix_csv='7th_CPC.csv', dob='20/07/1999', doj='9/10/24', is_ias=True,
    #                    pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066], fitment_factors=[2, 2, 2, 2, 2])
    progression = career_progression(is_ias=True, early_retirement=True, dor='10/4/30') 

    pprint.pprint(progression)

