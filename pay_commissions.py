"""
NPS vs UPS Pension Calculator - Pay Commissions Module

This module handles all aspects of career progression, pay matrix operations,
and promotion logic. It simulates an employee's career path including annual
increments, promotions, and pay commission implementations.

Key Functions:
- get_basic_pay(): Retrieve basic pay for level/year combination
- get_level_year_from_basic_pay(): Reverse lookup from basic pay
- annual_increment(): Apply annual increment within same level
- promote_employee(): Handle promotion to next level with IAS rules
- generate_next_pay_commission(): Create new CPC pay matrices
- career_progression(): Main career simulation engine

Career Progression Rules:
- Annual increments: Applied mid-year (July 1st)
- Promotions: Applied year-end (January 1st)
- Pay Commissions: Reset DA to 0, apply fitment factors
- IAS special rules: Skip levels 13A, 16; extra steps for levels 10-12

Author: Pension Calculator Team
Version: 1.0
"""

import pandas as pd
import numpy as np
import re
import os
import pprint
from typing import Union, Tuple, List, Dict, Any

from itertools import accumulate
from helper_functions import *
from rates import get_DA_matrix


def get_basic_pay(level: Union[int, str], year: int, pay_matrix_df: pd.DataFrame) -> int:
    """
    Fetch basic pay for given pay level and year.
    
    This function retrieves the basic pay amount from the pay matrix
    for a specific level and year combination. It handles edge cases
    like maximum pay within a level and validates inputs.
    
    Args:
        level (Union[int, str]): Pay level (e.g., 10, '13A')
        year (int): Year within the level (1-based indexing)
        pay_matrix_df (pd.DataFrame): Pay matrix DataFrame
        
    Returns:
        int: Basic pay amount in rupees
        
    Raises:
        ValueError: If level not found or year out of range
        
    Example:
        >>> df = load_csv_into_df('7th_CPC.csv')
        >>> get_basic_pay(10, 1, df)
        56100  # Starting basic pay for Level 10, Year 1
        >>> get_basic_pay('13A', 5, df)
        123100  # Basic pay for Level 13A, Year 5
    """
    level_str = str(level)
    
    # Validation: Check if level exists in pay matrix
    if level_str not in pay_matrix_df.columns:
        raise ValueError(f"Level {level} not found in pay matrix.")
    
    # Validation: Check if year is within valid range
    if not (1 <= year <= len(pay_matrix_df)):
        raise ValueError(f"Year {year} is out of range (must be 1 to {len(pay_matrix_df)}).")
    
    # Find maximum steps available for this level
    # Some levels have fewer steps than others (e.g., Level 13A might have 18 steps)
    max_steps = pay_matrix_df[level_str].last_valid_index() + 1  # Convert to 1-based
    
    # Get maximum basic pay for this level
    max_basic_pay = pay_matrix_df[level_str].iloc[max_steps - 1]
    
    # If at or beyond the last step, return maximum pay
    # Year can still increment but pay stays the same
    if year >= max_steps:
        return max_basic_pay
    
    # Return the basic pay for the specified year
    return int(pay_matrix_df[level_str].iloc[year - 1])


def get_level_year_from_basic_pay(basic_pay: int, pay_matrix_df: pd.DataFrame) -> Tuple[Union[str, int], int]:
    """
    Find pay level and year from basic pay amount.
    
    This function performs a reverse lookup to find which level and year
    a given basic pay corresponds to. It's useful for validating user
    inputs and finding the highest level where a basic pay appears.
    
    Args:
        basic_pay (int): Basic pay amount to search for
        pay_matrix_df (pd.DataFrame): Pay matrix DataFrame
        
    Returns:
        Tuple[Union[str, int], int]: (level, year) or (0, 0) if not found
        
    Example:
        >>> df = load_csv_into_df('7th_CPC.csv')
        >>> get_level_year_from_basic_pay(56100, df)
        ('10', 1)  # Level 10, Year 1
        >>> get_level_year_from_basic_pay(123100, df)
        ('13A', 5)  # Level 13A, Year 5
    """
    found_matches = []
    
    # Search through all levels and years
    for level in pay_matrix_df.columns:
        for i, value in enumerate(pay_matrix_df[level]):
            if value == basic_pay:
                year = i + 1  # Convert 0-based index to 1-based year
                found_matches.append((str(level), year))
    
    # If no matches found, return (0, 0) to indicate invalid input
    if not found_matches:
        return (0, 0)
    
    # Sort matches: highest level first, then lowest year
    # Handle special levels like '13A' by converting to float for sorting
    found_matches.sort(
        key=lambda x: (
            float(x[0].replace('A', '.5')) if 'A' in x[0] else float(x[0]), 
            -x[1]
        ), 
        reverse=True
    )
    
    # Return the best match (highest level, lowest year)
    best_match = found_matches[0]
    return best_match


