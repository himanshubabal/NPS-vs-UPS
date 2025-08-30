"""
NPS vs UPS Pension Calculator - Streamlit Application

A comprehensive pension scheme comparison tool for Indian government employees
to evaluate NPS (National Pension System) vs UPS (Unified Pension Scheme).

Author: Pension Calculator Team
Version: 2.0 - Redesigned Interface
"""

from all_data import get_all_data
from helpers.helper_functions import *
from helpers.helper_functions import format_indian_currency
from default_constants import *
from pay_commissions import get_level_year_from_basic_pay, get_basic_pay
from rates import get_DA_matrix

from babel.numbers import format_number, format_currency, format_compact_currency
from datetime import datetime, date
import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Page Configuration
st.set_page_config(
    page_title="NPS vs UPS Pension Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/nps-vs-ups',
        'Report a bug': "https://github.com/your-repo/nps-vs-ups/issues",
        'About': "## NPS vs UPS Pension Calculator\n\nCompare your retirement benefits between National Pension System (NPS) and Unified Pension Scheme (UPS)."
    }
)

# Load external CSS file
with open('styles/main.css', 'r') as f:
    css_content = f.read()

st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# Development Disclaimer
st.markdown("""
<div class="development-disclaimer">
    <h2>⚠️ DEVELOPMENT VERSION</h2>
    <p class="main-text">
        <strong>This application is currently under active development and may contain bugs or inaccuracies.</strong>
    </p>
    <p class="sub-text">
        Results should not be considered final or used for official pension planning decisions.
    </p>
    <p class="note-text">
        Please report any issues or bugs you encounter.
    </p>
</div>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>💰 NPS vs UPS Pension Calculator</h1>
    <p style="font-size: 1.2rem; margin: 0;">Compare your retirement benefits between <strong>National Pension System (NPS)</strong> and <strong>Unified Pension Scheme (UPS)</strong></p>
</div>
""", unsafe_allow_html=True)

# Load Data
PAY_MATRIX_7CPC_DF = load_csv_into_df(PAY_MATRIX_7CPC_CSV)

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Personal Information Section
    st.markdown("### 👤 Personal Information")
    dob = convert_dt_to_string(st.date_input(
        label='📅 Date of Birth',
        format='DD/MM/YYYY',
        value='1995-01-01',
        min_value='1965-01-01',
        max_value='2005-12-31',
        help='Enter your Date of Birth',
        key='dob'
    ))
    
    doj = convert_dt_to_string(st.date_input(
        label='🏢 Date of Joining',
        format='DD/MM/YYYY',
        value='2024-12-09',
        min_value='2006-01-01',
        max_value='2030-12-31',
        help='Enter your Date of Joining the Service',
        key='doj'
    ))
    
    # Service Selection
    choose_service = st.selectbox(
        label='🎯 Choose Your Service',
        options=SERVICES,
        placeholder='Select your service type',
        index=0,
        key='choose_service',
        help='Different services have different promotion rules and starting levels'
    )
    
    is_ias = choose_service == 'IAS'
    st.session_state['is_ias'] = is_ias
    
    # Early Retirement Option
    considering_early_retirement = st.checkbox(
        label='⏰ Considering Early Retirement',
        key='considering_early_retirement',
        help='Check if you plan to retire before the standard retirement age of 60'
    )
    
    if considering_early_retirement:
        dor = convert_dt_to_string(st.date_input(
            label='🏁 Date of Retirement',
            key='dor',
            min_value='2025-01-01',
            max_value=get_retirement_date(dob),
            help='Enter your planned retirement date'
        ))
    else:
        dor = convert_dt_to_string(get_retirement_date(dob))
        st.info(f"📅 Standard retirement date: {dor}")
    
    # Existing Corpus Section
    st.markdown("### 💰 Existing Corpus (Optional)")
    dt_doj = parse_date(doj)
    if dt_doj < datetime.strptime('01-01-2024', '%d-%m-%Y').date():
        is_considering_early_corpus = True
    else:
        is_considering_early_corpus = False
    
    considering_existing_corpus = st.checkbox(
        label='📊 Consider Existing NPS Corpus',
        key='considering_existing_corpus',
        value=is_considering_early_corpus,
        help='Include existing NPS Tier 1 corpus in calculations'
    )
    
    if considering_existing_corpus:
        earlier_corpus = st.number_input(
            label='💰 Existing NPS Corpus (₹)',
            step=1000,
            min_value=0,
            help='Enter your current NPS Tier 1 corpus amount',
            key='earlier_corpus'
        )
        
        starting_basic_pay = st.number_input(
            label='💵 Current Basic Pay (7th CPC)',
            step=100,
            min_value=0,
            help='Enter your current basic pay according to 7th CPC',
            key='starting_basic_pay'
        )
        
        if starting_basic_pay > 0:
            starting_level, starting_year = get_level_year_from_basic_pay(int(starting_basic_pay), PAY_MATRIX_7CPC_DF)
            if starting_level != 0:
                st.success(f"✅ Pay Level: {starting_level}, Year: {starting_year}")
            else:
                st.error("❌ Invalid Basic Pay. Please check the amount.")
                starting_level = 0
        else:
            starting_level = 0
    else:
        earlier_corpus = None
        st.markdown("### 🎯 Starting Position")
        
        # Starting Level Selection
        pay_levels_list = PAY_LEVELS
        if choose_service != 'Other Central Services':
            pay_levels_list = PAY_LEVELS[PAY_LEVELS.index('10'):]
            st.info(f"🎯 {choose_service} starts from Pay Level 10")
        
        starting_level = st.selectbox(
            label='📊 Starting Pay Level (7th CPC)',
            options=pay_levels_list,
            help='Select your starting pay level',
            key='starting_level'
        )
        starting_year = STARTING_YEAR_CPC
        starting_basic_pay = get_basic_pay(level=starting_level, year=starting_year, pay_matrix_df=PAY_MATRIX_7CPC_DF)
        st.success(f"💰 Starting Basic Pay: {format_indian_currency(starting_basic_pay)}")

