from pension import *


def get_all_date(dob:str, doj:str)
    None



if __name__ == "__main__":
    # Testing Variables
    interest_rate_tapering_dict = get_default_interes_rate_tapering_dict()
    final_corpus_amount, yearly_corpus, monthly_salary_detailed = get_final_amounts_all(scheme='UPS', investment_option='Auto_LC50', starting_level=10, 
                                                        starting_year_row_in_level=1, promotion_duration_array=[4, 5, 4, 1, 4, 7, 5, 3], 
                                                        present_pay_matrix_csv='7th_CPC.csv', is_ias=False,
                                                        dob='20/5/1996', doj='9/12/24', early_retirement=False, dor=None,
                                                        pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066], fitment_factors=[2, 2, 2, 2, 2],
                                                        initial_inflation_rate=7.0, final_inflation_rate=3.0, taper_period_yrs=40,
                                                        interest_rate_tapering_dict=interest_rate_tapering_dict)
    inflation_matrix = get_inflation_matrix(initial_inflation_rate = 7.0, final_inflation_rate = 3.0, 
                                            taper_period_yrs = 40, joining_year = 2024)
    withdraw_corpus, lumpsum_for_ups, adjusted_pension = get_final_amounts_all(final_corpus_amount, monthly_salary_detailed, scheme='UPS')
    inflation_factor = get_inflation_factor(inflation_matrix, monthly_salary_detailed)
    npv = get_npv(final_corpus_amount, inflation_factor)
    xirr_corpus = get_xirr(final_corpus_amount, monthly_salary_detailed)

    # pprint.pprint(monthly_salary_detailed)
    # pprint.pprint(inflation_matrix)
    print(withdraw_corpus, lumpsum_for_ups, adjusted_pension)
    # pprint.pprint(inflation_factor)
    # print(final_corpus_amount, npv)
    # pprint.pprint(xirr_corpus)

    pprint.pprint(get_future_pension(inflation_matrix, adjusted_pension=adjusted_pension, scheme='NPS', final_corpus_amount=final_corpus_amount*0.60, annuity_rate=6.0))