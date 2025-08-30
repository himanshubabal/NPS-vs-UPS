"""
NPS vs UPS Pension Calculator - Validation Utilities Module

This module provides validation functions for user inputs and data validation
in the pension calculator application.

Author: Pension Calculator Team
Version: 1.0
"""

from typing import Union, List, Dict, Any, Optional
from datetime import date
import pandas as pd


def validate_basic_pay(basic_pay: Union[int, float], 
                      pay_matrix_df: pd.DataFrame,
                      level: Union[int, str],
                      year_in_level: int) -> tuple[bool, str]:
    """
    Validate that basic pay matches a valid level/year combination in pay matrix.
    
    Args:
        basic_pay (Union[int, float]): Basic pay amount to validate
        pay_matrix_df (pd.DataFrame): Pay matrix dataframe
        level (Union[int, str]): Pay level to check
        year_in_level (int): Year within the level to check
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
        
    Example:
        >>> is_valid, msg = validate_basic_pay(56100, pay_matrix_df, 10, 1)
        >>> print(f"Valid: {is_valid}, Message: {msg}")
    """
    try:
        # Convert level to string for comparison
        level_str = str(level)
        
        # Check if level exists in pay matrix
        if level_str not in pay_matrix_df.columns:
            return False, f"Invalid pay level: {level}"
        
        # Check if year exists in pay matrix
        if year_in_level not in pay_matrix_df.index:
            return False, f"Invalid year in level: {year_in_level}"
        
        # Get expected basic pay from matrix
        expected_pay = pay_matrix_df.loc[year_in_level, level_str]
        
        # Check if basic pay matches
        if abs(basic_pay - expected_pay) > 1:  # Allow 1 rupee tolerance
            return False, f"Basic pay {basic_pay} doesn't match level {level}, year {year_in_level} (expected: {expected_pay})"
        
        return True, "Basic pay is valid"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_dates(dob: str, doj: str, dor: Optional[str] = None) -> tuple[bool, str]:
    """
    Validate date inputs and their logical relationships.
    
    Args:
        dob (str): Date of birth in DD/MM/YYYY format
        doj (str): Date of joining in DD/MM/YYYY format
        dor (Optional[str]): Date of retirement in DD/MM/YYYY format
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
        
    Example:
        >>> is_valid, msg = validate_dates("15/06/1995", "01/01/2024")
        >>> print(f"Valid: {is_valid}, Message: {msg}")
    """
    try:
        from .date_utils import parse_date
        
        # Parse dates
        birth_date = parse_date(dob)
        join_date = parse_date(doj)
        
        # Check if DOB is reasonable (not too old or too young)
        current_year = date.today().year
        if birth_date.year < 1960 or birth_date.year > 2005:
            return False, f"Date of birth {dob} is outside reasonable range (1960-2005)"
        
        # Check if DOJ is reasonable
        if join_date.year < 2006 or join_date.year > 2030:
            return False, f"Date of joining {doj} is outside reasonable range (2006-2030)"
        
        # Check if DOJ is after DOB
        if join_date <= birth_date:
            return False, "Date of joining must be after date of birth"
        
        # Check if DOJ is not too far in the future
        if join_date.year > current_year + 5:
            return False, f"Date of joining {doj} is too far in the future"
        
        # Validate retirement date if provided
        if dor:
            retirement_date = parse_date(dor)
            
            # Check if DOR is after DOJ
            if retirement_date <= join_date:
                return False, "Date of retirement must be after date of joining"
            
            # Check if DOR is reasonable (not too far in the future)
            if retirement_date.year > current_year + 50:
                return False, f"Date of retirement {dor} is too far in the future"
            
            # Check minimum service period (at least 10 years)
            service_years = (retirement_date - join_date).days / 365.25
            if service_years < 10:
                return False, f"Service period too short: {service_years:.1f} years (minimum 10 years required)"
        
        return True, "All dates are valid"
        
    except Exception as e:
        return False, f"Date validation error: {str(e)}"