def annual_increment(current_level: Union[int, str], year: int, pay_matrix_df: pd.DataFrame) -> Tuple[str, int, int]:
    """
    Apply annual increment within the same pay level.
    
    This function moves the employee one step down within the same level
    for annual increments. If already at maximum pay, the year increases
    but pay remains the same.
    
    Args:
        current_level (Union[int, str]): Current pay level
        year (int): Current year within the level (1-based)
        pay_matrix_df (pd.DataFrame): Pay matrix DataFrame
        
    Returns:
        Tuple[str, int, int]: (level, new_year, new_basic_pay)
        
    Raises:
        ValueError: If level is invalid
        
    Example:
        >>> df = load_csv_into_df('7th_CPC.csv')
        >>> annual_increment(10, 1, df)
        ('10', 2, 57800)  # Level 10, Year 2, new basic pay
        >>> annual_increment(10, 40, df)  # At max pay
        ('10', 41, 123100)  # Year increases, pay stays same
    """
    level_str = str(current_level)
    
    # Validation: Check if level exists
    if level_str not in pay_matrix_df.columns:
        raise ValueError(f"Invalid level: {current_level}")
    
    # Find maximum steps for this level
    max_steps = pay_matrix_df[level_str].last_valid_index() + 1
    max_basic_pay = pay_matrix_df[level_str].iloc[max_steps - 1]
    
    # If at or beyond maximum steps, increment year but keep same pay
    if year >= max_steps:
        return (level_str, year + 1, int(max_basic_pay))
    
    # Get next basic pay and increment year
    next_basic = int(pay_matrix_df[level_str].iloc[year])  # year is 1-based
    return (level_str, year + 1, next_basic)


def promote_employee(current_level: Union[int, str], year: int, pay_matrix_df: pd.DataFrame, 
                    is_ias: bool = DEFAULT_IS_IAS) -> Tuple[str, int, int]:
    """
    Promote employee to next level with IAS-specific rules.
    
    This function handles promotions with the following logic:
    1. Step down in current level (get stepped pay)
    2. Identify next level (skip 13A and 16 for IAS)
    3. Find pay ≥ stepped pay in next level
    4. Apply IAS special rules for levels 10-12
    
    Args:
        current_level (Union[int, str]): Current pay level
        year (int): Current year within level (1-based)
        pay_matrix_df (pd.DataFrame): Pay matrix DataFrame
        is_ias (bool): Whether IAS service (affects promotion rules)
        
    Returns:
        Tuple[str, int, int]: (new_level, new_year, new_basic_pay)
        
    Raises:
        ValueError: If level or year is invalid
        
    Example:
        >>> df = load_csv_into_df('7th_CPC.csv')
        >>> promote_employee(10, 5, df, is_ias=True)
        ('11', 1, 67700)  # Promoted to Level 11, Year 1
        >>> promote_employee(13, 3, df, is_ias=True)
        ('14', 1, 144200)  # IAS skips 13A, goes to 14
    """
    levels = list(pay_matrix_df.columns)
    current_level_str = str(current_level)
    
    # Validation: Check if current level exists
    if current_level_str not in levels:
        raise ValueError(f"Level {current_level} not found.")
    
    # Validation: Check if year is valid
    if not (1 <= year < len(pay_matrix_df)):
        raise ValueError(f"Year {year} must be between 1 and {len(pay_matrix_df) - 1}.")
    
    # Step 1: Get stepped pay (one step down in current level)
    stepped_pay = pay_matrix_df[current_level_str].iloc[year]  # year is 1-based
    
    # Handle case where current basic is at maximum
    max_basic_pay = pay_matrix_df[current_level_str].dropna().max()
    if pd.isna(stepped_pay):
        stepped_pay = max_basic_pay
    
    # Step 2: Identify next level
    curr_index = levels.index(current_level_str)
    
    # IAS special rule: Skip levels 13A and 16
    levels_to_skip = ['13A', '16']
    
    if curr_index + 1 < len(levels):
        # If IAS and next level should be skipped
        if is_ias and levels[curr_index + 1] in levels_to_skip:
            next_level_index = curr_index + 2
        else:
            next_level_index = curr_index + 1
    else:
        next_level_index = curr_index + 1
    
    # Ensure next level index is valid
    if next_level_index >= len(levels):
        next_level_index = len(levels) - 1
    
    # Get next level
    next_level = str(levels[next_level_index])
    next_column = pay_matrix_df[next_level]
    
    # Step 3: Find first cell ≥ stepped pay
    match_index = None
    for i, val in enumerate(next_column):
        if val >= stepped_pay:
            match_index = i
            break
    
    # IAS special rule: For levels 10-12, go two steps further down
    if is_ias and current_level_str in {'10', '11', '12'}:
        match_index = min(match_index + 2, len(next_column) - 1)
    
    # Fallback if no match found
    if match_index is None:
        return (next_level, len(next_column), int(next_column.iloc[-1]))
    
    return (next_level, match_index + 1, int(next_column.iloc[match_index]))


