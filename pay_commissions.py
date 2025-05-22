import pandas as pd
import numpy as np
import re
import os

from helper_functions import *


def get_basic_pay(level=10, year=1, pay_matrix_csv='7th_CPC.csv'):
    """
    Fetch basic pay for given pay level and year (0-based index).
    Uses PAY_MATRIX from 7th_CPC_filled.csv.
    
    :param level: int or str (e.g., 13, '13A')
    :param year: int (starts from 1)
    :return: int (basic pay)
    """
    # Load the pay matrix CSV once and keep in memory
    _PAY_MATRIX_DF = pd.read_csv(pay_matrix_csv)

    # Convert column names to string for consistency
    _PAY_MATRIX_DF.columns = _PAY_MATRIX_DF.columns.map(str)

    level_str = str(level)
    
    if level_str not in _PAY_MATRIX_DF.columns:
        raise ValueError(f"Level {level} not found in pay matrix.")

    if not (1 <= year <= len(_PAY_MATRIX_DF)):
        raise ValueError(f"Year {year} is out of range (must be 1 to {len(_PAY_MATRIX_DF)}).")

    return int(_PAY_MATRIX_DF[level_str].iloc[year - 1])


def get_level_year_from_basic_pay(basic_pay, pay_matrix_csv='7th_CPC.csv'):
    """
    Given a basic pay, find the highest level and least year it appears at.

    :param basic_pay: int
    :return: (level, year) tuple
    """
     # Load the pay matrix CSV once and keep in memory
    _PAY_MATRIX_DF = pd.read_csv(pay_matrix_csv)

    # Convert column names to string for consistency
    _PAY_MATRIX_DF.columns = _PAY_MATRIX_DF.columns.map(str)

    # Storing found matches here
    found_matches = []

    for level in _PAY_MATRIX_DF.columns:
        for i, value in enumerate(_PAY_MATRIX_DF[level]):
            if value == basic_pay:
                year = i + 1  # convert 0-based index to 1-based year
                found_matches.append((str(level), year))

    if not found_matches:
        raise ValueError(f"Basic pay ₹{basic_pay} not found in any level.")

    # Sort: highest level first, then lowest year
    found_matches.sort(key=lambda x: (float(x[0].replace('A', '.5')) if 'A' in x[0] else float(x[0]), -x[1]), reverse=True)

    best_match = found_matches[0]
    return best_match


# def annual_increment(current_level, year, basic_pay, pay_matrix_csv='7th_CPC.csv'):
def annual_increment(current_level, year, pay_matrix_csv='7th_CPC.csv'):
    """
    Increment pay by one row within the same level. If already at max pay, stay at same amount,
    but increase year by 1.

    :param current_level: int or str
    :param year: int (1-based)
    :param basic_pay: int
    :return: (level, new_year, new_basic_pay)
    """
    # Load the pay matrix CSV once and keep in memory
    _PAY_MATRIX_DF = pd.read_csv(pay_matrix_csv)

    # Convert column names to string for consistency
    _PAY_MATRIX_DF.columns = _PAY_MATRIX_DF.columns.map(str)

    level_str = str(current_level)

    if level_str not in _PAY_MATRIX_DF.columns:
        raise ValueError(f"Invalid level: {current_level}")
    
    # Since some levels have fewer steps (e.g., Level 13A might have only 18 stages, while Level 1 might have 40).
    #   Thus using 'max_steps', instead of using len(_PAY_MATRIX_DF) (which gives total number of rows in the DataFrame, 
    #   regardless of whether that level column has values)
    max_steps = _PAY_MATRIX_DF[level_str].last_valid_index() + 1  # since .iloc is 0-based
    max_basic_pay = _PAY_MATRIX_DF[level_str].iloc[max_steps - 1]

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

    next_basic = int(_PAY_MATRIX_DF[level_str].iloc[year])  # year is 1-based, so index = year
    return (level_str, year + 1, next_basic)


