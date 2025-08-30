"""
NPS vs UPS Pension Calculator - Main Application

A comprehensive pension scheme comparison tool for Indian government employees.
This application helps users evaluate National Pension System (NPS) vs Universal 
Pension Scheme (UPS) based on their career parameters and financial assumptions.

Key Features:
- Career progression simulation with customizable promotion timelines
- Financial modeling with inflation and interest rate projections
- Investment allocation strategies (Equity, Corporate Bonds, Government Bonds)
- Side-by-side comparison of NPS vs UPS benefits
- Interactive visualizations and detailed financial metrics

Author: Pension Calculator Team
Version: 2.0 - Refactored and Modular
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import utility modules
from utils.date_utils import parse_date, convert_dt_to_string, get_retirement_date
from utils.formatting import format_currency_amount, format_compact_currency_amount
from utils.validation import validate_user_inputs

# Import core calculation modules
from all_data import get_all_data
from default_constants import *

# Page Configuration
st.set_page_config(
    page_title="NPS vs UPS Pension Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/nps-vs-ups',
        'Report a bug': "https://github.com/your-repo/nps-vs-ups/issues",
        'About': "## NPS vs UPS Pension Calculator\n\nCompare your retirement benefits between National Pension System (NPS) and Universal Pension Scheme (UPS)."
    }
)

# Custom CSS for better styling and visibility
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .section-header {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 2rem 0 1rem 0;
    }
    .comparison-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border: 2px solid #e0e0e0;
    }
    .ups-card {
        border-color: #2196f3;
    }
    .nps-card {
        border-color: #4caf50;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        padding: 0 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1rem;
        padding: 10px 20px;
        margin: 0 0.5rem;
        color: #333 !important;
        font-weight: 500;
        border: 1px solid #ddd;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white !important;
        border-color: #667eea;
    }
    .stTabs [aria-selected="false"] {
        background-color: #ffffff;
        color: #333 !important;
        border-color: #ddd;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e8f0fe;
        border-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>💰 NPS vs UPS Pension Calculator</h1>
    <p style="font-size: 1.2rem; margin: 0;">Compare your retirement benefits between <strong>National Pension System (NPS)</strong> and <strong>Universal Pension Scheme (UPS)</strong></p>
</div>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_pay_matrix():
    """Load and cache the 7th CPC pay matrix."""
    try:
        return pd.read_csv(PAY_MATRIX_7CPC_CSV)
    except Exception as e:
        st.error(f"Error loading pay matrix: {e}")
        return None

PAY_MATRIX_7CPC_DF = load_pay_matrix()

if PAY_MATRIX_7CPC_DF is None:
    st.error("❌ Failed to load pay matrix. Please check data files.")
    st.stop()

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Personal Information Section
    st.markdown("### 👤 Personal Information")
    
    dob = convert_dt_to_string(st.date_input(
        label='📅 Date of Birth',
        format='DD/MM/YYYY',
        value='1995-01-01',
        key='dob',
        help='Your date of birth (affects retirement age)'
    ))
    
    doj = convert_dt_to_string(st.date_input(
        label='🏢 Date of Joining',
        format='DD/MM/YYYY',
        value='2024-10-10',
        key='doj',
        help='Date when you joined government service'
    ))
    
    # Early Retirement Option
    considering_early_retirement = st.checkbox(
        label='🕐 Considering Early Retirement?',
        value=False,
        key='considering_early_retirement',
        help='Check if you want to retire before standard retirement age'
    )
    
    if considering_early_retirement:
        dor = convert_dt_to_string(st.date_input(
            label='🏁 Early Retirement Date',
            format='DD/MM/YYYY',
            value='2040-01-01',
            key='dor',
            help='Your planned early retirement date'
        ))
    else:
        dor = convert_dt_to_string(get_retirement_date(dob))
        st.info(f"📅 Standard retirement date: {dor}")
    
    # Service Type
    st.markdown("### 🎖️ Service Configuration")
    
    service_type = st.selectbox(
        label='🏛️ Service Type',
        options=SERVICES,
        index=0,
        key='service_type',
        help='Your government service type (affects promotion rules)'
    )
    
    is_ias = (service_type == 'IAS')
    
    # Starting Level and Year
    starting_level = st.selectbox(
        label='📊 Starting Pay Level',
        options=PAY_LEVELS,
        index=PAY_LEVELS.index('10'),
        key='starting_level',
        help='Your starting pay level in 7th CPC system'
    )
    
    starting_year = st.number_input(
        label='📅 Starting Year in Level',
        min_value=1,
        max_value=40,
        value=1,
        key='starting_year',
        help='Year within your starting pay level'
    )
    
    # Existing Corpus Section
    st.markdown("### 💰 Existing NPS Corpus")
    
    considering_existing_corpus = st.checkbox(
        label='💼 Have Existing NPS Corpus?',
        value=False,
        key='considering_existing_corpus',
        help='Check if you have existing NPS Tier 1 corpus'
    )
    
    if considering_existing_corpus:
        earlier_corpus = st.number_input(
            label='💰 Current NPS Corpus (₹)',
            step=1000,
            min_value=0,
            max_value=10000000,
            value=100000,
            key='earlier_corpus',
            help='Your current NPS Tier 1 corpus amount'
        )
        st.info(f"📊 Current corpus: {format_compact_currency_amount(earlier_corpus)}")
    
    # Financial Parameters Section
    st.markdown("### 💹 Financial Parameters")
    
    # Investment Strategy
    investment_option = st.selectbox(
        label='📈 Investment Strategy',
        options=INVESTMENT_OPTIONS,
        index=INVESTMENT_OPTIONS.index('Auto_LC50'),
        key='investment_option',
        help='Investment allocation strategy for your corpus'
    )
    
    # Inflation and Interest Rates
    rate_mode = st.radio(
        label='📊 Rate Mode',
        options=['Constant', 'Variable (tapering)'],
        index=1,
        key='rate_mode',
        help='Choose between constant or variable rates'
    )
    
    if rate_mode == 'Constant':
        initial_inflation_rate = st.number_input(
            label='📈 Constant Inflation Rate (%)',
            step=0.1,
            min_value=0.0,
            max_value=20.0,
            value=DEFAULT_CONSTANT_INFLATION_RATE,
            key='initial_inflation_rate',
            help='Constant inflation rate throughout career'
        )
        final_inflation_rate = initial_inflation_rate
        
        E_initial = st.number_input(
            label='📊 Constant Equity Return (%)',
            step=0.1,
            min_value=0.0,
            max_value=20.0,
            value=DEFAULT_E,
            key='E_initial',
            help='Constant equity return rate'
        )
        E_final = E_initial
        
        C_initial = st.number_input(
            label='📊 Constant Corporate Bond Return (%)',
            step=0.1,
            min_value=0.0,
            max_value=15.0,
            value=DEFAULT_C,
            key='C_initial',
            help='Constant corporate bond return rate'
        )
        C_final = C_initial
        
        G_initial = st.number_input(
            label='📊 Constant Government Bond Return (%)',
            step=0.1,
            min_value=0.0,
            max_value=12.0,
            value=DEFAULT_G,
            key='G_initial',
            help='Constant government bond return rate'
        )
        G_final = G_initial
        
    else:  # Variable (tapering) mode
        col1, col2 = st.columns(2)
        
        with col1:
            initial_inflation_rate = st.number_input(
                label='📈 Initial Inflation Rate (%)',
                step=0.1,
                min_value=0.0,
                max_value=20.0,
                value=DEFAULT_INITIAL_INFLATION_RATE,
                key='initial_inflation_rate',
                help='Starting inflation rate'
            )
            
            E_initial = st.number_input(
                label='📊 Initial Equity Return (%)',
                step=0.1,
                min_value=0.0,
                max_value=20.0,
                value=DEFAULT_E_INITIAL,
                key='E_initial',
                help='Starting equity return rate'
            )
            
            C_initial = st.number_input(
                label='📊 Initial Corporate Bond Return (%)',
                step=0.1,
                min_value=0.0,
                max_value=15.0,
                value=DEFAULT_C_INITIAL,
                key='C_initial',
                help='Starting corporate bond return rate'
            )
            
            G_initial = st.number_input(
                label='📊 Initial Government Bond Return (%)',
                step=0.1,
                min_value=0.0,
                max_value=12.0,
                value=DEFAULT_G_INITIAL,
                key='G_initial',
                help='Starting government bond return rate'
            )
        
        with col2:
            final_inflation_rate = st.number_input(
                label='📉 Final Inflation Rate (%)',
                step=0.1,
                min_value=0.0,
                max_value=20.0,
                value=DEFAULT_FINAL_INFLATION_RATE,
                key='final_inflation_rate',
                help='Ending inflation rate'
            )
            
            E_final = st.number_input(
                label='📉 Final Equity Return (%)',
                step=0.1,
                min_value=0.0,
                max_value=20.0,
                value=DEFAULT_E_FINAL,
                key='E_final',
                help='Ending equity return rate'
            )
            
            C_final = st.number_input(
                label='📉 Final Corporate Bond Return (%)',
                step=0.1,
                min_value=0.0,
                max_value=15.0,
                value=DEFAULT_C_FINAL,
                key='C_final',
                help='Ending corporate bond return rate'
            )
            
            G_final = st.number_input(
                label='📉 Final Government Bond Return (%)',
                step=0.1,
                min_value=0.0,
                max_value=12.0,
                value=DEFAULT_G_FINAL,
                key='G_final',
                help='Ending government bond return rate'
            )
    
    # Retirement Options Section
    st.markdown("### 🎯 Retirement Options")
    
    # Annuity Rate
    retirement_year = parse_date(dor).year + 0.5 if parse_date(dor).month >= 7 else parse_date(dor).year
    inflation_at_retirement = 6.0  # Default value
    
    annuity_rate = st.number_input(
        label='📊 Annuity Rate (%)',
        step=0.1,
        min_value=1.0,
        max_value=10.0,
        value=inflation_at_retirement + 1,
        key='annuity_rate',
        help='Rate for converting NPS corpus to monthly pension'
    )
    
    # Withdrawal Percentage
    withdrawl_percentage = st.number_input(
        label='💸 Corpus Withdrawal (%)',
        step=1.0,
        min_value=1.0,
        max_value=60.0,
        value=DEFAULT_WITHDRAWL_PERCENTAGE,
        key='withdrawl_percentage',
        help='Percentage of corpus to withdraw at retirement'
    )

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
                'earlier_corpus': earlier_corpus if considering_existing_corpus else None,
                'earlier_corpus_end_date': UPS_IMPLEMENT_DATE,
                'govt_contrib_percent': 14.0,  # Government contribution percentage
                'employee_contrib_percent': 10.0,  # Employee contribution percentage
                'starting_level': starting_level,
                'starting_year_row_in_level': starting_year,
                'is_ias': is_ias,
                'present_pay_matrix_csv': PAY_MATRIX_7CPC_CSV,
                'promotion_duration_array': [4, 5, 4, 1, 4, 7, 5, 3],  # Default promotion schedule
                'pay_commission_implement_years': DEFAULT_PAY_COMMISSION_YEARS,
                'fitment_factors': DEFAULT_FITMENT_FACTORS,
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
            
            # Validate user inputs
            is_valid, validation_errors = validate_user_inputs(user_input)
            if not is_valid:
                st.error("❌ Input validation failed:")
                for error in validation_errors:
                    st.error(f"  • {error}")
                st.stop()
            
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
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Final Corpus</h3>
            <h2>{format_compact_currency_amount(all_data_ups['final_corpus_amount'])}</h2>
            <p>Total accumulated amount</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Monthly Pension</h3>
            <h2>{format_compact_currency_amount(all_data_ups['adjusted_pension'])}</h2>
            <p>Starting pension amount</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 XIRR</h3>
            <h2>{all_data_ups['xirr_corpus']:.1f}%</h2>
            <p>Investment return rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 NPV</h3>
            <h2>{format_compact_currency_amount(all_data_ups['npv'])}</h2>
            <p>Present value adjusted</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed Comparison
    st.markdown("## 🔍 Detailed Comparison")
    
    col_ups, col_nps = st.columns(2)
    
    with col_ups:
        st.markdown("""
        <div class="comparison-card ups-card">
            <h3>🏛️ UPS (Universal Pension Scheme)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        ups_metrics = {
            "Final Corpus": format_compact_currency_amount(all_data_ups['final_corpus_amount']),
            "Monthly Pension": format_compact_currency_amount(all_data_ups['adjusted_pension']),
            "Withdrawal Amount": format_compact_currency_amount(all_data_ups['withdraw_corpus']),
            "Lumpsum": format_compact_currency_amount(all_data_ups['lumpsum_for_ups']),
            "XIRR": f"{all_data_ups['xirr_corpus']:.1f}%",
            "NPV": format_compact_currency_amount(all_data_ups['npv'])
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
            "Final Corpus": format_compact_currency_amount(all_data_nps['final_corpus_amount']),
            "Monthly Pension": format_compact_currency_amount(all_data_nps['adjusted_pension']),
            "Withdrawal Amount": format_compact_currency_amount(all_data_nps['withdraw_corpus']),
            "Lumpsum": "₹0 (No lumpsum)",
            "XIRR": f"{all_data_nps['xirr_corpus']:.1f}%",
            "NPV": format_compact_currency_amount(all_data_nps['npv'])
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
        legend=dict(x=0.02, y=0.98),
        height=500
    )
    
    st.plotly_chart(fig_corpus, use_container_width=True)
    
    # Recommendation
    st.markdown("## 🎯 Recommendation")
    
    # Calculate recommendation based on key metrics
    ups_score = 0
    nps_score = 0
    
    # Monthly pension comparison (40% weight)
    if all_data_ups['adjusted_pension'] > all_data_nps['adjusted_pension']:
        ups_score += 40
    else:
        nps_score += 40
    
    # Final corpus comparison (30% weight)
    if all_data_ups['final_corpus_amount'] > all_data_nps['final_corpus_amount']:
        ups_score += 30
    else:
        nps_score += 30
    
    # XIRR comparison (20% weight)
    if all_data_ups['xirr_corpus'] > all_data_nps['xirr_corpus']:
        ups_score += 20
    else:
        nps_score += 20
    
    # NPV comparison (10% weight)
    if all_data_ups['npv'] > all_data_nps['npv']:
        ups_score += 10
    else:
        nps_score += 10
    
    # Display recommendation
    if ups_score > nps_score:
        st.success("🏆 **Recommendation: UPS (Universal Pension Scheme)**")
        st.info(f"**Score: UPS {ups_score}% vs NPS {nps_score}%**")
        st.markdown("""
        **Why UPS is better for you:**
        - Higher monthly pension
        - Better corpus growth
        - Higher investment returns
        - Better present value
        """)
    else:
        st.success("🏆 **Recommendation: NPS (National Pension System)**")
        st.info(f"**Score: NPS {nps_score}% vs UPS {ups_score}%**")
        st.markdown("""
        **Why NPS is better for you:**
        - Higher monthly pension
        - Better corpus growth
        - Higher investment returns
        - Better present value
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>💰 NPS vs UPS Pension Calculator | Built with Streamlit</p>
    <p>This calculator provides estimates based on current government policies. Please consult financial advisors for actual retirement planning.</p>
</div>
""", unsafe_allow_html=True)