# Main Content Area
if starting_level == 0 and considering_existing_corpus:
    st.error("❌ Please enter a valid basic pay amount to continue.")
    st.stop()

# Advanced Configuration Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Career Progression", "💰 Financial Parameters", "🏛️ Pay Commissions", "📊 Investment Options", "💰 Retirement Options"])

with tab1:
    st.markdown("### 📈 Career Progression Settings")
    
    if starting_level != 0:
        joining_year = parse_date(doj).year
        st.info(f"🎯 Your career will start from Pay Level {starting_level} in year {joining_year}")
        
        # Calculate years of service
        retirement_date = get_retirement_date(dob)
        years_of_service = (retirement_date - parse_date(doj)).days / 365.25
        
        # Promotion Schedule
        st.markdown("#### 🚀 Promotion Schedule")
        st.info(f"📅 Years of service: {years_of_service:.1f} years (from {joining_year} to {retirement_date.year})")
        
        with st.container():
            starting_level_index = PAY_LEVELS.index(str(starting_level))
            max_possible_promotions = len(PAY_LEVELS) - starting_level_index - 1
            
            # Limit promotions to actual service years
            max_promotions = min(max_possible_promotions, int(years_of_service))
            
            if max_promotions > 0:
                st.markdown("**Set your promotion timeline:**")
                st.caption(f"💡 Default timeline: {' → '.join(map(str, DEFAULT_PROMOTION_TIMELINE))} years (total: {sum(DEFAULT_PROMOTION_TIMELINE)} years)")
                st.caption(f"📅 **Note**: By default, showing only promotions that fit within your {years_of_service:.1f} years of service")
                
                # Initialize number of promotions - show only what fits within service duration
                if 'num_promotions' not in st.session_state:
                    # Calculate how many promotions can fit within service years
                    cumulative_years = 0
                    max_fitting_promotions = 0
                    for i, years in enumerate(DEFAULT_PROMOTION_TIMELINE):
                        if cumulative_years + years <= years_of_service:
                            max_fitting_promotions = i + 1
                            cumulative_years += years
                        else:
                            break
                    st.session_state.num_promotions = max_fitting_promotions
                
                prom_level, prom_period = [], []
                for curr_level in range(st.session_state.num_promotions):
                    st.markdown(f"---")
                    st.markdown(f"**Promotion {curr_level + 1}:**")
                    
                    col_prom_level, col_prom_year, col_prom_info = st.columns([1.2, 1.2, 1.6])
                    
                    with col_prom_level:
                        next_level = st.selectbox(
                            f'Next Level',
                            options=PAY_LEVELS[starting_level_index + curr_level + 1:],
                            key=f'col_level_year_{curr_level}',
                            help=f'Select the next pay level after {starting_level}'
                        )
                    
                    with col_prom_year:
                        # Default promotion timeline from constants
                        default_timeline = DEFAULT_PROMOTION_TIMELINE
                        default_value = default_timeline[curr_level] if curr_level < len(default_timeline) else 5
                        
                        prom_year = st.number_input(
                            f'Years to reach Level {next_level}',
                            min_value=1,
                            max_value=int(years_of_service),
                            value=default_value,
                            key=f'col_prom_year_{curr_level}',
                            help=f'How many years to reach Level {next_level}'
                        )
                    
                    with col_prom_info:
                        # Show promotion year info in the same row to save vertical space
                        if next_level and prom_year:
                            # Validate total promotion years don't exceed service years
                            total_promotion_years = sum(prom_period) + prom_year
                            if total_promotion_years > years_of_service:
                                st.error(f"⚠️ **Warning**: Total promotion years ({total_promotion_years:.1f}) exceeds your service period ({years_of_service:.1f} years)")
                            else:
                                promotion_year = joining_year + total_promotion_years
                                st.success(f"🎯 **Level {next_level} in {promotion_year}** (after {prom_year} years)")
                        
                        prom_level.append(next_level)
                        prom_period.append(prom_year)
                
                # Add/Remove promotion controls at the end
                st.markdown("---")
                col_add, col_remove = st.columns([1, 1])
                with col_add:
                    if st.button("➕ Add Promotion", key="add_promotion"):
                        if 'num_promotions' not in st.session_state:
                            st.session_state.num_promotions = max_promotions  # Start with all available
                        else:
                            st.session_state.num_promotions = min(st.session_state.num_promotions + 1, max_promotions)
                        st.rerun()
                
                with col_remove:
                    if st.button("➖ Remove Promotion", key="remove_promotion"):
                        if 'num_promotions' in st.session_state:
                            st.session_state.num_promotions = max(1, st.session_state.num_promotions - 1)
                            st.rerun()
                
                if len(prom_period) == 0:
                    prom_period = DEFAULT_PROMOTION_TIMELINE[:max_promotions]
                    st.info("ℹ️ Using default promotion schedule")
                
                # Career Summary moved here to expand horizontal space
                st.markdown("---")
                st.markdown("#### 📊 Career Summary")
                col_summary1, col_summary2, col_summary3 = st.columns(3)
                
                with col_summary1:
                    st.metric("Starting Level", starting_level)
                    st.metric("Starting Year", starting_year)
                
                with col_summary2:
                    st.metric("Years of Service", f"{years_of_service:.1f}")
                    st.metric("Max Possible Promotions", max_promotions)
                
                with col_summary3:
                    if len(prom_period) > 0:
                        st.metric("Total Promotion Years", f"{sum(prom_period)} years")
                        st.metric("Final Year", f"{joining_year + sum(prom_period)}")
                    else:
                        st.metric("Total Promotion Years", "N/A")
                        st.metric("Final Year", "N/A")
                
                if len(prom_period) > 0:
                    st.metric("Avg Promotion Time", f"{sum(prom_period)/len(prom_period):.1f} years")
                
                # Show promotion timeline summary
                if len(prom_period) > 0:
                    st.markdown("---")
                    st.markdown("#### 📅 Promotion Timeline Summary")
                    
                    timeline_data = []
                    cumulative_years = 0
                    current_level = starting_level
                    
                    for i, (level, years) in enumerate(zip(prom_level, prom_period)):
                        cumulative_years += years
                        promotion_year = joining_year + cumulative_years
                        
                        # Calculate correct age using proper date arithmetic
                        from datetime import date
                        dob_date = parse_date(dob)
                        promotion_date = date(promotion_year, dob_date.month, dob_date.day)
                        age_at_promotion = promotion_date.year - dob_date.year
                        
                        # Adjust age if birthday hasn't occurred yet in promotion year
                        if (promotion_date.month < dob_date.month) or (promotion_date.month == dob_date.month and promotion_date.day < dob_date.day):
                            age_at_promotion -= 1
                        
                        timeline_data.append({
                            "Promotion": i + 1,
                            "From Level": current_level,
                            "To Level": level,
                            "Years": years,
                            "Year": promotion_year,
                            "Age": age_at_promotion
                        })
                        current_level = level
                    
                    if timeline_data:
                        timeline_df = pd.DataFrame(timeline_data)
                        # Remove the index column for cleaner display
                        st.dataframe(timeline_df.set_index('Promotion'), use_container_width=True)
                        
                        # Show final career summary
                        final_year = joining_year + sum(prom_period)
                        st.success(f"🎯 **Final Career Summary**: You will reach Level {current_level} in {final_year} at age {timeline_data[-1]['Age']}")
            else:
                st.info("🎯 You're already at the highest pay level or service period too short for promotions")
                prom_period = DEFAULT_PROMOTION_TIMELINE[:max_promotions] if max_promotions > 0 else []
        


