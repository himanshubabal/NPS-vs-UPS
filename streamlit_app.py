from all_data import get_all_data
from helper_functions import *
from pay_commissions import get_level_year_from_basic_pay, get_basic_pay

# import locale
# import babel
from babel.numbers import format_number, format_currency, format_compact_currency
import streamlit as st
import pandas as pd

UPS_IMPLEMENT_DATE = '01/04/2025'
DATA_CPC_PATH = 'data/'
# PAY_MATRIX_7CPC_CSV = 'data/7th_CPC.csv'
PAY_MATRIX_7CPC_CSV = '7th_CPC.csv'
PAY_MATRIX_7CPC_DF = load_csv_into_df(PAY_MATRIX_7CPC_CSV)
STARTING_YEAR_CPC = 1       # Since new joining starts at year one only
DEFAULT_WITHDRAWL_PERCENTAGE = 25.00
DEFAULT_MAX_GRATUITY = 2500000      # 25L
TAPER_PERIOD = PENSION_DURATION = 40
PAY_LEVELS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '13A', '14', '15', '16', '17', '18']
INVESTMENT_OPTIONS = ['Standard/Benchmark', 'Auto_LC25', 'Auto_LC50', 'Auto_LC75', 'Active']
SERVICES = ['IFS (AIS)', 'IAS', 'IPS', 'Other Central Services']

