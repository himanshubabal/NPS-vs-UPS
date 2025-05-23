from pay_commissions import *
from rates import *
from helper_functions import *

from typing import Union

def get_salary_matrix(starting_level:Union[int,str] = 10, starting_year_in_level:int = 1, promotion_duration_array:list[int] = [4, 5, 4, 1, 4, 7, 5, 3], 
                       present_pay_matrix_csv:str = '7th_CPC.csv', dob:str = '20/5/1996', doj:str = '9/12/24', is_ias:bool = False,
                       pay_commission_implement_years:list[int] = [2026, 2036, 2046, 2056, 2066], fitment_factors:list[int] = [2, 2, 2, 2, 2],
                       initial_inflation_rate:float = 7.0, final_inflation_rate:float = 3.0):
    
    birth_date_parsed = parse_date(dob)
    joining_date_parsed = parse_date(doj)
    retire_date_parsed = get_retirement_date(dob)

    # Changing joining_year according to joining_date's month
    # If joined before 1st July, 
    # If joined after 1st July, 
    # if joining_date_parsed.month <= 6:
    #     joining_year = joining_date_parsed.year + 0.5
    # else:
    #     joining_year = joining_date_parsed.year + 1.0
    joining_year = joining_date_parsed.year + 0.5 if joining_date_parsed.month > 7 else joining_date_parsed.year
    duration_years = retire_date_parsed.year - joining_date_parsed.year

    career_progression_matrix = career_progression(starting_level=starting_level, starting_year_in_level=starting_year_in_level, 
                                                   promotion_duration_array=promotion_duration_array, present_pay_matrix_csv=present_pay_matrix_csv, 
                                                   dob=dob, doj=doj, is_ias=is_ias, pay_commission_implement_years=pay_commission_implement_years, 
                                                   fitment_factors=fitment_factors)

    da_matrix = get_DA_matrix(initial_inflation_rate=initial_inflation_rate, final_inflation_rate=final_inflation_rate, 
                              duration_years=duration_years, joining_year=joining_year, pay_commission_implement_years=pay_commission_implement_years)
    
    salary_matrix = {}
    salary_monthly_detailed_matrix = []

    for career_year in career_progression_matrix:
        # Get the variable details you need
        year = float(career_year['Year'])
        basic_pay = int(career_year['Basic Pay'])
        da = da_matrix[year]

        # Calculate salary as Basic + DA
        salary = int(basic_pay * (1 + float(da/100)))
        # Input data - for key 'year', give value 'salary'
        salary_matrix[year] = salary

        print(f'Year: {year}, DA: {da}, Basic Pay: {basic_pay} || Salary: {salary}')

    return salary_matrix



if __name__ == "__main__":
    print(get_salary_matrix())
    