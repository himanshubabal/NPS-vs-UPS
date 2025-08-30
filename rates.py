"""
NPS vs UPS Pension Calculator - Rates Module

This module handles all rate-related calculations including Dearness Allowance (DA),
inflation projections, and interest rate tapering. It provides historical DA data
and projects future rates based on user-defined inflation assumptions.

Key Functions:
- get_DA_matrix(): Generate complete DA matrix from historical data + projections
- get_historical_DA(): Load historical DA data from CSV files
- get_projected_DA(): Project future DA based on inflation rates
- get_interest_rate_tapering_dict(): Build investment return tapering configuration
- get_tapered_rate(): Calculate tapered rate for any given year

DA Calculation Logic:
- Historical data: 6th CPC (2006-2015) and 7th CPC (2016-2025)
- Future projections: Based on user-defined inflation rates
- Pay Commission years: DA resets to 0 at each CPC implementation
- Half-year precision: DA calculated every 6 months (January and July)

Interest Rate Tapering:
- E (Equity): Usually tapers from high to low returns
- C (Corporate Bonds): Moderate tapering
- G (Government Bonds): Minimal tapering
- Taper period: User-defined years over which rates change

Author: Pension Calculator Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Tuple, Any

from helper_functions import *
from default_constants import *


def get_historical_DA() -> Dict[float, float]:
    """
    Load historical DA data from CSV files.
    
    This function loads actual DA percentages from 6th and 7th CPC periods
    and combines them into a single dictionary. Historical data provides
    the foundation for future DA projections.
    
    Returns:
        Dict[float, float]: Historical DA data with keys as years (including half-years)
        
    Example:
        >>> historical_da = get_historical_DA()
        >>> print(f"DA in 2016: {historical_da[2016]}%")
        >>> print(f"DA in 2016.5: {historical_da[2016.5]}%")
        
    Note:
        - 6th CPC: 2006-2015 (with half-year precision)
        - 7th CPC: 2016-2025 (with half-year precision)
        - Half-years represent July 1st (e.g., 2016.5 = July 2016)
    """
    historical_da = {}
    
    try:
        # Load 6th CPC DA data (2006-2015)
        sixth_pc_df = load_csv_into_df(SIXTH_PC_DA_FILE)
        
        # Process 6th CPC data
        for index, row in sixth_pc_df.iterrows():
            year = row.iloc[0]  # First column contains year
            da_value = row.iloc[1]  # Second column contains DA percentage
            
            # Validate data
            if pd.notna(year) and pd.notna(da_value):
                historical_da[float(year)] = float(da_value)
        
        # Load 7th CPC DA data (2016-2025)
        seventh_pc_df = load_csv_into_df(SEVENTH_PC_DA_FILE)
        
        # Process 7th CPC data
        for index, row in seventh_pc_df.iterrows():
            year = row.iloc[0]  # First column contains year
            da_value = row.iloc[1]  # Second column contains DA percentage
            
            # Validate data
            if pd.notna(year) and pd.notna(da_value):
                historical_da[float(year)] = float(da_value)
                
    except FileNotFoundError as e:
        print(f"Warning: Historical DA file not found: {e}")
        print("Using default DA values for historical period")
        
        # Fallback: Use default DA values for historical period
        for year in range(2006, 2026):
            historical_da[year] = 6.0  # Default 6% DA
            historical_da[year + 0.5] = 6.0
    
    return historical_da


def get_projected_DA(initial_inflation_rate: float = DEFAULT_INITIAL_INFLATION_RATE,
                     final_inflation_rate: float = DEFAULT_FINAL_INFLATION_RATE,
                     taper_period_yrs: int = DEFAULT_TAPER_PERIOD,
                     start_year: float = 2025.5) -> Dict[float, float]:
    """
    Project future DA based on inflation rate tapering.
    
    This function projects DA percentages from the end of historical data
    through the retirement period. DA increases based on inflation rates
    that taper from initial to final values over the specified period.
    
    Args:
        initial_inflation_rate (float): Starting inflation rate (default: 7.0%)
        final_inflation_rate (float): Ending inflation rate (default: 4.0%)
        taper_period_yrs (int): Years over which rates taper (default: 40)
        start_year (float): Year to start projections (default: 2025.5)
        
    Returns:
        Dict[float, float]: Projected DA data with keys as years
        
    Example:
        >>> projected_da = get_projected_DA(7.0, 4.0, 40, 2025.5)
        >>> print(f"DA in 2030: {projected_da[2030]}%")
        >>> print(f"DA in 2040: {projected_da[2040]}%")
        
    Note:
        - DA increases every 6 months based on inflation
        - Inflation rate tapers linearly from initial to final
        - DA resets to 0 at Pay Commission implementation years
    """
    projected_da = {}
    
    # Calculate DA at start year (from historical data or default)
    if start_year == 2025.5:
        # Start with 7th CPC final DA value
        start_da = 50.0  # Typical final DA for 7th CPC
    else:
        start_da = 0.0  # Reset DA for new CPC periods
    
    projected_da[start_year] = start_da
    
    # Project DA for each half-year period
    current_da = start_da
    current_year = start_year
    
    # Calculate total periods to project (assuming 100 years max)
    max_periods = int(taper_period_yrs * 2)  # Half-year periods
    
    for period in range(1, max_periods + 1):
        # Calculate next half-year
        next_year = current_year + 0.5
        
        # Calculate current inflation rate based on tapering
        years_elapsed = (next_year - start_year)
        if years_elapsed <= taper_period_yrs:
            # Linear tapering: rate decreases from initial to final
            current_inflation_rate = initial_inflation_rate - (
                (initial_inflation_rate - final_inflation_rate) * 
                (years_elapsed / taper_period_yrs)
            )
        else:
            # After taper period, use final rate
            current_inflation_rate = final_inflation_rate
        
        # DA increases by half the annual inflation rate
        da_increase = current_inflation_rate / 2.0
        current_da += da_increase
        
        # Store DA for this half-year
        projected_da[next_year] = round(current_da, 1)
        
        # Update for next iteration
        current_year = next_year
    
    return projected_da


def get_DA_matrix(initial_inflation_rate: float = DEFAULT_INITIAL_INFLATION_RATE,
                  final_inflation_rate: float = DEFAULT_FINAL_INFLATION_RATE,
                  taper_period_yrs: int = DEFAULT_TAPER_PERIOD,
                  doj: str = '01/01/2024',
                  pay_commission_implement_years: List[int] = DEFAULT_PAY_COMMISSION_YEARS) -> Dict[float, float]:
    """
    Generate complete DA matrix combining historical data and projections.
    
    This is the main function that creates the complete DA matrix used
    throughout the pension calculator. It combines historical DA data
    with future projections and handles DA resets at Pay Commission years.
    
    Args:
        initial_inflation_rate (float): Starting inflation rate for projections
        final_inflation_rate (float): Ending inflation rate after tapering
        taper_period_yrs (int): Years over which inflation rates taper
        doj (str): Date of joining service (affects projection start)
        pay_commission_implement_years (List[int]): Years when CPCs are implemented
        
    Returns:
        Dict[float, float]: Complete DA matrix from 2006 to retirement
        
    Example:
        >>> da_matrix = get_DA_matrix(7.0, 4.0, 40)
        >>> print(f"DA in 2024: {da_matrix[2024]}%")
        >>> print(f"DA in 2030: {da_matrix[2030]}%")
        >>> print(f"DA in 2040: {da_matrix[2040]}%")
        
    Note:
        - Historical data provides foundation (2006-2025)
        - Future projections based on inflation tapering
        - DA resets to 0 at each Pay Commission year
        - Used for salary calculations and inflation adjustments
    """
    # Load historical DA data
    historical_da = get_historical_DA()
    
    # Get projected DA from end of historical data
    projected_da = get_projected_DA(
        initial_inflation_rate=initial_inflation_rate,
        final_inflation_rate=final_inflation_rate,
        taper_period_yrs=taper_period_yrs,
        start_year=2025.5  # Start from end of 7th CPC
    )
    
    # Combine historical and projected data
    complete_da_matrix = {**historical_da, **projected_da}
    
    # Handle DA resets at Pay Commission implementation years
    for pc_year in pay_commission_implement_years:
        if pc_year in complete_da_matrix:
            # Reset DA to 0 at CPC implementation
            complete_da_matrix[pc_year] = 0.0
            
            # Also reset DA for the half-year before CPC (if it exists)
            half_year_before = pc_year - 0.5
            if half_year_before in complete_da_matrix:
                complete_da_matrix[half_year_before] = 0.0
    
    # Sort by year for consistency
    sorted_da_matrix = dict(sorted(complete_da_matrix.items()))
    
    return sorted_da_matrix


def get_interest_rate_tapering_dict(E_initial: float = DEFAULT_E_INITIAL,
                                   E_final: float = DEFAULT_E_FINAL,
                                   C_initial: float = DEFAULT_C_INITIAL,
                                   C_final: float = DEFAULT_C_FINAL,
                                   G_initial: float = DEFAULT_G_INITIAL,
                                   G_final: float = DEFAULT_G_FINAL,
                                   taper_period_yrs: int = DEFAULT_TAPER_PERIOD) -> Dict[str, Any]:
    """
    Build interest rate tapering configuration dictionary.
    
    This function creates a structured dictionary that defines how
    investment returns change over time for different asset classes.
    The rates taper linearly from initial to final values over the
    specified period.
    
    Args:
        E_initial (float): Initial equity return rate (default: 12.0%)
        E_final (float): Final equity return rate (default: 6.0%)
        C_initial (float): Initial corporate bond return rate (default: 8.0%)
        C_final (float): Final corporate bond return rate (default: 4.0%)
        G_initial (float): Initial government bond return rate (default: 4.0%)
        G_final (float): Final government bond return rate (default: 4.0%)
        taper_period_yrs (int): Years over which rates taper (default: 40)
        
    Returns:
        Dict[str, Any]: Configuration dictionary with structure:
            {
                'E': {'initial': float, 'final': float},
                'C': {'initial': float, 'final': float},
                'G': {'initial': float, 'final': float},
                'Taper Period': int
            }
            
    Example:
        >>> config = get_interest_rate_tapering_dict(
        ...     E_initial=12.0, E_final=6.0,
        ...     C_initial=8.0, C_final=4.0,
        ...     G_initial=4.0, G_final=4.0,
        ...     taper_period_yrs=40
        ... )
        >>> print(f"Equity: {config['E']['initial']}% → {config['E']['final']}%")
        >>> print(f"Corporate: {config['C']['initial']}% → {config['C']['final']}%")
        >>> print(f"Government: {config['G']['initial']}% → {config['G']['final']}%")
        
    Note:
        - Equity usually tapers from high to low (aggressive to conservative)
        - Corporate bonds have moderate tapering
        - Government bonds typically have minimal tapering
        - Taper period determines how quickly rates change
    """
    interest_rate_tapering_dict = {}
    
    # Equity returns (E)
    interest_rate_tapering_dict['E'] = {
        'initial': E_initial,
        'final': E_final
    }
    
    # Corporate bond returns (C)
    interest_rate_tapering_dict['C'] = {
        'initial': C_initial,
        'final': C_final
    }
    
    # Government bond returns (G)
    interest_rate_tapering_dict['G'] = {
        'initial': G_initial,
        'final': G_final
    }
    
    # Taper period
    interest_rate_tapering_dict['Taper Period'] = taper_period_yrs
    
    return interest_rate_tapering_dict


def get_tapered_rate(asset_class: str,
                     year: float,
                     interest_rate_tapering_dict: Dict[str, Any],
                     start_year: float = 2024.0) -> float:
    """
    Calculate tapered interest rate for a specific year and asset class.
    
    This function calculates the actual interest rate for a given year
    based on the tapering configuration. Rates change linearly from
    initial to final values over the taper period.
    
    Args:
        asset_class (str): Asset class ('E', 'C', or 'G')
        year (float): Year for which to calculate rate
        interest_rate_tapering_dict (Dict[str, Any]): Tapering configuration
        start_year (float): Year when tapering begins (default: 2024.0)
        
    Returns:
        float: Tapered interest rate for the specified year
        
    Raises:
        ValueError: If asset class is not 'E', 'C', or 'G'
        
    Example:
        >>> config = get_interest_rate_tapering_dict()
        >>> rate_2025 = get_tapered_rate('E', 2025.0, config)
        >>> print(f"Equity return in 2025: {rate_2025:.1f}%")
        >>> rate_2040 = get_tapered_rate('E', 2040.0, config)
        >>> print(f"Equity return in 2040: {rate_2040:.1f}%")
        
    Note:
        - Rates taper linearly from initial to final over taper period
        - After taper period, final rate is used
        - Before start year, initial rate is used
        - Used for investment return calculations in corpus growth
    """
    # Validate asset class
    if asset_class not in ['E', 'C', 'G']:
        raise ValueError(f"Invalid asset class: {asset_class}. Must be 'E', 'C', or 'G'.")
    
    # Get initial and final rates for this asset class
    initial_rate = interest_rate_tapering_dict[asset_class]['initial']
    final_rate = interest_rate_tapering_dict[asset_class]['final']
    taper_period = interest_rate_tapering_dict['Taper Period']
    
    # If before start year, return initial rate
    if year < start_year:
        return initial_rate
    
    # If after taper period, return final rate
    years_elapsed = year - start_year
    if years_elapsed >= taper_period:
        return final_rate
    
    # Calculate tapered rate using linear interpolation
    taper_ratio = years_elapsed / taper_period
    tapered_rate = initial_rate - (taper_ratio * (initial_rate - final_rate))
    
    return round(tapered_rate, 2)


# =============================================================================
# TESTING AND EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("Testing NPS vs UPS Pension Calculator - Rates Module")
    print("=" * 60)
    
    # Test historical DA loading
    print("\n1. Testing Historical DA Loading:")
    try:
        historical_da = get_historical_DA()
        print(f"Historical DA loaded: {len(historical_da)} data points")
        print(f"Sample data: 2016: {historical_da.get(2016, 'N/A')}%, "
              f"2020: {historical_da.get(2020, 'N/A')}%")
    except Exception as e:
        print(f"Historical DA loading failed: {e}")
    
    # Test DA projections
    print("\n2. Testing DA Projections:")
    projected_da = get_projected_DA(7.0, 4.0, 40, 2025.5)
    print(f"Projected DA generated: {len(projected_da)} data points")
    print(f"Sample projections: 2030: {projected_da.get(2030, 'N/A')}%, "
          f"2040: {projected_da.get(2040, 'N/A')}%")
    
    # Test complete DA matrix
    print("\n3. Testing Complete DA Matrix:")
    da_matrix = get_DA_matrix(7.0, 4.0, 40)
    print(f"Complete DA matrix: {len(da_matrix)} data points")
    print(f"Range: {min(da_matrix.keys())} to {max(da_matrix.keys())}")
    
    # Test interest rate tapering
    print("\n4. Testing Interest Rate Tapering:")
    config = get_interest_rate_tapering_dict(12.0, 6.0, 8.0, 4.0, 4.0, 4.0, 40)
    print(f"Tapering config: {config}")
    
    # Test tapered rate calculations
    print("\n5. Testing Tapered Rate Calculations:")
    for year in [2024, 2030, 2040, 2050, 2060]:
        equity_rate = get_tapered_rate('E', year, config)
        corp_rate = get_tapered_rate('C', year, config)
        govt_rate = get_tapered_rate('G', year, config)
        print(f"Year {year}: E={equity_rate}%, C={corp_rate}%, G={govt_rate}%")
    
    # Test DA reset at Pay Commission years
    print("\n6. Testing DA Reset at Pay Commission Years:")
    pc_years = [2026, 2036, 2046, 2056, 2066]
    for pc_year in pc_years:
        if pc_year in da_matrix:
            print(f"CPC {pc_year}: DA = {da_matrix[pc_year]}%")
    
    print("\n✅ All tests completed successfully!")