def validate_financial_rates(inflation_rate: float,
                           equity_rate: float,
                           corporate_rate: float,
                           govt_rate: float) -> tuple[bool, str]:
    """
    Validate financial rate parameters.
    
    Args:
        inflation_rate (float): Inflation rate percentage
        equity_rate (float): Equity return rate percentage
        corporate_rate (float): Corporate bond return rate percentage
        govt_rate (float): Government bond return rate percentage
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
        
    Example:
        >>> is_valid, msg = validate_financial_rates(7.0, 12.0, 8.0, 8.0)
        >>> print(f"Valid: {is_valid}, Message: {msg}")
    """
    try:
        # Check if rates are within reasonable bounds
        if not (0.0 <= inflation_rate <= 20.0):
            return False, f"Inflation rate {inflation_rate}% is outside valid range (0-20%)"
        
        if not (0.0 <= equity_rate <= 20.0):
            return False, f"Equity rate {equity_rate}% is outside valid range (0-20%)"
        
        if not (0.0 <= corporate_rate <= 15.0):
            return False, f"Corporate bond rate {corporate_rate}% is outside valid range (0-15%)"
        
        if not (0.0 <= govt_rate <= 12.0):
            return False, f"Government bond rate {govt_rate}% is outside valid range (0-12%)"
        
        # Check logical relationships
        if equity_rate < corporate_rate:
            return False, f"Equity rate ({equity_rate}%) should be higher than corporate bond rate ({corporate_rate}%)"
        
        if corporate_rate < govt_rate:
            return False, f"Corporate bond rate ({corporate_rate}%) should be higher than government bond rate ({govt_rate}%)"
        
        if equity_rate < inflation_rate:
            return False, f"Equity rate ({equity_rate}%) should be higher than inflation rate ({inflation_rate}%) for real returns"
        
        return True, "All financial rates are valid"
        
    except Exception as e:
        return False, f"Financial rate validation error: {str(e)}"


def validate_contribution_percentages(employee_contrib: float,
                                    govt_contrib: float) -> tuple[bool, str]:
    """
    Validate contribution percentage parameters.
    
    Args:
        employee_contrib (float): Employee contribution percentage
        govt_contrib (float): Government contribution percentage
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
        
    Example:
        >>> is_valid, msg = validate_contribution_percentages(10.0, 14.0)
        >>> print(f"Valid: {is_valid}, Message: {msg}")
    """
    try:
        # Check if percentages are within valid ranges
        if not (5.0 <= employee_contrib <= 20.0):
            return False, f"Employee contribution {employee_contrib}% is outside valid range (5-20%)"
        
        if not (10.0 <= govt_contrib <= 20.0):
            return False, f"Government contribution {govt_contrib}% is outside valid range (10-20%)"
        
        # Check total contribution limit
        total_contrib = employee_contrib + govt_contrib
        if total_contrib > 30.0:
            return False, f"Total contribution {total_contrib}% exceeds maximum limit of 30%"
        
        return True, "Contribution percentages are valid"
        
    except Exception as e:
        return False, f"Contribution validation error: {str(e)}"


def validate_promotion_schedule(promotion_years: List[int],
                              starting_level: Union[int, str],
                              max_level: int = 18) -> tuple[bool, str]:
    """
    Validate promotion schedule array.
    
    Args:
        promotion_years (List[int]): List of years between promotions
        starting_level (Union[int, str]): Starting pay level
        max_level (int): Maximum available pay level
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
        
    Example:
        >>> is_valid, msg = validate_promotion_schedule([4, 5, 4], 10)
        >>> print(f"Valid: {is_valid}, Message: {msg}")
    """
    try:
        # Check if promotion_years is a list
        if not isinstance(promotion_years, list):
            return False, "Promotion schedule must be a list"
        
        # Check if all elements are positive integers
        for i, years in enumerate(promotion_years):
            if not isinstance(years, int) or years <= 0:
                return False, f"Promotion year {i+1} must be a positive integer, got: {years}"
        
        # Check if promotion schedule is reasonable
        total_years = sum(promotion_years)
        if total_years > 50:
            return False, f"Total promotion period {total_years} years is too long (max 50 years)"
        
        # Check if starting level is valid
        try:
            start_level = int(starting_level)
            if not (1 <= start_level <= max_level):
                return False, f"Starting level {start_level} is outside valid range (1-{max_level})"
        except ValueError:
            return False, f"Invalid starting level: {starting_level}"
        
        return True, "Promotion schedule is valid"
        
    except Exception as e:
        return False, f"Promotion schedule validation error: {str(e)}"