def generate_next_pay_commission(fitment_factor: float, 
                                present_pay_matrix_csv_path_and_name: str = PAY_MATRIX_7CPC_CSV, 
                                data_folder_path: str = DATA_FOLDER_PATH) -> pd.DataFrame:
    """
    Generate next CPC pay matrix based on fitment factor.
    
    This function creates a new pay matrix for the next Central Pay Commission
    by applying the fitment factor to all basic pay values. The new matrix
    is saved as a CSV file for future use.
    
    Args:
        fitment_factor (float): Factor to multiply basic pay by (e.g., 2.0 = double)
        present_pay_matrix_csv_path_and_name (str): Source pay matrix CSV file
        data_folder_path (str): Directory to save generated CSV
        
    Returns:
        pd.DataFrame: New pay matrix with updated basic pay values
        
    Raises:
        ValueError: If source filename doesn't contain CPC information
        
    Example:
        >>> new_matrix = generate_next_pay_commission(2.0, '7th_CPC.csv')
        >>> # Creates '8th_CPC_fitment_factor_2.0.csv' with doubled basic pay
    """
    # Extract current CPC number from source filename
    present_pay_matrix_csv_name = present_pay_matrix_csv_path_and_name.replace(data_folder_path, "")
    match = re.search(r"(\d+)(?:st|nd|rd|th)?_CPC", present_pay_matrix_csv_name)
    
    if not match:
        raise ValueError("Source filename must contain CPC name like '7th_CPC'")
    
    current_cpc = int(match.group(1))
    next_cpc = f"{current_cpc + 1}th_CPC"
    
    # Load and copy the source DataFrame
    present_pay_matrix_df = pd.read_csv(data_folder_path + present_pay_matrix_csv_path_and_name)
    new_df = present_pay_matrix_df.copy()
    
    # Apply fitment factor to all numeric columns (skip first column which is usually "Year")
    value_columns = new_df.columns[1:]
    
    for col in value_columns:
        # Skip non-numeric columns if any
        if not np.issubdtype(new_df[col].dtype, np.number):
            continue
        
        # Apply fitment factor and round to nearest ₹100
        new_df[col] = new_df[col].apply(
            lambda x: int(round(x * fitment_factor / 100.0) * 100) if not pd.isna(x) else np.nan
        ).astype("Int64")  # Use nullable integer type
    
    # Save to CSV with descriptive filename
    output_filename = f"{data_folder_path}{next_cpc}_fitment_factor_{fitment_factor}.csv"
    new_df.to_csv(output_filename, index=False)
    
    return new_df


