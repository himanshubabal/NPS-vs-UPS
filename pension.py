from contribution import *
from rates import *
from helpers.helper_functions import *

from datetime import date
from dateutil.relativedelta import relativedelta
import pprint
from pyxirr import xirr

def get_inflation_matrix(initial_inflation_rate: float = 7.0, 
                        final_inflation_rate: float = 4.0, 
                        taper_period_yrs: int = 40, 
                        joining_year: int = 2024) -> Dict[float, float]:
    """
    Get inflation matrix for calculations.
    
    This function returns inflation rates by year, similar to the DA matrix.
    For simplicity, we'll use the same logic as get_projected_DA.
    
    Args:
        initial_inflation_rate (float): Starting inflation rate
        final_inflation_rate (float): Ending inflation rate
        taper_period_yrs (int): Years over which rates taper
        joining_year (int): Year to start calculations
        
    Returns:
        Dict[float, float]: Inflation rates by year
    """
    # Start with initial inflation rate
    start_inflation = initial_inflation_rate
    projected_inflation = {}
    projected_inflation[joining_year] = start_inflation
    
    # Project inflation for each half-year period
    current_year = joining_year
    
    # Calculate total periods to project
    max_periods = int(taper_period_yrs * 2)  # Half-year periods
    
    for period in range(1, max_periods + 1):
        # Calculate next half-year
        next_year = current_year + 0.5
        
        # Calculate current inflation rate based on tapering
        years_elapsed = (next_year - joining_year)
        if years_elapsed <= taper_period_yrs:
            # Linear tapering: rate decreases from initial to final
            current_inflation_rate = initial_inflation_rate - (
                (initial_inflation_rate - final_inflation_rate) * 
                (years_elapsed / taper_period_yrs)
            )
        else:
            # After taper period, use final rate
            current_inflation_rate = final_inflation_rate
        
        # Store inflation rate for this half-year
        projected_inflation[next_year] = round(current_inflation_rate, 1)
        
        # Update for next iteration
        current_year = next_year
    
    return projected_inflation

# Average of last 12 months salary
def get_full_pension_amt_UPS(monthly_salary_detailed:dict):
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

# Gets -> withdraw_corpus, lumpsum_for_ups, adjusted_pension (given %withdrawl)
def get_final_amounts_all(final_corpus_amount:int, monthly_salary_detailed:dict, dob:str='20/5/1996', doj:str='9/12/24', 
                          early_retirement:bool=False, dor:str=None, withdrawl_percentage:float = 60.00, scheme:str = 'UPS', annuity_rate:float = None, 
                          initial_inflation_rate:float = 7.0, final_inflation_rate:float = 3.0, taper_period_yrs:int = 40):   
    # Validations
    if scheme not in ['NPS', 'UPS']:
        raise ValueError('Scheme chosen must be either NPS or UPS')
    # if scheme == 'NPS' and annuity_rate is None:
    #     raise ValueError('If choosing NPS, must provide Annuity Rate')
    
    # Parsing important dates
    doj_parsed = parse_date(doj)
    if early_retirement:
        if dor is None:
            raise ValueError('If retiring early, must provide Date of Retirement')
        else:
            dor_parsed = parse_date(dor)
    else:
        dor_parsed = get_retirement_date(dob, retirement_age=60)

    # IF NPS, and annuity_rate is not given, get annuity_rate from retirement year's inflation + 1 %
    if scheme == 'NPS' and annuity_rate is None:
        joining_year = parse_date(doj).year
        retire_year = dor_parsed.year
        retire_year += 0.5 if dor_parsed.month > 6 else 0
        inflation_matrix = get_inflation_matrix(initial_inflation_rate = initial_inflation_rate, final_inflation_rate = final_inflation_rate, 
                                                taper_period_yrs = taper_period_yrs, joining_year = joining_year)
        # Get DA at the time of retirement
        da_retire = inflation_matrix[retire_year]
        annuity_rate = (da_retire * 2) + 1

    # Calculating FULL Pension Amount
    if scheme == 'UPS':
        # Getting Full Pension (avg salary of last 12 months)
        full_pension_amt = get_full_pension_amt_UPS(monthly_salary_detailed)
        # If service less than 25 years (300 months), reduce pension prop
        months_served = get_month_difference(dor_parsed, doj_parsed)           # Months Served
        if months_served < 300:
            full_pension_amt *= months_served / 300
    if scheme == 'NPS':
        full_pension_amt = (final_corpus_amount * annuity_rate / 100) / 12      # Annuity return -> yearly -> divide by 12 to get monthly

    # Getting Lumpsum amount for UPS
    six_month_periods = get_six_month_periods(doj_parsed, dor_parsed)
    last_month_salary = max(monthly_salary_detailed[max(monthly_salary_detailed)].values())
    lumpsum_for_ups = int((last_month_salary / 10) * six_month_periods)
    
    # Final amounts, taking into consideration % withdraw
    withdraw_corpus = int(final_corpus_amount * withdrawl_percentage / 100)
    adjusted_pension = int(full_pension_amt * (100 - withdrawl_percentage) / 100)

    return (withdraw_corpus, lumpsum_for_ups, adjusted_pension)