# def promote_employee(current_level, year, basic_pay, pay_matrix_csv='7th_CPC.csv', is_ias=False):
def promote_employee(current_level, year, pay_matrix_csv='7th_CPC.csv', is_ias=False):
    """
    Promote employee based on rules:
    - Validate current position.
    - Step down in same level.
    - Move to next level (skip 13A if IAS from 13).
    - Find pay ≥ stepped_pay, then:
        * if IAS and level 10–12, go 2 rows further down.
    
    :param current_level: int or str
    :param year: int (1-based)
    :param basic_pay: int
    :param is_ias: bool
    :return: tuple (new_level, new_year, new_basic)
    """
    # Load the pay matrix CSV once and keep in memory
    _PAY_MATRIX_DF = pd.read_csv(pay_matrix_csv)

    # Convert column names to string for consistency
    _PAY_MATRIX_DF.columns = _PAY_MATRIX_DF.columns.map(str)


    levels = list(_PAY_MATRIX_DF.columns)
    current_level_str = str(current_level)

    # Validating -> if 'Level' is valid
    if current_level_str not in levels:
        raise ValueError(f"Level {current_level} not found.")

    # Validating -> if 'Year' is valid
    if not (1 <= year < len(_PAY_MATRIX_DF)):
        raise ValueError(f"Year {year} must be between 1 and {len(_PAY_MATRIX_DF) - 1}.")
    
    # Validating -> if 'Basic Pay' is valid (ie. this shall be the basic pay for the given level & year)
    # expected_basic = _PAY_MATRIX_DF[current_level_str].iloc[year - 1]
    # max_steps = _PAY_MATRIX_DF[current_level_str].last_valid_index() + 1
    # max_basic_pay = _PAY_MATRIX_DF[current_level_str].iloc[max_steps - 1]
    # # If present basic pay is the max of a level, skip this validation
    # if basic_pay != max_basic_pay:
    #     if basic_pay != expected_basic:
    #         raise ValueError(f"Mismatch: matrix has ₹{expected_basic} at Level {current_level}, Year {year}, not ₹{basic_pay}.")

    # Step 1: Move one cell down in same level
    stepped_pay = _PAY_MATRIX_DF[current_level_str].iloc[year]  # year is 1-based, so year = index
    # For cases when current basic is the maximum basic pay in that column, keep basic same, just inc year
    max_basic_pay = _PAY_MATRIX_DF[current_level_str].dropna().max()
    if pd.isna(stepped_pay):
        stepped_pay = max_basic_pay

    # Step 2: identify next level
    curr_index = levels.index(current_level_str)

    # IAS case: skip 13A if coming from 13
    if is_ias and current_level_str == '13':
        next_level_index = levels.index('14') if '14' in levels else curr_index + 2
    else:
        next_level_index = curr_index + 1
    
    # Validating -> whether higher level even exists
    if next_level_index >= len(levels):
        raise ValueError(f"No promotable level beyond {current_level_str}")

    # Step 2: Move to next level
    next_level = str(levels[next_level_index])
    next_column = _PAY_MATRIX_DF[next_level]

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
    def normalize_percent(value):
        """Convert percent input like 25 or '25%' to float (0.25)"""
        if isinstance(value, str) and value.endswith('%'):
            value = value.rstrip('%')
        return float(value) / 100 if float(value) > 1 else float(value)

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


