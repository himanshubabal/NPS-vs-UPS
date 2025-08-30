from pay_commissions import *
from rates import *
from helpers.helper_functions import *

import pprint

from typing import Union
from calendar import monthrange
from typing import List, Dict, Any


def get_salary_matrix(starting_level:Union[int,str] = 10, starting_year_row_in_level:int = 1, promotion_duration_array:list[int] = [4, 5, 4, 1, 4, 7, 5, 3], 
                       present_pay_matrix_csv:str = '7th_CPC.csv', pay_commission_implement_years:list[int] = [2026, 2036, 2046, 2056, 2066], fitment_factors:list[int] = [2, 2, 2, 2, 2],
                       dob:str = '20/5/1996', doj:str = '9/12/24', early_retirement:bool = False, dor:str = None, is_ias:bool = False,
                       initial_inflation_rate:float = 7.0, final_inflation_rate:float = 3.0, taper_period_yrs:int=40):

    # Get DA
    da_matrix = get_DA_matrix(initial_inflation_rate=initial_inflation_rate, final_inflation_rate=final_inflation_rate, doj=doj, 
                              taper_period_yrs=taper_period_yrs, pay_commission_implement_years=pay_commission_implement_years)

    # Get Career Progression
    career_progression_matrix = career_progression(starting_level=starting_level, starting_year_row_in_level=starting_year_row_in_level, 
                                                   promotion_duration_array=promotion_duration_array, present_pay_matrix_csv=present_pay_matrix_csv, 
                                                   dob=dob, doj=doj, is_ias=is_ias, early_retirement=early_retirement, dor=dor,
                                                   pay_commission_implement_years=pay_commission_implement_years, fitment_factors=fitment_factors,
                                                   da_matrix=da_matrix)
    
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


def get_monthly_salary(salary_matrix:dict=None, dob:str = '20/5/1996', doj:str = '9/12/24', 
                       early_retirement:bool = False, dor:str = None, take_earlier_corpus_into_account:bool = False):
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

        # Since only integer part (0.5 removed) is required from here on
        year = int(year)
        for month in months_range:
            # Check if month is before joining month in joining year or after retirement month in retirement year, make their salary zero
            if (year == joining.year and month < joining.month) or (year == retirement.year and month > retirement.month):
                adjusted_salary = 0
            else:
                adjusted_salary = six_monthly_salary

                # Adjust first month salary proportionally to days served
                if year == joining.year and month == joining.month:
                    # Only adjust if NOT taking earlier corpus into account, otherwise calculate for full month
                    if not take_earlier_corpus_into_account:
                        days_in_month = monthrange(year, month)[1]
                        served_days = days_in_month - joining.day + 1
                        adjusted_salary = int(six_monthly_salary * (served_days / days_in_month))

                # Adjust last month salary proportionally to days served
                # NOT REQUIRED -> since retirement happens on last day of the month ONLY
                # if year == retirement.year and month == retirement.month:
                #     days_in_month = monthrange(year, month)[1]
                #     served_days = retirement.day
                #     adjusted_salary = int(six_monthly_salary * (served_days / days_in_month))

            month_dict[month] = adjusted_salary
        
        # Add months dict as value for year key (int makes year round off)
        # [only if key exists -> can happen if doj is later than that of when salary_matrix was generated]
        if year in salary_monthly_detailed_matrix:
            salary_monthly_detailed_matrix[year].update(month_dict)
    
    return salary_monthly_detailed_matrix


def get_salary_matrix_from_career(career_progression: List[Dict[str, Any]],
                                 da_matrix: Dict[float, float]) -> Dict[float, float]:
    """
    Generate complete salary matrix combining basic pay with DA.
    
    This function takes career progression data (level, year, basic pay)
    and combines it with DA matrix to calculate total salary at each
    point in the employee's career. The result is used for contribution
    calculations and retirement benefit computations.
    
    Args:
        career_progression (List[Dict[str, Any]]): Career progression history
            Each dict contains: 'Level', 'Year Row in Level', 'Basic Pay', 'Year'
        da_matrix (Dict[float, float]): DA percentages by year (including half-years)
            
    Returns:
        Dict[float, float]: Total salary matrix with keys as years
        
    Raises:
        ValueError: If career progression or DA matrix is empty
        KeyError: If required keys missing from career progression
        
    Example:
        >>> career = [{'Level': '10', 'Basic Pay': 56100, 'Year': 2024.0}]
        >>> da = {2024.0: 50.0, 2024.5: 52.0}
        >>> salary = get_salary_matrix_from_career(career, da)
        >>> print(f"Salary in 2024: ₹{salary[2024.0]:,}")
        >>> print(f"Salary in 2024.5: ₹{salary[2024.5]:,}")
        
    Note:
        - Salary = Basic Pay × (1 + DA/100)
        - DA resets to 0 at Pay Commission years
        - Half-year precision matches career progression
        - Used for contribution and pension calculations
    """
    # Validation
    if not career_progression:
        raise ValueError("Career progression data cannot be empty")
    
    if not da_matrix:
        raise ValueError("DA matrix cannot be empty")
    
    # Required keys in career progression
    required_keys = ['Level', 'Basic Pay', 'Year']
    for entry in career_progression:
        if not all(key in entry for key in required_keys):
            raise KeyError(f"Career progression entry missing required keys: {required_keys}")
    
    # Initialize salary matrix
    salary_matrix = {}
    
    # Process each career progression entry
    for entry in career_progression:
        year = entry['Year']
        basic_pay = entry['Basic Pay']
        
        # Get DA percentage for this year
        if year in da_matrix:
            da_percentage = da_matrix[year]
        else:
            # Fallback: use nearest available DA or default
            available_years = sorted(da_matrix.keys())
            if available_years:
                # Find closest year
                closest_year = min(available_years, key=lambda x: abs(x - year))
                da_percentage = da_matrix[closest_year]
            else:
                da_percentage = 0.0  # Default if no DA data
        
        # Calculate total salary: Basic Pay × (1 + DA/100)
        total_salary = basic_pay * (1 + da_percentage / 100.0)
        
        # Store rounded salary
        salary_matrix[year] = round(total_salary)
    
    return salary_matrix


if __name__ == "__main__":
    salary_matrix = get_salary_matrix(early_retirement=True, dor='10/4/30')
    salary_monthly_detailed_matrix = get_monthly_salary(salary_matrix, early_retirement=True, dor='10/4/30')

    # pprint.pprint(salary_matrix)
    pprint.pprint(salary_monthly_detailed_matrix)
    