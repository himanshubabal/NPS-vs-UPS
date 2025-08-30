"""
NPS vs UPS Pension Calculator - Investment Options Module

This module handles all investment-related calculations including:
- ECG (Equity, Corporate Bonds, Government Bonds) allocation strategies
- Age-based investment allocation changes
- Investment return calculations
- Portfolio rebalancing logic

Key Functions:
- get_investment_allocation(): Main function for getting investment allocation
- get_ecg_matrix(): Generate age-based ECG allocation matrix
- ecg_returns(): Calculate returns based on ECG allocation

Investment Strategies:
- Standard/Benchmark: Conservative 15% equity, 85% bonds
- Auto_LC25: Low equity (25% max), conservative approach
- Auto_LC50: Moderate equity (50% max), balanced approach (Recommended)
- Auto_LC75: High equity (75% max), aggressive approach
- Active: Manual allocation with age-based adjustments

Author: Pension Calculator Team
Version: 1.0
"""

import pprint
from typing import Dict, Tuple, Union


def get_investment_allocation(investment_option: str = 'Auto_LC50', 
                             age: int = 30,
                             start_age: int = 20, 
                             end_age: int = 60) -> Tuple[float, float, float]:
    """
    Get investment allocation percentages for a specific age and investment option.
    
    This is the main function that other modules use to get investment allocation.
    It returns the percentage allocation for Equity (E), Corporate Bonds (C), 
    and Government Bonds (G) based on the chosen investment strategy and age.
    
    Args:
        investment_option (str): Investment strategy choice
            - 'Standard/Benchmark': Conservative approach
            - 'Auto_LC25': Low equity, conservative
            - 'Auto_LC50': Moderate equity, balanced (Recommended)
            - 'Auto_LC75': High equity, aggressive
            - 'Active': Manual allocation with age adjustments
        age (int): Current age for allocation calculation
        start_age (int): Starting age for allocation matrix (default: 20)
        end_age (int): Ending age for allocation matrix (default: 60)
    
    Returns:
        Tuple[float, float, float]: (E_percentage, C_percentage, G_percentage)
            - E_percentage: Equity allocation percentage
            - C_percentage: Corporate bond allocation percentage  
            - G_percentage: Government bond allocation percentage
    
    Raises:
        ValueError: If investment_option is not valid
        ValueError: If age is outside the valid range
    
    Example:
        >>> E, C, G = get_investment_allocation('Auto_LC50', age=35)
        >>> print(f"Equity: {E}%, Corporate: {C}%, Government: {G}%")
        Equity: 50.0%, Corporate: 30.0%, Government: 20.0%
    """
    # Validate age range
    if age < start_age or age > end_age:
        raise ValueError(f"Age {age} must be between {start_age} and {end_age}")
    
    # Get the full ECG matrix for the investment option
    ecg_matrix = get_ecg_matrix(investment_option, start_age, end_age)
    
    # Return allocation for the specific age
    if age in ecg_matrix:
        return ecg_matrix[age]['E'], ecg_matrix[age]['C'], ecg_matrix[age]['G']
    else:
        raise ValueError(f"Age {age} not found in allocation matrix")


def ecg_returns(corpus: int, 
                E_percentage: float = 50.00, 
                C_percentage: float = 30.00, 
                G_percentage: float = 20.00,
                E_return: float = 12.00, 
                C_return: float = 7.0, 
                G_return: float = 7.0) -> int:
    """
    Calculate investment returns based on ECG allocation and return rates.
    
    This function simulates how a corpus grows when invested across different
    asset classes (Equity, Corporate Bonds, Government Bonds) with different
    return rates for each class.
    
    Args:
        corpus (int): Initial corpus amount to invest
        E_percentage (float): Percentage allocated to Equity (default: 50.0)
        C_percentage (float): Percentage allocated to Corporate Bonds (default: 30.0)
        G_percentage (float): Percentage allocated to Government Bonds (default: 20.0)
        E_return (float): Annual return rate for Equity (default: 12.0)
        C_return (float): Annual return rate for Corporate Bonds (default: 7.0)
        G_return (float): Annual return rate for Government Bonds (default: 7.0)
    
    Returns:
        int: Total corpus after applying returns (rounded to integer)
    
    Raises:
        ValueError: If percentages don't sum to 100%
    
    Example:
        >>> final_corpus = ecg_returns(100000, E_percentage=60, C_percentage=25, G_percentage=15)
        >>> print(f"Final Corpus: ₹{final_corpus:,}")
        Final Corpus: ₹108,500
    """
    # Verify that all percentage combined reach 100%
    if abs(E_percentage + C_percentage + G_percentage - 100) > 0.01:
        raise ValueError('Combined percentage distribution of E, C & G must equal 100%')

    # Calculate corpus allocation for each asset class
    E_corpus = corpus * E_percentage / 100
    C_corpus = corpus * C_percentage / 100
    G_corpus = corpus * G_percentage / 100
    
    # Calculate returns for each asset class
    E_return_corpus = E_corpus * (1 + E_return / 100)
    C_return_corpus = C_corpus * (1 + C_return / 100)
    G_return_corpus = G_corpus * (1 + G_return / 100)

    # Calculate total return corpus
    total_return_corpus = int(E_return_corpus + C_return_corpus + G_return_corpus)
    
    return total_return_corpus


