"""
NPS vs UPS Pension Calculator - Salary Module

This module handles all salary-related calculations including basic pay,
Dearness Allowance (DA), total salary computation, and monthly breakdown.
It integrates career progression data with DA matrix to compute actual
salary amounts over the employee's career.

Key Functions:
- get_salary_matrix(): Generate complete salary matrix (Basic + DA)
- get_monthly_salary(): Calculate detailed monthly salary breakdown
- calculate_total_salary(): Combine basic pay with DA percentage
- validate_salary_data(): Ensure salary calculations are consistent

Salary Calculation Logic:
- Basic Pay: From career progression (level + year combinations)
- DA Percentage: From DA matrix (historical + projected)
- Total Salary: Basic Pay × (1 + DA/100)
- Monthly Breakdown: Annual salary divided by 12 months
- Half-year Precision: Salary calculated every 6 months

Integration Points:
- Career Progression: Basic pay changes over time
- DA Matrix: Inflation-adjusted allowance percentages
- Contribution Module: Salary drives contribution amounts
- Pension Module: Final salary affects retirement benefits

Author: Pension Calculator Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Tuple, Any

from helper_functions import *
from default_constants import *


def get_salary_matrix(career_progression: List[Dict[str, Any]],
                     da_matrix: Dict[float, float]) -> Dict[float, float]:
    """
    Generate complete salary matrix combining basic pay with DA.
    
    This function takes career progression data (level, year, basic pay)
    and combines it with DA matrix to calculate total salary at each
    point in the employee's career. The result is used for contribution
    calculations and retirement benefit computations.
    
    Args:
        career_progression (List[Dict[str, Any]]): Career progression history
            Each dict contains: 'Level', 'Year Row in Level', 'Basic Pay', 'Year'
        da_matrix (Dict[float, float]): DA percentages by year (including half-years)
            
    Returns:
        Dict[float, float]: Total salary matrix with keys as years
        
    Raises:
        ValueError: If career progression or DA matrix is empty
        KeyError: If required keys missing from career progression
        
    Example:
        >>> career = [{'Level': '10', 'Basic Pay': 56100, 'Year': 2024.0}]
        >>> da = {2024.0: 50.0, 2024.5: 52.0}
        >>> salary = get_salary_matrix(career, da)
        >>> print(f"Salary in 2024: ₹{salary[2024.0]:,}")
        >>> print(f"Salary in 2024.5: ₹{salary[2024.5]:,}")
        
    Note:
        - Salary = Basic Pay × (1 + DA/100)
        - DA resets to 0 at Pay Commission years
        - Half-year precision matches career progression
        - Used for contribution and pension calculations
    """
    # Validation
    if not career_progression:
        raise ValueError("Career progression data cannot be empty")
    
    if not da_matrix:
        raise ValueError("DA matrix cannot be empty")
    
    # Required keys in career progression
    required_keys = ['Level', 'Basic Pay', 'Year']
    for entry in career_progression:
        if not all(key in entry for key in required_keys):
            raise KeyError(f"Career progression entry missing required keys: {required_keys}")
    
    # Initialize salary matrix
    salary_matrix = {}
    
    # Process each career progression entry
    for entry in career_progression:
        year = entry['Year']
        basic_pay = entry['Basic Pay']
        
        # Get DA percentage for this year
        if year in da_matrix:
            da_percentage = da_matrix[year]
        else:
            # Fallback: use nearest available DA or default
            available_years = sorted(da_matrix.keys())
            if available_years:
                # Find closest year
                closest_year = min(available_years, key=lambda x: abs(x - year))
                da_percentage = da_matrix[closest_year]
            else:
                da_percentage = 0.0  # Default if no DA data
        
        # Calculate total salary: Basic Pay × (1 + DA/100)
        total_salary = basic_pay * (1 + da_percentage / 100.0)
        
        # Store rounded salary
        salary_matrix[year] = round(total_salary)
    
    return salary_matrix


def get_monthly_salary(salary_matrix: Dict[float, float],
                      career_progression: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate detailed monthly salary breakdown for contribution calculations.
    
    This function converts the half-yearly salary matrix into monthly
    breakdowns needed for contribution calculations. It handles the
    transition between half-year periods and provides monthly granularity.
    
    Args:
        salary_matrix (Dict[float, float]): Total salary by year (half-year precision)
        career_progression (List[Dict[str, Any]]): Career progression history
            
    Returns:
        Dict[str, Any]: Monthly salary breakdown with structure:
            {
                'monthly_salary_detailed': Dict[int, float],  # Month index → salary
                'total_annual_salary': float,                 # Total salary for year
                'monthly_averages': Dict[float, float]        # Year → monthly average
            }
        
    Example:
        >>> salary = {2024.0: 84150, 2024.5: 85400}
        >>> career = [{'Year': 2024.0}, {'Year': 2024.5}]
        >>> monthly = get_monthly_salary(salary, career)
        >>> print(f"Monthly breakdown: {len(monthly['monthly_salary_detailed'])} months")
        >>> print(f"Total annual 2024: ₹{monthly['total_annual_salary']:,.0f}")
        
    Note:
        - Converts half-yearly to monthly precision
        - Handles salary changes mid-year
        - Used for contribution calculations
        - Provides monthly averages for each year
    """
    monthly_salary_detailed = {}
    monthly_averages = {}
    
    # Get unique years from career progression
    years = sorted(set(entry['Year'] for entry in career_progression))
    
    for year in years:
        # Get salary for this year (integer part)
        year_int = int(year)
        
        # Get salary for this half-year period
        if year in salary_matrix:
            half_year_salary = salary_matrix[year]
        else:
            # Fallback: use previous half-year salary or default
            available_years = sorted(salary_matrix.keys())
            if available_years:
                prev_year = max(y for y in available_years if y < year)
                half_year_salary = salary_matrix[prev_year]
            else:
                half_year_salary = 50000  # Default salary
        
        # Calculate monthly salary for this half-year period
        monthly_salary = half_year_salary / 12.0
        
        # Assign monthly salaries for this half-year
        if year % 1 == 0.0:  # January-June (first half)
            start_month = 1
            end_month = 6
        else:  # July-December (second half)
            start_month = 7
            end_month = 12
        
        # Calculate month index (1-based, starting from career start)
        base_month = 1
        for prev_year in years:
            if prev_year < year:
                if prev_year % 1 == 0.0:
                    base_month += 6  # First half year
                else:
                    base_month += 6  # Second half year
        
        # Assign monthly salaries
        for month in range(start_month, end_month + 1):
            month_index = base_month + (month - start_month)
            monthly_salary_detailed[month_index] = round(monthly_salary, 2)
        
        # Calculate monthly average for this year
        if year_int not in monthly_averages:
            monthly_averages[year_int] = []
        monthly_averages[year_int].append(monthly_salary)
    
    # Calculate total annual salary (sum of all monthly salaries)
    total_annual_salary = sum(monthly_salary_detailed.values())
    
    # Calculate final monthly averages for each year
    final_monthly_averages = {}
    for year_int, salaries in monthly_averages.items():
        final_monthly_averages[year_int] = round(sum(salaries) / len(salaries), 2)
    
    return {
        'monthly_salary_detailed': monthly_salary_detailed,
        'total_annual_salary': total_annual_salary,
        'monthly_averages': final_monthly_averages
    }