def career_progression(starting_level: Union[int, str] = 10, 
                      starting_year_row_in_level: int = 1, 
                      promotion_duration_array: List[int] = [4, 5, 4, 1, 4, 7, 5, 3], 
                      present_pay_matrix_csv: str = '7th_CPC.csv', 
                      early_retirement: bool = False,
                      dob: str = '20/07/1999', 
                      doj: str = '9/10/24', 
                      dor: str = None, 
                      is_ias: bool = False, 
                      da_matrix: Dict[float, float] = None, 
                      percent_inc_salary: float = 15,
                      pay_commission_implement_years: List[int] = [2026, 2036, 2046, 2056, 2066], 
                      fitment_factors: List[int] = [2, 2, 2, 2, 2]) -> List[Dict[str, Any]]:
    """
    Simulate complete career progression from joining to retirement.
    
    This is the main career simulation engine that:
    1. Tracks level and year progression over time
    2. Applies annual increments (mid-year)
    3. Handles promotions (year-end)
    4. Implements pay commissions with fitment factors
    5. Returns detailed career history
    
    Args:
        starting_level (Union[int, str]): Initial pay level
        starting_year_row_in_level (int): Starting year within level
        promotion_duration_array (List[int]): Years between promotions
        present_pay_matrix_csv (str): Initial pay matrix file
        early_retirement (bool): Whether considering early retirement
        dob (str): Date of birth
        doj (str): Date of joining service
        dor (str): Date of retirement (required if early_retirement=True)
        is_ias (bool): Whether IAS service
        da_matrix (Dict[float, float]): DA projections (optional)
        percent_inc_salary (float): Salary increase % at CPCs
        pay_commission_implement_years (List[int]): Years when CPCs are implemented
        fitment_factors (List[int]): Fitment factors for each CPC
        
    Returns:
        List[Dict[str, Any]]: Career progression history with keys:
            - 'Level': Pay level at each point
            - 'Year Row in Level': Year within level
            - 'Basic Pay': Basic pay amount
            - 'Year': Calendar year (with half-year precision)
            - 'Years of Service': Service duration
            
    Raises:
        ValueError: If promotion array doesn't match CPC years
        ValueError: If early retirement without retirement date
        
    Example:
        >>> career = career_progression(
        ...     starting_level=10,
        ...     doj='01/01/2024',
        ...     is_ias=True,
        ...     promotion_duration_array=[4, 5, 4]
        ... )
        >>> print(f"Final Level: {career[-1]['Level']}")
        >>> print(f"Final Basic Pay: ₹{career[-1]['Basic Pay']:,}")
    """
    current_pay_matrix = load_csv_into_df(present_pay_matrix_csv)
    
    # ========== VALIDATION SECTION ==========
    
    # Validate fitment factors match pay commission years
    if fitment_factors is None:
        fitment_factors = [DEFAULT_FITMENT_FACTOR] * len(pay_commission_implement_years)
    else:
        if len(fitment_factors) != len(pay_commission_implement_years):
            raise ValueError("Number of fitment factors must match number of pay commission implementation years.")
    
    # Validate starting level exists in pay matrix
    levels = list(current_pay_matrix.columns)
    if str(starting_level) not in levels:
        raise ValueError(f"Invalid pay level: {str(starting_level)}")
    
    # Validate early retirement parameters
    if early_retirement and dor is None:
        raise ValueError('If retiring early, must provide Date of Retirement')
    
    # ========== MAIN LOGIC SECTION ==========
    
    # Extract key dates and calculate service parameters
    service_joining_year, service_joining_month = parse_date(doj).year, parse_date(doj).month
    
    if early_retirement:
        retirement_year, retirement_month = parse_date(dor).year, parse_date(dor).month
    else:
        retirement_year, retirement_month = get_retirement_date(dob).year, get_retirement_date(dob).month
    
    # Calculate promotion due years (cumulative)
    promotion_due_years_array = list(accumulate(promotion_duration_array, initial=service_joining_year))[1:]
    
    # Adjust for half-year precision
    # If joined after July, count from next year; if retired after July, add half year
    service_joining_year += 0.5 if service_joining_month > 6 else 0
    retirement_year += 0.5 if retirement_month > 6 else 0
    
    # Calculate maximum service years
    max_service_years = retirement_year - service_joining_year
    
    # Initialize career tracking variables
    pay_level = str(starting_level)
    year_row_in_current_pay_level = starting_year_row_in_level
    basic_pay = current_pay_matrix[pay_level].iloc[year_row_in_current_pay_level - 1]
    
    # Track array indices and service duration
    promotion_yr_array_index, pay_commission_index = 0, 0
    current_service_duration = 0
    present_pay_comm_no = extract_cpc_no_from_filename(present_pay_matrix_csv)
    
    # Initialize career progression list
    progression = []
    
    # Define consistent key names
    key_level, key_yr_row_in_level, key_basic_pay = 'Level', 'Year Row in Level', 'Basic Pay'
    key_year, key_years_of_service = 'Year', 'Years of Service'
    
    # ========== MAIN SIMULATION LOOP ==========
    
    while current_service_duration <= max_service_years:
        # Initialize half-year service details
        half_year_service_details = {}
        half_year_service_details[key_level] = pay_level
        half_year_service_details[key_yr_row_in_level] = year_row_in_current_pay_level
        half_year_service_details[key_basic_pay] = int(basic_pay)
        
        # Calculate current year
        year = service_joining_year + current_service_duration
        
        # LOGIC: Different operations at different times
        # - Mid-year (x.5): Annual increment
        # - Year-end (x.0): Promotion and Pay Commission
        
        # ANNUAL INCREMENT (Mid-year: July 1st)
        if year % 1 == 0.5 and current_service_duration >= 0.5:
            pay_level, year_row_in_current_pay_level, basic_pay = annual_increment(
                pay_level, year_row_in_current_pay_level, pay_matrix_df=current_pay_matrix
            )
            # Update tracking variables
            half_year_service_details[key_level] = pay_level
            half_year_service_details[key_yr_row_in_level] = year_row_in_current_pay_level
            half_year_service_details[key_basic_pay] = int(basic_pay)
        
        # PROMOTION AND PAY COMMISSION (Year-end: January 1st)
        if year % 1 != 0.5:
            # PAY COMMISSION IMPLEMENTATION
            # Applied before promotion so updated pay matrix is used
            if (year == pay_commission_implement_years[pay_commission_index] and 
                pay_commission_index < len(pay_commission_implement_years)):
                
                # Get fitment factor for this CPC
                fit_factor = fitment_factors[pay_commission_index]
                
                # Generate next CPC filename
                next_pay_comm_no = present_pay_comm_no + 1
                next_pay_comm_fileName = f"{next_pay_comm_no}th_CPC_fitment_factor_{fit_factor}.csv"
                
                # Load existing CPC or generate new one
                if os.path.exists(next_pay_comm_fileName):
                    current_pay_matrix = load_csv_into_df(next_pay_comm_fileName)
                else:
                    current_pay_matrix = generate_next_pay_commission(
                        fitment_factor=fit_factor, 
                        present_pay_matrix_csv_path_and_name=present_pay_matrix_csv
                    )
                
                # Update basic pay according to new pay matrix
                basic_pay = get_basic_pay(pay_level, year_row_in_current_pay_level, current_pay_matrix)
                
                # Update tracking variables for next CPC
                present_pay_matrix_csv = next_pay_comm_fileName
                pay_commission_index += 1
                present_pay_comm_no += 1
            
            # PROMOTION APPLICATION
            if (promotion_yr_array_index < len(promotion_duration_array) and 
                year == promotion_due_years_array[promotion_yr_array_index]):
                
                pay_level, year_row_in_current_pay_level, basic_pay = promote_employee(
                    pay_level, year_row_in_current_pay_level, 
                    pay_matrix_df=current_pay_matrix, is_ias=is_ias
                )
                promotion_yr_array_index += 1
            
            # Update tracking variables after promotion/CPC
            half_year_service_details[key_level] = pay_level
            half_year_service_details[key_yr_row_in_level] = year_row_in_current_pay_level
            half_year_service_details[key_basic_pay] = int(basic_pay)
        
        # Add independent variables
        half_year_service_details[key_years_of_service] = current_service_duration
        half_year_service_details[key_year] = year
        
        # Append to progression list
        progression.append(half_year_service_details)
        
        # Increment service duration by half year
        current_service_duration += 0.5
    
    return progression