def get_ecg_matrix(investment_option: str = 'Auto_LC50', 
                   start_age: int = 20, 
                   end_age: int = 60) -> Dict[int, Dict[str, float]]:
    """
    Generate age-based ECG allocation matrix for a given investment option.
    
    This function creates a comprehensive matrix showing how investment allocation
    changes with age for different investment strategies. It implements the
    age-based rebalancing logic used by pension funds.
    
    Args:
        investment_option (str): Investment strategy choice
            - 'Standard/Benchmark': Conservative 15% equity, 85% bonds
            - 'Auto_LC25': Low equity (25% max), conservative approach
            - 'Auto_LC50': Moderate equity (50% max), balanced approach
            - 'Auto_LC75': High equity (75% max), aggressive approach
            - 'Active': Manual allocation with age-based adjustments
        start_age (int): Starting age for allocation matrix (default: 20)
        end_age (int): Ending age for allocation matrix (default: 60)
    
    Returns:
        Dict[int, Dict[str, float]]: Age-based allocation matrix
            Format: {age: {'E': equity%, 'C': corporate%, 'G': government%}}
    
    Raises:
        ValueError: If investment_option is not valid
    
    Investment Strategy Details:
        - Benchmark: Fixed 15% E + 35% C + 50% G
        - Auto_LC25: E: 25%→5%, C: 45%→5%, G: 30%→90% (age 35→55)
        - Auto_LC50: E: 50%→10%, C: 30%→10%, G: 20%→80% (age 35→55)
        - Auto_LC75: E: 75%→15%, C: 10%→10%, G: 15%→75% (age 35→55)
        - Active: E: 75%→50%, C: 25%, G: 0%→25% (age 50→60)
    
    Example:
        >>> matrix = get_ecg_matrix('Auto_LC50', start_age=30, end_age=40)
        >>> print(f"Age 35 allocation: {matrix[35]}")
        Age 35 allocation: {'E': 50.0, 'C': 30.0, 'G': 20.0}
    """
    # Variables, so easy to refer
    active_choice = 'Active'
    auto_LC25, auto_LC50, auto_LC75 = 'Auto_LC25', 'Auto_LC50', 'Auto_LC75'
    benchmark = 'Standard/Benchmark'
    possible_invest_choices = [active_choice, auto_LC25, auto_LC50, auto_LC75, benchmark]
    
    if investment_option not in possible_invest_choices:
        raise ValueError(f'{investment_option} not a valid option. Please choose from {possible_invest_choices}')
    
    # Initialize and populate dictionary for age from start_age to end_age
    ecg_matrix = {age: {} for age in range(start_age, end_age+1)}

    for age in ecg_matrix:
        # Benchmark -> 15% E + 85% bonds (35% C + 50% G)
        if investment_option == benchmark:
            E_percent, C_percent, G_percent = 15, 35, 50
            
        # LC25 -> Till age of 35 -> E:25, C:45, G:30
        #         E: reduce by 1 each yr, C: reduce by 2 each yr, G: inc by 3 each yr
        #         Till age of 55 -> E:5, C:5, G:90
        elif investment_option == auto_LC25:
            if age <= 35:
                E_percent, C_percent, G_percent = 25, 45, 30
            elif age >= 55:
                E_percent, C_percent, G_percent = 5, 5, 90
            else:
                years_since_35 = age - 35
                E_percent = 25 - 1 * years_since_35
                C_percent = 45 - 2 * years_since_35
                G_percent = 30 + 3 * years_since_35
                
        # LC50 -> Till age of 35 -> E:50, C:30, G:20
        #         E: reduce by 2 each yr, C: reduce by 1 each yr, G: inc by 3 each yr
        #         Till age of 55 -> E:10, C:10, G:80
        elif investment_option == auto_LC50:
            if age <= 35:
                E_percent, C_percent, G_percent = 50, 30, 20
            elif age >= 55:
                E_percent, C_percent, G_percent = 10, 10, 80
            else:
                years_since_35 = age - 35
                E_percent = 50 - 2 * years_since_35
                C_percent = 30 - 1 * years_since_35
                G_percent = 20 + 3 * years_since_35
                
        # LC75 -> Till age 35 -> E:75, C:10, G:15
        #         E: reduce by 3 each year, C:inc by 1 for 10 yr const for next 5 reduce by 2 for next 5, G: inc by 3 each year 
        #         Till age of 55 -> E:15, C:10, G:75
        elif investment_option == auto_LC75:
            if age <= 35:
                E_percent, C_percent, G_percent = 75, 10, 15
            elif age >= 55:
                E_percent, C_percent, G_percent = 15, 10, 75
            else:
                years_since_35 = age - 35
                E_percent = 75 - 3 * years_since_35
                G_percent = 15 + 3 * years_since_35
                # C: inc by 1 for initial 10 yr, const for next 5, reduce by 2 for next 5
                if years_since_35 <= 10:
                    C_percent = 10 + years_since_35 * 1
                elif years_since_35 <= 15:
                    C_percent = 20  # constant for next 5 years (from 10 to 15)
                else:
                    C_percent = 20 - 2 * (years_since_35 - 15)
                    
        # Active -> E: max 75% upto age 50, after that 2.5% redn in E_max, till E_max is 50% by age of 60
        #           C: constant at 25%; G: 0% till age 50 and reaches 25% by age 60
        elif investment_option == active_choice:
            if age <= 50:       # Till age of 50
                E_percent, C_percent, G_percent = 75, 25, 0
            elif age <= 60:     # Age 50 to 60
                years_since_50 = age - 50
                E_percent = 75 - 2.5 * years_since_50
                C_percent = 25
                G_percent = 0 + 2.5 * years_since_50
            else:              # Above 60 (not needed)
                E_percent, C_percent, G_percent = 50, 25, 25     # Assume post-60 E stays at 50%
                
        # Error -> Not a valid input
        else:
            raise ValueError('Provide Valid Investment Options')

        # Store allocation percentages for this age
        ecg_matrix[age]['E'], ecg_matrix[age]['C'], ecg_matrix[age]['G'] = E_percent, C_percent, G_percent

    return ecg_matrix


