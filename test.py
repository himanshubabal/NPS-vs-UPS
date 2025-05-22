import pandas as pd
import numpy as np
import re
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta # For adding years to date

# --- Constants ---
DEFAULT_PAY_MATRIX_CSV = '7th_CPC.csv'
RETIREMENT_AGE_YEARS = 60

# --- Utility Functions (Implement these based on your actual needs) ---
def parse_date(date_str: str) -> date:
    """Parses a date string (e.g., 'dd/mm/yyyy') into a date object."""
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        try:
            return datetime.strptime(date_str, '%d/%m/%y').date()
        except ValueError:
            raise ValueError(f"Date format for '{date_str}' not recognized. Use 'dd/mm/yyyy' or 'dd/mm/yy'.")

def get_retirement_date(dob_str: str) -> date:
    """Calculates retirement date based on date of birth and retirement age."""
    birth_date = parse_date(dob_str)
    # Retirement is typically end of the month of attaining retirement age,
    # or a fixed date. For simplicity, let's assume exact years.
    retirement_d = birth_date + relativedelta(years=RETIREMENT_AGE_YEARS)
    return retirement_d

def extract_cpc_no_from_filename(filename: str) -> int:
    """Extracts the CPC number (e.g., 7 from '7th_CPC.csv')."""
    match = re.search(r"(\d+)(?:st|nd|rd|th)_CPC", filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    raise ValueError(f"Could not extract CPC number from filename: {filename}")

def _load_and_prepare_matrix(pay_matrix_csv: str) -> pd.DataFrame:
    """Loads pay matrix CSV and prepares it (e.g., string column names)."""
    if not os.path.exists(pay_matrix_csv):
        raise FileNotFoundError(f"Pay matrix CSV file not found: {pay_matrix_csv}")
    df = pd.read_csv(pay_matrix_csv)
    df.columns = df.columns.map(str)
    # Consider setting an index if the first column is 'Stage' or similar:
    # if df.columns[0].lower() in ['stage', 'index', 'cell no']:
    #     df = df.set_index(df.columns[0])
    # df.columns = df.columns.map(str) # re-map if index was set from a numeric column
    return df

# --- Core Pay Matrix Functions ---
def get_basic_pay(pay_matrix_df: pd.DataFrame, level: str | int, year: int) -> int:
    """
    Fetch basic pay for given pay level and year (1-based index).
    
    :param pay_matrix_df: DataFrame of the pay matrix.
    :param level: str or int (e.g., 13, '13A')
    :param year: int (1-based)
    :return: int (basic pay)
    """
    level_str = str(level)
    
    if level_str not in pay_matrix_df.columns:
        raise ValueError(f"Level {level_str} not found in pay matrix.")

    # Check if year is within the valid range for this specific level (number of non-NaN values)
    max_years_for_level = pay_matrix_df[level_str].count() # Number of actual pay stages
    if not (1 <= year <= max_years_for_level):
         # If allowing to go beyond max_years_for_level (e.g. for stagnation), 
         # then fetch the last valid pay.
        if year > max_years_for_level and max_years_for_level > 0:
            return int(pay_matrix_df[level_str].dropna().iloc[-1])
        raise ValueError(
            f"Year {year} is out of range for Level {level_str} (must be 1 to {max_years_for_level})."
        )
    
    basic_val = pay_matrix_df[level_str].iloc[year - 1]
    if pd.isna(basic_val):
        # This might happen if a level has fewer stages than others, and year is valid for DF but not level
        raise ValueError(f"No valid pay found for Level {level_str}, Year {year}. Check matrix data.")
    return int(basic_val)


def get_level_year_from_basic_pay(pay_matrix_df: pd.DataFrame, basic_pay: int) -> tuple[str, int]:
    """
    Given a basic pay, find the highest level and least year it appears at.

    :param pay_matrix_df: DataFrame of the pay matrix.
    :param basic_pay: int
    :return: (level, year) tuple
    """
    found_matches = []
    for level_col in pay_matrix_df.columns:
        # Skip non-numeric columns if any (e.g., if an 'Index' column wasn't set as index)
        if not pd.api.types.is_numeric_dtype(pay_matrix_df[level_col]):
            continue
        for i, value in enumerate(pay_matrix_df[level_col]):
            if pd.notna(value) and int(value) == basic_pay:
                year = i + 1  # convert 0-based index to 1-based year
                found_matches.append((str(level_col), year))

    if not found_matches:
        raise ValueError(f"Basic pay ₹{basic_pay} not found in any level.")

    # Sort: highest level first (handling '13A' as 13.5), then lowest year
    def sort_key(match_item):
        level_val = match_item[0]
        year_val = match_item[1]
        numeric_level = float(level_val.replace('A', '.5')) if 'A' in level_val else float(level_val)
        return (-numeric_level, year_val) # Negative for descending level, positive for ascending year

    found_matches.sort(key=sort_key)
    
    # The prompt asks for "highest level and least year".
    # The sort key above sorts by highest level first, then by lowest year.
    # So, the first element is the desired one.
    return found_matches[0]


def annual_increment(pay_matrix_df: pd.DataFrame, current_level: str | int, year: int) -> tuple[str, int, int]:
    """
    Increment pay by one row within the same level. If already at max pay for the level,
    stay at same amount, but increase year by 1.

    :param pay_matrix_df: DataFrame of the pay matrix.
    :param current_level: int or str
    :param year: int (1-based current year in level)
    :return: (level_str, new_year, new_basic_pay)
    """
    level_str = str(current_level)

    if level_str not in pay_matrix_df.columns:
        raise ValueError(f"Invalid level: {level_str}")
    
    level_series = pay_matrix_df[level_str].dropna()
    if level_series.empty:
        raise ValueError(f"Level {level_str} has no pay data.")
        
    max_steps_for_level = len(level_series)
    max_basic_pay_for_level = int(level_series.iloc[-1])

    if year >= max_steps_for_level: # At or beyond the last defined step for this level
        new_year = year + 1
        new_basic_pay = max_basic_pay_for_level
    else:
        new_year = year + 1
        # year is 1-based current, so new pay is at current year's 0-based index
        new_basic_pay = int(level_series.iloc[year]) 
                                               
    return level_str, new_year, new_basic_pay


def promote_employee(pay_matrix_df: pd.DataFrame, current_level: str | int, year_in_current_level: int, is_ias: bool = False) -> tuple[str, int, int]:
    """
    Promote employee based on rules.

    :param pay_matrix_df: DataFrame of the pay matrix.
    :param current_level: int or str
    :param year_in_current_level: int (1-based current year in the current level)
    :param is_ias: bool
    :return: tuple (new_level, new_year_in_new_level, new_basic_pay)
    """
    current_level_str = str(current_level)
    all_levels = list(pay_matrix_df.columns) # Assuming all columns are pay levels after initial prep

    if current_level_str not in all_levels:
        raise ValueError(f"Level {current_level_str} not found in pay matrix.")

    # Validate year_in_current_level (current stage)
    current_level_series = pay_matrix_df[current_level_str].dropna()
    if not (1 <= year_in_current_level <= len(current_level_series)):
        # Allow promotion even if at a "stagnation" year beyond max steps, using max pay of current level
        if year_in_current_level > len(current_level_series) and len(current_level_series) > 0:
            current_pay_at_stage = current_level_series.iloc[-1]
            # The "one step down" logic for stepped_pay needs to use the last actual increment if possible
            # or just the max pay if already at max.
            # For promotion, one notional increment is given in the *current* level first.
            # So, if at year 10 of 10, the notional increment is to stage 11 (which is same pay as 10).
            # If current_level_series has N items (indexed 0 to N-1), year_in_current_level is 1 to N.
            # Stepped pay is at index year_in_current_level (if year_in_current_level < N)
            if year_in_current_level < len(current_level_series):
                 stepped_pay_index = year_in_current_level 
            else: # at or beyond the last step
                 stepped_pay_index = len(current_level_series) -1 
            stepped_pay = current_level_series.iloc[stepped_pay_index]

        else:
            raise ValueError(
                f"Year {year_in_current_level} is out of range for Level {current_level_str} "
                f"(max {len(current_level_series)} steps)."
            )
    else:
        # Step 1: Get pay of one step down in the *same current level*
        # year_in_current_level is 1-based. iloc is 0-based.
        # If currently at year_in_current_level, next step is at index year_in_current_level.
        if year_in_current_level < len(current_level_series): # Not at the last step
            stepped_pay = current_level_series.iloc[year_in_current_level]
        else: # At the last step of the current level
            stepped_pay = current_level_series.iloc[year_in_current_level - 1]


    # Step 2: Identify next level
    current_level_idx_in_all_levels = all_levels.index(current_level_str)
    
    next_level_idx = current_level_idx_in_all_levels + 1
    if is_ias and current_level_str == '13' and '13A' in all_levels and '14' in all_levels:
        if all_levels[next_level_idx] == '13A': # Check if next is indeed 13A
            next_level_idx += 1 # Skip 13A, go to 14

    if next_level_idx >= len(all_levels):
        raise ValueError(f"No promotable level beyond {current_level_str}.")
    
    next_level_str = all_levels[next_level_idx]
    next_level_series = pay_matrix_df[next_level_str].dropna()

    if next_level_series.empty:
        raise ValueError(f"Promotable Level {next_level_str} has no pay data.")

    # Step 3: Find first cell in next_level_series >= stepped_pay
    found_match_idx_in_next_level = -1
    for i, val in enumerate(next_level_series):
        if val >= stepped_pay:
            found_match_idx_in_next_level = i
            break
    
    if found_match_idx_in_next_level == -1: # Should not happen if pay generally increases
        # Fallback: take the highest pay in the next level if no direct match >= stepped_pay
        # This case implies stepped_pay was higher than any pay in next_level_str, which is unusual.
        # Or if next_level_series was empty (handled above).
        # More likely, it means all values in next_level_series were NaN or less than stepped_pay.
        # If next_level_series is not empty, take the max.
        new_basic_pay = int(next_level_series.iloc[-1])
        new_year_in_new_level = len(next_level_series) # 1-based year
    else:
        # IAS Rule: if current level 10–12, go two steps further down from the matched cell
        if is_ias and current_level_str in {'10', '11', '12'}:
            found_match_idx_in_next_level = min(found_match_idx_in_next_level + 2, len(next_level_series) - 1)
        
        new_basic_pay = int(next_level_series.iloc[found_match_idx_in_next_level])
        new_year_in_new_level = found_match_idx_in_next_level + 1 # Convert 0-based index to 1-based year

    return next_level_str, new_year_in_new_level, new_basic_pay


def generate_next_pay_commission(
    present_pay_matrix_csv: str = DEFAULT_PAY_MATRIX_CSV,
    present_pay_matrix_df: pd.DataFrame | None = None,
    fitment_factor: float | None = None,
    percent_inc_salary: float | str | None = None,
    percent_last_DA: float | str | None = None,
    default_fitment_factor: float = 2.0
) -> pd.DataFrame:
    """
    Generates the next CPC Pay Matrix.
    Loads from present_pay_matrix_csv if present_pay_matrix_df is not provided.
    """
    def normalize_percent(value: float | str) -> float:
        if isinstance(value, str) and value.endswith('%'):
            value = value.rstrip('%')
        val_float = float(value)
        return val_float / 100.0 if val_float > 1.0 else val_float

    if fitment_factor is None:
        if percent_inc_salary is not None and percent_last_DA is not None:
            inc = normalize_percent(percent_inc_salary)
            da = normalize_percent(percent_last_DA)
            fitment_factor = round((1 + da) * (1 + inc), 2) # Standard rounding might be preferred
        elif default_fitment_factor is not None:
            fitment_factor = default_fitment_factor
        else:
            raise ValueError("Either fitment_factor or (percent_inc_salary and percent_last_DA) or default_fitment_factor must be provided.")
            
    current_cpc_num = extract_cpc_no_from_filename(present_pay_matrix_csv)
    next_cpc_num_str = f"{current_cpc_num + 1}"
    # Use "th" for simplicity, can be made more grammatically correct (st, nd, rd, th) if needed
    next_cpc_name = f"{next_cpc_num_str}th_CPC" 

    if present_pay_matrix_df is None:
        source_df = _load_and_prepare_matrix(present_pay_matrix_csv)
    else:
        source_df = present_pay_matrix_df.copy() # Work on a copy
        source_df.columns = source_df.columns.map(str) # Ensure column names are strings

    new_df = source_df.copy()

    # Identify numeric columns to apply fitment (assuming first column might be an index if not set)
    # If index_col was used in _load_and_prepare_matrix, all columns are pay levels.
    # Otherwise, we need to be careful.
    # For safety, iterate through columns and check dtype.
    for col in new_df.columns:
        if pd.api.types.is_numeric_dtype(new_df[col]):
            # Apply transformation, rounding to nearest 100
            new_df[col] = new_df[col].apply(
                lambda x: int(round(x * fitment_factor / 100.0) * 100) if pd.notna(x) else pd.NA
            ).astype("Int64") # Use pandas nullable integer type

    output_filename = f"{next_cpc_name}_fitment_factor_{fitment_factor:.2f}.csv"
    new_df.to_csv(output_filename, index=True if new_df.index.name is not None else False) # Save index if it exists
    print(f"Generated next pay matrix: {output_filename}")
    return new_df


def career_progression(
    initial_level: str | int,
    initial_year_in_level: int,
    promotion_years_array: list[int],
    initial_pay_matrix_csv: str = DEFAULT_PAY_MATRIX_CSV,
    dob: str = '01/01/2000', # dd/mm/yyyy
    doj: str = '09/12/2024', # dd/mm/yyyy
    is_ias: bool = False,
    pay_commission_details: list[dict] | None = None # e.g. [{'year': 2026, 'fitment': 2.57}, ...]
) -> list[dict]:
    """
    Simulates career progression with annual increments, promotions, and pay commission changes.

    :param initial_level: Starting pay level.
    :param initial_year_in_level: Starting stage in the initial_level (1-based).
    :param promotion_years_array: List of years to spend in each level before promotion.
                                   The length of this array determines the number of promotions.
    :param initial_pay_matrix_csv: Filename of the starting pay matrix (e.g., '7th_CPC.csv').
    :param dob: Date of Birth string ('dd/mm/yyyy').
    :param doj: Date of Joining service string ('dd/mm/yyyy').
    :param is_ias: Boolean, if the employee is in IAS (for special promotion rules).
    :param pay_commission_details: List of dictionaries, each specifying 'year' of implementation
                                   and 'fitment' factor (or 'inc_salary' and 'last_da').
                                   Example: [{'year': 2026, 'fitment': 2.0}, {'year': 2036, 'inc_salary': 0.15, 'last_da': 0.50}]
    :return: List of dictionaries, each representing the state for a service year.
    """
    current_pay_matrix_df = _load_and_prepare_matrix(initial_pay_matrix_csv)
    current_pay_matrix_filename = initial_pay_matrix_csv

    if pay_commission_details is None:
        # Default Pay Commission schedule if none provided
        pay_commission_details = [
            {'year': 2026, 'fitment': 2.0},
            {'year': 2036, 'fitment': 2.0},
            {'year': 2046, 'fitment': 2.0},
            {'year': 2056, 'fitment': 2.0},
        ]
    pay_commission_details.sort(key=lambda x: x['year']) # Ensure sorted by year

    date_of_joining = parse_date(doj)
    retirement_date_val = get_retirement_date(dob)
    
    # Max service duration: calculation should be more precise (e.g., up to retirement month)
    # For simplicity, using years.
    max_total_service_years = retirement_date_val.year - date_of_joining.year
    if date_of_joining.month > retirement_date_val.month or \
       (date_of_joining.month == retirement_date_val.month and date_of_joining.day > retirement_date_val.day):
        max_total_service_years -=1


    level = str(initial_level)
    year_in_level = initial_year_in_level
    
    progression_log = []
    
    # Validate initial level against available levels in the matrix
    all_matrix_levels = list(current_pay_matrix_df.columns) # Assuming columns are levels
    if level not in all_matrix_levels:
        raise ValueError(f"Initial level {level} not found in pay matrix columns: {all_matrix_levels}")

    # Validate max number of promotions
    current_level_idx = all_matrix_levels.index(level)
    potential_promotions = len(all_matrix_levels) - 1 - current_level_idx
    if is_ias and '13A' in all_matrix_levels and '14' in all_matrix_levels and \
       all_matrix_levels.index('13A') > current_level_idx and \
       all_matrix_levels.index('13') == current_level_idx : # if current is 13 and 13A exists
        potential_promotions -=1 # IAS skips 13A from 13
    
    if len(promotion_years_array) > potential_promotions:
        raise ValueError(
            f"Requested {len(promotion_years_array)} promotions, but only {potential_promotions} "
            f"are possible from Level {level} in the provided matrix structure."
        )

    current_service_duration_years = 0 # 0-indexed, number of full years completed
    years_spent_in_current_level = 0
    promotion_step_idx = 0 # Index for promotion_years_array
    pay_commission_event_idx = 0

    # Initial basic pay
    basic_pay = get_basic_pay(current_pay_matrix_df, level, year_in_level)

    while current_service_duration_years <= max_total_service_years:
        actual_calendar_year = date_of_joining.year + current_service_duration_years

        progression_log.append({
            "Service Year No.": current_service_duration_years + 1, # 1-indexed for display
            "Calendar Year": actual_calendar_year,
            "Level": level,
            "Year in Level": year_in_level,
            "Basic Pay": basic_pay,
            "Pay Matrix Used": os.path.basename(current_pay_matrix_filename)
        })

        # --- PAY COMMISSION IMPLEMENTATION (effective from NEXT service year) ---
        # Check if a pay commission is due to be *prepared* this calendar year for next year's effect.
        if pay_commission_event_idx < len(pay_commission_details):
            pc_event = pay_commission_details[pay_commission_event_idx]
            # If PC implementation year is NEXT calendar year, generate it NOW.
            if actual_calendar_year == pc_event['year'] - 1:
                print(f"\nINFO: Preparing Pay Commission for effect from {pc_event['year']}...")
                current_pay_matrix_df = generate_next_pay_commission(
                    present_pay_matrix_csv=current_pay_matrix_filename, # Use the filename of the current matrix as base
                    present_pay_matrix_df = current_pay_matrix_df, # Pass the current df too
                    fitment_factor=pc_event.get('fitment'),
                    percent_inc_salary=pc_event.get('inc_salary'),
                    percent_last_DA=pc_event.get('last_da')
                )
                # Update filename for the newly generated matrix
                new_cpc_num = extract_cpc_no_from_filename(current_pay_matrix_filename) + 1
                fit_factor_val = pc_event.get('fitment', 2.0) # Get actual fitment used for filename
                if pc_event.get('fitment') is None and pc_event.get('inc_salary') is not None: # Recalculate for filename if derived
                     inc = normalize_percent(pc_event.get('inc_salary'))
                     da = normalize_percent(pc_event.get('last_da'))
                     fit_factor_val = round((1 + da) * (1 + inc), 2)

                current_pay_matrix_filename = f"{new_cpc_num}th_CPC_fitment_factor_{fit_factor_val:.2f}.csv"
                pay_commission_event_idx += 1
                print(f"INFO: Switched to new pay matrix: {current_pay_matrix_filename} for subsequent calculations.")
                # After a pay commission, the basic pay needs to be re-fixed in the new matrix.
                # Find equivalent or next higher pay in the *same level and year_in_level* but in the *new matrix*.
                # This means the current basic_pay effectively gets multiplied by fitment factor.
                # The generate_next_pay_commission already creates the new matrix with new values.
                # We just need to look up the new basic for the current level and year_in_level.
                basic_pay = get_basic_pay(current_pay_matrix_df, level, year_in_level)
                print(f"INFO: Basic pay revised to {basic_pay} under new commission for Level {level}, Year {year_in_level}.")


        # --- Increment service duration and years in current level for NEXT YEAR's calculation ---
        current_service_duration_years += 1
        if current_service_duration_years > max_total_service_years: # Check if service ended
             break
        
        years_spent_in_current_level += 1
        
        # --- PROMOTION LOGIC (occurs at the *start* of the service year AFTER completing years_for_promotion) ---
        promoted_this_cycle = False
        if promotion_step_idx < len(promotion_years_array):
            years_for_this_promotion_step = promotion_years_array[promotion_step_idx]
            if years_spent_in_current_level >= years_for_this_promotion_step :
                print(f"\nINFO: Attempting Promotion from Level {level} after {years_spent_in_current_level} years.")
                try:
                    new_level, new_year_in_level, new_basic_pay = promote_employee(
                        current_pay_matrix_df, level, year_in_level, is_ias=is_ias
                    )
                    level = new_level
                    year_in_level = new_year_in_level
                    basic_pay = new_basic_pay
                    
                    print(f"INFO: Promoted to Level {level}, Year {year_in_level}, Basic Pay: {basic_pay}")
                    
                    years_spent_in_current_level = 0 # Reset for new level
                    promotion_step_idx += 1
                    promoted_this_cycle = True
                except ValueError as e:
                    print(f"WARNING: Promotion failed or no further promotable level: {e}")
                    # Stay in current level, proceed to annual increment if applicable
                    pass # Will proceed to annual increment

        # --- ANNUAL INCREMENT (if not promoted in this cycle) ---
        if not promoted_this_cycle:
            try:
                # print(f"DEBUG: Annual Increment from L{level}, Y{year_in_level}, BP{basic_pay}")
                _, new_year_in_level, new_basic_pay = annual_increment(
                    current_pay_matrix_df, level, year_in_level
                )
                year_in_level = new_year_in_level
                basic_pay = new_basic_pay
                # print(f"DEBUG: Incremented to L{level}, Y{year_in_level}, BP{basic_pay}")

            except ValueError as e:
                # This might happen if level is invalid (should be caught earlier) or year is out of range
                # For example, if annual_increment doesn't handle stagnation beyond max steps gracefully.
                print(f"WARNING: Annual increment failed: {e}. Max pay for level likely reached.")
                # Keep basic_pay and year_in_level as is, but year_in_level might continue to increase (stagnation)
                year_in_level +=1 # Continue incrementing year for tracking, pay stays same
        
    return progression_log


# --- Example Usage ---
if __name__ == "__main__":
    # Create a dummy 7th_CPC.csv for testing
    dummy_data = {
        'Stage': list(range(1, 41)),
        '1': [18000 + 500 * i for i in range(40)],
        '2': [19900 + 600 * i for i in range(40)],
        '3': [21700 + 700 * i for i in range(40)],
        '10': [56100 + 1500 * i for i in range(20)] + [np.nan]*20, # Level 10 has 20 stages
        '11': [67700 + 1800 * i for i in range(18)] + [np.nan]*22, # Level 11 has 18 stages
        '12': [78800 + 2000 * i for i in range(16)] + [np.nan]*24,
        '13': [123100 + 3000 * i for i in range(15)]+ [np.nan]*25,
        '13A': [131100 + 3500 * i for i in range(12)]+ [np.nan]*28,
        '14': [144200 + 4000 * i for i in range(10)]+ [np.nan]*30,
        '15': [182200 + 5000 * i for i in range(8)]+ [np.nan]*32,
        '16': [205400 + 0 * i for i in range(5)]+ [np.nan]*35, # Fixed pay for some stages
        '17': [225000 + 0 * i for i in range(3)]+ [np.nan]*37, # Fixed pay
        '18': [250000 + 0 * i for i in range(2)]+ [np.nan]*38, # Fixed pay
    }
    dummy_df = pd.DataFrame(dummy_data)
    # Pad shorter levels with last valid pay to simulate reaching max, then fill rest with NaN
    for col in dummy_df.columns:
        if col == 'Stage':
            continue
        level_series = dummy_df[col].dropna()
        if not level_series.empty:
            last_valid_pay = level_series.iloc[-1]
            # Find first NaN
            first_nan_idx = dummy_df[col].isna().idxmax() if dummy_df[col].isna().any() else len(dummy_df[col])
            # Fill up to original length (40 in this dummy data)
            # dummy_df[col].iloc[len(level_series):first_nan_idx] = last_valid_pay # This line has issues with chained assignment on slices
            # Correct way to fill:
            current_length = len(level_series)
            if current_length < len(dummy_df[col]): # If there are NaNs to fill
                 dummy_df[col] = level_series.reindex(dummy_df.index).fillna(method='ffill')


    dummy_df.to_csv(DEFAULT_PAY_MATRIX_CSV, index=False)
    print(f"Created dummy '{DEFAULT_PAY_MATRIX_CSV}' for testing.")

    # Test get_basic_pay
    print("\n--- Testing get_basic_pay ---")
    test_df = _load_and_prepare_matrix(DEFAULT_PAY_MATRIX_CSV)
    print(f"Pay for Level 10, Year 1: {get_basic_pay(test_df, 10, 1)}")      # Expected: 56100
    print(f"Pay for Level 10, Year 20: {get_basic_pay(test_df, 10, 20)}")    # Expected: 56100 + 1500*19
    try:
        print(f"Pay for Level 10, Year 21 (stagnation): {get_basic_pay(test_df, 10, 21)}") # Expected: last pay of L10
    except ValueError as e:
        print(e)

    # Test get_level_year_from_basic_pay
    print("\n--- Testing get_level_year_from_basic_pay ---")
    lvl, yr = get_level_year_from_basic_pay(test_df, 56100) # Should be 10, 1
    print(f"For basic pay 56100: Level {lvl}, Year {yr}")
    lvl, yr = get_level_year_from_basic_pay(test_df, 144200) # Should be 14, 1
    print(f"For basic pay 144200: Level {lvl}, Year {yr}")


    # Test annual_increment
    print("\n--- Testing annual_increment ---")
    l, y, bp = annual_increment(test_df, '10', 1)
    print(f"Increment from L10, Y1: New Level {l}, New Year {y}, New Basic {bp}") # Y2, 57600
    l, y, bp = annual_increment(test_df, '10', 20) # At max of L10 (20 stages)
    print(f"Increment from L10, Y20 (max): New Level {l}, New Year {y}, New Basic {bp}") # Y21, 84600


    # Test promote_employee
    print("\n--- Testing promote_employee ---")
    # Promote from L10, Y5 (current pay: 56100 + 1500*4 = 62100)
    # Stepped pay in L10 at Y6 (index 5) would be 56100 + 1500*5 = 63600
    # Find >=63600 in L11. L11 starts at 67700. So L11, Y1.
    l, y, bp = promote_employee(test_df, '10', 5) 
    print(f"Promotion from L10 Y5: New Level {l}, New Year {y}, New Basic {bp}")

    # Test IAS promotion from L12 to L13 (should skip 13A if it exists and go to 14)
    # Current: L12, Y8 (Pay at Y8 in L12: 78800 + 2000*7 = 92800)
    # Stepped pay in L12 at Y9 (index 8): 78800 + 2000*8 = 94800
    # Find >=94800 in L13. L13 starts at 123100. So L13, Y1.
    # IAS Rule from L12: 2 steps further down in L13. So L13, Y3.
    l, y, bp = promote_employee(test_df, '12', 8, is_ias=True)
    print(f"IAS Promotion from L12 Y8: New Level {l}, New Year {y}, New Basic {bp}")
    
    # Test IAS promotion from L13 (should skip 13A if it exists and go to 14)
    # Current: L13, Y2 (Pay at Y2 in L13: 123100 + 3000*1 = 126100)
    # Stepped pay in L13 at Y3 (index 2): 123100 + 3000*2 = 129100
    # Find >=129100 in L14 (since L13A is skipped). L14 starts at 144200. So L14, Y1.
    l, y, bp = promote_employee(test_df, '13', 2, is_ias=True)
    print(f"IAS Promotion from L13 Y2: New Level {l}, New Year {y}, New Basic {bp}")

    # Test generate_next_pay_commission
    print("\n--- Testing generate_next_pay_commission ---")
    # _8th_df = generate_next_pay_commission(present_pay_matrix_csv=DEFAULT_PAY_MATRIX_CSV, fitment_factor=2.57)
    # print("8th CPC Matrix (first 5 rows of Level 10):")
    # print(_8th_df[['10']].head())
    # _9th_df = generate_next_pay_commission(present_pay_matrix_csv=f"8th_CPC_fitment_factor_2.57.csv", 
    #                                        percent_inc_salary=0.15, percent_last_DA=0.50) # Fitment = (1.5)*(1.15) = 1.725 -> 1.73
    # print("9th CPC Matrix (first 5 rows of Level 10):")
    # print(_9th_df[['10']].head())


    print("\n--- Testing career_progression ---")
    try:
        progression_history = career_progression(
            initial_level=10,
            initial_year_in_level=1,
            promotion_years_array=[4, 5, 4, 3, 4], # Years to spend in L10, L11, L12, L13, L13A before promoting
            initial_pay_matrix_csv=DEFAULT_PAY_MATRIX_CSV,
            dob='01/07/1995', # Assuming DOB for retirement calculation
            doj='09/12/2024', # Date of Joining
            is_ias=False, # Set to True for IAS rules
            pay_commission_details=[
                {'year': 2026, 'fitment': 2.10}, # 8th CPC in 2026 (prepared in 2025)
                {'year': 2036, 'inc_salary': '15%', 'last_da': '40%'} # 9th CPC in 2036 (prepared in 2035)
            ]
        )
        
        print("\nCareer Progression Log:")
        log_df = pd.DataFrame(progression_history)
        print(log_df.to_string())

        # Verify if files were created
        if os.path.exists("8th_CPC_fitment_factor_2.10.csv"):
             print("\nSuccessfully created: 8th_CPC_fitment_factor_2.10.csv")
        # For 9th CPC: Fitment = (1+0.40)*(1+0.15) = 1.40 * 1.15 = 1.61
        if os.path.exists("9th_CPC_fitment_factor_1.61.csv"): 
             print("Successfully created: 9th_CPC_fitment_factor_1.61.csv")


    except Exception as e:
        import traceback
        print(f"An error occurred during career progression: {e}")
        print(traceback.format_exc())