# NEXT --> Career journey -> defined through given promotions (level/which prom, year of prom)
# ToDo --> max no of promotions --> verify max upto L18, from length of prom_array
# (Done) ToDo --> DoB, Retirement Year, only for service duration years
# (Done) ToDo --> implement Pay commissions also every 10 years starting from 2026, 36, 46, 56, 66, etc
def career_progression(present_level=10, present_year_in_level=1, promotion_years_array=[4, 5, 4, 1, 4, 7, 5, 3], 
                       pay_matrix_csv='7th_CPC.csv', dob='1/1/2000', doj='9/12/24', is_ias=False,
                       pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066], fitment_factors=[2, 2, 2, 2, 2]):
    """
    Simulates career progression with annual increments and level promotions
    based on fixed number of years spent per level.

    :param present_level: str or int — starting pay level
    :param present_year: int — current stage in the level
    :param promotion_years_array: list[int] — years to spend in each level before promotion
    :param service_joining_year: int — base service year (default 2024)
    :return: list of dicts for each service year with level, year-in-level, and pay
    """
    # Load the pay matrix CSV once and keep in memory
    current_pay_matrix = pd.read_csv(pay_matrix_csv)
    # Convert column names to string for consistency
    current_pay_matrix.columns = current_pay_matrix.columns.map(str)

    # Pay Commissions Validation
    if pay_commission_implement_years is None:
        pay_commission_implement_years = [2026, 2036, 2046, 2056, 2066]
    # Use default fitment factor = 2 if none provided
    if fitment_factors is None:
        fitment_factors = [2] * len(pay_commission_implement_years)
    else:
        if len(fitment_factors) != len(pay_commission_implement_years):
            raise ValueError("Number of fitment factors must match number of pay commission implementation years.")

    # Extracting Year in which joined service from Date of Joining of Service, and year of retirement
    service_joining_year = parse_date(doj).year
    retirement_year = get_retirement_date(dob).year
    max_service_years = retirement_year - service_joining_year

    # Present pay level, etc
    level = str(present_level) # 10
    year = present_year_in_level # 1
    progression = []

    # Validate Present Level
    levels = list(current_pay_matrix.columns)
    if level not in levels:
        raise ValueError(f"Invalid pay level: {level}")
    # Calculate max number of possible promotions
    current_index = levels.index(level)
    if is_ias and '13A' in levels and level == '13':
        max_promotions = len(levels) - current_index - 2  # skipping 13A
    else:
        max_promotions = len(levels) - current_index - 1
    # Check if promotion_years_array has more no of promotions than possible
    if len(promotion_years_array) > max_promotions:
        raise ValueError(
            f"Too many promotions requested: only {max_promotions} promotions possible from Level {level}, "
            f"but got {len(promotion_years_array)} promotion steps."
        )

    # Data to be updated in each loop
    basic_pay = current_pay_matrix[level].iloc[year - 1]
    current_service_year = 0
    level_index = 0  # Tracks position in promotion_years_array
    years_in_current_level = 0
    pay_commission_index = 0  # Index of pay_commission_implement_years
    present_pay_comm_no = extract_cpc_no_from_filename(pay_matrix_csv); # 7

    # FOR: Year -> 2026 (8th CPC year)
    while current_service_year <= max_service_years: # 2 < 37
        service_year = service_joining_year + current_service_year # 2026 = 2024 + 2

        # Record current state
        progression.append({
            "Years of Service": current_service_year + 1, # 3=2+1
            "Year": service_year, # 2026
            "Level": level, # 10
            "Year in Level": year, # 3=2+1
            "Basic Pay": basic_pay # 59500 ????????
        })

        years_in_current_level += 1 # 1
        current_service_year += 1 # 1

        # LOG
        # print(str(current_service_year) + ". " + "Year: " + str(service_year) + ", Level: " + str(level) + 
        #       ", Year in Current Level: " + str(years_in_current_level) + ", Basic Pay: " + str(basic_pay))

        # ----------------- PAY COMMISSION -----------------
        # Apply new pay commission if due nexy year - so that new pay matrix are used for next year
        # apply in 2025 (not in 2026)                                              2025==2026-1
        if pay_commission_index < len(pay_commission_implement_years) and service_year == pay_commission_implement_years[pay_commission_index]-1:
            fit_factor = fitment_factors[pay_commission_index]
            next_pay_comm_no = present_pay_comm_no + 1 # Eg. 8 = 7 + 1;  9 = 8 + 1
            next_pay_comm_fileName = f"{next_pay_comm_no}th_CPC_fitment_factor_{fit_factor}.csv"

            # L O G
            # print('.............................................P_A_Y  C_O_M_M_I_S_S_I_O_N......................................')
            # print('Pay Commission No: ' + str(next_pay_comm_no))
            # print('Fine Name: ' + next_pay_comm_fileName)

            # If csv exists, load it, if not, prepare it & load
            if os.path.exists(next_pay_comm_fileName):
                current_pay_matrix = pd.read_csv(next_pay_comm_fileName)
            else:
                current_pay_matrix = generate_next_pay_commission(present_pay_matrix_csv=pay_matrix_csv, fitment_factor=fit_factor)
            
            # Update related fields
            current_pay_matrix.columns = current_pay_matrix.columns.map(str)
            pay_matrix_csv = next_pay_comm_fileName
            pay_commission_index += 1 # 1=0+1
            present_pay_comm_no += 1 # 8=7+1
            

        # PROMOTION logic --> see if promotions available, and present year is equal to that in promtion yr array
        if level_index < len(promotion_years_array) and years_in_current_level == promotion_years_array[level_index]:
            # print('============ P R O M O T I O N ============')
            # level, year, basic_pay = promote_employee(level, year, basic_pay, pay_matrix_csv=pay_matrix_csv, is_ias=is_ias)
            level, year, basic_pay = promote_employee(level, year, pay_matrix_csv=pay_matrix_csv, is_ias=is_ias)
            # print(level, year, basic_pay)
            # Update variables
            years_in_current_level = 0
            level_index += 1
            continue  # skip increment on promotion year

        # Apply annual increment (whether in middle of level or after final promotion)
        try:
            # print('-------Applying----Increment------')
            # level, year, basic_pay = annual_increment(level, year, basic_pay, pay_matrix_csv=pay_matrix_csv)
            level, year, basic_pay = annual_increment(level, year, pay_matrix_csv=pay_matrix_csv)
            # print(level, year, basic_pay)
        except ValueError:
            break  # Likely maxed out pay
        
    return progression



