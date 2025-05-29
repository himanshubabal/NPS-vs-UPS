from salary import get_monthly_salary
from invest_options import get_ecg_matrix
from rates import get_interest_matrix
from salary import *
from helper_functions import *

from typing import Union
import numpy as np
import pprint


def get_monthly_contribution(monthly_salary:int = 56100, employee_contrib_percent:float = 10, govt_contrib_percent:float = 10):
    '''Given a month's salary, and % contribution of employee & employer,
    Returns that month's total contributions'''
    employee_contrib = monthly_salary * employee_contrib_percent / 100
    govt_contrib = monthly_salary * govt_contrib_percent / 100
    net_monthly_contrib = employee_contrib + govt_contrib

    return net_monthly_contrib


def get_yearly_contribution(monthly_salary_detailed:dict = None, employee_contrib_percent:float = 10, govt_contrib_percent:float = 10,
                            take_earlier_corpus_into_account:bool = False, earlier_corpus:int = None):
    '''Given detailed_salary_matrix[year][month], and % contribution of employee & employer,
    Returns Yearwise Net Returns (since interest % calculation is done at year end)'''
    if monthly_salary_detailed is None:
        monthly_salary_detailed = get_monthly_salary()
    if take_earlier_corpus_into_account and earlier_corpus is None:
        raise ValueError('Must provide value of Existing Corpus and New Consideration Date -- if take_earlier_corpus_amt_upto_1st_april')

    net_yearly_contribution = {}

    for year in monthly_salary_detailed:
        # If taking into account earlier corpus, initial value of total_yearly_contribution shall be "earlier_corpus"
        total_yearly_contribution = 0 if not take_earlier_corpus_into_account else earlier_corpus

        for month in monthly_salary_detailed[year]:
            this_month_salary = monthly_salary_detailed[year][month]
            this_month_contrib = get_monthly_contribution(monthly_salary=this_month_salary, employee_contrib_percent=employee_contrib_percent, govt_contrib_percent=govt_contrib_percent)
            total_yearly_contribution += this_month_contrib

        net_yearly_contribution[year] = int(total_yearly_contribution)

    return net_yearly_contribution


def get_yearly_corpus(yearly_contributions:dict = None, dob:str = '20/05/1996', doj:str = '9/12/24', 
                      investment_option:str = 'Auto_LC50', interest_rate_tapering_dict:dict=None,
                      early_retirement:bool = False, dor:str = None):
    '''Returns Total Value of corpus till that year (after compounding)'''
    if yearly_contributions is None:
        yearly_contributions = get_yearly_contribution()
    if interest_rate_tapering_dict is None:
        interest_rate_tapering_dict = get_interest_rate_tapering_dict()

    # Parsing Date
    dob_parsed = parse_date(dob)
    doj_parsed = parse_date(doj)

    # Calculating joining age, retirement age and job duration
    joining_age = doj_parsed.year - dob_parsed.year
    if early_retirement:
        if dor is None:
            raise ValueError('If retiring early, must provide Date of Retirement')
        else:
            retirement_age = parse_date(dor).year - dob_parsed.year
    else:
        retirement_age = 60

    # Getting distribution b/w E, C, G wrt scheme chosen and age
    ecg_matrix = get_ecg_matrix(investment_option = investment_option, start_age = joining_age, end_age = retirement_age)
    # Getting interest rates, separately for E, C, G -- tapering from initial to final rate over 'Taper Period' givemn in interest_rate_tapering_dict
    E_interest_matrix = get_interest_matrix(initial_interest_rate = interest_rate_tapering_dict['E']['initial'], 
                                            final_interest_rate = interest_rate_tapering_dict['E']['final'], 
                                            taper_period_yrs = interest_rate_tapering_dict['Taper Period'], joining_year = doj_parsed.year)
    C_interest_matrix = get_interest_matrix(initial_interest_rate = interest_rate_tapering_dict['C']['initial'], 
                                            final_interest_rate = interest_rate_tapering_dict['C']['final'], 
                                            taper_period_yrs = interest_rate_tapering_dict['Taper Period'], joining_year = doj_parsed.year)
    G_interest_matrix = get_interest_matrix(initial_interest_rate = interest_rate_tapering_dict['C']['initial'], 
                                            final_interest_rate = interest_rate_tapering_dict['G']['final'], 
                                            taper_period_yrs = interest_rate_tapering_dict['Taper Period'], joining_year = doj_parsed.year)

    # Yearwise Corpus
    corpus_at_year_end = {}
    for year in yearly_contributions:
        # getting age, since age determines ratio of E, C, G
        age = year - dob_parsed.year
        # Corpus calculations
        current_yr_contrib = yearly_contributions[year]
        corpus_till_last_yr = corpus_at_year_end[year - 1] if year != doj_parsed.year else 0
        corpus_till_now = corpus_till_last_yr + current_yr_contrib 

        ecg_dist_for_current_age = ecg_matrix[age]
        E_corpus = corpus_till_now * ecg_dist_for_current_age['E'] / 100
        C_corpus = corpus_till_now * ecg_dist_for_current_age['C'] / 100
        G_corpus = corpus_till_now * ecg_dist_for_current_age['G'] / 100

        E_returns = E_corpus * (1 + E_interest_matrix[year]/100)
        C_returns = C_corpus * (1 + C_interest_matrix[year]/100)
        G_returns = G_corpus * (1 + G_interest_matrix[year]/100)

        net_returns = E_returns + C_returns + G_returns
        corpus_at_year_end[year] = int(net_returns)
    
    return corpus_at_year_end

