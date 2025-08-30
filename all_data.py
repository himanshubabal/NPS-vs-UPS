"""
NPS vs UPS Pension Calculator - Data Aggregation Module

This module serves as the central orchestrator for all pension calculations.
It coordinates between different calculation modules and provides a unified
interface for the Streamlit application.

Key Functions:
- get_all_data(): Main entry point for all calculations
- main_function(): Orchestrates the calculation pipeline
- auto_pass_arguments_to_function(): Smart argument filtering

Data Flow:
1. User inputs → get_all_data() → parameter validation
2. Interest rate tapering → rates module → investment returns
3. Career progression → pay_commissions module → level/pay changes
4. Salary matrix → salary module → monthly breakdown
5. Contributions → contribution module → corpus growth
6. Retirement benefits → pension module → final amounts
7. Financial metrics → pension module → NPV, XIRR, projections

Author: Pension Calculator Team
Version: 1.0
"""

import pprint
from typing import Union, Dict, Any, Tuple

from pension import *
from pay_commissions import career_progression
from salary import get_salary_matrix, get_monthly_salary
from contribution import get_final_corpus


def get_all_data(scheme: str = 'UPS', 
                 investment_option: str = 'Auto_LC50', 
                 withdrawl_percentage: float = 60.00, 
                 annuity_rate: float = None, 
                 dob: str = '01/01/1996', 
                 doj: str = '10/10/2024', 
                 early_retirement: bool = False, 
                 dor: str = None, 
                 take_earlier_corpus_into_account: bool = False, 
                 earlier_corpus: int = None, 
                 earlier_corpus_end_date: str = None, 
                 govt_contrib_percent: float = None,  
                 employee_contrib_percent: float = None, 
                 starting_level: Union[int, str] = 10, 
                 starting_year_row_in_level: int = 1, 
                 is_ias: bool = False, 
                 present_pay_matrix_csv: str = '7th_CPC.csv', 
                 promotion_duration_array: list[int] = [4, 5, 4, 1, 4, 7, 5, 3], 
                 pay_commission_implement_years: list[int] = [2026, 2036, 2046, 2056, 2066], 
                 fitment_factors: list[int] = [2, 2, 2, 2, 2], 
                 initial_inflation_rate: float = 7.0, 
                 final_inflation_rate: float = 4.0, 
                 initial_interest_rate: float = 12.0, 
                 final_interest_rate: float = 6.0, 
                 taper_period_yrs: int = 40, 
                 pension_duration: int = 40, 
                 E_initial: float = 12.0, 
                 E_final: float = 6.0,
                 C_initial: float = 8.0, 
                 C_final: float = 4.0,
                 G_initial: float = 8.0, 
                 G_final: float = 4.0
                 ) -> Dict[str, Any]:
    """
    Main entry point for all pension calculations.
    
    This function orchestrates the entire calculation pipeline by:
    1. Building interest rate tapering dictionary
    2. Calling main_function with all parameters
    3. Returning comprehensive results for both schemes
    
    Args:
        scheme (str): Pension scheme - 'UPS' or 'NPS'
        investment_option (str): Investment strategy (Auto_LC25, Auto_LC50, etc.)
        withdrawl_percentage (float): Percentage of corpus to withdraw at retirement
        annuity_rate (float): Annuity rate for NPS (defaults to inflation + 1%)
        dob (str): Date of birth in DD/MM/YYYY format
        doj (str): Date of joining service in DD/MM/YYYY format
        early_retirement (bool): Whether considering early retirement
        dor (str): Date of retirement (required if early_retirement=True)
        take_earlier_corpus_into_account (bool): Include existing NPS corpus
        earlier_corpus (int): Amount of existing NPS corpus
        earlier_corpus_end_date (str): Date until which existing corpus is valid
        govt_contrib_percent (float): Government contribution percentage
        employee_contrib_percent (float): Employee contribution percentage
        starting_level (Union[int, str]): Starting pay level (7th CPC)
        starting_year_row_in_level (int): Year within the starting level
        is_ias (bool): Whether IAS service (affects promotion rules)
        present_pay_matrix_csv (str): CSV file for current pay matrix
        promotion_duration_array (list[int]): Years between promotions
        pay_commission_implement_years (list[int]): Years when CPCs are implemented
        fitment_factors (list[int]): Fitment factors for each CPC
        initial_inflation_rate (float): Starting inflation rate
        final_inflation_rate (float): Ending inflation rate
        taper_period_yrs (int): Years over which rates taper
        pension_duration (int): Years to project pension after retirement
        E_initial (float): Initial equity return rate
        E_final (float): Final equity return rate
        C_initial (float): Initial corporate bond return rate
        C_final (float): Final corporate bond return rate
        G_initial (float): Initial government bond return rate
        G_final (float): Final government bond return rate
    
    Returns:
        Dict[str, Any]: Comprehensive calculation results including:
            - da_matrix: Dearness Allowance projections
            - career_progression: Level and pay progression
            - salary_matrix: Basic pay + DA over time
            - final_corpus_amount: Total corpus at retirement
            - yearly_corpus: Year-by-year corpus growth
            - monthly_salary_detailed: Monthly salary breakdown
            - withdraw_corpus: Amount withdrawn at retirement
            - lumpsum_for_ups: UPS lumpsum benefit
            - adjusted_pension: Monthly pension amount
            - inflation_factor: Cumulative inflation factor
            - npv: Net Present Value
            - xirr_corpus: Extended Internal Rate of Return
            - future_pension_matrix: Pension projections post-retirement
    
    Raises:
        ValueError: If scheme is not 'UPS' or 'NPS'
        ValueError: If early retirement is True but dor is not provided
        ValueError: If taking earlier corpus into account but corpus/date not provided
    
    Example:
        >>> results = get_all_data(
        ...     scheme='UPS',
        ...     dob='01/01/1995',
        ...     doj='01/01/2024',
        ...     starting_level=10,
        ...     investment_option='Auto_LC50'
        ... )
        >>> print(f"Final Corpus: ₹{results['final_corpus_amount']:,}")
        >>> print(f"Monthly Pension: ₹{results['adjusted_pension']:,}")
    """
    
    # TODO: Add comprehensive parameter validation here
    
    # Build interest rate tapering dictionary for investment calculations
    # This defines how E (Equity), C (Corporate Bonds), G (Government Bonds)
    # returns change from initial to final values over the taper period
    interest_rate_tapering_dict = get_interest_rate_tapering_dict(
        E_initial=E_initial, 
        E_final=E_final,
        C_initial=C_initial, 
        C_final=C_final,
        G_initial=G_initial, 
        G_final=G_final,
        taper_period_yrs=taper_period_yrs
    )

    # Call main calculation function with all parameters
    all_data = main_function(
        scheme=scheme, 
        investment_option=investment_option, 
        withdrawl_percentage=withdrawl_percentage, 
        annuity_rate=annuity_rate, 
        dob=dob, 
        doj=doj, 
        early_retirement=early_retirement, 
        dor=dor, 
        take_earlier_corpus_into_account=take_earlier_corpus_into_account, 
        earlier_corpus=earlier_corpus, 
        earlier_corpus_end_date=earlier_corpus_end_date, 
        govt_contrib_percent=govt_contrib_percent,  
        employee_contrib_percent=employee_contrib_percent, 
        starting_level=starting_level, 
        starting_year_row_in_level=starting_year_row_in_level, 
        is_ias=is_ias, 
        present_pay_matrix_csv=present_pay_matrix_csv, 
        promotion_duration_array=promotion_duration_array, 
        pay_commission_implement_years=pay_commission_implement_years, 
        fitment_factors=fitment_factors, 
        initial_inflation_rate=initial_inflation_rate, 
        final_inflation_rate=final_inflation_rate, 
        initial_interest_rate=initial_interest_rate, 
        final_interest_rate=final_interest_rate, 
        taper_period_yrs=taper_period_yrs, 
        pension_duration=pension_duration,
        interest_rate_tapering_dict=interest_rate_tapering_dict
    )
    
    return all_data