# --- Example Usage ---
if __name__ == "__main__":
    # progression = career_progression()
    progression = career_progression(is_ias=True)

    for year in progression:
        print(year)

    # print(career_progression(is_ias=True))

    # date_str = "10-Apr-96"
    # print(f"Day: {parse_date(date_str).date}, Month: {parse_date(date_str).month}, Year: {parse_date(date_str).year}")

    # print(promote_employee(current_level='16', year=3, basic_pay=217900, pay_matrix_csv='7th_CPC.csv', is_ias=False))
    # print(promote_employee(current_level='16', year=4, basic_pay=224400, pay_matrix_csv='7th_CPC.csv', is_ias=False))
    # print(promote_employee(current_level='16', year=5, basic_pay=224400, pay_matrix_csv='7th_CPC.csv', is_ias=False))
    # print(promote_employee(current_level='16', year=6, basic_pay=224400, pay_matrix_csv='7th_CPC.csv', is_ias=False))
    
    
    
    # print(annual_increment(current_level=16, year=1, basic_pay=205400, pay_matrix_csv='7th_CPC.csv'))
    # print(annual_increment(current_level=16, year=2, basic_pay=211600, pay_matrix_csv='7th_CPC.csv'))
    # print(annual_increment(current_level=16, year=3, basic_pay=217900, pay_matrix_csv='7th_CPC.csv'))
    # print(annual_increment(current_level=16, year=4, basic_pay=224400, pay_matrix_csv='7th_CPC.csv'))
    # print(annual_increment(current_level=16, year=5, basic_pay=224400, pay_matrix_csv='7th_CPC.csv'))
    # print(annual_increment(current_level=16, year=6, basic_pay=224400, pay_matrix_csv='7th_CPC.csv'))
    # print(annual_increment(current_level=16, year=7, basic_pay=224400, pay_matrix_csv='7th_CPC.csv'))
    # print(annual_increment(current_level=16, year=8, basic_pay=224400, pay_matrix_csv='7th_CPC.csv'))
    # print(annual_increment(current_level=16, year=9, basic_pay=224400, pay_matrix_csv='7th_CPC.csv'))

    # print(get_basic_pay(10, 1))
    # print(get_basic_pay('11', 1))
    # print(get_level_year_from_basic_pay(56100))  # ➝ ('10', 1)
    # print(get_level_year_from_basic_pay(112400)) # ➝ ('12', 13)
    # print(get_level_year_from_basic_pay(250000)) # ➝ ('18', 1)
    # print(get_basic_pay('13A', 5)) # -> 147600
    # # print(promote_employee(10, 3, 59500))
    # # print(promote_employee('13A', 5, 147600))
    # # print(promote_employee('13A', 5, 152000))
    # # print(promote_employee('10', 5, 63100))
    # print(promote_employee(10, 5, 63100))
    # print(promote_employee(10, 5, 63100, is_ias=True))
    # print(annual_increment(10, 1, 56100))    # ➝ ('10', 2, 57800)
    # print(len(_PAY_MATRIX_DF))
    # print(annual_increment("13A", 18, 216600))  # ➝ ('13A', 19, 216600) — same pay, year increased


    # generate_next_pay_commission("7th_CPC.csv", percent_inc_salary=0.18, percent_last_DA=0.5)
    # generate_next_pay_commission(present_pay_matrix_csv="7th_CPC.csv", fitment_factor=1.86)
    # generate_next_pay_commission() --> will outout '8th_CPC_fitment_factor_2.csv'
    # generate_next_pay_commission(present_pay_matrix_csv="7th_CPC.csv")
    # generate_next_pay_commission(present_pay_matrix_csv="8th_CPC_fitment_factor_1.86.csv", percent_inc_salary=0.21, percent_last_DA=0.66)
    # generate_next_pay_commission(present_pay_matrix_csv="9th_CPC_fitment_factor_2.01.csv", percent_inc_salary=0.26, percent_last_DA=0.66)
    # generate_next_pay_commission(present_pay_matrix_csv="10th_CPC_fitment_factor_2.09.csv", percent_inc_salary=0.20, percent_last_DA=0.66)