def calculate_total_salary(basic_pay: float, da_percentage: float) -> float:
    """
    Calculate total salary from basic pay and DA percentage.
    
    This is a utility function that computes total salary using
    the formula: Total Salary = Basic Pay × (1 + DA/100)
    
    Args:
        basic_pay (float): Basic pay amount in rupees
        da_percentage (float): DA percentage (e.g., 50.0 for 50%)
        
    Returns:
        float: Total salary including DA
        
    Example:
        >>> salary = calculate_total_salary(56100, 50.0)
        >>> print(f"Total salary: ₹{salary:,.0f}")
        84150  # ₹56,100 × (1 + 50/100) = ₹84,150
        
    Note:
        - Basic pay is the foundation salary without allowances
        - DA percentage is added to basic pay
        - Result is rounded to nearest rupee
        - Used throughout salary calculations
    """
    total_salary = basic_pay * (1 + da_percentage / 100.0)
    return round(total_salary)


def validate_salary_data(salary_matrix: Dict[float, float],
                        career_progression: List[Dict[str, Any]]) -> bool:
    """
    Validate salary data for consistency and completeness.
    
    This function performs various checks to ensure salary calculations
    are valid and consistent with career progression data.
    
    Args:
        salary_matrix (Dict[float, float]): Total salary by year
        career_progression (List[Dict[str, Any]]): Career progression history
            
    Returns:
        bool: True if validation passes, False otherwise
        
    Raises:
        ValueError: If validation fails with specific error details
        
    Example:
        >>> is_valid = validate_salary_data(salary_matrix, career_progression)
        >>> if not is_valid:
        ...     print("Salary validation failed")
        
    Validation Checks:
        - Salary matrix not empty
        - Career progression not empty
        - All career years have corresponding salaries
        - Salaries are positive numbers
        - Year keys are consistent between datasets
    """
    # Check if datasets are not empty
    if not salary_matrix:
        raise ValueError("Salary matrix is empty")
    
    if not career_progression:
        raise ValueError("Career progression is empty")
    
    # Get years from both datasets
    salary_years = set(salary_matrix.keys())
    career_years = set(entry['Year'] for entry in career_progression)
    
    # Check if all career years have corresponding salaries
    missing_years = career_years - salary_years
    if missing_years:
        raise ValueError(f"Missing salary data for years: {missing_years}")
    
    # Check if all salaries are positive
    negative_salaries = [year for year, salary in salary_matrix.items() if salary <= 0]
    if negative_salaries:
        raise ValueError(f"Non-positive salaries found for years: {negative_salaries}")
    
    # Check if year keys are consistent
    if salary_years != career_years:
        raise ValueError(f"Year mismatch: salary years {salary_years} != career years {career_years}")
    
    # All validations passed
    return True


