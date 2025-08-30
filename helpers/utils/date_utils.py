"""
NPS vs UPS Pension Calculator - Date Utilities Module

This module provides date-related utility functions for the pension calculator.
It handles date parsing, conversion, and retirement date calculations.

Author: Pension Calculator Team
Version: 1.0
"""

from datetime import datetime, date, timedelta
from typing import Union, Optional


def parse_date(date_string: str) -> date:
    """
    Parse date string in DD/MM/YYYY format to date object.
    
    Args:
        date_string (str): Date string in DD/MM/YYYY format
        
    Returns:
        date: Parsed date object
        
    Raises:
        ValueError: If date string format is invalid
        
    Example:
        >>> parse_date("15/06/1995")
        datetime.date(1995, 6, 15)
        >>> parse_date("01/01/2024")
        datetime.date(2024, 1, 1)
    """
    try:
        return datetime.strptime(date_string, "%d/%m/%Y").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format. Expected DD/MM/YYYY, got: {date_string}") from e


def convert_dt_to_string(dt: Union[date, datetime]) -> str:
    """
    Convert date or datetime object to DD/MM/YYYY string format.
    
    Args:
        dt (Union[date, datetime]): Date or datetime object to convert
        
    Returns:
        str: Date string in DD/MM/YYYY format
        
    Example:
        >>> convert_dt_to_string(date(1995, 6, 15))
        '15/06/1995'
        >>> convert_dt_to_string(datetime(2024, 1, 1))
        '01/01/2024'
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime("%d/%m/%Y")


def get_retirement_date(dob: str, retirement_age: int = 60) -> date:
    """
    Calculate standard retirement date based on date of birth.
    
    This function calculates when an employee would normally retire based on
    their date of birth and the standard retirement age (60 years for government employees).
    
    Args:
        dob (str): Date of birth in DD/MM/YYYY format
        retirement_age (int): Standard retirement age in years (default: 60)
        
    Returns:
        date: Calculated retirement date
        
    Example:
        >>> get_retirement_date("15/06/1995")
        datetime.date(2055, 6, 15)
        >>> get_retirement_date("01/01/1990", 58)
        datetime.date(2048, 1, 1)
        
    Note:
        - Standard retirement age for government employees is 60 years
        - Some services may have different retirement ages
        - Early retirement options are available through separate UI controls
    """
    birth_date = parse_date(dob)
    retirement_date = birth_date + timedelta(days=retirement_age * 365)
    
    # Adjust for leap years
    leap_years = sum(1 for year in range(birth_date.year, retirement_date.year + 1) 
                     if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
    retirement_date += timedelta(days=leap_years)
    
    return retirement_date


def calculate_service_duration(doj: str, dor: str) -> tuple[int, int]:
    """
    Calculate total service duration in years and months.
    
    Args:
        doj (str): Date of joining in DD/MM/YYYY format
        dor (str): Date of retirement in DD/MM/YYYY format
        
    Returns:
        tuple[int, int]: (years, months) of service
        
    Example:
        >>> calculate_service_duration("01/01/2024", "01/01/2054")
        (30, 0)
        >>> calculate_service_duration("15/06/2020", "15/08/2050")
        (30, 2)
    """
    join_date = parse_date(doj)
    retirement_date = parse_date(dor)
    
    # Calculate difference
    delta = retirement_date - join_date
    
    # Convert to years and months
    years = delta.days // 365
    remaining_days = delta.days % 365
    
    # Approximate months (not exact due to varying month lengths)
    months = int(remaining_days / 30.44)
    
    return years, months


def is_valid_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate that start date is before end date.
    
    Args:
        start_date (str): Start date in DD/MM/YYYY format
        end_date (str): End date in DD/MM/YYYY format
        
    Returns:
        bool: True if start_date < end_date, False otherwise
        
    Example:
        >>> is_valid_date_range("01/01/2024", "01/01/2025")
        True
        >>> is_valid_date_range("01/01/2025", "01/01/2024")
        False
    """
    start = parse_date(start_date)
    end = parse_date(end_date)
    return start < end


def get_financial_year(date_obj: Union[date, str]) -> int:
    """
    Get financial year for a given date.
    
    Financial year runs from April 1st to March 31st of the next calendar year.
    
    Args:
        date_obj (Union[date, str]): Date object or string in DD/MM/YYYY format
        
    Returns:
        int: Financial year (e.g., 2024 for dates between Apr 2024 - Mar 2025)
        
    Example:
        >>> get_financial_year("15/06/2024")
        2024
        >>> get_financial_year("01/01/2025")
        2024
        >>> get_financial_year("01/04/2025")
        2025
    """
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
    
    if date_obj.month >= 4:
        return date_obj.year
    else:
        return date_obj.year - 1


if __name__ == "__main__":
    # Test the date utility functions
    print("Testing Date Utilities...")
    
    # Test parse_date
    test_dates = ["15/06/1995", "01/01/2024", "31/12/1990"]
    for test_date in test_dates:
        parsed = parse_date(test_date)
        print(f"parse_date('{test_date}') = {parsed}")
    
    # Test retirement date calculation
    dob = "15/06/1995"
    retirement = get_retirement_date(dob)
    print(f"Retirement date for DOB {dob}: {retirement}")
    
    # Test service duration
    doj = "01/01/2024"
    dor = "01/01/2054"
    years, months = calculate_service_duration(doj, dor)
    print(f"Service duration from {doj} to {dor}: {years} years, {months} months")
    
    # Test financial year
    test_dates = ["15/06/2024", "01/01/2025", "01/04/2025"]
    for test_date in test_dates:
        fy = get_financial_year(test_date)
        print(f"Financial year for {test_date}: {fy}")
    
    print("All date utility tests completed!")