with tab2:
    st.markdown("### 💰 Financial Parameters")
    
    # Rate Variability Selection
    rate_variability = st.radio(
        label='📊 Rate Assumptions',
        options=['Constant', 'Variable (Tapering)'],
        index=1,
        help='Choose between constant rates or rates that change over time'
    )
    
    if rate_variability == 'Constant':
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            user_inflation_const = st.number_input(
                label='📈 Inflation Rate (%)',
                step=0.1,
                min_value=0.0,
                max_value=20.0,
                value=DEFAULT_CONSTANT_INFLATION_RATE,
                help='Annual inflation rate throughout your career'
            )
        
        with col2:
            user_E_cons = st.number_input(
                label='📊 Equity Returns (%)',
                step=0.1,
                min_value=0.0,
                max_value=15.0,
                value=DEFAULT_E,
                help='Annual equity investment returns'
            )
        
        with col3:
            user_C_cons = st.number_input(
                label='🏢 Corporate Bond Returns (%)',
                step=0.1,
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_C,
                help='Annual corporate bond returns'
            )
        
        with col4:
            user_G_cons = st.number_input(
                label='🏛️ Government Bond Returns (%)',
                step=0.1,
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_G,
                help='Annual government bond returns'
            )
        
        # Set constant rates
        initial_inflation_rate = final_inflation_rate = user_inflation_const
        E_initial = E_final = user_E_cons
        C_initial = C_final = user_C_cons
        G_initial = G_final = user_G_cons
        
    else:  # Tapering Case
        st.markdown("#### 📈 Rate Tapering Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Inflation Rates**")
            user_inflation_taper_initial = st.number_input(
                label='Initial Inflation (%)',
                step=0.1,
                min_value=0.0,
                max_value=20.0,
                value=DEFAULT_INITIAL_INFLATION_RATE
            )
            user_inflation_taper_final = st.number_input(
                label='Final Inflation (%)',
                step=0.1,
                min_value=0.0,
                max_value=20.0,
                value=DEFAULT_FINAL_INFLATION_RATE
            )
        
        with col2:
            st.markdown("**Investment Returns**")
            col_E, col_C, col_G = st.columns(3)
            
            with col_E:
                st.markdown("**Equity**")
                user_E_taper_initial = st.number_input('Initial (%)', value=DEFAULT_E_INITIAL, key='E_taper_initial')
                user_E_taper_final = st.number_input('Final (%)', value=DEFAULT_E_FINAL, key='E_taper_final')
            
            with col_C:
                st.markdown("**Corporate**")
                user_C_taper_initial = st.number_input('Initial (%)', value=DEFAULT_C_INITIAL, key='C_taper_initial')
                user_C_taper_final = st.number_input('Final (%)', value=DEFAULT_C_FINAL, key='C_taper_final')
            
            with col_G:
                st.markdown("**Government**")
                user_G_taper_initial = st.number_input('Initial (%)', value=DEFAULT_G_INITIAL, key='G_taper_initial')
                user_G_taper_final = st.number_input('Final (%)', value=DEFAULT_G_FINAL, key='G_taper_final')
        
        # Set tapering rates
        initial_inflation_rate = user_inflation_taper_initial
        final_inflation_rate = user_inflation_taper_final
        
        # Validate and normalize investment allocation percentages
        total_initial = user_E_taper_initial + user_C_taper_initial + user_G_taper_initial
        total_final = user_E_taper_final + user_C_taper_final + user_G_taper_final
        
        # Normalize allocation percentages without showing warnings
        if abs(total_initial - 100.0) > 0.01:
            E_initial = (user_E_taper_initial / total_initial) * 100.0
            C_initial = (user_C_taper_initial / total_initial) * 100.0
            G_initial = (user_G_taper_initial / total_initial) * 100.0
        else:
            E_initial = user_E_taper_initial
            C_initial = user_C_taper_initial
            G_initial = user_G_taper_initial
            
        if abs(total_final - 100.0) > 0.01:
            E_final = (user_E_taper_final / total_final) * 100.0
            C_final = (user_C_taper_final / total_final) * 100.0
            G_final = (user_G_taper_final / total_final) * 100.0
        else:
            E_final = user_E_taper_final
            C_final = user_C_taper_final
            G_final = user_G_taper_final
        
        # Store allocation percentages for use in calculations
        # (Display moved to Investment Options section)