def main_function(**kwargs) -> Dict[str, Any]:
    """
    Orchestrates the main calculation pipeline.
    
    This function coordinates all calculation modules in the correct sequence:
    1. DA Matrix: Dearness Allowance projections
    2. Career Progression: Level and pay advancement
    3. Salary Matrix: Basic pay + DA calculations
    4. Final Corpus: Contribution and investment returns
    5. Retirement Benefits: Pension, lumpsum, withdrawal
    6. Financial Metrics: NPV, XIRR, future projections
    
    Args:
        **kwargs: All parameters passed from get_all_data()
    
    Returns:
        Dict[str, Any]: Complete calculation results
    
    Note:
        The function uses auto_pass_arguments_to_function() to intelligently
        filter parameters for each sub-function, ensuring only relevant
        arguments are passed.
    """
    all_data = {}

    # Step 0: Calculate DA Matrix (Dearness Allowance projections)
    # This combines historical DA data with projected inflation rates
    # and resets DA to 0 at each Pay Commission implementation year
    da_matrix = auto_pass_arguments_to_function(get_DA_matrix, **kwargs)

    # Step 1: Calculate Career Progression
    # Simulates the employee's career path including:
    # - Annual increments (mid-year)
    # - Promotions (year-end)
    # - Pay Commission implementations
    # - Level and pay changes over time
    career_progn = auto_pass_arguments_to_function(career_progression, **kwargs)
    
    # Step 2: Calculate Salary Matrix
    # Combines career progression with DA matrix to compute:
    # - Basic pay at each career stage
    # - DA percentage at each half-year
    # - Total salary (Basic + DA) over career span
    salary_matrix = auto_pass_arguments_to_function(get_salary_matrix, **kwargs)
    
    # Store basic data for further calculations
    all_data['da_matrix'] = da_matrix
    all_data['career_progression'] = career_progn
    all_data['salary_matrix'] = salary_matrix

    # Step 3: Calculate Final Corpus
    # This is the core calculation that determines:
    # - Monthly salary breakdown
    # - Employee and government contributions
    # - Investment returns based on age-based allocation
    # - Corpus growth over the entire career
    final_corpus_amount, yearly_corpus, monthly_salary_detailed = auto_pass_arguments_to_function(
        get_final_corpus, **kwargs
    )
    
    all_data['final_corpus_amount'] = final_corpus_amount
    all_data['yearly_corpus'] = yearly_corpus
    all_data['monthly_salary_detailed'] = monthly_salary_detailed

    # Add newly calculated variables to kwargs for next functions
    kwargs['final_corpus_amount'] = final_corpus_amount
    kwargs['monthly_salary_detailed'] = monthly_salary_detailed
    
    # Step 4: Calculate Retirement Benefits
    # Determines what the employee receives at retirement:
    # - Monthly pension amount
    # - Lumpsum payment (UPS only)
    # - Total withdrawal amount
    # - Adjusted pension based on withdrawal percentage
    withdraw_corpus, lumpsum_for_ups, adjusted_pension = auto_pass_arguments_to_function(
        get_final_amounts_all, **kwargs
    )
    
    all_data['withdraw_corpus'] = withdraw_corpus
    all_data['lumpsum_for_ups'] = lumpsum_for_ups
    all_data['adjusted_pension'] = adjusted_pension

    # Add new variables to kwargs for final calculations
    kwargs['amount'] = final_corpus_amount
    kwargs['adjusted_pension'] = adjusted_pension
    
    # Step 5: Calculate Financial Metrics
    # Provides comprehensive financial analysis:
    # - Inflation factor for NPV calculations
    # - Net Present Value of final corpus
    # - Extended Internal Rate of Return
    # - Future pension projections post-retirement
    
    # NPV calculation with inflation adjustment
    inflation_factor, npv = auto_pass_arguments_to_function(get_npv_for_given_inflation, **kwargs)
    
    # XIRR calculation for investment performance
    xirr_corpus = auto_pass_arguments_to_function(get_xirr, **kwargs)
    
    # Future pension projections
    future_pension_matrix = auto_pass_arguments_to_function(get_future_pension, **kwargs)

    # Store all financial metrics
    all_data['xirr_corpus'] = xirr_corpus
    all_data['npv'] = npv
    all_data['inflation_factor'] = inflation_factor
    all_data['future_pension_matrix'] = future_pension_matrix

    return all_data


if __name__ == "__main__":
    # Test the module with default parameters
    print("Testing NPS vs UPS Pension Calculator - Data Module")
    print("=" * 60)
    
    # Run with default parameters
    test_results = get_all_data()
    
    # Display key results
    print(f"Final Corpus Amount: ₹{test_results['final_corpus_amount']:,}")
    print(f"Monthly Pension: ₹{test_results['adjusted_pension']:,}")
    print(f"XIRR: {test_results['xirr_corpus']:.2f}%")
    print(f"NPV: ₹{test_results['npv']:,}")
    
    # Show complete results structure
    print("\nComplete Results Structure:")
    pprint.pprint(test_results)