# Gets: -> final_corpus_amount, yearly_corpus, monthly_salary_detailed
def get_final_corpus(scheme:str='UPS', investment_option:str = 'Auto_LC50', starting_level:Union[int,str] = 10, 
                    starting_year_row_in_level:int = 1, promotion_duration_array:list[int] = [4, 5, 4, 1, 4, 7, 5, 3],
                    govt_contrib_percent:float = None,  employee_contrib_percent:float = None,
                    present_pay_matrix_csv:str = '7th_CPC.csv', is_ias:bool = False,
                    dob:str = '20/5/1996', doj:str = '9/12/24', early_retirement:bool = False, dor:str = None,
                    pay_commission_implement_years:list[int] = [2026, 2036, 2046, 2056, 2066], fitment_factors:list[int] = [2, 2, 2, 2, 2],
                    initial_inflation_rate:float = 7.0, final_inflation_rate:float = 3.0, taper_period_yrs:int=40, interest_rate_tapering_dict:dict=None, 
                    take_earlier_corpus_into_account:bool = False, earlier_corpus:int = None, earlier_corpus_end_date:str = None):
    # Validation
    if scheme not in ['NPS', 'UPS']:
        raise ValueError('Scheme chosen must be either NPS or UPS')
    if early_retirement and dor is None:
        raise ValueError('If retiring early, must provide Date of Retirement')
    if interest_rate_tapering_dict is None:
        interest_rate_tapering_dict = get_interest_rate_tapering_dict()
    if take_earlier_corpus_into_account and (earlier_corpus is None or earlier_corpus_end_date is None):
        raise ValueError('If taking existing corpus into considertion -> must provide the existing corpus and the date upto which it is')
    
    # doj -> if considering earlier corpus: doj -> earlier_corpus_date
    if take_earlier_corpus_into_account:
        doj = earlier_corpus_end_date

    # If not given % contribution of employee and govt explicitly, take default value acc to scheme (10%/14%)
    if govt_contrib_percent is None or employee_contrib_percent is None:
        govt_contrib_percent = 10 if scheme == 'UPS' else 14
        employee_contrib_percent = 10

    salary_matrix = get_salary_matrix(starting_level=starting_level, starting_year_row_in_level=starting_year_row_in_level, promotion_duration_array=promotion_duration_array, 
                       present_pay_matrix_csv=present_pay_matrix_csv, dob=dob, doj=doj, is_ias=is_ias, early_retirement=early_retirement, dor=dor,
                       pay_commission_implement_years=pay_commission_implement_years, fitment_factors=fitment_factors,
                       initial_inflation_rate=initial_inflation_rate, final_inflation_rate=final_inflation_rate, taper_period_yrs=taper_period_yrs)
    monthly_salary_detailed = get_monthly_salary(salary_matrix=salary_matrix, dob=dob, doj=doj, early_retirement=early_retirement, dor=dor)
    yearly_contribution = get_yearly_contribution(monthly_salary_detailed=monthly_salary_detailed, employee_contrib_percent=employee_contrib_percent, govt_contrib_percent=govt_contrib_percent,
                                                  take_earlier_corpus_into_account=take_earlier_corpus_into_account, earlier_corpus=earlier_corpus)
    yearly_corpus = get_yearly_corpus(yearly_contributions=yearly_contribution, dob=dob, doj=doj, early_retirement=early_retirement, dor=dor,
                      investment_option=investment_option, interest_rate_tapering_dict=interest_rate_tapering_dict)
    # Final Corpus Amt -> max (last entry) in yearly-wise corpus
    final_corpus_amount = yearly_corpus[max(yearly_corpus)]

    return (final_corpus_amount, yearly_corpus, monthly_salary_detailed)


if __name__ == "__main__":
    yearly_contributions = get_yearly_contribution()
    # pprint.pprint(yearly_contributions)

    yearly_corpus = get_yearly_corpus()
    # pprint.pprint(yearly_corpus)

    final_corpus_amount, yearly_corpus, monthly_salary_detailed = get_final_corpus(scheme='UPS', is_ias=True, early_retirement=True, dor='10/4/30', earlier_corpus_end_date='01/04/2025', 
                                                                                               take_earlier_corpus_into_account=True, earlier_corpus=1000000)
    # pprint.pprint(monthly_salary_detailed)
    print(final_corpus_amount)