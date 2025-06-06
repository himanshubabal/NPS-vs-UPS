# from helper_functions import load_csv_into_df

PAY_LEVELS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '13A', '14', '15', '16', '17', '18']
INVESTMENT_OPTIONS = ['Standard/Benchmark', 'Auto_LC25', 'Auto_LC50', 'Auto_LC75', 'Active']
SERVICES = ['IFS (AIS)', 'IAS', 'IPS', 'Other Central Services']
DEFAULT_PAY_COMMISSION_YEARS = [2026, 2036, 2046, 2056, 2066]
DEFAULT_FITMENT_FACTOR = 2
DEFAULT_FITMENT_FACTORS = [DEFAULT_FITMENT_FACTOR] * 5
DEFAULT_PC_INCREASE_PERCENT = 15.0
DEFAULT_PC_INCREASE_PERCENT_LIST = [DEFAULT_PC_INCREASE_PERCENT] * 5
DEFAULT_IS_IAS = False

UPS_IMPLEMENT_DATE = '01/04/2025'
DATA_FOLDER_PATH = 'data/'
# PAY_MATRIX_7CPC_CSV = 'data/7th_CPC.csv'
PAY_MATRIX_7CPC_CSV = '7th_CPC.csv'
SIXTH_PC_DA_FILE = '6th_CPC_DA.csv'
SEVENTH_PC_DA_FILE = '7th_CPC_DA.csv'
SIXTH_PC_DA_START_YEAR = 2006
SIXTH_PC_DA_END_YEAR = 2015.5
SEVENTH_PC_DA_START_YEAR = 2016
SEVENTH_PC_DA_END_YEAR = 2025.5
# PAY_MATRIX_7CPC_DF = load_csv_into_df(PAY_MATRIX_7CPC_CSV)
STARTING_YEAR_CPC = 1       # Since new joining starts at year one only

DEFAULT_WITHDRAWL_PERCENTAGE = 25.00    # 25% withdrawl
DEFAULT_MAX_GRATUITY = 2500000      # 25 Lakh
DEFAULT_TAPER_PERIOD = 40
DEFAULT_PENSION_DURATION = 40

# Default Rates
DEFAULT_CONSTANT_INFLATION_RATE = 7.0

DEFAULT_E = 12.0
DEFAULT_C = 8.0
DEFAULT_G = 8.0

DEFAULT_INITIAL_INFLATION_RATE = 7.0
DEFAULT_FINAL_INFLATION_RATE = 4.0

DEFAULT_E_INITIAL = 12.0
DEFAULT_E_FINAL = 6.0
DEFAULT_C_INITIAL = 8.0
DEFAULT_C_FINAL = 4.0
DEFAULT_G_INITIAL = 4.0
DEFAULT_G_FINAL = 4.0