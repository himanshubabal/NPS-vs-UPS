"""
NPS vs UPS Pension Calculator - Formatting Utilities Module

This module provides formatting utilities for numbers, currency, and other data
display in the pension calculator application.

Author: Pension Calculator Team
Version: 1.0
"""

from babel.numbers import format_number, format_currency, format_compact_currency
from typing import Union, Optional


def format_currency_amount(amount: Union[int, float], currency: str = 'INR') -> str:
    """
    Format amount as currency with proper Indian formatting.
    
    Args:
        amount (Union[int, float]): Amount to format
        currency (str): Currency code (default: 'INR')
        
    Returns:
        str: Formatted currency string
        
    Example:
        >>> format_currency_amount(1000000)
        '₹1,000,000.00'
        >>> format_currency_amount(1500000.50)
        '₹1,500,000.50'
    """
    try:
        return format_currency(amount, currency, locale='en_IN')
    except Exception:
        # Fallback formatting if babel fails
        return f"₹{amount:,.2f}"


def format_compact_currency_amount(amount: Union[int, float], currency: str = 'INR') -> str:
    """
    Format large amounts in compact form (e.g., ₹1.00Cr, ₹50.00L).
    
    Args:
        amount (Union[int, float]): Amount to format
        currency (str): Currency code (default: 'INR')
        
    Returns:
        str: Compact formatted currency string
        
    Example:
        >>> format_compact_currency_amount(10000000)
        '₹1.00Cr'
        >>> format_compact_currency_amount(500000)
        '₹5.00L'
        >>> format_compact_currency_amount(1000)
        '₹1,000'
    """
    try:
        return format_compact_currency(amount, currency, locale='en_IN')
    except Exception:
        # Fallback compact formatting
        if amount >= 10000000:  # 1 Crore
            return f"₹{amount/10000000:.2f}Cr"
        elif amount >= 100000:  # 1 Lakh
            return f"₹{amount/100000:.2f}L"
        else:
            return f"₹{amount:,.0f}"


def format_number_with_commas(number: Union[int, float], decimal_places: int = 0) -> str:
    """
    Format number with comma separators for thousands.
    
    Args:
        number (Union[int, float]): Number to format
        decimal_places (int): Number of decimal places (default: 0)
        
    Returns:
        str: Formatted number string
        
    Example:
        >>> format_number_with_commas(1234567)
        '1,234,567'
        >>> format_number_with_commas(1234567.89, 2)
        '1,234,567.89'
    """
    try:
        return format_number(number, locale='en_IN', decimal_quantization=False)
    except Exception:
        # Fallback formatting
        if decimal_places == 0:
            return f"{int(number):,}"
        else:
            return f"{number:,.{decimal_places}f}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format decimal value as percentage.
    
    Args:
        value (float): Decimal value (e.g., 0.075 for 7.5%)
        decimal_places (int): Number of decimal places (default: 1)
        
    Returns:
        str: Formatted percentage string
        
    Example:
        >>> format_percentage(0.075)
        '7.5%'
        >>> format_percentage(0.1234, 2)
        '12.34%'
    """
    percentage = value * 100
    return f"{percentage:.{decimal_places}f}%"


def format_large_number(number: Union[int, float]) -> str:
    """
    Format large numbers in human-readable form.
    
    Args:
        number (Union[int, float]): Number to format
        
    Returns:
        str: Human-readable formatted string
        
    Example:
        >>> format_large_number(1000000)
        '1.0M'
        >>> format_large_number(1500000000)
        '1.5B'
        >>> format_large_number(500000)
        '500K'
    """
    if number >= 1_000_000_000:
        return f"{number/1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number/1_000:.1f}K"
    else:
        return str(int(number))


def format_currency_range(min_amount: Union[int, float], 
                         max_amount: Union[int, float], 
                         currency: str = 'INR') -> str:
    """
    Format a range of currency amounts.
    
    Args:
        min_amount (Union[int, float]): Minimum amount
        max_amount (Union[int, float]): Maximum amount
        currency (str): Currency code (default: 'INR')
        
    Returns:
        str: Formatted currency range string
        
    Example:
        >>> format_currency_range(100000, 500000)
        '₹1,00,000 - ₹5,00,000'
        >>> format_currency_range(1000000, 2000000)
        '₹10.00L - ₹20.00L'
    """
    min_formatted = format_compact_currency_amount(min_amount, currency)
    max_formatted = format_compact_currency_amount(max_amount, currency)
    return f"{min_formatted} - {max_formatted}"


def format_table_cell(value: Union[str, int, float], 
                     cell_type: str = 'text',
                     **kwargs) -> str:
    """
    Format value for display in table cells.
    
    Args:
        value (Union[str, int, float]): Value to format
        cell_type (str): Type of cell ('text', 'currency', 'percentage', 'number')
        **kwargs: Additional formatting options
        
    Returns:
        str: Formatted cell value
        
    Example:
        >>> format_table_cell(1000000, 'currency')
        '₹1,000,000.00'
        >>> format_table_cell(0.075, 'percentage')
        '7.5%'
        >>> format_table_cell(1234567, 'number')
        '1,234,567'
    """
    if cell_type == 'currency':
        return format_currency_amount(value, **kwargs)
    elif cell_type == 'percentage':
        return format_percentage(value, **kwargs)
    elif cell_type == 'number':
        return format_number_with_commas(value, **kwargs)
    else:
        return str(value)


if __name__ == "__main__":
    # Test the formatting utility functions
    print("Testing Formatting Utilities...")
    
    # Test currency formatting
    test_amounts = [1000, 50000, 100000, 1000000, 10000000]
    for amount in test_amounts:
        formatted = format_currency_amount(amount)
        compact = format_compact_currency_amount(amount)
        print(f"Amount: {amount:>10} -> {formatted:>15} | {compact:>10}")
    
    # Test number formatting
    test_numbers = [1234, 12345, 123456, 1234567]
    for num in test_numbers:
        formatted = format_number_with_commas(num)
        large = format_large_number(num)
        print(f"Number: {num:>10} -> {formatted:>15} | {large:>5}")
    
    # Test percentage formatting
    test_percentages = [0.05, 0.075, 0.1234, 0.5]
    for pct in test_percentages:
        formatted = format_percentage(pct)
        print(f"Percentage: {pct:>8} -> {formatted:>8}")
    
    # Test currency range
    ranges = [(100000, 500000), (1000000, 2000000)]
    for min_val, max_val in ranges:
        formatted = format_currency_range(min_val, max_val)
        print(f"Range: {min_val:>8} - {max_val:>8} -> {formatted}")
    
    print("All formatting utility tests completed!")
