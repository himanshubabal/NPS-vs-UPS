"""
NPS vs UPS Pension Calculator - Utilities Package

This package provides utility functions and helpers used across the application.
It centralizes common operations like date parsing, formatting, and validation.

Author: Pension Calculator Team
Version: 1.0
"""

from .date_utils import (
    parse_date,
    convert_dt_to_string,
    get_retirement_date
)

from .formatting import (
    format_currency,
    format_compact_currency,
    format_number
)

from .validation import (
    validate_basic_pay,
    validate_dates,
    validate_financial_rates
)

__all__ = [
    # Date utilities
    'parse_date',
    'convert_dt_to_string', 
    'get_retirement_date',
    
    # Formatting utilities
    'format_currency',
    'format_compact_currency',
    'format_number',
    
    # Validation utilities
    'validate_basic_pay',
    'validate_dates',
    'validate_financial_rates'
]