# =============================================================================
# TESTING AND EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("Testing NPS vs UPS Pension Calculator - Pay Commissions Module")
    print("=" * 70)
    
    # Test basic pay retrieval
    print("\n1. Testing Basic Pay Retrieval:")
    df = load_csv_into_df('7th_CPC.csv')
    print(f"Level 10, Year 1: ₹{get_basic_pay(10, 1, df):,}")
    print(f"Level 13A, Year 5: ₹{get_basic_pay('13A', 5, df):,}")
    
    # Test level/year lookup
    print("\n2. Testing Level/Year Lookup:")
    level, year = get_level_year_from_basic_pay(56100, df)
    print(f"Basic Pay ₹56,100 → Level {level}, Year {year}")
    
    # Test annual increment
    print("\n3. Testing Annual Increment:")
    new_level, new_year, new_pay = annual_increment(10, 1, df)
    print(f"Level 10, Year 1 → Level {new_level}, Year {new_year}, Pay ₹{new_pay:,}")
    
    # Test promotion
    print("\n4. Testing Promotion:")
    prom_level, prom_year, prom_pay = promote_employee(10, 5, df, is_ias=True)
    print(f"Level 10 → Level {prom_level}, Year {prom_year}, Pay ₹{prom_pay:,}")
    
    # Test career progression
    print("\n5. Testing Career Progression:")
    da_matrix = get_DA_matrix()
    progression = career_progression(
        is_ias=True, 
        early_retirement=True, 
        dor='10/4/30', 
        da_matrix=da_matrix
    )
    
    print(f"Career progression generated: {len(progression)} half-year periods")
    print(f"Final level: {progression[-1]['Level']}")
    print(f"Final basic pay: ₹{progression[-1]['Basic Pay']:,}")
    
    # Display sample progression
    print("\n6. Sample Career Progression (first 5 periods):")
    for i, period in enumerate(progression[:5]):
        print(f"Period {i+1}: Level {period['Level']}, Year {period['Year Row in Level']}, "
              f"Pay ₹{period['Basic Pay']:,}, Service Year {period['Years of Service']}")

