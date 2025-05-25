from salary import get_monthly_salary
import pprint

def get_monthly_contribution(montly_salary:int = 56100, employee_contrib_percent:float = 10, govt_contrib_percent:float = 10):
    '''Given a month's salary, and % contribution of employee & employer,
    Returns that month's total contributions'''
    employee_contrib = montly_salary * employee_contrib_percent / 100
    govt_contrib = montly_salary * govt_contrib_percent / 100
    net_monthly_contrib = employee_contrib + govt_contrib

    return net_monthly_contrib


def get_net_yearly_contribution(monthly_salary_detailed:dict=None, employee_contrib_percent:float = 10, govt_contrib_percent:float = 10):
    '''Given detailed_salary_matrix[year][month], and % contribution of employee & employer,
    Returns Yearwise Net Returns (since interest % calculation is done at year end)'''
    if monthly_salary_detailed is None:
        monthly_salary_detailed = get_monthly_salary()

    net_yearly_contribution = {}

    for year in monthly_salary_detailed:
        total_yearly_contribution = 0

        for month in monthly_salary_detailed[year]:
            this_month_salary = monthly_salary_detailed[year][month]
            this_month_contrib = get_monthly_contribution(montly_salary=this_month_salary, employee_contrib_percent=employee_contrib_percent, govt_contrib_percent=govt_contrib_percent)
            total_yearly_contribution += this_month_contrib

        net_yearly_contribution[year] = int(total_yearly_contribution)

    return net_yearly_contribution





if __name__ == "__main__":
    # monthly_contribution = get_monthly_contribution()
    # pprint.pprint(monthly_contribution)

    net_yearly_contribution = get_net_yearly_contribution()
    pprint.pprint(net_yearly_contribution)