with tab3:
    st.markdown("### 🏛️ Pay Commission Settings")
    
    st.info("💡 Pay Commissions are major salary revisions that occur every 10 years. They reset DA to 0 and apply fitment factors.")
    
    # Display Pay Commission Years
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Implementation Years**")
        for i, year in enumerate(DEFAULT_PAY_COMMISSION_YEARS):
            st.metric(f"CPC {i+1}", year)
    
    with col2:
        st.markdown("**Fitment Factors**")
        fit_list = []
        for i in range(len(DEFAULT_PAY_COMMISSION_YEARS)):
            fit_factor = st.number_input(
                f'CPC {i+1} Factor',
                min_value=1.0,
                max_value=5.0,
                value=float(DEFAULT_FITMENT_FACTORS[i]),
                step=0.1,
                key=f'col_fit_factor_{i}',
                help=f'Fitment factor for {DEFAULT_PAY_COMMISSION_YEARS[i]}'
            )
            fit_list.append(fit_factor)
    
    with col3:
        st.markdown("**Salary Increase %**")
        for i in range(len(DEFAULT_PAY_COMMISSION_YEARS)):
            try:
                percent_inc = round(((fit_list[i] / (1 + 0.5/100.0)) - 1) * 100.0, 1)
                st.metric(f"CPC {i+1} Increase", f"{percent_inc}%")
            except:
                st.metric(f"CPC {i+1} Increase", "N/A")

with tab4:
    st.markdown("### 📊 Investment Options")
    