# locale.setlocale(locale.LC_ALL, 'en_IN')
st.set_page_config(
    page_title="NPS v/s UPS",
    page_icon="pension_2.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title("NPS v/s UPS")

st.write('Enter Your Details')
dob = convert_dt_to_string(st.date_input(label='Date of Birth', format='DD/MM/YYYY', value='1995-01-01', min_value='1965-01-01', 
                                            max_value='2005-12-31', help='Enter your Date of Birth', key='dob'))

# If DOJ is before 7th CPC (ie. before 1st Jan 2016 -> do what?)
# (also, historic data of DA shall be considered) 


col_doj, col_considering_early_retirement, col_dor = st.columns(3, vertical_alignment='bottom')
with col_doj:
    dt_doj = st.date_input(label='Date of Joining', format='DD/MM/YYYY', value='2024-12-09', min_value='1985-01-01', 
                           max_value='2030-12-31', help='Enter your Date of Joining the Service', key='doj')
with col_considering_early_retirement:
    considering_early_retirement = st.checkbox(label='Considering Early Retirement', key='considering_early_retirement')
with col_dor:
    if not considering_early_retirement:
        dt_dor = get_retirement_date(dob)
        st.date_input(label='(Verify) Date of Retirement', format='DD/MM/YYYY', value=str(dt_dor), key='dor', disabled=True)
    else:
        dt_dor = st.date_input(label='Enter Date of Retirement', format='DD/MM/YYYY', key='dor')


col_choose_service, col_considering_existing_corpus = st.columns(2, vertical_alignment='bottom')
with col_choose_service:
    choose_service = st.selectbox(label='Choose Your Service', options=SERVICES, 
                                    placeholder='IAS/IPS/IFS/etc', index=0, key='choose_service')
    if choose_service == 'IAS':
        is_ias = True
    else:
        is_ias = False
    st.session_state['is_ias'] = is_ias
with col_considering_existing_corpus:
    considering_existing_corpus = st.checkbox(label='Consider Existing NPS Tier 1 Corpus', key='considering_existing_corpus')

# col_checkbox_existing_corpus, col_display_doj = st.columns(2)
# with col_checkbox_existing_corpus:
#     considering_existing_corpus = st.checkbox(label='Consider Existing NPS Tier 1 Corpus', key='considering_existing_corpus')
# with col_display_doj:
#     if considering_existing_corpus:
#         st.write('(New DoJ - 1st April 2025)')

# considering_existing_corpus = st.checkbox(label='Consider Existing NPS Tier 1 Corpus')

if considering_existing_corpus:
    # Consider Joining from 'UPS_IMPLEMENT_DATE' if considering_existing_corpus
    dt_doj = parse_date(UPS_IMPLEMENT_DATE)

    # Column View - so that it looks better
    col_existing_corpus_input, col_existing_corpus_display = st.columns(2)
    col_existing_corpus_input.text('Existing NPS Tier 1 corpus as on Today (in ₹)')
    col_existing_corpus_display.text('(Verify) Your Corpus')
    with col_existing_corpus_input:
        earlier_corpus = int(st.number_input(label='Existing NPS Tier 1 corpus as on Today (in ₹)', 
                                             step=1000, label_visibility='collapsed', key='earlier_corpus'))
    with col_existing_corpus_display:
        earlier_corpus_formatted = format_compact_currency(earlier_corpus, 'INR', locale='en_IN', fraction_digits=4)
        st.text_input(label='Verify Corpus', value=earlier_corpus_formatted, label_visibility='collapsed', disabled=True)
    
    # Ask user to input existing corpus value
    # earlier_corpus = int(st.number_input(label='Existing NPS Tier 1 corpus as on Today (in ₹)', step=100))
    # earlier_corpus_formatted = format_compact_currency(earlier_corpus, 'INR', locale='en_IN', fraction_digits=4)
    # Display the corpus value
    # st.write(f'Your Corpus till 1st April 2025: {earlier_corpus_formatted}')

    # Add column in front of Basic Pay
    col_basic_pay, col_pay_level = st.columns(2)
    col_basic_pay.text('Current Basic Pay (Acc to 7th CPC)')
    col_pay_level.text('(Verify) Corresponding Pay Level')
    with col_basic_pay:
        starting_basic_pay = st.number_input(label='Current Basic Pay (Acc to 7th CPC)', step=100, 
                                             label_visibility='collapsed', key='starting_basic_pay')
    with col_pay_level:
        starting_level, starting_year = get_level_year_from_basic_pay(int(starting_basic_pay), PAY_MATRIX_7CPC_DF)
        display_str = f'Pay Level: {starting_level},  Pay Year Index: {starting_year}'
        st.text_input(label='Chosen Values', value=display_str, label_visibility='collapsed', disabled=True)


    # Ask user to enter current Basic Pay
    # starting_basic_pay = st.number_input(label='Current Basic Pay (Acc to 7th CPC)', step=100)
    # Get/Verify Pay Level
    # starting_level, starting_year = get_level_year_from_basic_pay(int(starting_basic_pay), PAY_MATRIX_7CPC_DF)
    # IF wrong Pay Level entered, warn user; else display par level and year
    if starting_level == 0 or starting_year == 0:
        st.warning('Please Enter Correct Basic Pay (Acc to 7th CPC)')
    # else:
    #     st.write(f'Pay Level: {starting_level},  Pay Year Index: {starting_year}')
else:   # If considering for a new recruitment, ask user the relevant details
    # dt_doj = st.date_input(label='Date of Joining', format='DD/MM/YYYY', value='2024-12-09', 
    #                 min_value='1985-01-01', max_value='2030-12-31', help='Enter your Date of Joining the Service')
    earlier_corpus = None
    col_starting_level, col_starting_basic_pay = st.columns(2)
    col_starting_level.text('Starting Pay Level (7th CPC)')
    col_starting_basic_pay.text('(Verify) Basic Pay')
    with col_starting_level:
        # Start at default Pay Level 10
        starting_level = st.selectbox(label='Starting Pay Level (7th CPC)', index=9, options=PAY_LEVELS, label_visibility='collapsed')
    with col_starting_basic_pay:
        starting_year = STARTING_YEAR_CPC       # Since new joining starts at year one only
        starting_basic_pay = get_basic_pay(level=starting_level, year=starting_year, pay_matrix_df=PAY_MATRIX_7CPC_DF)
        st.text_input(label='Starting Basic Pay', value=starting_basic_pay, label_visibility='collapsed', disabled=True)


    # starting_level = st.selectbox(label='Starting Pay Level (7th CPC)', index=9, options=PAY_LEVELS)
    # starting_year = STARTING_YEAR_CPC       # Since new joining starts at year one only
    # starting_basic_pay = get_basic_pay(level=starting_level, year=starting_year, pay_matrix_df=PAY_MATRIX_7CPC_DF)
    # st.write(f'Basic Pay: {starting_basic_pay}')
    # ??????????????????????? -- For now, considering only those who joined after 7th CPC was implemented
    # starting_pay_commission = st.selectbox(label='Starting Pay Commission', index=1, options=['6th CPC', '7th CPC'])


# ToDo -> for mobile, can add rows on click of button
with st.expander(label='(Optional) Promotions', expanded=False, icon=None):
    if starting_level != 0:
        # Promotion aspect
        # Pay commission aspect
        joining_year = dt_doj.year
        st.write('Promotion Details')
        col_prom_level, col_prom_year, col_show_prom = st.columns(3, border=True)
        col_prom_level.text('Next Promotion\'s Level')
        col_prom_year.text('Next Promotion Due In')
        col_show_prom.text('Verify')
        starting_level_index = PAY_LEVELS.index(starting_level)

        for curr_level in range(len(PAY_LEVELS) - starting_level_index - 1):
            col_prom_level_key = 'col_level_year_' + str(curr_level)
            col_prom_year_key = 'col_prom_year_' + str(curr_level)
            col_show_prom_key = 'col_prom_show_' + str(curr_level)
            with col_prom_level:
                st.selectbox('Pay Level', index=None, placeholder='Next Pay Level', label_visibility='collapsed', 
                            options=PAY_LEVELS[starting_level_index+curr_level+1:],key=col_prom_level_key)
            with col_prom_year:
                st.number_input(label='Promotion Year / Duration', step=1, min_value=1, max_value=2060, value=None, 
                                placeholder='eg. 2028', key=col_prom_year_key, label_visibility='collapsed')
            with col_show_prom:
                chosen_prom_year = st.session_state[col_prom_year_key]
                if chosen_prom_year is not None:
                    if chosen_prom_year < 40:
                        display_year = joining_year + chosen_prom_year
                    else:
                        display_year = chosen_prom_year
                else:
                    display_year = chosen_prom_year

                val = f'Level: {str(st.session_state[col_prom_level_key])}, Due in: {str(display_year)}'
                st.text_input(label='Chosen Values', value=val, label_visibility='collapsed', 
                                    disabled=True, key=col_show_prom_key)


with st.expander(label='(Optional) Pay Commissions & Fitment Factors', expanded=False):
    col_pc_imp_yrs, col_fit_factor = st.columns(2, border=True)
    col_pc_imp_yrs.text('Pay Commission Implementation Year')
    col_fit_factor.text('Fitment Factor')

    # Assuming max PC's one can see is 4
    for index_yr in range(4):
        col_pc_imp_yrs_key = 'col_pc_imp_yrs_' + str(index_yr)
        col_fit_factor_key = 'col_fit_factor_' + str(index_yr)
        with col_pc_imp_yrs:
            st.number_input(label='PC Year', step=10, min_value=2026, max_value=2080, value=None, 
                                placeholder='eg. 2026', key=col_pc_imp_yrs_key, label_visibility='collapsed')
        with col_fit_factor:
            st.number_input(label='PC Year', step=0.1, min_value=1.0, max_value=4.0, value=None, 
                                placeholder='eg. 1.86', key=col_fit_factor_key, label_visibility='collapsed')


with st.expander(label='(Optional) Inflation and Interest Rates (ECG)', expanded=False):
    rate_variability = st.radio(label='Assume rates to be constant, or variable?', options=['Constant', 'Variable (tapering)'])

    if rate_variability == 'Constant':
        user_inflation_const = st.number_input(label='Inflation (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 7', key='inflation_const')
        col_E_const, col_C_const, col_G_const = st.columns(3)
        with col_E_const:
            user_E_cons = st.number_input(label='Equity return (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 12', key='E_const')
        with col_C_const:
            user_C_cons = st.number_input(label='Corporate Bond return (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 8', key='C_const')
        with col_G_const:
            user_G_cons = st.number_input(label='Govt Bond return (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 7', key='G_const')

    else:   # Tapering Case
        col_inflation_initial, col_inflation_final = st.columns(2)
        with col_inflation_initial:
            user_inflation_taper_initial = st.number_input(label='Inflation initially (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 7', key='inflation_taper_initial')
        with col_inflation_final:
            user_inflation_taper_final = st.number_input(label='Inflation at the end (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 3.5', key='inflation_taper_final')
        
        col_E_taper, col_C_taper, col_G_taper = st.columns(3)
        with col_E_taper:
            user_E_taper_initial = st.number_input(label='Equity return initially (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 12', key='E_taper_initial')
            user_E_taper_final = st.number_input(label='Equity return finally (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 6', key='E_taper_final')
        with col_C_taper:
            user_C_taper_initial = st.number_input(label='Corporate Bond return initially (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 8', key='C_taper_initial')
            user_C_taper_final = st.number_input(label='Corporate Bond return finally (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 5', key='C_taper_final')
        with col_G_taper:
            user_G_taper_initial = st.number_input(label='Govt Bond return initially (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 7', key='G_taper_initial')
            user_G_taper_final = st.number_input(label='Govt Bond return finally (%)', step=0.1, min_value=0.0, max_value=10.0, value=None, 
                                            placeholder='eg. 4', key='G_taper_final')


with st.expander(label='(Optional) Investment Related', expanded=False):
    # Investment Options -- LC50, 25, etc
    # Annuity (for NPS)
    # Corpus withdrawl
    # Gratuity Cap
    col_investment_option, col_annuity_rate, col_withdrawl_percentage, col_max_gratuity = st.columns(4, vertical_alignment='bottom')

    with col_investment_option:
        investment_option = st.selectbox(label='Choose Your Investment Option', options=INVESTMENT_OPTIONS, 
                                         placeholder='Default: Auto LC50', index=None, key='investment_option')
    with col_annuity_rate:
        annuity_rate = st.number_input(label='Annuity Rate', step=0.1, min_value=1.0, max_value=10.0, value=None, 
                                        placeholder='Default: inflation+1% (at retirement)', key='annuity_rate')
    with col_withdrawl_percentage:
        withdrawl_percentage = st.number_input(label='Corpus % withdrawn at retirement', step=1.0, min_value=1.0, max_value=60.0, value=None, 
                                        placeholder='Default: 25%', key='withdrawl_percentage')
    with col_max_gratuity:
        max_gratuity = st.number_input(label='Maximum Gratuity capped by central govt (₹)', step=100, min_value=2500000, max_value=100000000, value=None, 
                                        placeholder='Current: ₹25 Lakh', key='max_gratuity')


# st.write(investment_option, annuity_rate, withdrawl_percentage, max_gratuity)

submit_basic_user_details = st.button(label='Submit')


# st.write(st.session_state)

if submit_basic_user_details:
    # If user entered basic pay is incorrect, stop execution, and display error
    if considering_existing_corpus and starting_level == 0:
        st.toast('Please Enter Correct Basic Pay (Acc to 7th CPC)', icon="🚨")
        st.error('Please Enter Correct Basic Pay (Acc to 7th CPC)', icon="🚨")
        st.stop()

    user_input = {}

    prom_level, prom_period = [], []
    for i in range(8):
        prom_level_key, prom_period_key = f'col_level_year_{i}', f'col_prom_year_{i}'
        prom_level_user, prom_period_user = st.session_state[prom_level_key], st.session_state[prom_period_key]

        if prom_level_user is not None and prom_period_user is not None:
            if prom_period_user > 2000:
                prom_period_user = prom_period_user - joining_year
            prom_level.append(prom_level_user)
            prom_period.append(prom_period_user)
    if len(prom_period) == 0:
        prom_period = [4, 5, 4, 1, 4, 7, 5, 3]

    pc_list, fit_list = [], []
    for i in range(4):
        prom_level_key, prom_period_key = f'col_pc_imp_yrs_{i}', f'col_fit_factor_{i}'
        pc_user, fit_user = st.session_state[prom_level_key], st.session_state[prom_period_key]

        if pc_user is not None and fit_user is not None:
            pc_list.append(pc_user)
            fit_list.append(fit_user)
    if len(pc_list) == 0:
        pc_list = [2026, 2036, 2046, 2056, 2066]
        fit_list = [2, 2, 2, 2, 2]


    if rate_variability == 'Constant':
        if all (rate is not None for rate in [user_inflation_const, user_E_cons, user_C_cons, user_G_cons]):
        # if user_inflation_const is not None:
            initial_inflation_rate = final_inflation_rate = user_inflation_const
            E_initial = E_final = user_E_cons
            C_initial = C_final = user_C_cons
            G_initial = G_final = user_G_cons
        else:
            initial_inflation_rate = final_inflation_rate = 6.0
            E_initial = E_final = 12.0
            C_initial = C_final = 8.0
            G_initial = G_final = 8.0
    else:   # Tapering Case
        if all (rate is not None for rate in [user_inflation_taper_initial, user_inflation_taper_final, user_E_taper_initial, 
                                              user_E_taper_final, user_C_taper_initial, user_C_taper_final, user_G_taper_initial, user_G_taper_final]):
            initial_inflation_rate = user_inflation_taper_initial
            final_inflation_rate = user_inflation_taper_final
            E_initial = user_E_taper_initial
            E_final = user_E_taper_final
            C_initial = user_C_taper_initial
            C_final = user_C_taper_final
            G_initial = user_G_taper_initial
            G_final = user_G_taper_final
        else:
            initial_inflation_rate = 7.0
            final_inflation_rate = 3.0
            E_initial = 12.0
            E_final = 6.0
            C_initial = 8.0
            C_final = 4.0
            G_initial = 8.0
            G_final = 4.0


    if investment_option is None:
        investment_option = INVESTMENT_OPTIONS[2]       # Auto_LC50
    if annuity_rate is None:
        annuity_rate = final_inflation_rate + 1
    if withdrawl_percentage is None:
        withdrawl_percentage = DEFAULT_WITHDRAWL_PERCENTAGE
    if max_gratuity is None:
        max_gratuity = DEFAULT_MAX_GRATUITY

    doj = convert_dt_to_string(dt_doj)
    dor = convert_dt_to_string(dt_dor)

    # 'scheme', 'govt_contrib_percent', 'employee_contrib_percent'  <-- remaining
    user_input['scheme'] = None
    user_input['investment_option'] = investment_option
    user_input['withdrawl_percentage'] = withdrawl_percentage
    user_input['annuity_rate'] = annuity_rate
    user_input['dob'] = dob
    user_input['doj'] = doj
    user_input['early_retirement'] = considering_early_retirement
    user_input['dor'] = dor
    user_input['take_earlier_corpus_into_account'] = considering_existing_corpus
    user_input['earlier_corpus'] = earlier_corpus
    user_input['earlier_corpus_end_date'] = UPS_IMPLEMENT_DATE
    user_input['govt_contrib_percent'] = None
    user_input['employee_contrib_percent'] = None
    user_input['starting_level'] = starting_level
    user_input['starting_year_row_in_level'] = starting_year
    user_input['is_ias'] = is_ias
    user_input['present_pay_matrix_csv'] = PAY_MATRIX_7CPC_CSV
    user_input['promotion_duration_array'] = prom_period
    user_input['pay_commission_implement_years'] = pc_list
    user_input['fitment_factors'] = fit_list
    user_input['initial_inflation_rate'] = initial_inflation_rate
    user_input['final_inflation_rate'] = final_inflation_rate
    user_input['initial_interest_rate'] = None      # Since providing ECG
    user_input['final_interest_rate'] = None
    user_input['taper_period_yrs'] = TAPER_PERIOD
    user_input['pension_duration'] = PENSION_DURATION
    user_input['E_initial'] = E_initial
    user_input['E_final'] = E_final
    user_input['C_initial'] = C_initial
    user_input['C_final'] = C_final
    user_input['G_initial'] = G_initial
    user_input['G_final'] = G_final

    
    # st.write(user_input)

    user_input['scheme'] = 'UPS'
    all_data_ups = get_all_data(**user_input)

    user_input['scheme'] = 'NPS'
    all_data_nps = get_all_data(**user_input)

    # st.write(all_data_ups)

    yearly_corpus_nps = all_data_nps['yearly_corpus']
    yearly_corpus_ups = all_data_ups['yearly_corpus']

    future_pension_matrix_nps = all_data_nps['future_pension_matrix']
    future_pension_matrix_ups = all_data_ups['future_pension_matrix']

    # st.write(yearly_corpus_nps)

    yearly_corpus_comparison = pd.DataFrame({'NPS': yearly_corpus_nps, 'UPS': yearly_corpus_ups})
    future_pension_comparison = pd.DataFrame({'NPS': future_pension_matrix_nps, 'UPS': future_pension_matrix_ups})

    # format_compact_currency(earlier_corpus, 'INR', locale='en_IN', fraction_digits=4)
    # yearly_corpus_comparison['NPS Formatted'] = yearly_corpus_comparison['NPS'].apply(lambda x: format_compact_currency(x, 'INR', locale='en_IN', fraction_digits=4))
    # yearly_corpus_comparison['UPS Formatted'] = yearly_corpus_comparison['UPS'].apply(lambda x: format_compact_currency(x, 'INR', locale='en_IN', fraction_digits=4))
    # yearly_corpus_comparison['NPS Formatted'] = yearly_corpus_comparison['NPS'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
    # yearly_corpus_comparison['UPS Formatted'] = yearly_corpus_comparison['UPS'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))

    # st.write(yearly_corpus_comparison.index)
    # st.write(yearly_corpus_comparison.columns.to_list())

    # st.dataframe(yearly_corpus_comparison)
    # st.dataframe(future_pension_comparison)

    # st.data_editor(yearly_corpus_comparison, column_config={'_index':st.column_config.NumberColumn(format='plain')})


    st.line_chart(yearly_corpus_comparison, y=['NPS', 'UPS'], x_label='Year', y_label='Amount in ₹')
    st.line_chart(future_pension_comparison, y=['NPS', 'UPS'], x_label='Year', y_label='Amount in ₹')

    # st.dataframe(yearly_corpus_nps, hide_index=False)
    # st.dataframe(future_pension_matrix_ups, hide_index=False)

    # # Get All the required data
    # all_ups_data = get_all_data(scheme='UPS', dob=dob, doj=doj, starting_level=starting_level)
    # all_nps_data = get_all_data(scheme='NPS', dob=dob, doj=doj, starting_level=starting_level, annuity_rate=7)

    # all_data = get_all_data(dob=dob, doj=doj, starting_level=starting_level)

    # career_progression = all_data['career_progression']
    # salary_matrix = all_data['salary_matrix']
    # final_corpus_amount = all_data['final_corpus_amount']
    # yearly_corpus = all_data['yearly_corpus']
    # monthly_salary_detailed = all_data['monthly_salary_detailed']
    # withdraw_corpus = all_data['withdraw_corpus']
    # lumpsum_for_ups = all_data['lumpsum_for_ups']
    # adjusted_pension = all_data['adjusted_pension']
    # xirr_corpus = all_data['xirr_corpus']
    # npv = all_data['npv']
    # future_pension_matrix = all_data['future_pension_matrix']

    # st.line_chart(data=yearly_corpus, )
    # st.line_chart(data=future_pension_matrix)


    # st.write(all_data)


    









if __name__ == "__main__":
    

    # 
    # st.dataframe(data=load_csv_into_df('7th_CPC copy.csv'), hide_index=True)
    pass


# st.write(locale.currency(100000000))
# st.write(format_number(100000000, locale='en_IN'))
# st.write(format_currency(100000000, 'INR', locale='en_IN'))
# st.write(format_compact_currency(100000000, 'INR', locale='en_IN'))
# st.write(format_compact_currency(101000000, 'INR', locale='en_IN', fraction_digits=2))
# st.write(format_compact_currency(101000000, 'INR', locale='en_IN', fraction_digits=4))
# st.write(format_compact_currency(1500, 'INR', locale='en_IN', fraction_digits=2))
# st.write(format_compact_currency(100010000, 'INR', locale='en_IN'))
# st.write(format_compact_currency(1000000, 'INR', locale='en_IN'))
# st.write(format_compact_currency(1000100, 'INR', locale='en_IN'))
# Apply formatting to the 'Salary' column  (format_inr() is a function i helper_func)
# df['Salary (INR)'] = df['Salary'].apply(format_inr)      <-- can/shall also use format_inr_no_paise
# st.write(format_compact_currency(101000000, 'INR', locale='en_IN', fraction_digits=2))