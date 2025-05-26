from contribution import get_final_corpus
from rates import get_inflation_matrix
from helper_functions import *

import pprint

def get_full_pension_amt(monthly_salary_detailed:dict):
    # Step 1: Flatten and filter non-zero
    monthly_salaries = [
        monthly_salary_detailed[year][month]
        for year in sorted(monthly_salary_detailed)
        for month in range(1, 13)
        if month in monthly_salary_detailed[year] and monthly_salary_detailed[year][month] > 0
        ]
    
    # Step 2: Take last 12 non-zero months
    last_12_month_salary = monthly_salaries[-12:]

    # Step 3: Calculate average
    pension_average_last_12_mnth = int(sum(last_12_month_salary) / len(last_12_month_salary))

    return pension_average_last_12_mnth

def get_final_amounts_all(final_corpus_amount:int, monthly_salary_detailed:dict, dob:str='20/5/1996', doj:str='9/12/24', 
                          early_retirement:bool=False, dor:str=None, withdrawl_percentage:float = 60.00):    
    dob_parsed = parse_date(dob)
    doj_parsed = parse_date(doj)
    if early_retirement:
        if dor is None:
            raise ValueError('If retiring early, must provide Date of Retirement')
        else:
            dor_parsed = parse_date(dor)
    else:
        dor_parsed = get_retirement_date(dob, retirement_age=60)
    
    # Getting Full Pension (avg salary of last 12 months)
    full_pension_amt = get_full_pension_amt(monthly_salary_detailed)

    # Getting Lumpsum amount for UPS
    six_month_periods = get_six_month_periods(doj_parsed, dor_parsed)
    last_month_salary = max(monthly_salary_detailed[max(monthly_salary_detailed)].values())
    lumpsum_for_ups = int((last_month_salary / 10) * six_month_periods)
    
    withdraw_corpus = int(final_corpus_amount * withdrawl_percentage / 100)
    adjusted_pension = int(full_pension_amt * (100 - withdrawl_percentage) / 100)

    return (withdraw_corpus, lumpsum_for_ups, adjusted_pension)

interest_rate_tapering_dict = get_default_interes_rate_tapering_dict()
final_corpus_amount, yearly_corpus, monthly_salary_detailed = get_final_corpus(scheme='UPS', investment_option='Auto_LC50', starting_level=10, 
                                                    starting_year_row_in_level=1, promotion_duration_array=[4, 5, 4, 1, 4, 7, 5, 3], 
                                                    present_pay_matrix_csv='7th_CPC.csv', is_ias=False,
                                                    dob='20/5/1996', doj='9/12/24', early_retirement=False, dor=None,
                                                    pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066], fitment_factors=[2, 2, 2, 2, 2],
                                                    initial_inflation_rate=7.0, final_inflation_rate=3.0, taper_period_yrs=40,
                                                    interest_rate_tapering_dict=interest_rate_tapering_dict)

inflation_matrix = get_inflation_matrix(initial_inflation_rate = 6.0, final_inflation_rate = 6.0, 
                        taper_period_yrs = 40, joining_year = 2024)

def get_inflation_factor(inflation_matrix:dict, monthly_salary_detailed:dict, doj:str='9/12/24'):
    doj_parsed = parse_date(doj)

    if doj_parsed.month <= 6:
        None

    # For 6 months period --> monthly
    # year = (1+yr rate)^no of years
    # 6 mnth = (1 + 6 mn rate) ^ no of 6 mn periods
    # 1 mnth = (1 + 1 mn rate) ^ no of months
    #   1 mn rate: 6 mn rate / 6 = year infl rate / 12

    infla_prod_factor = 1
    for year in monthly_salary_detailed:
        for month in monthly_salary_detailed[year]:
            mnth_salary = monthly_salary_detailed[year][month]

            if mnth_salary is not 0:
                if month <= 6:
                    mnth_da = inflation_matrix[year] / 6.0
                else:
                    mnth_da = inflation_matrix[year + 0.5] / 6.0
                print(f'Year: {year}, Month: {month}, Monthly DA: {mnth_da}')
                infla_prod_factor *= (1 + mnth_da / 100)

    return infla_prod_factor

# print(final_corpus_amount)
# pprint.pprint(yearly_corpus)
pprint.pprint(monthly_salary_detailed)
print(get_final_amounts_all(final_corpus_amount, monthly_salary_detailed))
pprint.pprint(inflation_matrix)
pprint.pprint(get_inflation_factor(inflation_matrix, monthly_salary_detailed))