def get_salary_summary(salary_matrix: Dict[float, float],
                      career_progression: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate comprehensive salary summary statistics.
    
    This function provides useful summary information about the salary
    progression including growth rates, averages, and key milestones.
    
    Args:
        salary_matrix (Dict[float, float]): Total salary by year
        career_progression (List[Dict[str, Any]]): Career progression history
            
    Returns:
        Dict[str, Any]: Salary summary with structure:
            {
                'starting_salary': float,
                'final_salary': float,
                'salary_growth_rate': float,
                'average_salary': float,
                'salary_milestones': List[Tuple[float, float]]
            }
        
    Example:
        >>> summary = get_salary_summary(salary_matrix, career_progression)
        >>> print(f"Starting salary: ₹{summary['starting_salary']:,}")
        >>> print(f"Final salary: ₹{summary['final_salary']:,}")
        >>> print(f"Growth rate: {summary['salary_growth_rate']:.1f}%")
        
    Note:
        - Growth rate calculated as CAGR
        - Milestones show salary at key career points
        - Used for analysis and reporting
        - Helps understand salary progression patterns
    """
    if not salary_matrix or not career_progression:
        return {}
    
    # Get salary progression
    years = sorted(salary_matrix.keys())
    salaries = [salary_matrix[year] for year in years]
    
    # Basic statistics
    starting_salary = salaries[0]
    final_salary = salaries[-1]
    
    # Calculate growth rate (CAGR)
    if len(years) > 1:
        total_years = years[-1] - years[0]
        if total_years > 0:
            salary_growth_rate = ((final_salary / starting_salary) ** (1 / total_years) - 1) * 100
        else:
            salary_growth_rate = 0.0
    else:
        salary_growth_rate = 0.0
    
    # Calculate average salary
    average_salary = sum(salaries) / len(salaries)
    
    # Find salary milestones (every 25% increase)
    milestones = []
    base_salary = starting_salary
    milestone_multipliers = [1.25, 1.5, 2.0, 3.0, 4.0, 5.0]
    
    for multiplier in milestone_multipliers:
        target_salary = base_salary * multiplier
        # Find first year when salary reaches this milestone
        for year, salary in salary_matrix.items():
            if salary >= target_salary:
                milestones.append((year, salary))
                break
    
    return {
        'starting_salary': starting_salary,
        'final_salary': final_salary,
        'salary_growth_rate': round(salary_growth_rate, 2),
        'average_salary': round(average_salary, 2),
        'salary_milestones': milestones,
        'total_periods': len(years),
        'salary_range': (min(salaries), max(salaries))
    }


# =============================================================================
# TESTING AND EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("Testing NPS vs UPS Pension Calculator - Salary Module")
    print("=" * 60)
    
    # Sample career progression data
    sample_career = [
        {'Level': '10', 'Basic Pay': 56100, 'Year': 2024.0, 'Year Row in Level': 1},
        {'Level': '10', 'Basic Pay': 57800, 'Year': 2024.5, 'Year Row in Level': 2},
        {'Level': '11', 'Basic Pay': 67700, 'Year': 2025.0, 'Year Row in Level': 1},
        {'Level': '11', 'Basic Pay': 69700, 'Year': 2025.5, 'Year Row in Level': 2}
    ]
    
    # Sample DA matrix
    sample_da = {
        2024.0: 50.0,   # January 2024
        2024.5: 52.0,   # July 2024
        2025.0: 54.0,   # January 2025
        2025.5: 56.0    # July 2025
    }
    
    print("\n1. Testing Salary Matrix Generation:")
    try:
        salary_matrix = get_salary_matrix(sample_career, sample_da)
        print(f"Salary matrix generated: {len(salary_matrix)} entries")
        for year, salary in salary_matrix.items():
            print(f"Year {year}: ₹{salary:,}")
    except Exception as e:
        print(f"Salary matrix generation failed: {e}")
    
    print("\n2. Testing Monthly Salary Breakdown:")
    try:
        monthly_data = get_monthly_salary(salary_matrix, sample_career)
        print(f"Monthly breakdown: {len(monthly_data['monthly_salary_detailed'])} months")
        print(f"Total annual salary: ₹{monthly_data['total_annual_salary']:,.0f}")
        print(f"Monthly averages: {monthly_data['monthly_averages']}")
    except Exception as e:
        print(f"Monthly salary breakdown failed: {e}")
    
    print("\n3. Testing Salary Validation:")
    try:
        is_valid = validate_salary_data(salary_matrix, sample_career)
        print(f"Salary validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    except Exception as e:
        print(f"Salary validation failed: {e}")
    
    print("\n4. Testing Salary Summary:")
    try:
        summary = get_salary_summary(salary_matrix, sample_career)
        print(f"Starting salary: ₹{summary['starting_salary']:,}")
        print(f"Final salary: ₹{summary['final_salary']:,}")
        print(f"Growth rate: {summary['salary_growth_rate']:.1f}%")
        print(f"Average salary: ₹{summary['average_salary']:,}")
        print(f"Salary milestones: {summary['salary_milestones']}")
    except Exception as e:
        print(f"Salary summary failed: {e}")
    
    print("\n5. Testing Utility Functions:")
    try:
        total_salary = calculate_total_salary(56100, 50.0)
        print(f"Basic: ₹56,100, DA: 50% → Total: ₹{total_salary:,}")
        
        # Test with different DA percentages
        for da in [25, 50, 75, 100]:
            salary = calculate_total_salary(56100, da)
            print(f"DA {da}%: ₹{salary:,}")
    except Exception as e:
        print(f"Utility function test failed: {e}")
    
    print("\n✅ All salary module tests completed!")
    