def validate_investment_allocation(equity_pct: float,
                                 corporate_pct: float,
                                 govt_pct: float) -> tuple[bool, str]:
    """
    Validate investment allocation percentages.
    
    Args:
        equity_pct (float): Equity allocation percentage
        corporate_pct (float): Corporate bond allocation percentage
        govt_pct (float): Government bond allocation percentage
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
        
    Example:
        >>> is_valid, msg = validate_investment_allocation(50.0, 30.0, 20.0)
        >>> print(f"Valid: {is_valid}, Message: {msg}")
    """
    try:
        # Check if percentages are within valid ranges
        if not (0.0 <= equity_pct <= 100.0):
            return False, f"Equity allocation {equity_pct}% is outside valid range (0-100%)"
        
        if not (0.0 <= corporate_pct <= 100.0):
            return False, f"Corporate bond allocation {corporate_pct}% is outside valid range (0-100%)"
        
        if not (0.0 <= govt_pct <= 100.0):
            return False, f"Government bond allocation {govt_pct}% is outside valid range (0-100%)"
        
        # Check if percentages sum to 100%
        total_pct = equity_pct + corporate_pct + govt_pct
        if abs(total_pct - 100.0) > 0.01:  # Allow small floating point error
            return False, f"Allocation percentages sum to {total_pct}%, must equal 100%"
        
        return True, "Investment allocation is valid"
        
    except Exception as e:
        return False, f"Investment allocation validation error: {str(e)}"


def validate_user_inputs(user_inputs: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Comprehensive validation of all user inputs.
    
    Args:
        user_inputs (Dict[str, Any]): Dictionary of user input parameters
        
    Returns:
        tuple[bool, List[str]]: (is_valid, list_of_error_messages)
        
    Example:
        >>> is_valid, errors = validate_user_inputs(user_input_dict)
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"Error: {error}")
    """
    errors = []
    
    try:
        # Validate dates
        if 'dob' in user_inputs and 'doj' in user_inputs:
            is_valid, msg = validate_dates(
                user_inputs['dob'], 
                user_inputs['doj'], 
                user_inputs.get('dor')
            )
            if not is_valid:
                errors.append(msg)
        
        # Validate financial rates
        if all(key in user_inputs for key in ['initial_inflation_rate', 'E_initial', 'C_initial', 'G_initial']):
            is_valid, msg = validate_financial_rates(
                user_inputs['initial_inflation_rate'],
                user_inputs['E_initial'],
                user_inputs['C_initial'],
                user_inputs['G_initial']
            )
            if not is_valid:
                errors.append(msg)
        
        # Validate contribution percentages
        if all(key in user_inputs for key in ['employee_contrib_percent', 'govt_contrib_percent']):
            is_valid, msg = validate_contribution_percentages(
                user_inputs['employee_contrib_percent'],
                user_inputs['govt_contrib_percent']
            )
            if not is_valid:
                errors.append(msg)
        
        # Validate promotion schedule
        if 'promotion_duration_array' in user_inputs:
            is_valid, msg = validate_promotion_schedule(
                user_inputs['promotion_duration_array'],
                user_inputs.get('starting_level', 10)
            )
            if not is_valid:
                errors.append(msg)
        
        # Validate investment allocation
        if all(key in user_inputs for key in ['E_initial', 'C_initial', 'G_initial']):
            is_valid, msg = validate_investment_allocation(
                user_inputs['E_initial'],
                user_inputs['C_initial'],
                user_inputs['G_initial']
            )
            if not is_valid:
                errors.append(msg)
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
        return False, errors


if __name__ == "__main__":
    # Test the validation utility functions
    print("Testing Validation Utilities...")
    
    # Test date validation
    print("\n1. Testing Date Validation:")
    test_cases = [
        ("15/06/1995", "01/01/2024", None),
        ("01/01/1990", "01/01/2020", "01/01/2050"),
        ("01/01/1950", "01/01/2024", None),  # Invalid DOB
    ]
    
    for dob, doj, dor in test_cases:
        is_valid, msg = validate_dates(dob, doj, dor)
        print(f"DOB: {dob}, DOJ: {doj}, DOR: {dor} -> Valid: {is_valid}, Message: {msg}")
    
    # Test financial rate validation
    print("\n2. Testing Financial Rate Validation:")
    test_rates = [
        (7.0, 12.0, 8.0, 8.0),  # Valid
        (15.0, 10.0, 8.0, 8.0),  # Invalid (equity < inflation)
        (5.0, 8.0, 12.0, 8.0),   # Invalid (corporate > equity)
    ]
    
    for rates in test_rates:
        is_valid, msg = validate_financial_rates(*rates)
        print(f"Rates: {rates} -> Valid: {is_valid}, Message: {msg}")
    
    # Test contribution validation
    print("\n3. Testing Contribution Validation:")
    test_contribs = [
        (10.0, 14.0),  # Valid
        (25.0, 14.0),  # Invalid (employee too high)
        (10.0, 25.0),  # Invalid (total too high)
    ]
    
    for emp, govt in test_contribs:
        is_valid, msg = validate_contribution_percentages(emp, govt)
        print(f"Employee: {emp}%, Government: {govt}% -> Valid: {is_valid}, Message: {msg}")
    
    print("\nAll validation utility tests completed!")
