

# Takes an initial value, a final value, and a duration
# Than linearly reduces fron initial to final value over the duration_periods
def get_progressive_change_matrix(initial_rate, final_rate, divide_periods, increment_step):
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


def get_DA_matrix(initial_inflation_rate: float = 7.0, final_inflation_rate: float = 3.0, duration_years: int = 40, 
                  joining_year=2024, joining_da=55, pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066]):
    # For duration years * 2 (so 6 monthly), increment of 6 months (hence increment_step of 0.5)
    inflation_matrix = get_progressive_change_matrix(initial_inflation_rate, final_inflation_rate, duration_years*2, 0.5)
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

        if year < pay_commission_implement_years[0]:
            current_da += joining_da

        # Handling Pay Commissions, if pay commission -> make DA 0, and start again
        if year == pay_commission_implement_years[pay_commission_index]:
            pay_commission_index += 1
            current_da = 0
        
        da_matrix[year] = round(current_da, 2)

    return da_matrix


def get_interest_matrix(initial_interest_rate: float = 12.0, final_interest_rate: float = 6.0, 
                        duration_years: int = 40, joining_year: float = 2024.0):
    # For duration years * 2 (so 6 monthly), increment of 6 months (hence increment_step of 0.5)
    int_matrix = get_progressive_change_matrix(initial_interest_rate, final_interest_rate, duration_years*2, 0.5)
    final_interest_matrix = {}
    # Keeping the interest rates of joining first half and second half year same
    final_interest_matrix[float(joining_year)] = initial_interest_rate

    for six_month_period in int_matrix:
        # since the interest matrix starts from 0.0
        year = joining_year + six_month_period + 0.5
        final_interest_matrix[year] = int_matrix[six_month_period]

    return final_interest_matrix

if __name__ == "__main__":
    joining_year = 2024.5
    initial_rate = 7
    final_rate = 3
    duration_years = 40
    
    da_matrix = get_DA_matrix(joining_year=joining_year, initial_inflation_rate=initial_rate, final_inflation_rate=final_rate, duration_years=duration_years)
    int_matrix = get_interest_matrix(joining_year=joining_year, initial_interest_rate=initial_rate, final_interest_rate=final_rate, duration_years=duration_years)
    
    for i in da_matrix:
        print(f"Year: {i}, DA: {da_matrix[i]}, Interest: {int_matrix[i]}")

# ToDo --> different lengths of the two matrix