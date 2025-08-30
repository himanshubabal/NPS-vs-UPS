"""
NPS vs UPS Pension Calculator - Core Package

This package contains the core calculation modules for the pension calculator.
It provides the main business logic for pension calculations, career progression,
and financial modeling.

Author: Pension Calculator Team
Version: 1.0
"""

from .pension_calculator import PensionCalculator
from .career_manager import CareerManager
from .financial_model import FinancialModel
from .investment_manager import InvestmentManager

__all__ = [
    'PensionCalculator',
    'CareerManager', 
    'FinancialModel',
    'InvestmentManager'
]
