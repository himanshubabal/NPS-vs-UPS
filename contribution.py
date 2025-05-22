


def get_inflation_matrix(initial_inflation_rate: float = 7.0, final_inflation_rate: float = 3.0, duration_years: int = 40):
    six_month_periods = duration_years * 2
    inflation_reduction_step = (initial_inflation_rate - final_inflation_rate)/six_month_periods     # delta DA change

    inflation_matrix = {}
    inflation_matrix[0.0] = initial_inflation_rate          # Initial inflation
    
    current_inflation = initial_inflation_rate

    for i in range (six_month_periods):
        current_year_period = (i+1) * 0.5
        current_inflation -= inflation_reduction_step
        inflation_matrix[current_year_period] = round(current_inflation, 2)
    
    return inflation_matrix


def get_DA_matrix(inflation_matrix, joining_year=2024, pay_commission_implement_years=[2026, 2036, 2046, 2056, 2066]):
    pay_commission_index = 0
    current_da = 0
    year = joining_year
    da_matrix = {}
    da_matrix[joining_year] = inflation_matrix[0.0]/2.0

    for six_month_period in inflation_matrix:
        year += 0.5
        current_da += inflation_matrix[six_month_period]/2.0

        if year == pay_commission_implement_years[pay_commission_index]:
            pay_commission_index += 1
            current_da = 0
        
        da_matrix[year] = round(current_da, 2)

    return da_matrix


def get_interest_matrix(initial_inflation_rate: float = 12.0, final_inflation_rate: float = 6.0, 
                        duration_years: int = 40, joining_year: float = 2024.0):
    int_matrix = get_inflation_matrix(initial_inflation_rate, final_inflation_rate, duration_years)
    final_interest_matrix = {}

    for interest in int_matrix:
        final_interest_matrix[joining_year+interest] = int_matrix[interest]

    return final_interest_matrix

if __name__ == "__main__":
    # print(get_DA_matrix())
    inflation_matrix = get_inflation_matrix()
    # print(inflation_matrix)

    da_matrix = get_DA_matrix(inflation_matrix)
    for i in da_matrix:
        print(f"Year: {i}, DA: {da_matrix[i]}")

    print('-----------------------')

    int_matrix = get_interest_matrix()
    for i in int_matrix:
        print(f"Year: {i}, Interest: {int_matrix[i]}")

# ToDo --> different lengths of the two matrix