with tab5:
    st.markdown("### 💰 Retirement Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Annuity Rate
        retirement_year = parse_date(dor).year + 0.5 if parse_date(dor).month >= 7 else parse_date(dor).month
        inflation_at_retirement = 6.0  # Default value
        
        annuity_rate = st.number_input(
            label='📊 Annuity Rate (%)',
            step=0.1,
            min_value=1.0,
            max_value=10.0,
            value=inflation_at_retirement + 1,
            help='Rate for converting NPS corpus to monthly pension'
        )
    
    with col2:
        # Withdrawal Percentage
        withdrawl_percentage = st.number_input(
            label='💸 Corpus Withdrawal (%)',
            step=1.0,
            min_value=1.0,
            max_value=60.0,
            value=DEFAULT_WITHDRAWL_PERCENTAGE,
            help='Percentage of corpus to withdraw at retirement'
        )
    
    with col3:
        # Maximum Gratuity
        max_gratuity = st.number_input(
            label='🎁 Maximum Gratuity (₹)',
            help='Government-capped gratuity amount',
            step=100000,
            min_value=2500000,
            max_value=100000000,
            value=DEFAULT_MAX_GRATUITY
        )
    
    # Investment Strategy Selection
    investment_option = st.selectbox(
        label='🎯 Investment Strategy',
        options=INVESTMENT_OPTIONS,
        index=2,  # Default to Auto_LC50
        help='Choose how your corpus will be invested across Equity, Corporate Bonds, and Government Bonds'
    )
    
    # Display Investment Strategy Details and Allocation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📈 Strategy Details")
        strategy_descriptions = {
            'Standard/Benchmark': 'Conservative approach with 15% equity allocation',
            'Auto_LC25': 'Aggressive to conservative with max 25% equity',
            'Auto_LC50': 'Moderate to conservative with max 50% equity (Recommended)',
            'Auto_LC75': 'Very aggressive to conservative with max 75% equity',
            'Active': 'Manual allocation with age-based adjustments'
        }
        st.info(strategy_descriptions.get(investment_option, 'Custom investment strategy'))
    
    with col2:
        st.markdown("#### 📊 Asset Allocation")
        
        # Display normalized allocation percentages
        if 'E_initial' in locals() and 'E_final' in locals():
            st.markdown("**Initial Allocation**")
            st.metric("Equity", f"{E_initial:.1f}%")
            st.metric("Corporate", f"{C_initial:.1f}%")
            st.metric("Government", f"{G_initial:.1f}%")
            st.metric("Total", f"{E_initial + C_initial + G_initial:.1f}%")
            
            st.markdown("**Final Allocation**")
            st.metric("Equity", f"{E_final:.1f}%")
            st.metric("Corporate", f"{C_final:.1f}%")
            st.metric("Government", f"{G_final:.1f}%")
            st.metric("Total", f"{E_final + C_final + G_final:.1f}%")
            
            # Yearwise Allocation Table and Plot
            st.markdown("---")
            st.markdown("**📈 Yearwise Allocation Progression**")
            
            # Calculate years of service for allocation progression
            if 'doj' in locals() and 'dor' in locals():
                try:
                    doj_date = parse_date(doj)
                    dor_date = parse_date(dor)
                    years_of_service = (dor_date - doj_date).days / 365.25
                    
                    # Create yearwise allocation data
                    years = list(range(int(doj_date.year), int(dor_date.year) + 1))
                    allocation_data = []
                    
                    for year in years:
                        # Linear interpolation between initial and final allocations
                        progress = (year - doj_date.year) / years_of_service if years_of_service > 0 else 0
                        progress = min(1.0, max(0.0, progress))  # Clamp between 0 and 1
                        
                        E_year = E_initial + (E_final - E_initial) * progress
                        C_year = C_initial + (C_final - C_initial) * progress
                        G_year = G_initial + (G_final - G_initial) * progress
                        
                        allocation_data.append({
                            'Year': year,
                            'Equity (%)': round(E_year, 1),
                            'Corporate (%)': round(C_year, 1),
                            'Government (%)': round(G_year, 1),
                            'Total (%)': round(E_year + C_year + G_year, 1)
                        })
                    
                    # Display yearwise allocation table
                    if allocation_data:
                        df_allocation = pd.DataFrame(allocation_data)
                        st.dataframe(
                            df_allocation,
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Year": st.column_config.NumberColumn("Year", format="%d"),
                                "Equity (%)": st.column_config.NumberColumn("Equity (%)", format="%.1f%%"),
                                "Corporate (%)": st.column_config.NumberColumn("Corporate (%)", format="%.1f%%"),
                                "Government (%)": st.column_config.NumberColumn("Government (%)", format="%.1f%%"),
                                "Total (%)": st.column_config.NumberColumn("Total (%)", format="%.1f%%")
                            }
                        )
                        
                        # Create allocation progression plot
                        fig_allocation = go.Figure()
                        
                        # Add traces for each asset class
                        fig_allocation.add_trace(go.Scatter(
                            x=[row['Year'] for row in allocation_data],
                            y=[row['Equity (%)'] for row in allocation_data],
                            mode='lines+markers',
                            name='Equity',
                            line=dict(color='#ff9800', width=3),
                            marker=dict(size=6)
                        ))
                        
                        fig_allocation.add_trace(go.Scatter(
                            x=[row['Year'] for row in allocation_data],
                            y=[row['Corporate (%)'] for row in allocation_data],
                            mode='lines+markers',
                            name='Corporate',
                            line=dict(color='#2196f3', width=3),
                            marker=dict(size=6)
                        ))
                        
                        fig_allocation.add_trace(go.Scatter(
                            x=[row['Year'] for row in allocation_data],
                            y=[row['Government (%)'] for row in allocation_data],
                            mode='lines+markers',
                            name='Government',
                            line=dict(color='#4caf50', width=3),
                            marker=dict(size=6)
                        ))
                        
                        # Update layout
                        fig_allocation.update_layout(
                            title="Asset Allocation Progression Over Years",
                            xaxis_title="Year",
                            yaxis_title="Allocation Percentage (%)",
                            height=400,
                            showlegend=True,
                            template='plotly_white',
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="center",
                                x=0.5
                            ),
                            yaxis=dict(
                                range=[0, 100],
                                tickformat=".0f"
                            )
                        )
                        
                        st.plotly_chart(fig_allocation, use_container_width=True)
                        
                except Exception as e:
                    st.warning(f"⚠️ Could not calculate yearwise allocation: {str(e)}")
        else:
            st.info("💡 Set allocation percentages in Financial Parameters tab to see details here")



# Calculate Results Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    calculate_button = st.button(
        "🚀 Calculate Pension Comparison",
        type="primary",
        use_container_width=True,
        help="Click to calculate and compare NPS vs UPS benefits"
    )

