from pay_commissions import *
from rates import *
from helper_functions import *

import pprint

from typing import Union

def get_salary_matrix(starting_level:Union[int,str] = 10, starting_year_in_level:int = 1, promotion_duration_array:list[int] = [4, 5, 4, 1, 4, 7, 5, 3], 
                       present_pay_matrix_csv:str = '7th_CPC.csv', dob:str = '20/5/1996', doj:str = '9/12/24', is_ias:bool = False,
                       pay_commission_implement_years:list[int] = [2026, 2036, 2046, 2056, 2066], fitment_factors:list[int] = [2, 2, 2, 2, 2],
                       initial_inflation_rate:float = 7.0, final_inflation_rate:float = 3.0):
    
    # Get dates parsed in easy to use format
    joining_date_parsed = parse_date(doj)
    retire_date_parsed = get_retirement_date(dob)

    # Changing joining_year according to joining_date's month
    # If joined before 1st July, add nothing;    # If joined after 1st July, add 0.5
    joining_year = joining_date_parsed.year + 0.5 if joining_date_parsed.month > 7 else joining_date_parsed.year
    duration_years = retire_date_parsed.year - joining_date_parsed.year

    # Get Career Progression
    career_progression_matrix = career_progression(starting_level=starting_level, starting_year_in_level=starting_year_in_level, 
                                                   promotion_duration_array=promotion_duration_array, present_pay_matrix_csv=present_pay_matrix_csv, 
                                                   dob=dob, doj=doj, is_ias=is_ias, pay_commission_implement_years=pay_commission_implement_years, 
                                                   fitment_factors=fitment_factors)

    # Get DA
    da_matrix = get_DA_matrix(initial_inflation_rate=initial_inflation_rate, final_inflation_rate=final_inflation_rate, 
                              duration_years=duration_years, joining_year=joining_year, pay_commission_implement_years=pay_commission_implement_years)
    
    # Get 6-monthly salary
    salary_matrix = {}
    for career_year in career_progression_matrix:
        # Get the variable details you need
        year = float(career_year['Year'])
        basic_pay = int(career_year['Basic Pay'])
        da = da_matrix[year]

        # Calculate salary as Basic + DA
        salary = int(basic_pay * (1 + float(da/100)))
        # Input data - for key 'year', give value 'salary'
        salary_matrix[year] = salary

    # Init empty dictionary for years in range joining year to retire year
    # salary_monthly_detailed_matrix = {year: {} for year in range(joining_date_parsed.year, retire_date_parsed.year+1)}
    # for year, six_monthly_salary in salary_matrix.items():
    #     month_dict = {}
    #     if year % 1 == 0.5:     # year ending with 0.5
    #         month_dict = {key: six_monthly_salary for key in range(7,13)}
    #     if year % 1 != 0.5:
    #         month_dict = {key: six_monthly_salary for key in range(1,7)}
        
    #     salary_monthly_detailed_matrix[int(year)].update(month_dict)

    return salary_matrix

def get_monthly_salary(salary_matrix, joining_year, retirement_year):
    # Init empty dictionary for years in range joining year to retire year
    salary_monthly_detailed_matrix = {year: {} for year in range(int(joining_year), int(retirement_year)+1)}
    for year, six_monthly_salary in salary_matrix.items():
        month_dict = {}
        if year % 1 == 0.5:     # year ending with 0.5 -> means second half of year -> month 7 to 12
            month_dict = {key: six_monthly_salary for key in range(7,13)}
        if year % 1 != 0.5:     # year ending with 0.0 -> means first half of year -> month 1 to 6
            month_dict = {key: six_monthly_salary for key in range(1,7)}
        
        # Add months dict as value for year key (int makes year round off)
        salary_monthly_detailed_matrix[int(year)].update(month_dict)
    
    return salary_monthly_detailed_matrix

if __name__ == "__main__":
    salary_matrix = get_salary_matrix()
    salary_monthly_detailed_matrix = get_monthly_salary(salary_matrix, 2024, 2056)

    pprint.pprint(salary_matrix)
    pprint.pprint(salary_monthly_detailed_matrix)
    