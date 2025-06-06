import pprint
from default_constants import *
from helper_functions import *

# Takes an initial value, a final value, and a duration
# Than linearly reduces fron initial to final value over the duration_periods
def get_progressive_change_matrix(initial_rate:float, final_rate:float, divide_periods:int, increment_step:float):
    # Delta change in rate
    reduction_step = (initial_rate - final_rate)/divide_periods

    # Init final dictionary to be returned
    progressive_change_matrix = {}
    # So that first entry starte from the given rate, 
    # otherwise would've started from reduced value of rate
    progressive_change_matrix[0.0] = initial_rate
    
    # Init current rate, it would change in every loop
    current_rate = initial_rate

    # Goes from 0 to divide_periods-1
    for i in range (divide_periods):
        # since i starts from 0
        # current_year_period increases in 
        current_year_period = (i+1) * increment_step
        current_rate -= reduction_step
        progressive_change_matrix[current_year_period] = round(current_rate, 2)
    
    return progressive_change_matrix

# Done -> historic data of 7th PC DA (same to do in interest matrix also)
# def get_DA_matrix(initial_inflation_rate: float = 7.0, final_inflation_rate: float = 3.0, taper_period_yrs: int = 40, doj: str = '9/12/24', 
#                   joining_year:float=2024.0, pay_commission_implement_years:list[int]=[2026, 2036, 2046, 2056, 2066]):
def get_DA_matrix(initial_inflation_rate: float = 7.0, final_inflation_rate: float = 3.0, taper_period_yrs: int = 40, doj: str = '9/12/24', 
                  pay_commission_implement_years:list[int]=[2026, 2036, 2046, 2056, 2066]):
    # For duration years * 2 (so 6 monthly), increment of 6 months (hence increment_step of 0.5)
    inflation_matrix = get_progressive_change_matrix(initial_inflation_rate, final_inflation_rate, taper_period_yrs*2, 0.5)

    doj_parsed = parse_date(doj)
    joining_year = doj_parsed.year + 0.5 if doj_parsed.month >= 7 else doj_parsed.year

    current_year = joining_year
    da_matrix = {}

    # Case pre-2026 years -> used saved data (ToDo -> yr before 2006 [for now, not allowed in streamlit_app.py])
    if current_year <= SEVENTH_PC_DA_END_YEAR:
        if current_year >= SIXTH_PC_DA_START_YEAR and current_year <= SIXTH_PC_DA_END_YEAR:
            sixth_pc_df = load_csv_into_df(csv_name=SIXTH_PC_DA_FILE, data_path=DATA_FOLDER_PATH)
            sixth_pc_da_matrix = sixth_pc_df.set_index('Year')['DA'].to_dict()
            da_matrix.update(sixth_pc_da_matrix)
        if current_year >= SEVENTH_PC_DA_START_YEAR and current_year <= SEVENTH_PC_DA_END_YEAR:
            seventh_pc_df = load_csv_into_df(csv_name=SEVENTH_PC_DA_FILE, data_path=DATA_FOLDER_PATH)
            seventh_pc_da_matrix = seventh_pc_df.set_index('Year')['DA'].to_dict()
            da_matrix.update(seventh_pc_da_matrix)
        current_year = SEVENTH_PC_DA_END_YEAR + 0.5

    current_da, pay_commission_index = 0, 0
    for half_yr in inflation_matrix:
        current_da += inflation_matrix[half_yr] / 2.0

        if current_year == pay_commission_implement_years[pay_commission_index]:
            current_da = 0.0
            pay_commission_index += 1
        
        da_matrix[current_year] = round(current_da, 2)
        current_year += 0.5

    return da_matrix


def get_inflation_matrix(initial_inflation_rate: float = 7.0, final_inflation_rate: float = 3.0, 
                        taper_period_yrs: int = 40, joining_year: int = 2024):
    inf_matrix = get_progressive_change_matrix(initial_inflation_rate, final_inflation_rate, taper_period_yrs*2, 0.5)

    inflation_matrix = {}
    inflation_matrix[joining_year] = initial_inflation_rate / 2.0

    for period in inf_matrix:
        inflation_matrix[joining_year + period + 0.5] = inf_matrix[period] / 2.0

    return inflation_matrix


