from all_data import get_all_data
from helper_functions import *

import streamlit as st


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

st.title("Hello World....!!!")

with st.form('Basic User Details'):
    st.write('Enter Your Details')
    dt_dob = st.date_input(label='Date of Birth', format='DD/MM/YYYY', value='1995-01-01', 
                        min_value='1965-01-01', max_value='2005-12-31', help='Enter your Date of Birth')
    dt_doj = st.date_input(label='Date of Joining', format='DD/MM/YYYY', value='2024-12-09', 
                        min_value='1985-01-01', max_value='2030-12-31', help='Enter your Date of Joining the Service')
    starting_level = st.selectbox(label='Starting Pay Level (7th CPC)', index=9, options=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '13A', '14', '15', '16', '17', '18'])
    # starting_basic_pay = get_basic_pay()  --> can get starting year from it
    starting_pay_commission = st.selectbox(label='Starting Pay Commission', index=1, options=['6th CPC', '7th CPC'])
    submit_basic_user_details = st.form_submit_button('Submit')

if submit_basic_user_details:
    dob = convert_dt_to_string(dt_dob)
    doj = convert_dt_to_string(dt_doj)

    all_ups_data = get_all_data(scheme='UPS', dob=dob, doj=doj, starting_level=starting_level)
    all_nps_data = get_all_data(scheme='NPS', dob=dob, doj=doj, starting_level=starting_level)

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


    st.write(all_data)


    


if __name__ == "__main__":


    # 
    st.dataframe(data=load_csv_into_df('7th_CPC copy.csv'), hide_index=True)
