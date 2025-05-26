from pay_commissions import *
from rates import *
from helper_functions import *

import pprint

from typing import Union
from calendar import monthrange


def get_salary_matrix(starting_level:Union[int,str] = 10, starting_year_row_in_level:int = 1, promotion_duration_array:list[int] = [4, 5, 4, 1, 4, 7, 5, 3], 
                       present_pay_matrix_csv:str = '7th_CPC.csv', pay_commission_implement_years:list[int] = [2026, 2036, 2046, 2056, 2066], fitment_factors:list[int] = [2, 2, 2, 2, 2],
                       dob:str = '20/5/1996', doj:str = '9/12/24', early_retirement:bool = False, dor:str = None, is_ias:bool = False,
                       initial_inflation_rate:float = 7.0, final_inflation_rate:float = 3.0, taper_period_yrs:int=40):
    
    # Get dates parsed in easy to use format
    joining_date_parsed = parse_date(doj)
    # If retiring early, get Date of Retirement (dor) from user input
    if early_retirement and dor is None:
        raise ValueError('If retiring early, must provide Date of Retirement')
    # if early_retirement:
    #     if dor is None:
    #         raise ValueError('If retiring early, must provide Date of Retirement')
    #     else:
    #         retire_date_parsed = parse_date(dor)
    # else:   # Else retire at the age of 60
    #     retire_date_parsed = get_retirement_date(dob, retirement_age=60)

    # Changing joining_year according to joining_date's month
    # If joined before 1st July, add nothing;    # If joined after 1st July, add 0.5
    joining_year = joining_date_parsed.year + 0.5 if joining_date_parsed.month > 7 else joining_date_parsed.year

    # Get Career Progression
    career_progression_matrix = career_progression(starting_level=starting_level, starting_year_row_in_level=starting_year_row_in_level, 
                                                   promotion_duration_array=promotion_duration_array, present_pay_matrix_csv=present_pay_matrix_csv, 
                                                   dob=dob, doj=doj, is_ias=is_ias, early_retirement=early_retirement, dor=dor,
                                                   pay_commission_implement_years=pay_commission_implement_years, fitment_factors=fitment_factors)

    # Get DA
    da_matrix = get_DA_matrix(initial_inflation_rate=initial_inflation_rate, final_inflation_rate=final_inflation_rate, 
                              taper_period_yrs=taper_period_yrs, joining_year=joining_year, pay_commission_implement_years=pay_commission_implement_years)
    
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

    return salary_matrix

def get_monthly_salary(salary_matrix:dict=None, dob:str = '20/5/1996', doj:str = '9/12/24', early_retirement:bool = False, dor:str = None):
    if salary_matrix is None:
        salary_matrix = get_salary_matrix()
    # Imp dates
    joining = parse_date(doj)
    # If retiring early, get Date of Retirement (dor) from user input
    if early_retirement:
        if dor is None:
            raise ValueError('If retiring early, must provide Date of Retirement')
        else:
            retirement = parse_date(dor)
    else:   # Else retire at the age of 60
        retirement = get_retirement_date(dob, retirement_age=60)

    # Init empty dictionary for years in range joining year to retire year
    salary_monthly_detailed_matrix = {year: {} for year in range(int(joining.year), int(retirement.year)+1)}
    for year, six_monthly_salary in salary_matrix.items():
        month_dict = {}
        
        # Getting month list for given half-year
        if year % 1 == 0.5:
            months_range = range(7, 13)  # Second half -- year ending with 0.5 -> means second half of year -> month 7 to 12
        else:
            months_range = range(1, 7)   # First half -- year ending with 0.0 -> means first half of year -> month 1 to 6

        # Since only integer part (0.5 removed) is required from hereon
        year = int(year)
        for month in months_range:
            # Check if month is before joining month in joining year or after retirement month in retirement year, make their salary zero
            if (year == joining.year and month < joining.month) or (year == retirement.year and month > retirement.month):
                adjusted_salary = 0
            else:
                adjusted_salary = six_monthly_salary

                # Adjust first month salary proportionally to days served
                if year == joining.year and month == joining.month:
                    days_in_month = monthrange(year, month)[1]
                    served_days = days_in_month - joining.day + 1
                    adjusted_salary = int(six_monthly_salary * (served_days / days_in_month))

                # Adjust last month salary proportionally to days served
                if year == retirement.year and month == retirement.month:
                    days_in_month = monthrange(year, month)[1]
                    served_days = retirement.day
                    adjusted_salary = int(six_monthly_salary * (served_days / days_in_month))

            month_dict[month] = adjusted_salary
        
        # Add months dict as value for year key (int makes year round off)
        salary_monthly_detailed_matrix[year].update(month_dict)
    
    return salary_monthly_detailed_matrix

if __name__ == "__main__":
    salary_matrix = get_salary_matrix(early_retirement=True, dor='10/4/30')
    salary_monthly_detailed_matrix = get_monthly_salary(salary_matrix, early_retirement=True, dor='10/4/30')

    # pprint.pprint(salary_matrix)
    pprint.pprint(salary_monthly_detailed_matrix)
    