def get_interest_matrix(initial_interest_rate: float = 12.0, final_interest_rate: float = 6.0, 
                        taper_period_yrs: int = 40, joining_year: int = 2024):
    # For duration years * 2 (so 6 monthly), increment of 6 months (hence increment_step of 0.5)
    progressive_interest_change_matrix = get_progressive_change_matrix(initial_interest_rate, final_interest_rate, taper_period_yrs, 1.0)
    final_interest_matrix = {}
    # Keeping the interest rates of joining first half and second half year same
    final_interest_matrix[joining_year] = initial_interest_rate

    for period in progressive_interest_change_matrix:
        # since the interest matrix starts from 0.0, start year from 6 months ahead, initial yr interest set above
        year = joining_year + period + 1
        final_interest_matrix[int(year)] = progressive_interest_change_matrix[period]

    return final_interest_matrix

# ToDo -> historic data of 7th PC DA (same to do in interest matrix also)
def get_DA_matrix_backup(initial_inflation_rate: float = 7.0, final_inflation_rate: float = 3.0, taper_period_yrs: int = 40, 
                  joining_year:float=2024.0, joining_da:float=55, pay_commission_implement_years:list[int]=[2026, 2036, 2046, 2056, 2066]):
    # For duration years * 2 (so 6 monthly), increment of 6 months (hence increment_step of 0.5)
    inflation_matrix = get_progressive_change_matrix(initial_inflation_rate, final_inflation_rate, taper_period_yrs*2, 0.5)
    # inflation_matrix = get_inflation_matrix(initial_inflation_rate = 12.0, final_inflation_rate = 6.0, 
                                            # taper_period_yrs = 40, joining_year = 2024)
    # to handle pay commission, resetting DA to 0 every time new pay commission is applied
    pay_commission_index = 0
    current_da = 0
    # to keep track of years
    year = joining_year
    da_matrix = {}
    # Keeping the DA of joining first half and second half year same
    da_matrix[float(joining_year)] = inflation_matrix[0.0]/2.0 + joining_da

    for six_month_period in inflation_matrix:
        # since the inflation matrix starts from 0.0, start year from 6 months ahead, initial yr DA set above
        year += 0.5
        current_da += inflation_matrix[six_month_period]/2.0

        # 6th and 7th CPC data shall be inserted here
        if year < pay_commission_implement_years[0]:
            current_da += joining_da

        # Handling Pay Commissions, if pay commission -> make DA 0, and start again
        if year == pay_commission_implement_years[pay_commission_index]:
            pay_commission_index += 1
            current_da = 0
        
        da_matrix[year] = round(current_da, 2)

    return da_matrix

if __name__ == "__main__":
    joining_year = 2004.0
    initial_rate = 7
    final_rate = 3
    taper_period_yrs = 40
    joining_da = 55
    pay_commission_implement_years = [2026, 2036, 2046, 2056, 2066]
    
    # da_matrix = get_DA_matrix(joining_year=joining_year, initial_inflation_rate=initial_rate, final_inflation_rate=final_rate, duration_years=duration_years, joining_da=joining_da, pay_commission_implement_years=pay_commission_implement_years)
    # int_matrix = get_interest_matrix(joining_year=joining_year, initial_interest_rate=initial_rate, final_interest_rate=final_rate, duration_years=duration_years)
    
    da_matrix = get_DA_matrix()
    # da_matrix_new = get_DA_matrix_new()

    # int_matrix = get_interest_matrix()
    inflation_matrix = get_inflation_matrix()

    # pprint.pprint(da_matrix) 
    # pprint.pprint(da_matrix_new) 


    # for i in da_matrix:
    #     print(f"Year: {i}, DA: {da_matrix[i]}, Interest: {int_matrix[i]}")

    # pprint.pprint (int_matrix)
    pprint.pprint(da_matrix)    
    # pprint.pprint(inflation_matrix)
    # pprint.pprint(inflation_matrix)
    # print(len(da_matrix), len(inflation_matrix))