# Inflation over the period
def get_inflation_factor(monthly_salary_detailed:dict, doj:str='9/12/24', 
                        initial_inflation_rate = 7.0, final_inflation_rate = 3.0, taper_period_yrs = 40):
    # ---------- LOGIC ---------
    # For 6 months period --> monthly
    # year = (1+yr rate)^no of years
    # 6 mnth = (1 + 6 mn rate) ^ no of 6 mn periods
    # 1 mnth = (1 + 1 mn rate) ^ no of months
    #   1 mn rate: 6 mn rate / 6 = year infl rate / 12
    #   Monthly Rate = (1 + 6-Month Rate)^1/6 −1

    joining_year = parse_date(doj).year
    inflation_matrix = get_inflation_matrix(initial_inflation_rate = initial_inflation_rate, final_inflation_rate = final_inflation_rate, 
                                            taper_period_yrs = taper_period_yrs, joining_year = joining_year)

    infla_prod_factor = 1
    for year in monthly_salary_detailed:
        for month in monthly_salary_detailed[year]:
            mnth_salary = monthly_salary_detailed[year][month]

            if mnth_salary != 0:
                # Monthly Rate=(1+6-Month Rate)^1/6 −1
                if month <= 6:
                    six_mnth_da = inflation_matrix[year]
                    mnth_da = (1 + six_mnth_da / 100) ** (1/6) - 1
                else:
                    six_mnth_da = inflation_matrix[year + 0.5]
                    mnth_da = (1 + six_mnth_da / 100) ** (1/6) - 1
                infla_prod_factor *= (1 + mnth_da)
                # print(f'Year: {year}, Month: {month}, Six Month DA: {six_mnth_da}, Monthly DA: {mnth_da}, Infl: {infla_prod_factor}')

    return round(infla_prod_factor, 2)

# NPV (Net Present Value): value of future amount in present term -> basically inflation adjusted value
def get_npv_for_given_inflation(amount:int, monthly_salary_detailed:dict, doj:str='9/12/24', 
                        initial_inflation_rate = 7.0, final_inflation_rate = 3.0, taper_period_yrs = 40):
    inflation_factor = get_inflation_factor(monthly_salary_detailed, doj=doj, initial_inflation_rate=initial_inflation_rate, final_inflation_rate=final_inflation_rate, taper_period_yrs=taper_period_yrs)
    npv = int(get_npv(amount, inflation_factor))
    return (inflation_factor, npv)

# XIRR (Extended Internal Rate of Return): calculate the annualized rate of return
def get_xirr(final_corpus_amount:int, monthly_salary_detailed:dict, scheme:str='UPS'):
    if scheme not in ['NPS', 'UPS']:
        raise ValueError('Scheme chosen must be either NPS or UPS')
    
    cash_flow = {}
    last_yr, last_mnth = 0, 0
    for year in monthly_salary_detailed:
        for month in monthly_salary_detailed[year]:
            dt = date(year, month, 1)
            salary = monthly_salary_detailed[year][month]
            if salary != 0:
                if scheme == 'UPS':
                    contrib = int(salary * 0.20)
                else:
                    contrib = int(salary * 0.24)
                cash_flow[dt] = -1 * contrib
                last_yr, last_mnth = year, month
    cash_flow[date(last_yr, last_mnth+1, 1)] = final_corpus_amount
    annual_xirr = xirr(cash_flow)
    annual_xirr_percent = round(annual_xirr * 100, 2)
    return annual_xirr_percent

