"""
NPS vs UPS Pension Calculator - Default Constants Module

This module defines all configuration constants, default values, and system
parameters used throughout the pension calculator application. It serves as
a central configuration file that can be easily modified to adjust system
behavior without changing core logic.

Key Categories:
- Pay Structure: Pay levels, CPC years, fitment factors
- Service Options: Available services, investment strategies
- Financial Defaults: Inflation rates, interest rates, tapering periods
- System Limits: Date ranges, amount limits, validation bounds
- File Paths: Data directory, CSV file names

Author: Pension Calculator Team
Version: 1.0
"""

# =============================================================================
# PAY STRUCTURE CONSTANTS
# =============================================================================

# Available pay levels in the 7th CPC system
# Levels 1-18 represent different hierarchical positions in government service
# Level 10 is typically the starting level for AIS (All India Service) officers
PAY_LEVELS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '13A', '14', '15', '16', '17', '18']

# Investment allocation strategies available to users
# These define how corpus is distributed across Equity (E), Corporate Bonds (C), and Government Bonds (G)
INVESTMENT_OPTIONS = ['Standard/Benchmark', 'Auto_LC25', 'Auto_LC50', 'Auto_LC75', 'Active']

# Available government services for selection
# AIS services have special promotion rules and starting level restrictions
SERVICES = ['IFS (AIS)', 'IAS', 'IPS', 'Other Central Services']

# =============================================================================
# PAY COMMISSION CONSTANTS
# =============================================================================

# Years when future Central Pay Commissions are expected to be implemented
# These years trigger DA reset to 0 and application of fitment factors
DEFAULT_PAY_COMMISSION_YEARS = [2026, 2036, 2046, 2056, 2066]

# Default fitment factor applied to basic pay when new CPC is implemented
# Fitment factor = (1 + DA%) × (1 + Salary Increase %)
DEFAULT_FITMENT_FACTOR = 2

# Default fitment factors for each pay commission (5 CPCs × factor 2)
# Users can override these values in the UI
DEFAULT_FITMENT_FACTORS = [DEFAULT_FITMENT_FACTOR] * 5

# Default percentage increase in salary over and above DA at each CPC
# This is used to calculate fitment factors when user doesn't specify
DEFAULT_PC_INCREASE_PERCENT = 15.0

# List of default salary increase percentages for each CPC
DEFAULT_PC_INCREASE_PERCENT_LIST = [DEFAULT_PC_INCREASE_PERCENT] * 5

# =============================================================================
# SERVICE-SPECIFIC CONSTANTS
# =============================================================================

# Default IAS flag (affects promotion rules)
# IAS officers skip certain levels (13A, 16) during promotions
DEFAULT_IS_IAS = False

# Default promotion timeline for career progression
# Represents years to reach next level: [4, 5, 4, 1, 4, 7, 5, 3]
# Total career duration: 33 years, Average: 4.1 years per promotion
DEFAULT_PROMOTION_TIMELINE = [4, 5, 4, 1, 4, 7, 5, 3]

# =============================================================================
# SYSTEM DATES AND PATHS
# =============================================================================

# Date when UPS (Universal Pension Scheme) is expected to be implemented
# This affects calculations for existing corpus scenarios
UPS_IMPLEMENT_DATE = '01/04/2025'

# Path to the data directory containing CSV files
# All pay matrices, DA data, and generated CPC files are stored here
DATA_FOLDER_PATH = 'assets/data/'

# Main 7th CPC pay matrix file
# This contains the basic pay structure for all levels and years
PAY_MATRIX_7CPC_CSV = '7th_CPC.csv'

# Historical DA (Dearness Allowance) data files
# These contain actual DA percentages from 6th and 7th CPC periods
SIXTH_PC_DA_FILE = '6th_CPC_DA.csv'
SEVENTH_PC_DA_FILE = '7th_CPC_DA.csv'

# Year ranges for historical DA data
# 6th CPC: 2006-2015 (with half-year precision)
SIXTH_PC_DA_START_YEAR = 2006
SIXTH_PC_DA_END_YEAR = 2015.5

# 7th CPC: 2016-2025 (with half-year precision)
SEVENTH_PC_DA_START_YEAR = 2016
SEVENTH_PC_DA_END_YEAR = 2025.5

# Starting year within a pay level for new recruits
# New employees always start at year 1 within their assigned level
STARTING_YEAR_CPC = 1

# =============================================================================
# RETIREMENT AND WITHDRAWAL CONSTANTS
# =============================================================================

# Default percentage of corpus that can be withdrawn at retirement
# NPS allows up to 60% withdrawal, with 40% going to annuity
DEFAULT_WITHDRAWL_PERCENTAGE = 25.00

# Maximum gratuity amount capped by central government
# Current limit is ₹25 lakhs (₹2.5 million)
DEFAULT_MAX_GRATUITY = 2500000

# =============================================================================
# TIME PERIOD CONSTANTS
# =============================================================================

# Default number of years over which interest rates taper
# Longer taper periods result in more gradual rate changes
DEFAULT_TAPER_PERIOD = 40

# Default number of years to project pension after retirement
# This affects future pension calculations and long-term planning
DEFAULT_PENSION_DURATION = 40

# =============================================================================
# FINANCIAL RATE CONSTANTS
# =============================================================================

# Default constant inflation rate (when not using tapering)
# This represents a steady inflation assumption throughout the career
DEFAULT_CONSTANT_INFLATION_RATE = 7.0

# Default investment return rates (constant mode)
# These represent steady returns across the entire career period
DEFAULT_E = 12.0  # Equity returns
DEFAULT_C = 8.0   # Corporate bond returns
DEFAULT_G = 8.0   # Government bond returns

