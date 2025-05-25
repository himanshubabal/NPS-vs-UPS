import pprint

def ecg_returns(corpus:int, E_percentage:float = 50.00, C_percentage:float = 30.00, G_percentage:float = 20.00,
                            E_return:float = 12.00,     C_return:float = 7.0,       G_return:float = 7.0):
    # Verify that all percentage combined reach 100%
    if (E_percentage + C_percentage + G_percentage != 100):
        raise ValueError('Combined `%` distribution of E, C & G shall be 100%')

    E_corpus = corpus * E_percentage / 100
    C_corpus = corpus * C_percentage / 100
    G_corpus = corpus * G_percentage / 100
    
    E_return_corpus = E_corpus * (1 + E_return / 100)
    C_return_corpus = C_corpus * (1 + C_return / 100)
    G_return_corpus = G_corpus * (1 + G_return / 100)

    total_retuen_corpus = int(E_return_corpus + C_return_corpus + G_return_corpus)
    
    return total_retuen_corpus


def get_ecg_matrix(investment_option:str = 'Auto_LC50', start_age:int = 20, end_age:int = 60):
    # Variables, so easy to refer
    active_choice = 'Active'
    auto_LC25, auto_LC50, auto_LC75 = 'Auto_LC25', 'Auto_LC50', 'Auto_LC75'
    benchmark = 'Standard/Benchmark'
    possible_invest_choices = [active_choice, auto_LC25, auto_LC50, auto_LC75, benchmark]
    if investment_option not in possible_invest_choices:
        raise ValueError(f'{investment_option} not a valid option. Please choose from {possible_invest_choices}')
    
    # ------------ L O G I C ------------
    # Benchmark -> 15% E + 85% bonds (say 35% C + 50% G)
    # Active -> E: max 75% upto age 50, after that 2.5% redn in E_max, till E_max is 50% by age of 60
    # Auto -> 3 possible options (from 35 age till 55 age)
    #   LC75 -> Till age 35 -> E:75, C:10, G:15
    #           E: reduce by 3 each year, C:inc by 1 for 10 yr const for next 5 reduce by 2 for next 5, G: inc by 3 each year 
    #           Till age of 55 -> E:15, C:10, G:75
    #   LC50 -> Till age of 35 -> E:50, C:30, G:20
    #           E: reduce by 2 each yr, C: reduce by 1 each yr, G: inc by 3 each yr
    #           Till age of 55 -> E:10, C:10, G:80
    #   LC25 -> Till age of 35 -> E:25, C:45, G:30
    #           E: reduce by 1 each yr, C: reduce by 2 each yr, G: inc by 3 each yr
    #           Till age of 55 -> E:5, C:5, G:90

    # Initialise and populate dictionary for age from 20 to 60 (start_age to end_age)
    ecg_matrix = {age: {} for age in range(start_age, end_age+1)}

    for age in ecg_matrix:
        # Benchmark -> 15% E + 85% bonds (say 35% C + 50% G)
        if investment_option == benchmark:
            E_percent, C_percent, G_percent = 15, 35, 50
        # LC25 -> Till age of 35 -> E:25, C:45, G:30
        #         E: reduce by 1 each yr, C: reduce by 2 each yr, G: inc by 3 each yr
        #         Till age of 55 -> E:5, C:5, G:90
        if investment_option == auto_LC25:
            if age <= 35:
                E_percent, C_percent, G_percent = 25, 45, 30
            elif age >= 55:
                E_percent, C_percent, G_percent = 5, 5, 90
            else:
                years_since_35 = age - 35
                E_percent = 25 - 1 * years_since_35
                C_percent = 45 - 2 * years_since_35
                G_percent = 30 + 3 * years_since_35
        # LC50 -> Till age of 35 -> E:50, C:30, G:20
        #         E: reduce by 2 each yr, C: reduce by 1 each yr, G: inc by 3 each yr
        #         Till age of 55 -> E:10, C:10, G:80
        if investment_option == auto_LC50:
            if age <= 35:
                E_percent, C_percent, G_percent = 50, 30, 20
            elif age >= 55:
                E_percent, C_percent, G_percent = 10, 10, 80
            else:
                years_since_35 = age - 35
                E_percent = 50 - 2 * years_since_35
                C_percent = 30 - 1 * years_since_35
                G_percent = 20 + 3 * years_since_35
        # LC75 -> Till age 35 -> E:75, C:10, G:15
        #         E: reduce by 3 each year, C:inc by 1 for 10 yr const for next 5 reduce by 2 for next 5, G: inc by 3 each year 
        #         Till age of 55 -> E:15, C:10, G:75
        if investment_option == auto_LC75:
            if age <= 35:
                E_percent, C_percent, G_percent = 75, 10, 15
            elif age >= 55:
                E_percent, C_percent, G_percent = 15, 10, 75
            else:
                years_since_35 = age - 35
                E_percent = 75 - 3 * years_since_35
                G_percent = 15 + 3 * years_since_35
                # C: inc by 1 for initial 10 yr, const for next 5, reduce by 2 for next 5
                if years_since_35 <= 10:
                    C_percent = 10 + years_since_35 * 1
                elif years_since_35 <= 15:
                    C_percent = 20  # constant for next 5 years (from 10 to 15)
                else:
                    C_percent = 20 - 2 * (years_since_35 - 15)
        # Active -> E: max 75% upto age 50, after that 2.5% redn in E_max, till E_max is 50% by age of 60
        #           C: constant at 25%; G: 0% till age 50 and reaches 25% by age 60
        else:
            if age <= 50:       # Till age of 50
                E_percent, C_percent, G_percent = 75, 25, 0
            elif age <= 60:     # Age 50 to 60
                years_since_50 = age - 50
                E_percent = 75 - 2.5 * years_since_50
                C_percent = 25
                G_percent = 0 + 2.5 * years_since_50
            else:              # Above 60 (not needed)
                E_percent, C_percent, G_percent = 50, 25, 25     # Assume post-60 E stays at 50%

        ecg_matrix[age]['E'], ecg_matrix[age]['C'], ecg_matrix[age]['G'] = E_percent, C_percent, G_percent

    return ecg_matrix


# def 



if __name__ == "__main__":
    # return_corpus = ecg_returns(100000)

    # pprint.pprint(salary_matrix)
    # pprint.pprint(return_corpus)

    ecg_matrix = get_ecg_matrix(investment_option = 'Active')
    pprint.pprint(ecg_matrix)