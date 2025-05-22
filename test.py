import pandas as pd
import numpy as np
import re
import os

from helper_functions import *
from pay_commissions import *

# Career journey -> defined through given promotions (level/which prom, year of prom)
def career_progression(starting_level=10, starting_year_in_level=1, promotion_years_array=[4, 5, 4, 1, 4, 7, 5, 3], 
                       present_pay_matrix_csv='7th_CPC.csv', dob='20/07/1969', doj='9/10/24', is_ias=False,
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
    if len(promotion_years_array) > max_promotions:
        raise ValueError(
            f"Too many promotions requested: only {max_promotions} promotions possible from Level {str(starting_level)}, "
            f"but got {len(promotion_years_array)} promotion steps."
        )

    # Extracting Year in which joined service from Date of Joining of Service, and year of retirement           # For '20/09/1966' & '9/10/24'
    service_joining_year, service_joining_month = parse_date(doj).year, parse_date(doj).month                   # 9, 2024
    retirement_year, retirement_month = get_retirement_date(dob).year, get_retirement_date(dob).month           # 7, 2026
    # If joined after 1st July, start counting from next year onwards, else count half year
    # If retirement after 1st July, additional increment applicable, thus count additional half year
    service_joining_year += 1 if service_joining_month > 6 else 0.5                                             # since 9>6: 2025 (2024+1)
    retirement_year += 0.5 if retirement_month > 6 else 0                                                       # since 7>6: 2026.5 (2026+0.5)
    max_service_years = retirement_year - service_joining_year                                                  # 2026.5-2025.0 = 1.5

    # Starting pay level, etc  --> also updated after each loop
    pay_level = str(starting_level)                                                             # 10 (Level)
    year_in_pay_level = starting_year_in_level                                                  # 1  (Year Row)
    progression = []

    # Data to be updated in each loop
    basic_pay = current_pay_matrix[pay_level].iloc[year_in_pay_level - 1]                       # since in df - 1st row is taken as label
    current_service_year = 0            # Tracks total years spent in service                   # 0
    current_service_duration = 0
    level_index = 0                     # Tracks position in promotion_years_array              # 0 
    years_in_current_pay_level = 0      # Tracks years spent in current pay level               # 0 
    pay_commission_index = 0            # Index of pay_commission_implement_years               # 0
    present_pay_comm_no = extract_cpc_no_from_filename(present_pay_matrix_csv);                 # 7

    # FOR: Year -> 2026 (8th CPC year)
    # while current_service_year <= max_service_years:                                            # 0 < 1.5
    while current_service_duration <= max_service_years:
        # service_tenure = {}


        # Increment -- only in middle of year -- ie. year ends with x.5
        # Promotion -- only when year ends -- ie. year ends with x.0
        # Pay Comm -- only when year ends -- only in those years applicable

        if year % 1 == 0.5:
            # Increment
            None
        
        if year % 1 != 0.5:
            # Pay Comm & Promotion

            # PAY COMM
            if year == pay_commission_implement_years[pay_commission_index]:
                pay_commission_index += 1
            
            # PROMOTION
            None
        
        # Put in dict

        # inc 'year' and other indices




        year = service_joining_year + current_service_year                                      # 2025 (2025+0)
        current_service_year += 0.5                                                             # 0.5
        years_in_current_pay_level += 1 if year % 1 == 0.5 else 0                               # 1 (1+0, since 2025%1 =/= 0.5)

        # Record current state
        progression.append({
            "Years of Service": current_service_year,
            "Year": year,
            "Level": pay_level,
            "Year in Level": year_in_pay_level,
            "Basic Pay": int(basic_pay)
        })

        print(f'"Years of Service": {current_service_year}, "Year": {year}, "Level": {pay_level}, "Year in Level": {year_in_pay_level}, "Basic Pay": {basic_pay}')

        # ----------------- PAY COMMISSION -----------------
        # Prepare new pay commission if due next year - so that new pay matrix are used for next year
        # apply in 2025 (not in 2026)                                      2025==2026-1
        if (pay_commission_index < len(pay_commission_implement_years) 
            and year == pay_commission_implement_years[pay_commission_index]-0.5):
            fit_factor = fitment_factors[pay_commission_index]
            next_pay_comm_no = present_pay_comm_no + 1                                                  # Eg. 8 = 7 + 1;  9 = 8 + 1
            next_pay_comm_fileName = f"{next_pay_comm_no}th_CPC_fitment_factor_{fit_factor}.csv"

            # If csv exists, load it, if not, prepare it & load
            if os.path.exists(next_pay_comm_fileName):
                current_pay_matrix = load_csv_into_df(next_pay_comm_fileName)
            else:
                current_pay_matrix = generate_next_pay_commission(present_pay_matrix_csv=present_pay_matrix_csv, fitment_factor=fit_factor)
            
            # Update related fields
            # current_pay_matrix.columns = current_pay_matrix.columns.map(str)
            present_pay_matrix_csv = next_pay_comm_fileName
            pay_commission_index += 1                                                                   # 1=0+1
            present_pay_comm_no += 1                                                                    # 8=7+1
            print ('--------------------------------------------------')
            print ('----------------- PAY COMMISSION -----------------')
            print ('--------------------------------------------------')
            

        # PROMOTION logic --> see if promotions available, and present year is equal to that in promtion yr array
        if (level_index < len(promotion_years_array) 
            and years_in_current_pay_level == promotion_years_array[level_index]
            and year % 1 == 0.5):
            print('============ P R O M O T I O N ============')
            # level, year, basic_pay = promote_employee(level, year, basic_pay, pay_matrix_csv=pay_matrix_csv, is_ias=is_ias)
            pay_level, year_in_pay_level, basic_pay = promote_employee(pay_level, year_in_pay_level, pay_matrix_csv=present_pay_matrix_csv, is_ias=is_ias)
            # print(level, year, basic_pay)
            # Update variables
            years_in_current_pay_level = 0
            level_index += 1
            continue  # skip increment on promotion year (continue ends loop here, next part of code is not run in this case)

        # Increment -- > applicable only in July each year (ie. mid year), 
        #                and must have atleast 6 months of service till 1st July that year
        # print(current_service_year)
        # if service_year % 1 == 0.5 and current_service_year >= 0.5:
        # if year % 1 == 0.5:                                                                     # 2025
        if year % 1 != 0.5:                                                                     # 2025
            print(f'---- Increment Applicable => Year: {year}, Service Duration: {current_service_year}')
            print(f'Previous Level-Year: {year_in_pay_level}, Basic: {basic_pay}')
            pay_level, year_in_pay_level, basic_pay = annual_increment(pay_level, year_in_pay_level, pay_matrix_csv=present_pay_matrix_csv)
            print(f'Next Level-Year: {year_in_pay_level}, Basic: {basic_pay}')

        print('- - - - - - - - - - - - - - - - -')
        print('\n')

     # FOR: Year -> 2026 (8th CPC year)
    
    return progression

    while current_service_year <= max_service_years:                                            # 0 < 1.5
        # If joined before 31st Dec, count for increment
        # Join month > 7 (joined after july) --> initial half of that year -- no service
        # Join month b/w 1 & 6 (joined between Jan to June) --> initial half -- service, but no increment that year

        year = service_joining_year + current_service_year                                      # 2025 (2025+0)
        current_service_year += 0.5                                                             # 0.5
        years_in_current_pay_level += 1 if year % 1 == 0.5 else 0                               # 1 (1+0, since 2025%1 =/= 0.5)

        # Record current state
        progression.append({
            "Years of Service": current_service_year,
            "Year": year,
            "Level": pay_level,
            "Year in Level": year_in_pay_level,
            "Basic Pay": basic_pay
        })

        print(f'"Years of Service": {current_service_year}, "Year": {year}, "Level": {pay_level}, "Year in Level": {year_in_pay_level}, "Basic Pay": {basic_pay}')

        # ----------------- PAY COMMISSION -----------------
        # Prepare new pay commission if due next year - so that new pay matrix are used for next year
        # apply in 2025 (not in 2026)                                      2025==2026-1
        if (pay_commission_index < len(pay_commission_implement_years) 
            and year == pay_commission_implement_years[pay_commission_index]):
            fit_factor = fitment_factors[pay_commission_index]
            next_pay_comm_no = present_pay_comm_no + 1                                                  # Eg. 8 = 7 + 1;  9 = 8 + 1
            next_pay_comm_fileName = f"{next_pay_comm_no}th_CPC_fitment_factor_{fit_factor}.csv"

            # If csv exists, load it, if not, prepare it & load
            if os.path.exists(next_pay_comm_fileName):
                current_pay_matrix = load_csv_into_df(next_pay_comm_fileName)
            else:
                current_pay_matrix = generate_next_pay_commission(present_pay_matrix_csv=present_pay_matrix_csv, fitment_factor=fit_factor)
            
            # Update related fields
            # current_pay_matrix.columns = current_pay_matrix.columns.map(str)
            present_pay_matrix_csv = next_pay_comm_fileName
            pay_commission_index += 1                                                                   # 1=0+1
            present_pay_comm_no += 1                                                                    # 8=7+1
            print ('--------------------------------------------------')
            print ('----------------- PAY COMMISSION -----------------')
            print ('--------------------------------------------------')
            

        # PROMOTION logic --> see if promotions available, and present year is equal to that in promtion yr array
        if (level_index < len(promotion_years_array) 
            and years_in_current_pay_level == promotion_years_array[level_index]): #and year % 1 == 0.5:
            print('============ P R O M O T I O N ============')
            # level, year, basic_pay = promote_employee(level, year, basic_pay, pay_matrix_csv=pay_matrix_csv, is_ias=is_ias)
            pay_level, year_in_pay_level, basic_pay = promote_employee(pay_level, year_in_pay_level, pay_matrix_csv=present_pay_matrix_csv, is_ias=is_ias)
            # print(level, year, basic_pay)
            # Update variables
            years_in_current_pay_level = 0
            level_index += 1
            continue  # skip increment on promotion year (continue ends loop here, next part of code is not run in this case)

        # Increment -- > applicable only in July each year (ie. mid year), 
        #                and must have atleast 6 months of service till 1st July that year
        # print(current_service_year)
        # if service_year % 1 == 0.5 and current_service_year >= 0.5:
        # if year % 1 == 0.5:                                                                     # 2025
        if year % 1 != 0.5:                                                                     # 2025
            print(f'---- Increment Applicable => Year: {year}, Service Duration: {current_service_year}')
            print(f'Previous Level-Year: {year_in_pay_level}, Basic: {basic_pay}')
            pay_level, year_in_pay_level, basic_pay = annual_increment(pay_level, year_in_pay_level, pay_matrix_csv=present_pay_matrix_csv)
            print(f'Next Level-Year: {year_in_pay_level}, Basic: {basic_pay}')

        print('--------------------------------')

    # return progression



# --- Example Usage ---
if __name__ == "__main__":
    # progression = career_progression(starting_level=10, starting_year_in_level=1, promotion_years_array=[4, 5, 4, 1, 4, 7, 5, 3], 
    #                    starting_pay_matrix_csv='7th_CPC.csv', dob='20/05/1996', doj='9/12/24', is_ias=False,
    #                    pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066], fitment_factors=[2, 2, 2, 2, 2])

    print("\n\n\n\n")

    progression = career_progression()

    print("\n\n")
    for year in progression:
        print(year)