# Default initial rates for tapering mode
# These are the starting rates that gradually change over time
DEFAULT_INITIAL_INFLATION_RATE = 7.0
DEFAULT_E_INITIAL = 12.0
DEFAULT_C_INITIAL = 8.0
DEFAULT_G_INITIAL = 8.0  # Government bonds start at 8% and taper to 4%

# Default final rates for tapering mode
# These are the ending rates after the taper period
DEFAULT_FINAL_INFLATION_RATE = 4.0
DEFAULT_E_FINAL = 6.0
DEFAULT_C_FINAL = 4.0
DEFAULT_G_FINAL = 4.0

# =============================================================================
# CONSTANT DESCRIPTIONS AND USAGE
# =============================================================================

"""
CONSTANT USAGE GUIDE:

1. PAY_LEVELS: Used in UI dropdowns and validation
   - Levels 1-9: Lower administrative positions
   - Level 10: Starting level for AIS officers
   - Levels 11-18: Higher administrative positions
   - Level 13A: Special level (skipped by IAS officers)

2. INVESTMENT_OPTIONS: Defines available investment strategies
   - Standard/Benchmark: Conservative 15% equity allocation
   - Auto_LC25: Lifecycle with 25% max equity (aggressive to conservative)
   - Auto_LC50: Lifecycle with 50% max equity (moderate to conservative) - DEFAULT
   - Auto_LC75: Lifecycle with 75% max equity (very aggressive to conservative)
   - Active: Manual allocation with age-based adjustments

3. PAY_COMMISSION_YEARS: Triggers major salary revisions
   - Each year triggers DA reset to 0
   - Fitment factors are applied to basic pay
   - New pay matrices are generated or loaded

4. FINANCIAL RATES: Drive investment returns and inflation
   - E (Equity): Higher returns, higher risk, tapers from 12% to 6%
   - C (Corporate Bonds): Medium returns, medium risk, tapers from 8% to 4%
   - G (Government Bonds): Lower returns, lower risk, tapers from 8% to 4%

5. TIME PERIODS: Affect calculation granularity
   - Taper period: How quickly rates change (40 years = gradual change)
   - Pension duration: How long to project post-retirement (40 years)

6. WITHDRAWAL AND GRATUITY: Retirement benefit limits
   - Withdrawal: How much corpus can be taken as lumpsum
   - Gratuity: Government-capped retirement benefit

MODIFICATION GUIDELINES:

- PAY_LEVELS: Add new levels if CPC introduces them
- PAY_COMMISSION_YEARS: Update based on government announcements
- FINANCIAL_RATES: Adjust based on market expectations and policy changes
- TIME_PERIODS: Modify based on retirement age changes or planning horizons
- FILE_PATHS: Update if data directory structure changes

VALIDATION RULES:

- All rates must be positive numbers
- Final rates should generally be lower than initial rates (tapering down)
- Pay commission years should be in ascending order
- Fitment factors should typically be >= 1.0
- Time periods should be reasonable (10-100 years)
"""

# =============================================================================
# DEPRECATED OR ALTERNATIVE CONSTANTS
# =============================================================================

# Alternative file path (commented out)
# PAY_MATRIX_7CPC_CSV = 'data/7th_CPC.csv'

# Alternative data loading (commented out)
# PAY_MATRIX_7CPC_DF = load_csv_into_df(PAY_MATRIX_7CPC_CSV)

# =============================================================================
# CONSTANT VALIDATION (for development/testing)
# =============================================================================

def validate_constants():
    """
    Validate that all constants have reasonable values.
    
    This function can be called during development to ensure
    constants are properly configured.
    
    Returns:
        bool: True if all constants are valid
        
    Raises:
        ValueError: If any constant has an invalid value
    """
    # Validate pay levels
    if not all(level.isdigit() or level.endswith('A') for level in PAY_LEVELS):
        raise ValueError("Invalid pay level format in PAY_LEVELS")
    
    # Validate investment options
    if len(INVESTMENT_OPTIONS) < 1:
        raise ValueError("INVESTMENT_OPTIONS cannot be empty")
    
    # Validate pay commission years
    if not all(isinstance(year, int) and year > 2020 for year in DEFAULT_PAY_COMMISSION_YEARS):
        raise ValueError("Pay commission years must be integers > 2020")
    
    # Validate financial rates
    if any(rate < 0 for rate in [DEFAULT_E, DEFAULT_C, DEFAULT_G]):
        raise ValueError("Financial rates cannot be negative")
    
    if DEFAULT_FINAL_INFLATION_RATE > DEFAULT_INITIAL_INFLATION_RATE:
        raise ValueError("Final inflation rate should be <= initial rate")
    
    # Validate time periods
    if DEFAULT_TAPER_PERIOD < 1 or DEFAULT_PENSION_DURATION < 1:
        raise ValueError("Time periods must be positive")
    
    return True


if __name__ == "__main__":
    # Test constant validation
    try:
        validate_constants()
        print("✅ All constants are valid!")
        
        # Display key constants
        print(f"\n📊 Key Configuration:")
        print(f"Pay Levels: {len(PAY_LEVELS)} levels available")
        print(f"Investment Options: {len(INVESTMENT_OPTIONS)} strategies")
        print(f"Pay Commissions: {len(DEFAULT_PAY_COMMISSION_YEARS)} future CPCs")
        print(f"Default Inflation: {DEFAULT_CONSTANT_INFLATION_RATE}%")
        print(f"Default Equity Return: {DEFAULT_E}%")
        print(f"Taper Period: {DEFAULT_TAPER_PERIOD} years")
        print(f"Pension Duration: {DEFAULT_PENSION_DURATION} years")
        
    except ValueError as e:
        print(f"❌ Constant validation failed: {e}")
        exit(1)