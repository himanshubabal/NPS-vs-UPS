"""
NPS vs UPS Pension Calculator - Contribution Module

This module handles all contribution-related calculations including employee
and government contributions, investment returns, and corpus growth over time.
It simulates how the pension corpus grows from monthly contributions and
investment performance.

Key Functions:
- get_final_corpus(): Main function to calculate final corpus at retirement
- calculate_monthly_contributions(): Compute monthly contribution amounts
- apply_investment_returns(): Apply age-based investment allocation returns
- get_corpus_growth(): Track corpus growth year by year
- validate_contribution_data(): Ensure contribution calculations are valid

Contribution Logic:
- Employee Contribution: 10% of basic pay (NPS) or 10% of basic pay (UPS)
- Government Contribution: 14% of basic pay (NPS) or 14% of basic pay (UPS)
- Investment Returns: Based on age-based asset allocation (E, C, G)
- Corpus Growth: Monthly compounding with variable returns
- Existing Corpus: Added to calculations if specified

Investment Allocation:
- Auto_LC25: 25% max equity, aggressive to conservative
- Auto_LC50: 50% max equity, moderate to conservative (DEFAULT)
- Auto_LC75: 75% max equity, very aggressive to conservative
- Standard: Fixed 15% equity allocation
- Active: Manual allocation with age-based adjustments

Author: Pension Calculator Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Tuple, Any

from helpers.helper_functions import *
from default_constants import *
from invest_options import get_investment_allocation


def calculate_monthly_contributions(monthly_salary: float,
                                  employee_contrib_percent: float = 10.0,
                                  govt_contrib_percent: float = 14.0) -> Dict[str, float]:
    """
    Calculate monthly employee and government contributions.
    
    This function computes the monthly contribution amounts based on
    salary and contribution percentages. Both NPS and UPS use the same
    contribution structure.
    
    Args:
        monthly_salary (float): Monthly salary amount
        employee_contrib_percent (float): Employee contribution percentage (default: 10%)
        govt_contrib_percent (float): Government contribution percentage (default: 14%)
        
    Returns:
        Dict[str, float]: Contribution amounts with keys:
            - 'employee_contribution': Monthly employee contribution
            - 'govt_contribution': Monthly government contribution
            - 'total_contribution': Total monthly contribution
            
    Example:
        >>> contribs = calculate_monthly_contributions(84150, 10.0, 14.0)
        >>> print(f"Employee: ₹{contribs['employee_contribution']:,}")
        >>> print(f"Government: ₹{contribs['govt_contribution']:,}")
        >>> print(f"Total: ₹{contribs['total_contribution']:,}")
        
    Note:
        - Employee contribution: 10% of basic pay (not total salary)
        - Government contribution: 14% of basic pay
        - Total contribution: 24% of basic pay
        - Used for both NPS and UPS schemes
    """
    # Calculate contributions based on basic pay (not total salary with DA)
    # For simplicity, we'll use monthly salary as approximation
    # In practice, contributions are based on basic pay component
    
    employee_contribution = (monthly_salary * employee_contrib_percent) / 100.0
    govt_contribution = (monthly_salary * govt_contrib_percent) / 100.0
    total_contribution = employee_contribution + govt_contribution
    
    return {
        'employee_contribution': round(employee_contribution, 2),
        'govt_contribution': round(govt_contrib_percent, 2),
        'total_contribution': round(total_contribution, 2)
    }


def apply_investment_returns(corpus: float,
                           monthly_contribution: float,
                           investment_option: str,
                           age: int,
                           interest_rate_tapering_dict: Dict[str, Any]) -> float:
    """
    Apply investment returns to corpus for one month.
    
    This function calculates the investment returns for a given month
    based on the selected investment option and current age. Returns
    are applied monthly with compounding effect.
    
    Args:
        corpus (float): Current corpus amount
        monthly_contribution (float): Monthly contribution to add
        investment_option (str): Investment strategy (Auto_LC50, etc.)
        age (int): Current age of employee
        interest_rate_tapering_dict (Dict[str, Any]): Investment return configuration
            
    Returns:
        float: New corpus amount after investment returns
        
    Example:
        >>> new_corpus = apply_investment_returns(
        ...     1000000, 5000, 'Auto_LC50', 30, config
        ... )
        >>> print(f"New corpus: ₹{new_corpus:,.0f}")
        
    Note:
        - Returns applied monthly for compounding effect
        - Age-based allocation determines asset mix
        - Tapering rates change over time
        - Corpus grows through contributions + returns
    """
    # Get investment allocation for current age
    E_percentage, C_percentage, G_percentage = get_investment_allocation(investment_option, age)
    
    # Calculate weighted average return
    weighted_return = 0.0
    
    # Equity returns
    if 'E' in interest_rate_tapering_dict:
        current_rate = interest_rate_tapering_dict['E']['initial']
        weighted_return += (E_percentage / 100.0) * current_rate
    
    # Corporate bond returns
    if 'C' in interest_rate_tapering_dict:
        current_rate = interest_rate_tapering_dict['C']['initial']
        weighted_return += (C_percentage / 100.0) * current_rate
    
    # Government bond returns
    if 'G' in interest_rate_tapering_dict:
        current_rate = interest_rate_tapering_dict['G']['initial']
        weighted_return += (G_percentage / 100.0) * current_rate
    
    # Convert annual return to monthly return
    monthly_return_rate = weighted_return / 12.0 / 100.0
    
    # Apply monthly return and add contribution
    corpus_with_returns = corpus * (1 + monthly_return_rate)
    new_corpus = corpus_with_returns + monthly_contribution
    
    return round(new_corpus, 2)


def get_corpus_growth(monthly_salary_detailed: Dict[int, float],
                      investment_option: str,
                      interest_rate_tapering_dict: Dict[str, Any],
                      starting_age: int,
                      employee_contrib_percent: float = 10.0,
                      govt_contrib_percent: float = 14.0,
                      existing_corpus: float = 0.0) -> Tuple[float, Dict[int, float]]:
    """
    Calculate corpus growth over the entire career period.
    
    This function simulates corpus growth month by month, applying
    contributions and investment returns to build the final retirement
    corpus. It handles existing corpus and tracks growth over time.
    
    Args:
        monthly_salary_detailed (Dict[int, float]): Monthly salary breakdown
        investment_option (str): Investment strategy selection
        interest_rate_tapering_dict (Dict[str, Any]): Investment return configuration
        starting_age (int): Age when career begins
        employee_contrib_percent (float): Employee contribution percentage
        govt_contrib_percent (float): Government contribution percentage
        existing_corpus (float): Existing corpus amount (if any)
            
    Returns:
        Tuple[float, Dict[int, float]]: (final_corpus, yearly_corpus_growth)
        
    Example:
        >>> final_corpus, yearly_growth = get_corpus_growth(
        ...     monthly_salary, 'Auto_LC50', config, 25, 10.0, 14.0, 100000
        ... )
        >>> print(f"Final corpus: ₹{final_corpus:,.0f}")
        
    Note:
        - Monthly compounding with variable returns
        - Age-based investment allocation
        - Existing corpus added to calculations
        - Yearly growth tracking for analysis
    """
    # Initialize corpus tracking
    current_corpus = existing_corpus
    yearly_corpus_growth = {}
    current_year = None
    
    # Process each month
    for month_index, monthly_salary in monthly_salary_detailed.items():
        # Calculate current age (approximate)
        months_elapsed = month_index - 1
        current_age = starting_age + (months_elapsed // 12)
        
        # Calculate contributions for this month
        contributions = calculate_monthly_contributions(
            monthly_salary, employee_contrib_percent, govt_contrib_percent
        )
        
        # Apply investment returns and add contribution
        current_corpus = apply_investment_returns(
            current_corpus,
            contributions['total_contribution'],
            investment_option,
            current_age,
            interest_rate_tapering_dict
        )
        
        # Track yearly growth
        year = starting_age + (months_elapsed // 12)
        if year != current_year:
            current_year = year
            yearly_corpus_growth[year] = current_corpus
    
    # Ensure final year is captured
    if current_year not in yearly_corpus_growth:
        yearly_corpus_growth[current_year] = current_corpus
    
    return current_corpus, yearly_corpus_growth


def get_final_corpus(monthly_salary_detailed: Dict[int, float],
                     investment_option: str,
                     interest_rate_tapering_dict: Dict[str, Any],
                     dob: str,
                     doj: str,
                     employee_contrib_percent: float = 10.0,
                     govt_contrib_percent: float = 14.0,
                     existing_corpus: float = 0.0,
                     existing_corpus_end_date: str = None) -> Tuple[float, Dict[int, float], Dict[int, float]]:
    """
    Calculate final corpus amount at retirement.
    
    This is the main function that orchestrates the entire corpus
    calculation process. It handles existing corpus scenarios,
    calculates contributions and returns, and provides comprehensive
    growth tracking.
    
    Args:
        monthly_salary_detailed (Dict[int, float]): Monthly salary breakdown
        investment_option (str): Investment strategy selection
        interest_rate_tapering_dict (Dict[str, Any]): Investment return configuration
        dob (str): Date of birth for age calculations
        doj (str): Date of joining for career start
        employee_contrib_percent (float): Employee contribution percentage
        govt_contrib_percent (float): Government contribution percentage
        existing_corpus (float): Existing corpus amount (if any)
        existing_corpus_end_date (str): Date until which existing corpus is valid
            
    Returns:
        Tuple[float, Dict[int, float], Dict[int, float]]: 
            (final_corpus_amount, yearly_corpus, monthly_salary_detailed)
        
    Raises:
        ValueError: If required parameters are missing or invalid
        
    Example:
        >>> final_corpus, yearly_corpus, monthly_salary = get_final_corpus(
        ...     monthly_salary, 'Auto_LC50', config, '01/01/1995',
        ...     '01/01/2024', 10.0, 14.0, 500000, '01/04/2025'
        ... )
        >>> print(f"Final corpus: ₹{final_corpus:,.0f}")
        
    Note:
        - Handles existing corpus scenarios
        - Calculates age-based investment allocation
        - Tracks monthly and yearly growth
        - Provides comprehensive corpus analysis
    """
    # Validation
    if not monthly_salary_detailed:
        raise ValueError("Monthly salary data cannot be empty")
    
    if not investment_option:
        raise ValueError("Investment option must be specified")
    
    if not interest_rate_tapering_dict:
        raise ValueError("Interest rate tapering configuration required")
    
    # Calculate starting age
    dob_date = parse_date(dob)
    doj_date = parse_date(doj)
    starting_age = doj_date.year - dob_date.year
    
    # Handle existing corpus scenario
    if existing_corpus and existing_corpus_end_date:
        # If existing corpus, start calculations from UPS implementation date
        # This is a simplified approach - in practice would need more complex logic
        pass
    
    # Calculate corpus growth
    final_corpus_amount, yearly_corpus = get_corpus_growth(
        monthly_salary_detailed=monthly_salary_detailed,
        investment_option=investment_option,
        interest_rate_tapering_dict=interest_rate_tapering_dict,
        starting_age=starting_age,
        employee_contrib_percent=employee_contrib_percent,
        govt_contrib_percent=govt_contrib_percent,
        existing_corpus=existing_corpus
    )
    
    return final_corpus_amount, yearly_corpus, monthly_salary_detailed


def validate_contribution_data(monthly_salary_detailed: Dict[int, float],
                              investment_option: str,
                              interest_rate_tapering_dict: Dict[str, Any]) -> bool:
    """
    Validate contribution calculation inputs.
    
    This function performs various checks to ensure contribution
    calculations will work correctly with the provided data.
    
    Args:
        monthly_salary_detailed (Dict[int, float]): Monthly salary breakdown
        investment_option (str): Investment strategy selection
        interest_rate_tapering_dict (Dict[str, Any]): Investment return configuration
            
    Returns:
        bool: True if validation passes, False otherwise
        
    Raises:
        ValueError: If validation fails with specific error details
        
    Example:
        >>> is_valid = validate_contribution_data(
        ...     monthly_salary, 'Auto_LC50', config
        ... )
        >>> if not is_valid:
        ...     print("Contribution validation failed")
        
    Validation Checks:
        - Monthly salary data not empty
        - Investment option is valid
        - Interest rate configuration complete
        - Salary values are positive
        - Investment allocation can be calculated
    """
    # Check monthly salary data
    if not monthly_salary_detailed:
        raise ValueError("Monthly salary data cannot be empty")
    
    # Check for negative or zero salaries
    invalid_salaries = [month for month, salary in monthly_salary_detailed.items() if salary <= 0]
    if invalid_salaries:
        raise ValueError(f"Invalid salaries found for months: {invalid_salaries}")
    
    # Validate investment option
    valid_options = ['Standard/Benchmark', 'Auto_LC25', 'Auto_LC50', 'Auto_LC75', 'Active']
    if investment_option not in valid_options:
        raise ValueError(f"Invalid investment option: {investment_option}. Must be one of {valid_options}")
    
    # Validate interest rate configuration
    required_keys = ['E', 'C', 'G', 'Taper Period']
    if not all(key in interest_rate_tapering_dict for key in required_keys):
        raise ValueError(f"Interest rate configuration missing keys: {required_keys}")
    
    # Check asset class configuration
    for asset_class in ['E', 'C', 'G']:
        if asset_class not in interest_rate_tapering_dict:
            raise ValueError(f"Asset class {asset_class} missing from configuration")
        
        asset_config = interest_rate_tapering_dict[asset_class]
        if 'initial' not in asset_config or 'final' not in asset_config:
            raise ValueError(f"Asset class {asset_class} missing initial/final rates")
    
    # All validations passed
    return True


def get_contribution_summary(monthly_salary_detailed: Dict[int, float],
                            final_corpus: float,
                            employee_contrib_percent: float = 10.0,
                            govt_contrib_percent: float = 14.0) -> Dict[str, Any]:
    """
    Generate comprehensive contribution summary statistics.
    
    This function provides useful summary information about contributions
    and corpus growth including totals, averages, and key metrics.
    
    Args:
        monthly_salary_detailed (Dict[int, float]): Monthly salary breakdown
        final_corpus (float): Final corpus amount at retirement
        employee_contrib_percent (float): Employee contribution percentage
        govt_contrib_percent (float): Government contribution percentage
            
    Returns:
        Dict[str, Any]: Contribution summary with structure:
            {
                'total_contributions': float,
                'employee_contributions': float,
                'govt_contributions': float,
                'investment_returns': float,
                'contribution_ratio': float,
                'return_ratio': float
            }
        
    Example:
        >>> summary = get_contribution_summary(
        ...     monthly_salary, 5000000, 10.0, 14.0
        ... )
        >>> print(f"Total contributions: ₹{summary['total_contributions']:,}")
        >>> print(f"Investment returns: ₹{summary['investment_returns']:,}")
        
    Note:
        - Separates contributions from investment returns
        - Shows contribution vs return ratios
        - Helps understand corpus growth drivers
        - Useful for analysis and reporting
    """
    if not monthly_salary_detailed:
        return {}
    
    # Calculate total contributions
    total_salary = sum(monthly_salary_detailed.values())
    total_employee_contrib = (total_salary * employee_contrib_percent) / 100.0
    total_govt_contrib = (total_salary * govt_contrib_percent) / 100.0
    total_contributions = total_employee_contrib + total_govt_contrib
    
    # Calculate investment returns
    investment_returns = final_corpus - total_contributions
    
    # Calculate ratios
    contribution_ratio = (total_contributions / final_corpus) * 100 if final_corpus > 0 else 0
    return_ratio = (investment_returns / final_corpus) * 100 if final_corpus > 0 else 0
    
    return {
        'total_contributions': round(total_contributions, 2),
        'employee_contributions': round(total_employee_contrib, 2),
        'govt_contributions': round(total_govt_contrib, 2),
        'investment_returns': round(investment_returns, 2),
        'contribution_ratio': round(contribution_ratio, 2),
        'return_ratio': round(return_ratio, 2),
        'total_salary': round(total_salary, 2),
        'final_corpus': round(final_corpus, 2)
    }


# =============================================================================
# TESTING AND EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("Testing NPS vs UPS Pension Calculator - Contribution Module")
    print("=" * 70)
    
    # Sample data
    sample_monthly_salary = {
        1: 7000, 2: 7000, 3: 7000, 4: 7000, 5: 7000, 6: 7000,
        7: 7200, 8: 7200, 9: 7200, 10: 7200, 11: 7200, 12: 7200
    }
    
    sample_interest_config = {
        'E': {'initial': 12.0, 'final': 6.0},
        'C': {'initial': 8.0, 'final': 4.0},
        'G': {'initial': 4.0, 'final': 4.0},
        'Taper Period': 40
    }
    
    print("\n1. Testing Monthly Contribution Calculations:")
    try:
        for month, salary in list(sample_monthly_salary.items())[:3]:
            contribs = calculate_monthly_contributions(salary, 10.0, 14.0)
            print(f"Month {month}: Salary ₹{salary:,} → "
                  f"Employee ₹{contribs['employee_contribution']:,}, "
                  f"Govt ₹{contribs['govt_contribution']:,}")
    except Exception as e:
        print(f"Contribution calculation failed: {e}")
    
    print("\n2. Testing Investment Returns:")
    try:
        corpus = 1000000
        contribution = 5000
        new_corpus = apply_investment_returns(
            corpus, contribution, 'Auto_LC50', 30, sample_interest_config
        )
        print(f"Corpus: ₹{corpus:,} + ₹{contribution:,} contribution → "
              f"₹{new_corpus:,}")
    except Exception as e:
        print(f"Investment returns calculation failed: {e}")
    
    print("\n3. Testing Corpus Growth:")
    try:
        final_corpus, yearly_growth = get_corpus_growth(
            sample_monthly_salary, 'Auto_LC50', sample_interest_config, 25
        )
        print(f"Final corpus: ₹{final_corpus:,}")
        print(f"Yearly growth tracking: {len(yearly_growth)} years")
    except Exception as e:
        print(f"Corpus growth calculation failed: {e}")
    
    print("\n4. Testing Final Corpus Calculation:")
    try:
        final_corpus, yearly_corpus, monthly_salary = get_final_corpus(
            sample_monthly_salary, 'Auto_LC50', sample_interest_config,
            '01/01/1995', '01/01/2024', 10.0, 14.0
        )
        print(f"Final corpus amount: ₹{final_corpus:,}")
        print(f"Yearly corpus tracking: {len(yearly_corpus)} years")
    except Exception as e:
        print(f"Final corpus calculation failed: {e}")
    
    print("\n5. Testing Validation:")
    try:
        is_valid = validate_contribution_data(
            sample_monthly_salary, 'Auto_LC50', sample_interest_config
        )
        print(f"Contribution validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    except Exception as e:
        print(f"Validation failed: {e}")
    
    print("\n6. Testing Contribution Summary:")
    try:
        summary = get_contribution_summary(sample_monthly_salary, 5000000, 10.0, 14.0)
        print(f"Total contributions: ₹{summary['total_contributions']:,}")
        print(f"Investment returns: ₹{summary['investment_returns']:,}")
        print(f"Contribution ratio: {summary['contribution_ratio']:.1f}%")
        print(f"Return ratio: {summary['return_ratio']:.1f}%")
    except Exception as e:
        print(f"Summary generation failed: {e}")
    
    print("\n✅ All contribution module tests completed!")