# Assuming no Pay Commission applies after retirement
def get_future_pension(adjusted_pension:int = None, early_retirement:bool = False, dor:str = None, dob:str='20/5/96', doj:str='9/12/24', 
                       pension_duration:int=40, scheme:str = 'UPS', final_corpus_amount:int = None, annuity_rate:float = None,
                       initial_inflation_rate:float = 7.0, final_inflation_rate:float = 3.0, taper_period_yrs:int = 40):
    # Validation
    if scheme == 'NPS' and final_corpus_amount is None:
        raise ValueError('If choosing NPS, must provide Final Corpas Value')
    if scheme == 'UPS' and adjusted_pension is None:
        raise ValueError('If choosing UPS, must provide Final (Adjusted) Pension')
    
    joining_year = parse_date(doj).year
    inflation_matrix = get_inflation_matrix(initial_inflation_rate = initial_inflation_rate, final_inflation_rate = final_inflation_rate, 
                                            taper_period_yrs = taper_period_yrs, joining_year = joining_year)

    # Get Retirement Date, Month, Year
    if early_retirement:
        if dor is None:
            raise ValueError('If retiring early, must provide Date of Retirement')
        else:
            dor_parsed = parse_date(dor)
    else:   # Else retire at the age of 60
        dor_parsed = get_retirement_date(dob, retirement_age=60)
    # Getting, and adjusting retirement date accordingly
    retire_year = dor_parsed.year
    retire_year += 0.5 if dor_parsed.month > 6 else 0
    
    # Get DA at the time of retirement
    da_retire = inflation_matrix[retire_year]
    # If Annuity rate is not given for NPS, take it as inflation+1 (usually annuity is in that range)
    if scheme == 'NPS' and annuity_rate is None:
        annuity_rate = (da_retire * 2) + 1

    future_pension_matrix, period = {}, 0
    while period < pension_duration * 2:
        if scheme == 'UPS':
            mnth_pension_1 = int(adjusted_pension * (1 + (da_retire * (period + 1)) / 100))
            mnth_pension_2 = int(adjusted_pension * (1 + (da_retire * (period + 2)) / 100))
        if scheme == 'NPS':
            year_pension = final_corpus_amount * annuity_rate / 100
            mnth_pension_1 = mnth_pension_2 = int(year_pension / 12)
        # Add pensions
        future_pension_matrix[retire_year + period / 2] = mnth_pension_1
        future_pension_matrix[retire_year + period / 2 + 0.5] = mnth_pension_2
        period += 2

    return future_pension_matrix


if __name__ == "__main__":
    # Testing Variables
    # interest_rate_tapering_dict = get_interest_rate_tapering_dict()
    # inflation_matrix = get_inflation_matrix(initial_inflation_rate = 7.0, final_inflation_rate = 3.0, 
    #                                         taper_period_yrs = 40, joining_year = 2024)
    final_corpus_amount, yearly_corpus, monthly_salary_detailed = get_final_corpus()
    withdraw_corpus, lumpsum_for_ups, adjusted_pension = get_final_amounts_all(final_corpus_amount, monthly_salary_detailed, scheme='UPS')

    # inflation_factor = get_inflation_factor(monthly_salary_detailed)
    npv = get_npv_for_given_inflation(final_corpus_amount, monthly_salary_detailed)
    xirr_corpus = get_xirr(final_corpus_amount, monthly_salary_detailed)
    future_pension_matrix = get_future_pension(adjusted_pension=adjusted_pension, scheme='NPS', final_corpus_amount=final_corpus_amount*0.60, annuity_rate=6.0)

    # pprint.pprint(monthly_salary_detailed)
    # pprint.pprint(inflation_matrix)
    print(withdraw_corpus, lumpsum_for_ups, adjusted_pension)
    # pprint.pprint(inflation_factor)
    print(final_corpus_amount, npv)
    pprint.pprint(xirr_corpus)

    pprint.pprint(future_pension_matrix)
