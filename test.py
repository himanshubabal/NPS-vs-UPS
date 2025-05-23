import pandas as pd
import numpy as np
import re
import os

from itertools import accumulate

from helper_functions import *
from pay_commissions import *

# Career journey -> defined through given promotions (level/which prom, year of prom)
def career_progression_new(starting_level=10, starting_year_in_level=1, promotion_duration_array=[4, 5, 4, 1, 4, 7, 5, 3], 
                       present_pay_matrix_csv='7th_CPC.csv', dob='20/07/1999', doj='9/10/24', is_ias=False,
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

    # ----------- M A I N ---- L O G I C -----------
    # Extracting Year in which joined service from Date of Joining of Service, and year of retirement
    service_joining_year, service_joining_month = parse_date_old(doj).year, parse_date_old(doj).month
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
    year_row_in_current_pay_level = starting_year_in_level
    basic_pay = current_pay_matrix[pay_level].iloc[year_row_in_current_pay_level - 1]       # since 1st row is taken as label (in 'df') 

    # Data to be updated in each loop
    promotion_yr_array_index, pay_commission_index = 0, 0                                   # Tracks index of arrays
    current_service_duration = 0                                                            # Tracks years spent in service
    present_pay_comm_no = extract_cpc_no_from_filename(present_pay_matrix_csv)
    
    # The main object, returned at the end
    progression = []
    # so that these variables can be used in the loop, and changing key name can be done in one place
    key_level, key_yr_row_in_level, key_basic_pay = 'Level', 'Year Row in Level', 'Basic Pay'
    key_year, key_years_of_service = 'Years of Service', 'Year'

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
            pay_level, year_row_in_current_pay_level, basic_pay = annual_increment(pay_level, year_row_in_current_pay_level, pay_matrix_df=present_pay_matrix_csv)
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
                basic_pay = get_basic_pay(pay_level, year_row_in_current_pay_level, next_pay_comm_fileName)
                # Udating loop variables for when the next time pay commission is applicable
                present_pay_matrix_csv = next_pay_comm_fileName
                pay_commission_index += 1
                present_pay_comm_no += 1    
            
            # Promotion --> apply only if further promotions exisis AND only in those years it is due [calc in promotion_due_years_array]
            if promotion_yr_array_index < len(promotion_duration_array):                # Checking if further promotions are available
                if year == promotion_due_years_array[promotion_yr_array_index]:         # Only in the years promotion is due
                    # Promotion function applies
                    pay_level, year_row_in_current_pay_level, basic_pay = promote_employee(pay_level, year_row_in_current_pay_level, pay_matrix_df=present_pay_matrix_csv, is_ias=is_ias)
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



# Career journey -> defined through given promotions (level/which prom, year of prom)
def career_progression_old(starting_level=10, starting_year_in_level=1, promotion_years_array=[4, 5, 4, 1, 4, 7, 5, 3], 
                       starting_pay_matrix_csv='7th_CPC.csv', dob='20/07/1996', doj='9/10/24', is_ias=False,
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
    current_pay_matrix = pd.read_csv(starting_pay_matrix_csv)
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
    service_joining_year = parse_date_old(doj).year
    service_joining_month = parse_date_old(doj).month
    # If joined after 1st July, start counting from next year onwards, else count half year
    service_joining_year += 1 if service_joining_month > 6 else 0.5
    retirement_year = get_retirement_date(dob).year  
    retirement_month = get_retirement_date(dob).month   
    # If retirement after 1st July, additional increment applicable
    retirement_year += 0.5 if retirement_month > 6 else 0 
    max_service_years = retirement_year - service_joining_year

    # Present pay level, etc
    level = str(starting_level)
    year = starting_year_in_level
    progression = []

    # Validate Present Level
    levels = list(current_pay_matrix.columns)
    if level not in levels:
        raise ValueError(f"Invalid pay level: {level}")
    # Calculate max number of possible promotions
    current_index = levels.index(level)
    if is_ias and '13A' in levels and level == '13':
        max_promotions = len(levels) - current_index - 2
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
    level_index = 0                     # Tracks position in promotion_years_array
    years_in_current_level = 0
    pay_commission_index = 0            # Index of pay_commission_implement_years
    present_pay_comm_no = extract_cpc_no_from_filename(starting_pay_matrix_csv); # 7

    # FOR: Year -> 2026 (8th CPC year)
    while current_service_year <= max_service_years:
        # If joined before 31st Dec, count for increment
        # Join month > 7 (joined after july) --> initial half of that year -- no service
        # Join month b/w 1 & 6 (joined between Jan to June) --> initial half -- service, but no increment that year

        service_year = service_joining_year + current_service_year
        current_service_year += 0.5
        years_in_current_level += 1 if service_year % 1 == 0.5 else 0

        # Record current state
        progression.append({
            "Years of Service": current_service_year,
            "Year": service_year,
            "Level": level,
            "Year in Level": year,
            "Basic Pay": basic_pay
        })

        # ----------------- PAY COMMISSION -----------------
        # Apply new pay commission if due nexy year - so that new pay matrix are used for next year
        # apply in 2025 (not in 2026)                                              2025==2026-1
        if pay_commission_index < len(pay_commission_implement_years) and service_year == pay_commission_implement_years[pay_commission_index]-1:
            fit_factor = fitment_factors[pay_commission_index]
            next_pay_comm_no = present_pay_comm_no + 1 # Eg. 8 = 7 + 1;  9 = 8 + 1
            next_pay_comm_fileName = f"{next_pay_comm_no}th_CPC_fitment_factor_{fit_factor}.csv"

            # If csv exists, load it, if not, prepare it & load
            if os.path.exists(next_pay_comm_fileName):
                current_pay_matrix = pd.read_csv(next_pay_comm_fileName)
            else:
                current_pay_matrix = generate_next_pay_commission(present_pay_matrix_csv=starting_pay_matrix_csv, fitment_factor=fit_factor)
            
            # Update related fields
            current_pay_matrix.columns = current_pay_matrix.columns.map(str)
            starting_pay_matrix_csv = next_pay_comm_fileName
            pay_commission_index += 1 # 1=0+1
            present_pay_comm_no += 1 # 8=7+1
            

        # PROMOTION logic --> see if promotions available, and present year is equal to that in promtion yr array
        if level_index < len(promotion_years_array) and years_in_current_level == promotion_years_array[level_index]:
            # print('============ P R O M O T I O N ============')
            # level, year, basic_pay = promote_employee(level, year, basic_pay, pay_matrix_csv=pay_matrix_csv, is_ias=is_ias)
            level, year, basic_pay = promote_employee(level, year, pay_matrix_df=starting_pay_matrix_csv, is_ias=is_ias)
            # print(level, year, basic_pay)
            # Update variables
            years_in_current_level = 0
            level_index += 1
            continue  # skip increment on promotion year (continue ends loop here, next part of code is not run in this case)
        
        # Increment -- > applicable only in July each year (ie. mid year), 
        #                and must have atleast 6 months of service till 1st July that year
        # print(current_service_year)
        # if service_year % 1 == 0.5 and current_service_year >= 0.5:
        if service_year % 1 == 0.5:
            print(f'Increment Applicable => Year: {service_year}, Service Duration: {current_service_year}')
            print(f'Previous Level-Year: {year}, Basic: {basic_pay}')
            level, year, basic_pay = annual_increment(level, year, pay_matrix_df=starting_pay_matrix_csv)
            print(f'Next Level-Year: {year}, Basic: {basic_pay}')

    return progression

# --- Example Usage ---
if __name__ == "__main__":
    progression = career_progression_new(starting_level=10, starting_year_in_level=1, promotion_duration_array=[4, 5, 4, 1, 4, 7, 5, 3], 
                       present_pay_matrix_csv='7th_CPC.csv', dob='20/05/2001', doj='9/12/24', is_ias=True,
                       pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066], fitment_factors=[2, 2, 2, 2, 2])

    # progression = career_progression_new()

    for year in progression:
        print(year)