# Results Section
if calculate_button:
    st.markdown("---")
    
    # Show calculation progress
    with st.spinner("🔄 Calculating your pension benefits..."):
        try:
            # Prepare user input
            user_input = {
                'scheme': 'UPS',
                'investment_option': investment_option,
                'withdrawl_percentage': withdrawl_percentage,
                'annuity_rate': annuity_rate,
                'dob': dob,
                'doj': doj,
                'early_retirement': considering_early_retirement,
                'dor': dor,
                'take_earlier_corpus_into_account': considering_existing_corpus,
                'earlier_corpus': earlier_corpus,
                'earlier_corpus_end_date': UPS_IMPLEMENT_DATE,
                # Contribution percentages are automatically set based on scheme:
                # NPS: Employee 10%, Government 14%
                # UPS: Employee 10%, Government 10%
                'starting_level': starting_level,
                'starting_year_row_in_level': starting_year,
                'is_ias': is_ias,
                'present_pay_matrix_csv': PAY_MATRIX_7CPC_CSV,
                'promotion_duration_array': prom_period,
                'pay_commission_implement_years': DEFAULT_PAY_COMMISSION_YEARS,
                'fitment_factors': fit_list if 'fit_list' in locals() else DEFAULT_FITMENT_FACTORS,
                'initial_inflation_rate': initial_inflation_rate,
                'final_inflation_rate': final_inflation_rate,
                'initial_interest_rate': 12.0,  # Initial investment return rate
                'final_interest_rate': 6.0,  # Final investment return rate
                'taper_period_yrs': DEFAULT_TAPER_PERIOD,
                'pension_duration': DEFAULT_PENSION_DURATION,
                'E_initial': E_initial,
                'E_final': E_final,
                'C_initial': C_initial,
                'C_final': C_final,
                'G_initial': G_initial,
                'G_final': G_final
            }
            
            # Get UPS data
            all_data_ups = get_all_data(**user_input)
            
            # Get NPS data
            user_input['scheme'] = 'NPS'
            all_data_nps = get_all_data(**user_input)
            
            st.success("✅ Calculations completed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error during calculation: {str(e)}")
            st.stop()
    
    # Results Display
    st.markdown("## 📊 Results & Comparison")
    
    # Key Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Final Corpus</h3>
            <h2>₹{:,}</h2>
            <p>Total accumulated amount</p>
        </div>
        """.format(all_data_ups['final_corpus_amount']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Monthly Pension</h3>
            <h2>₹{:,}</h2>
            <p>Starting pension amount</p>
        </div>
        """.format(all_data_ups['adjusted_pension']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 XIRR</h3>
            <h2>{:.1f}%</h2>
            <p>Investment return rate</p>
        </div>
        """.format(all_data_ups['xirr_corpus']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 NPV</h3>
            <h2>₹{:,}</h2>
            <p>Present value adjusted</p>
        </div>
        """.format(all_data_ups['npv']), unsafe_allow_html=True)
    
    # Detailed Comparison
    st.markdown("## 🔍 Detailed Comparison")
    
    col_ups, col_nps = st.columns(2)
    
    with col_ups:
        st.markdown("""
        <div class="comparison-card ups-card">
            <h3>🏛️ UPS (Unified Pension Scheme)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        ups_metrics = {
            "Final Corpus": format_indian_currency(all_data_ups['final_corpus_amount']),
            "Monthly Pension": format_indian_currency(all_data_ups['adjusted_pension']),
            "Withdrawal Amount": format_indian_currency(all_data_ups['withdraw_corpus']),
            "Lumpsum": format_indian_currency(all_data_ups['lumpsum_for_ups']),
            "XIRR": f"{all_data_ups['xirr_corpus']:.1f}%",
            "NPV": format_indian_currency(all_data_ups['npv'])
        }
        
        for metric, value in ups_metrics.items():
            st.metric(metric, value)
    
    with col_nps:
        st.markdown("""
        <div class="comparison-card nps-card">
            <h3>📊 NPS (National Pension System)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        nps_metrics = {
            "Final Corpus": format_indian_currency(all_data_nps['final_corpus_amount']),
            "Monthly Pension": format_indian_currency(all_data_nps['adjusted_pension']),
            "Withdrawal Amount": format_indian_currency(all_data_nps['withdraw_corpus']),
            "Lumpsum": "₹0 (No lumpsum)",
            "XIRR": f"{all_data_nps['xirr_corpus']:.1f}%",
            "NPV": format_indian_currency(all_data_nps['npv'])
        }
        
        for metric, value in nps_metrics.items():
            st.metric(metric, value)
    
    # Visualizations
    st.markdown("## 📈 Visual Analysis")
    
    # Corpus Growth Chart
    st.markdown("### 💰 Corpus Growth Over Time")
    
    yearly_corpus_nps = all_data_nps['yearly_corpus']
    yearly_corpus_ups = all_data_ups['yearly_corpus']
    
    # Create Plotly chart for corpus growth
    fig_corpus = go.Figure()
    
    # Add UPS line
    fig_corpus.add_trace(go.Scatter(
        x=list(yearly_corpus_ups.keys()),
        y=list(yearly_corpus_ups.values()),
        mode='lines+markers',
        name='UPS',
        line=dict(color='#2196f3', width=3),
        marker=dict(size=6)
    ))
    
    # Add NPS line
    fig_corpus.add_trace(go.Scatter(
        x=list(yearly_corpus_nps.keys()),
        y=list(yearly_corpus_nps.values()),
        mode='lines+markers',
        name='NPS',
        line=dict(color='#4caf50', width=3),
        marker=dict(size=6)
    ))
    
    fig_corpus.update_layout(
        title="Corpus Growth Comparison",
        xaxis_title="Year",
        yaxis_title="Corpus Amount (₹)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    # Update hover template to show Indian formatting
    fig_corpus.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>" +
                     "Year: %{x}<br>" +
                     "Corpus: ₹%{y:,.0f}<br>" +
                     "<extra></extra>"
    )
    
    st.plotly_chart(fig_corpus, use_container_width=True)
    
    # Pension Projection Chart
    st.markdown("### 📊 Future Pension Projection")
    
    future_pension_matrix_nps = all_data_nps['future_pension_matrix']
    future_pension_matrix_ups = all_data_ups['future_pension_matrix']
    
    fig_pension = go.Figure()
    
    # Add UPS pension line
    fig_pension.add_trace(go.Scatter(
        x=list(future_pension_matrix_ups.keys()),
        y=list(future_pension_matrix_ups.values()),
        mode='lines+markers',
        name='UPS Pension',
        line=dict(color='#2196f3', width=3),
        marker=dict(size=6)
    ))
    
    # Add NPS pension line
    fig_pension.add_trace(go.Scatter(
        x=list(future_pension_matrix_nps.keys()),
        y=list(future_pension_matrix_nps.values()),
        mode='lines+markers',
        name='NPS Pension',
        line=dict(color='#4caf50', width=3),
        marker=dict(size=6)
    ))
    
    fig_pension.update_layout(
        title="Monthly Pension Projection",
        xaxis_title="Year",
        yaxis_title="Monthly Pension (₹)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    # Update hover template to show Indian formatting
    fig_pension.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>" +
                     "Year: %{x}<br>" +
                     "Monthly Pension: ₹%{y:,.0f}<br>" +
                     "<extra></extra>"
    )
    
    st.plotly_chart(fig_pension, use_container_width=True)
    
    # Recommendation Section
    st.markdown("## 🎯 Recommendation")
    
    # Calculate recommendation score
    weights = {
        'Monthly Pension at Start (₹)': 0.35,
        '10-year Pension Total (₹)': 0.25,
        'Total Withdrawal at Retirement (₹)': 0.15,
        'Final Corpus (₹)': 0.15,
        'NPV (₹)': 0.05,
        'XIRR (%)': 0.05,
    }
    
    # Calculate 10-year pension totals
    def ten_year_pension_total(future_pension_matrix, years=10):
        keys_sorted = sorted(future_pension_matrix.keys())
        take = [future_pension_matrix[k] for k in keys_sorted[:years * 2]]
        return int(sum(v * 6 for v in take))
    
    ten_year_pension_ups = ten_year_pension_total(future_pension_matrix_ups, 10)
    ten_year_pension_nps = ten_year_pension_total(future_pension_matrix_nps, 10)
    
    # Build comparison metrics
    metrics_data = [
        {'Metric': 'Final Corpus (₹)', 'UPS': all_data_ups['final_corpus_amount'], 'NPS': all_data_nps['final_corpus_amount']},
        {'Metric': 'Total Withdrawal at Retirement (₹)', 'UPS': all_data_ups['withdraw_corpus'] + all_data_ups['lumpsum_for_ups'] + max_gratuity, 'NPS': all_data_nps['withdraw_corpus'] + max_gratuity},
        {'Metric': 'Monthly Pension at Start (₹)', 'UPS': all_data_ups['adjusted_pension'], 'NPS': all_data_nps['adjusted_pension']},
        {'Metric': '10-year Pension Total (₹)', 'UPS': ten_year_pension_ups, 'NPS': ten_year_pension_nps},
        {'Metric': 'NPV (₹)', 'UPS': all_data_ups['npv'], 'NPS': all_data_nps['npv']},
        {'Metric': 'XIRR (%)', 'UPS': all_data_ups['xirr_corpus'], 'NPS': all_data_nps['xirr_corpus']},
    ]
    
    # Calculate scores
    scores = {'UPS': 0.0, 'NPS': 0.0}
    reasons = {'UPS': [], 'NPS': []}
    
    for m, w in weights.items():
        v_ups = float(next(item['UPS'] for item in metrics_data if item['Metric'] == m))
        v_nps = float(next(item['NPS'] for item in metrics_data if item['Metric'] == m))
        
        if v_ups > v_nps:
            scores['UPS'] += w
            reasons['UPS'].append(m)
        elif v_nps > v_ups:
            scores['NPS'] += w
            reasons['NPS'].append(m)
    
    winner = 'UPS' if scores['UPS'] > scores['NPS'] else ('NPS' if scores['NPS'] > scores['UPS'] else 'Tie')
    score_pct_ups = int(round(scores['UPS'] * 100))
    score_pct_nps = int(round(scores['NPS'] * 100))
    
    # Display recommendation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏛️ UPS Score</h3>
            <h2>{score_pct_ups}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 NPS Score</h3>
            <h2>{score_pct_nps}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if winner == 'Tie':
            st.markdown("""
            <div class="success-box">
                <h3>🤝 Both schemes perform similarly</h3>
                <p>Consider qualitative factors like risk appetite and liquidity preferences to make your decision.</p>
            </div>
            """, unsafe_allow_html=True)
        elif winner == 'UPS':
            st.markdown(f"""
            <div class="success-box">
                <h3>🏆 Recommended: UPS</h3>
                <p>UPS performs better based on your inputs. Key advantages:</p>
                <ul>
                    <li>{', '.join(reasons['UPS'][:3])}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="success-box">
                <h3>🏆 Recommended: NPS</h3>
                <p>NPS performs better based on your inputs. Key advantages:</p>
                <ul>
                    <li>{', '.join(reasons['NPS'][:3])}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed Metrics Table
    st.markdown("### 📊 Detailed Metrics Comparison")
    
    df_metrics = pd.DataFrame(metrics_data)
    df_metrics['Difference'] = df_metrics['UPS'] - df_metrics['NPS']
    df_metrics['Winner'] = df_metrics['Difference'].apply(lambda x: 'UPS' if x > 0 else ('NPS' if x < 0 else 'Tie'))
    
    # Format the table with Indian currency formatting
    def format_indian_currency_df(value):
        """Format value for dataframe display in Indian currency style"""
        if pd.isna(value):
            return ""
        if isinstance(value, (int, float)):
            return format_indian_currency(value)
        return str(value)
    
    # Apply formatting to numeric columns
    df_metrics_formatted = df_metrics.copy()
    numeric_columns = ['UPS', 'NPS', 'Difference']
    for col in numeric_columns:
        df_metrics_formatted[col] = df_metrics_formatted[col].apply(format_indian_currency_df)
    
    st.dataframe(
        df_metrics_formatted,
        column_config={
            "Winner": st.column_config.SelectboxColumn("Winner", options=["UPS", "NPS", "Tie"])
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Career Progression Summary
    st.markdown("### 📈 Career Progression Summary")
    
    career_progression = all_data_ups['career_progression']
    salary_matrix = all_data_ups['salary_matrix']
    
    if career_progression and salary_matrix:
        df_career = pd.DataFrame(career_progression)
        df_career['Year'] = df_career['Year'].astype(str)
        df_career.set_index('Year', inplace=True)
        
        # Create combined career progression chart (both metrics on same plot)
        fig_career = go.Figure()
        
        # Basic Pay line
        fig_career.add_trace(
            go.Scatter(
                x=df_career.index,
                y=df_career['Basic Pay'],
                mode='lines+markers',
                name='Basic Pay',
                line=dict(color='#ff9800', width=3),
                yaxis='y'
            )
        )
        
        # Level progression - handle special levels like '13A'
        def convert_level_to_numeric(level_str):
            """Convert level string to numeric value for plotting."""
            try:
                if level_str == '13A':
                    return 13.5  # Place 13A between 13 and 14
                else:
                    return float(level_str)
            except:
                return 0.0
        
        level_numeric = df_career['Level'].apply(convert_level_to_numeric)
        
        # Level progression line (secondary y-axis)
        fig_career.add_trace(
            go.Scatter(
                x=df_career.index,
                y=level_numeric,
                mode='lines+markers',
                name='Pay Level',
                line=dict(color='#9c27b0', width=3),
                yaxis='y2'
            )
        )
        
        # Update layout for combined chart with dual y-axes
        fig_career.update_layout(
            title="Career Progression: Basic Pay & Level Progression",
            height=500,
            showlegend=True,
            template='plotly_white',
            xaxis=dict(title="Year"),
            yaxis=dict(
                title=dict(text="Basic Pay (₹)", font=dict(color="#ff9800")),
                tickfont=dict(color="#ff9800"),
                side="left"
            ),
            yaxis2=dict(
                title=dict(text="Pay Level", font=dict(color="#9c27b0")),
                tickfont=dict(color="#9c27b0"),
                side="right",
                overlaying="y",
                range=[0, max(level_numeric) + 1]  # Set appropriate range for levels
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update hover templates to show Indian formatting
        fig_career.data[0].hovertemplate = (
            "<b>Basic Pay</b><br>" +
            "Year: %{x}<br>" +
            "Basic Pay: ₹%{y:,.0f}<br>" +
            "<extra></extra>"
        )
        fig_career.data[1].hovertemplate = (
            "<b>Pay Level</b><br>" +
            "Year: %{x}<br>" +
            "Level: %{y}<br>" +
            "<extra></extra>"
        )
        
        st.plotly_chart(fig_career, use_container_width=True)
    
    # Additional Information
    st.markdown("## ℹ️ Additional Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h4>💡 About UPS</h4>
            <ul>
                <li>Unified Pension Scheme for government employees</li>
                <li>Provides lumpsum at retirement</li>
                <li>Monthly pension based on service duration</li>
                <li>Employee contribution: 10%</li>
                <li>Government contribution: 10%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h4>💡 About NPS</h4>
            <ul>
                <li>National Pension System with market-linked returns</li>
                <li>60% corpus withdrawal allowed</li>
                <li>40% must be used for annuity</li>
                <li>Employee contribution: 10%</li>
                <li>Government contribution: 14%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>💰 NPS vs UPS Pension Calculator | Built with Streamlit</p>
    <p>⚠️ This calculator provides estimates based on current policies. Please consult financial advisors for actual planning.</p>
</div>
""", unsafe_allow_html=True)