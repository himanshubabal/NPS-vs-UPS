from all_data import get_all_data
from helper_functions import *
from pay_commissions import get_level_year_from_basic_pay, get_basic_pay

# import locale
# import babel
from babel.numbers import format_number, format_currency, format_compact_currency
import streamlit as st

UPS_IMPLEMENT_DATE = '01/04/2025'
DATA_CPC_PATH = 'data/'
PAY_MATRIX_7CPC_DF = load_csv_into_df('data/7th_CPC.csv')
STARTING_YEAR_CPC = 1       # Since new joining starts at year one only
PAY_LEVELS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '13A', '14', '15', '16', '17', '18']

# locale.setlocale(locale.LC_ALL, 'en_IN')
st.set_page_config(
    page_title="NPS v/s UPS",
    page_icon="data/pension_2.png",
    # layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title("NPS v/s UPS")


st.write('Enter Your Details')
dt_dob = st.date_input(label='Date of Birth', format='DD/MM/YYYY', value='1995-01-01', 
                    min_value='1965-01-01', max_value='2005-12-31', help='Enter your Date of Birth')

# If DOJ is before 7th CPC (ie. before 1st Jan 2016 -> do what?)
# (also, historic data of DA shall be considered)

considering_existing_corpus = st.checkbox(label='Consider Existing NPS Tier 1 Corpus')

if considering_existing_corpus:
    # Consider Joining from 'UPS_IMPLEMENT_DATE' if considering_existing_corpus
    dt_doj = parse_date(UPS_IMPLEMENT_DATE)
    
    # Ask user to input existing corpus value
    earlier_corpus = int(st.number_input(label='Existing NPS Tier 1 corpus as on Today (in ₹)', step=100))
    earlier_corpus_formatted = format_compact_currency(earlier_corpus, 'INR', locale='en_IN', fraction_digits=4)
    # Display the corpus value
    st.write(f'Your Corpus till 1st April 2025: {earlier_corpus_formatted}')

    # Ask user to enter current Basic Pay
    starting_basic_pay = st.number_input(label='Current Basic Pay (Acc to 7th CPC)', step=100)
    # Get/Verify Pay Level
    starting_level, starting_year = get_level_year_from_basic_pay(int(starting_basic_pay), PAY_MATRIX_7CPC_DF)
    # IF wrong Pay Level entered, warn user; else display par level and year
    if starting_level == 0 or starting_year == 0:
        st.warning('Please Enter Correct Basic Pay (Acc to 7th CPC)')
    else:
        st.write(f'Pay Level: {starting_level},  Pay Year Index: {starting_year}')
else:   # If considering for a new recruitment, ask user the relevant details
    dt_doj = st.date_input(label='Date of Joining', format='DD/MM/YYYY', value='2024-12-09', 
                    min_value='1985-01-01', max_value='2030-12-31', help='Enter your Date of Joining the Service')
    starting_level = st.selectbox(label='Starting Pay Level (7th CPC)', index=9, options=PAY_LEVELS)
    starting_year = STARTING_YEAR_CPC       # Since new joining starts at year one only
    starting_basic_pay = get_basic_pay(level=starting_level, year=starting_year, pay_matrix_df=PAY_MATRIX_7CPC_DF)
    st.write(f'Basic Pay: {starting_basic_pay}')
    # ??????????????????????? -- For now, considering only those who joined after 7th CPC was implemented
    # starting_pay_commission = st.selectbox(label='Starting Pay Commission', index=1, options=['6th CPC', '7th CPC'])

with st.expander(label='Advance Configuration', expanded=False, icon=None):
    st.write('Expanded')
    # Promotion aspect
    # Pay commission aspect
    joining_year = dt_doj.year
    with st.form(key='promotion_form'):
        st.write('Promotion Details')
        col_prom_level, col_prom_year = st.columns(2)
        with col_prom_level:
            st.text_input(label='Level')
            st.text_input(label='Level')
            st.text_input(label='Level')
            st.text_input(label='Level')
            st.text_input(label='Level')
            st.text_input(label='Level')
            st.text_input(label='Level')
            st.text_input(label='Level')
        with col_prom_year:
            st.text_input (label='Period / Year')
            st.text_input (label='Period / Year')
            st.text_input (label='Period / Year')
            st.text_input (label='Period / Year')
            st.text_input (label='Period / Year')
            st.text_input (label='Period / Year')
            st.text_input (label='Period / Year')
            st.text_input (label='Period / Year')
        # st.text_input(label='Pay Level')
        # st.text_input (label='Period / Year')
        # add_row = st.button(label='Add Row')
        # if add_row:
        #     add_row(0, col_prom_year, col_prom_level)
        st.form_submit_button(label='Submit')


# def add_row(row, col_prom_level, col_prom_year):
#     with col_prom_level:
#         st.text_input(label='Level')
#     with col_prom_year:
#         st.text_input (label='Period / Year')


submit_basic_user_details = st.button(label='Submit')


if submit_basic_user_details:
    # If user entered basic pay is incorrect, stop execution, and display error
    if considering_existing_corpus and starting_level == 0:
        st.toast('Please Enter Correct Basic Pay (Acc to 7th CPC)', icon="🚨")
        st.error('Please Enter Correct Basic Pay (Acc to 7th CPC)', icon="🚨")
        st.stop()

    # Get DoB and DoJ in string format (since all my functions expect string input in dates)
    dob = convert_dt_to_string(dt_dob)
    doj = convert_dt_to_string(dt_doj)

    # Get All the required data
    all_ups_data = get_all_data(scheme='UPS', dob=dob, doj=doj, starting_level=starting_level)
    all_nps_data = get_all_data(scheme='NPS', dob=dob, doj=doj, starting_level=starting_level, annuity_rate=7)

    all_data = get_all_data(dob=dob, doj=doj, starting_level=starting_level)

    career_progression = all_data['career_progression']
    salary_matrix = all_data['salary_matrix']
    final_corpus_amount = all_data['final_corpus_amount']
    yearly_corpus = all_data['yearly_corpus']
    monthly_salary_detailed = all_data['monthly_salary_detailed']
    withdraw_corpus = all_data['withdraw_corpus']
    lumpsum_for_ups = all_data['lumpsum_for_ups']
    adjusted_pension = all_data['adjusted_pension']
    xirr_corpus = all_data['xirr_corpus']
    npv = all_data['npv']
    future_pension_matrix = all_data['future_pension_matrix']

    st.line_chart(data=yearly_corpus, )
    st.line_chart(data=future_pension_matrix)


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