def get_investment_summary(investment_option: str = 'Auto_LC50', 
                           age: int = 30) -> Dict[str, Union[str, float, str]]:
    """
    Get a summary of investment strategy and current allocation.
    
    Args:
        investment_option (str): Investment strategy choice
        age (int): Current age for allocation
    
    Returns:
        Dict[str, Union[str, float, str]]: Investment summary including:
            - strategy: Description of the strategy
            - risk_level: Risk assessment (Low/Medium/High)
            - equity_allocation: Current equity percentage
            - recommendation: Strategy recommendation
    """
    E, C, G = get_investment_allocation(investment_option, age)
    
    strategy_descriptions = {
        'Standard/Benchmark': 'Conservative approach with fixed 15% equity allocation',
        'Auto_LC25': 'Low equity, conservative approach suitable for risk-averse investors',
        'Auto_LC50': 'Moderate equity, balanced approach recommended for most investors',
        'Auto_LC75': 'High equity, aggressive approach for investors with high risk tolerance',
        'Active': 'Manual allocation with age-based adjustments for experienced investors'
    }
    
    risk_levels = {
        'Standard/Benchmark': 'Low',
        'Auto_LC25': 'Low',
        'Auto_LC50': 'Medium',
        'Auto_LC75': 'High',
        'Active': 'Variable'
    }
    
    recommendations = {
        'Standard/Benchmark': 'Best for conservative investors near retirement',
        'Auto_LC25': 'Good for conservative investors with moderate time horizon',
        'Auto_LC50': 'Recommended for most investors with balanced risk appetite',
        'Auto_LC75': 'Suitable for young investors with high risk tolerance',
        'Active': 'For experienced investors who want control over allocation'
    }
    
    return {
        'strategy': strategy_descriptions.get(investment_option, 'Custom strategy'),
        'risk_level': risk_levels.get(investment_option, 'Unknown'),
        'equity_allocation': E,
        'bond_allocation': C + G,
        'recommendation': recommendations.get(investment_option, 'Consult financial advisor')
    }


if __name__ == "__main__":
    print("=== Investment Options Module Test ===\n")
    
    # Test get_investment_allocation function
    print("1. Testing get_investment_allocation():")
    try:
        E, C, G = get_investment_allocation('Auto_LC50', age=35)
        print(f"   Age 35, Auto_LC50: E={E}%, C={C}%, G={G}%")
        
        E, C, G = get_investment_allocation('Standard/Benchmark', age=40)
        print(f"   Age 40, Benchmark: E={E}%, C={C}%, G={G}%")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Testing ecg_returns():")
    try:
        return_corpus = ecg_returns(100000, E_percentage=60, C_percentage=25, G_percentage=15)
        print(f"   Initial: ₹100,000, Final: ₹{return_corpus:,}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Testing get_ecg_matrix():")
    try:
        ecg_matrix = get_ecg_matrix(investment_option='Auto_LC50', start_age=30, end_age=40)
        print(f"   Auto_LC50 matrix (ages 30-40): {len(ecg_matrix)} entries")
        print(f"   Age 35 allocation: {ecg_matrix[35]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing get_investment_summary():")
    try:
        summary = get_investment_summary('Auto_LC50', age=35)
        print(f"   Summary: {summary}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Test Complete ===")
    