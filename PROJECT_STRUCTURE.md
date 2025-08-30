# NPS vs UPS Pension Calculator - Project Structure

## 📁 **Directory Organization**

```
nps_vs_ups/
├── 📄 streamlit_app.py          # Main application (core logic only)
├── 📄 app.py                    # Alternative simplified app
├── 📄 all_data.py               # Calculation orchestrator
├── 📄 pay_commissions.py        # Career progression logic
├── 📄 rates.py                  # DA and interest rate management
├── 📄 salary.py                 # Salary calculations
├── 📄 contribution.py            # Contribution calculations
├── 📄 invest_options.py         # Investment allocation strategies
├── 📄 pension.py                # Retirement benefit calculations
├── 📄 default_constants.py      # Configuration constants
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                 # Project documentation
├── 📄 PROJECT_STRUCTURE.md      # This file
├── 📄 .gitignore                # Git ignore rules
│
├── 📁 helpers/                  # Helper functions and utilities
│   ├── 📄 __init__.py          # Package initialization
│   ├── 📄 helper_functions.py  # Legacy helper functions
│   │
│   ├── 📁 utils/               # Utility modules
│   │   ├── 📄 __init__.py      # Utils package init
│   │   ├── 📄 date_utils.py    # Date handling utilities
│   │   ├── 📄 formatting.py    # Formatting utilities
│   │   └── 📄 validation.py    # Validation utilities
│   │
│   └── 📁 core/                # Core calculation modules (future)
│       └── 📄 __init__.py      # Core package init
│
├── 📁 styles/                   # CSS and styling
│   └── 📄 main.css             # Main stylesheet (dark theme)
│
└── 📁 assets/                   # Static assets
    ├── 📁 data/                # CSV data files
    │   ├── 📄 7th_CPC.csv      # Pay matrix data
    │   ├── 📄 6th_CPC_DA.csv   # Historical DA data
    │   └── 📄 7th_CPC_DA.csv   # Current DA data
    │
    └── 📁 images/               # Image files
        └── 📄 *.png             # Screenshots and images
```

## 🎯 **File Purposes**

### **Core Application Files**
- **`streamlit_app.py`**: Main Streamlit application with core logic
- **`app.py`**: Alternative simplified version
- **`all_data.py`**: Orchestrates all calculation modules

### **Calculation Modules**
- **`pay_commissions.py`**: Career progression and promotion logic
- **`rates.py`**: Dearness Allowance and interest rate calculations
- **`salary.py`**: Salary matrix and monthly breakdown calculations
- **`contribution.py`**: Employee and government contribution logic
- **`invest_options.py`**: Investment allocation strategies (ECG)
- **`pension.py`**: Retirement benefits and financial metrics

### **Configuration & Utilities**
- **`default_constants.py`**: All configuration constants and defaults
- **`helpers/`**: Package containing all utility functions
- **`styles/`**: CSS styling for dark theme compatibility
- **`assets/`**: Data files and images

## 🔄 **Import Structure**

### **Main Application Imports**
```python
from all_data import get_all_data
from helpers.helper_functions import *
from default_constants import *
from pay_commissions import get_level_year_from_basic_pay, get_basic_pay
from rates import get_DA_matrix
```

### **Helper Package Imports**
```python
from helpers.utils.date_utils import parse_date, convert_dt_to_string
from helpers.utils.formatting import format_currency_amount
from helpers.utils.validation import validate_user_inputs
```

## 📊 **Data Flow**

1. **User Input** → `streamlit_app.py`
2. **Validation** → `helpers/utils/validation.py`
3. **Constants** → `default_constants.py`
4. **Calculations** → `all_data.py` orchestrates:
   - Career progression (`pay_commissions.py`)
   - Salary calculations (`salary.py`)
   - Contributions (`contribution.py`)
   - Investment returns (`invest_options.py`)
   - Retirement benefits (`pension.py`)
5. **Results** → Display in Streamlit UI
6. **Styling** → `styles/main.css`

## 🎨 **Styling Architecture**

- **External CSS**: All styles moved to `styles/main.css`
- **Dark Theme**: Comprehensive dark theme compatibility
- **Responsive Design**: Optimized for different screen sizes
- **Component Styling**: Consistent styling across all UI elements

## 🚀 **Benefits of New Structure**

1. **Cleaner Base Directory**: Only core application files in root
2. **Modular Organization**: Related functions grouped logically
3. **Easier Maintenance**: Clear separation of concerns
4. **Better Scalability**: Easy to add new modules and features
5. **Improved Readability**: Clear file organization and naming
6. **External Styling**: CSS separated from Python logic
7. **Asset Management**: Data and images properly organized

## 🔧 **Development Workflow**

1. **Core Logic**: Edit calculation modules in root directory
2. **Utilities**: Add helper functions in `helpers/` package
3. **Styling**: Modify CSS in `styles/main.css`
4. **Data**: Update CSV files in `assets/data/`
5. **Testing**: Run `streamlit run streamlit_app.py`
6. **Documentation**: Update README and structure files

## 📝 **Adding New Features**

1. **New Calculation Module**: Add to root directory
2. **New Utility Function**: Add to appropriate `helpers/utils/` module
3. **New UI Component**: Add CSS to `styles/main.css`
4. **New Data File**: Place in `assets/data/`
5. **Update Imports**: Modify relevant `__init__.py` files
6. **Update Documentation**: Modify this file and README
