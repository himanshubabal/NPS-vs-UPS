import pprint

from pension import *
from pay_commissions import career_progression
from salary import get_salary_matrix, get_monthly_salary
from contribution import get_final_corpus


def get_all_data(scheme:str='UPS', investment_option:str = 'Auto_LC50', 
                withdrawl_percentage:float = 60.00, annuity_rate:float = None, 
                dob:str = '01/01/1996', doj:str = '10/10/2024', 
                early_retirement:bool = False, dor:str = None, 
                take_earlier_corpus_into_account:bool = False, earlier_corpus:int = None, earlier_corpus_end_date:str = None, 
                govt_contrib_percent:float = None,  employee_contrib_percent:float = None, 
                starting_level:Union[int,str] = 10, starting_year_row_in_level:int = 1, is_ias:bool = False, 
                present_pay_matrix_csv:str = '7th_CPC.csv', promotion_duration_array:list[int] = [4, 5, 4, 1, 4, 7, 5, 3], 
                pay_commission_implement_years:list[int] = [2026, 2036, 2046, 2056, 2066], fitment_factors:list[int] = [2, 2, 2, 2, 2], 
                initial_inflation_rate:float = 7.0, final_inflation_rate:float = 3.0, 
                initial_interest_rate: float = 12.0, final_interest_rate: float = 6.0, 
                taper_period_yrs:int=40, pension_duration:int=40, 
                E_initial:float = 12.0, E_final:float = 6.0,
                C_initial:float = 8.0, C_final:float = 4.0,
                G_initial:float = 8.0, G_final:float = 4.0
                ):
    
    # Validate everything here


    # 
    interest_rate_tapering_dict = get_interest_rate_tapering_dict(E_initial=E_initial, E_final=E_final,
                                                                C_initial=C_initial, C_final=C_final,
                                                                G_initial=G_initial, G_final=G_final,
                                                                taper_period_yrs=taper_period_yrs)

    all_data = main_function(scheme = scheme, investment_option = investment_option, 
                            withdrawl_percentage = withdrawl_percentage, annuity_rate = annuity_rate, 
                            dob = dob, doj = doj, 
                            early_retirement = early_retirement, dor = dor, 
                            take_earlier_corpus_into_account = take_earlier_corpus_into_account, 
                            earlier_corpus = earlier_corpus, earlier_corpus_end_date = earlier_corpus_end_date, 
                            govt_contrib_percent = govt_contrib_percent,  employee_contrib_percent = employee_contrib_percent, 
                            starting_level = starting_level, starting_year_row_in_level = starting_year_row_in_level, is_ias = is_ias, 
                            present_pay_matrix_csv = present_pay_matrix_csv, promotion_duration_array = promotion_duration_array, 
                            pay_commission_implement_years = pay_commission_implement_years, fitment_factors = fitment_factors, 
                            initial_inflation_rate = initial_inflation_rate, final_inflation_rate = final_inflation_rate, 
                            initial_interest_rate = initial_interest_rate, final_interest_rate = final_interest_rate, 
                            taper_period_yrs = taper_period_yrs, pension_duration = pension_duration,
                            interest_rate_tapering_dict = interest_rate_tapering_dict)
    
    return all_data


def main_function(**kwargs):
    all_data = {}

    # 1. pay_commission.py
    career_progn = auto_pass_arguments_to_function(career_progression, **kwargs)
    # pprint.pprint(career_progn)

    salary_matrix = auto_pass_arguments_to_function(get_salary_matrix, **kwargs)
    # kwargs['salary_matrix'] = salary_matrix
    # salary_monthly_detailed_matrix = auto_pass_arguments_to_function(get_monthly_salary, **kwargs)
    # pprint.pprint(salary_matrix)
    # pprint.pprint(salary_monthly_detailed_matrix)

    all_data['career_progression'] = career_progn
    all_data['salary_matrix'] = salary_matrix

    final_corpus_amount, yearly_corpus, monthly_salary_detailed = auto_pass_arguments_to_function(get_final_corpus, **kwargs)
    # pprint.pprint(monthly_salary_detailed)
    # pprint.pprint(yearly_corpus)
    # print(final_corpus_amount)

    all_data['final_corpus_amount'] = final_corpus_amount
    all_data['yearly_corpus'] = yearly_corpus
    all_data['monthly_salary_detailed'] = monthly_salary_detailed

    kwargs['final_corpus_amount'] = final_corpus_amount
    kwargs['monthly_salary_detailed'] = monthly_salary_detailed
    
    withdraw_corpus, lumpsum_for_ups, adjusted_pension = auto_pass_arguments_to_function(get_final_amounts_all, **kwargs)
    # print(withdraw_corpus, lumpsum_for_ups, adjusted_pension)

    all_data['withdraw_corpus'] = withdraw_corpus
    all_data['lumpsum_for_ups'] = lumpsum_for_ups
    all_data['adjusted_pension'] = adjusted_pension

    kwargs['amount'] = final_corpus_amount
    kwargs['adjusted_pension'] = adjusted_pension

    npv = auto_pass_arguments_to_function(get_npv_for_given_inflation, **kwargs)
    xirr_corpus = auto_pass_arguments_to_function(get_xirr, **kwargs)
    future_pension_matrix = auto_pass_arguments_to_function(get_future_pension, **kwargs)
    # print(final_corpus_amount, npv)
    # print(xirr_corpus)
    # pprint.pprint(future_pension_matrix)

    all_data['xirr_corpus'] = xirr_corpus
    all_data['npv'] = npv
    all_data['future_pension_matrix'] = future_pension_matrix

    return all_data



if __name__ == "__main__":
    pprint.pprint(get_all_data())