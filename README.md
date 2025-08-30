# NPS vs UPS Pension Calculator

A comprehensive pension scheme comparison tool for Indian government employees to evaluate **NPS (National Pension System)** vs **UPS (Universal Pension Scheme)** based on career parameters and financial assumptions.

## 🎯 Purpose

This application helps government employees make informed decisions about their pension scheme choice by providing:
- Detailed career progression simulation
- Financial modeling with customizable parameters
- Side-by-side comparison of NPS vs UPS benefits
- Data-driven recommendations with weighted scoring
- Interactive visualizations and charts

## 🏗️ Architecture

```
streamlit_app.py (Main UI)
├── all_data.py (Data aggregation & orchestration)
├── helper_functions.py (Utility functions & helpers)
├── default_constants.py (Configuration & defaults)
├── pay_commissions.py (Career progression & pay matrix)
├── rates.py (DA & interest rate calculations)
├── salary.py (Salary computation & monthly breakdown)
├── contribution.py (Contribution & corpus calculation)
├── pension.py (Retirement benefits & financial metrics)
└── invest_options.py (Investment allocation strategies)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation
```bash
# Clone or download the project
cd nps_vs_ups

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py --server.port 8501
```

### Access
Open your browser and navigate to: **http://localhost:8501**

## 📋 User Input Options

### 1. Personal & Career Details

#### Date of Birth (DOB)
- **Range**: 1965-01-01 to 2005-12-31
- **Default**: 1995-01-01
- **Impact**: Determines retirement age (60 years) and service duration

#### Date of Joining (DOJ)
- **Range**: 2006-01-01 to 2030-12-31
- **Default**: 2024-12-09
- **Impact**: Starting point for career progression and calculations

#### Early Retirement
- **Toggle**: Checkbox for early retirement consideration
- **When Enabled**: Allows custom retirement date input
- **Range**: 2025-01-01 to calculated retirement age
- **Impact**: Affects service duration and pension calculations

#### Service Type
- **Options**: 
  - `IFS (AIS)` - Indian Foreign Service (All India Service)
  - `IAS` - Indian Administrative Service
  - `IPS` - Indian Police Service
  - `Other Central Services`
- **Default**: `IFS (AIS)`
- **Impact**: 
  - IAS: Special promotion rules (skips levels 13A, 16)
  - AIS: Starts from Pay Level 10 minimum
  - Other: Full pay level range available

### 2. Existing Corpus & Current Status

#### Consider Existing NPS Corpus
- **Toggle**: Checkbox for existing NPS Tier 1 corpus
- **Auto-Enable**: Automatically checked if DOJ < 2024-01-01
- **Impact**: 
  - Shifts calculation start date to UPS implementation date
  - Includes existing corpus in calculations
  - Requires current basic pay input

#### Existing Corpus Amount
- **Input**: Number input for current NPS corpus
- **Step**: ₹1,000 increments
- **Display**: Formatted compact currency (e.g., ₹1.00Cr)
- **Impact**: Added to yearly contributions as initial value

#### Current Basic Pay (7th CPC)
- **Input**: Current basic pay according to 7th CPC
- **Step**: ₹100 increments
- **Validation**: Must match valid pay level/year combination
- **Auto-Display**: Corresponding pay level and year index
- **Impact**: Starting point for career progression

### 3. Career Progression

#### Starting Pay Level (New Recruits)
- **Options**: Pay Levels 1-18 (with AIS restrictions)
- **Default**: Level 10 for AIS services
- **Auto-Calculate**: Basic pay based on level and starting year
- **Impact**: Initial career position and progression path

#### Promotion Schedule
- **Dynamic Rows**: Based on available levels from starting position
- **Input Fields**:
  - **Next Promotion Level**: Select from available higher levels
  - **Promotion Year**: Absolute year (e.g., 2028) or duration (e.g., 4 years)
- **Auto-Validation**: Shows selected level and due year
- **Default Schedule**: [4, 5, 4, 1, 4, 7, 5, 3] years if none specified
- **Impact**: Career advancement timing and pay progression

### 4. Financial Parameters

#### Inflation & Interest Rate Mode
- **Options**: 
  - `Constant` - Fixed rates throughout career
  - `Variable (tapering)` - Rates change over time

#### Constant Mode
- **Inflation Rate**: 0.0% to 20.0% (default: 7.0%)
- **Equity Return**: 0.0% to 15.0% (default: 12.0%)
- **Corporate Bond Return**: 0.0% to 10.0% (default: 8.0%)
- **Government Bond Return**: 0.0% to 10.0% (default: 8.0%)

#### Variable (Tapering) Mode
- **Inflation**: Initial (0.0% to 20.0%) → Final (0.0% to 20.0%)
  - Default: 7.0% → 4.0%
- **Equity**: Initial (0.0% to 20.0%) → Final (0.0% to 20.0%)
  - Default: 12.0% → 6.0%
- **Corporate Bonds**: Initial (0.0% to 10.0%) → Final (0.0% to 10.0%)
  - Default: 8.0% → 4.0%
- **Government Bonds**: Initial (0.0% to 10.0%) → Final (0.0% to 10.0%)
  - Default: 4.0% → 4.0%
- **Taper Period**: 40 years (default)

### 5. Pay Commission Settings

#### Implementation Years
- **Default Schedule**: [2026, 2036, 2046, 2056, 2066]
- **Auto-Calculate**: 
  - **DA at PC Year**: Last half-year DA before commission
  - **Salary Increase %**: Derived from fitment factor and DA
  - **Fitment Factor**: (1 + DA%) × (1 + Salary Increase %)
- **User Override**: Custom fitment factors for each commission
- **Impact**: Salary jumps and DA resets at commission years

### 6. Investment & Retirement Options

#### Investment Strategy
- **Options**:
  - `Standard/Benchmark`: 15% Equity, 35% Corporate Bonds, 50% Government Bonds
  - `Auto_LC25`: Lifecycle 25% (aggressive to conservative)
  - `Auto_LC50`: Lifecycle 50% (moderate to conservative) - **Default**
  - `Auto_LC75`: Lifecycle 75% (very aggressive to conservative)
  - `Active`: 75% Equity till 50, then tapering to 50%
- **Glide Path**: Age-based asset allocation changes
- **Impact**: Risk-return profile and corpus growth

#### Annuity Rate (NPS)
- **Range**: 1.0% to 10.0%
- **Default**: Inflation at retirement + 1%
- **Calculation**: Based on retirement year DA projection
- **Impact**: Monthly pension amount from NPS corpus

#### Corpus Withdrawal
- **Range**: 1.0% to 60.0%
- **Default**: 25%
- **Impact**: 
  - Amount withdrawn at retirement
  - Remaining corpus for annuity/pension

#### Maximum Gratuity
- **Range**: ₹25,00,000 to ₹10,00,00,000
- **Default**: ₹25,00,000 (current government cap)
- **Impact**: Additional retirement benefit amount

## 📊 Output Metrics

### 1. Career Progression
- **Level Progression**: Pay level changes over time
- **Basic Pay Growth**: Annual increments and promotions
- **Salary Matrix**: Basic + DA over career span
- **Service Duration**: Years and months in service

### 2. Financial Projections
- **Yearly Corpus**: NPS corpus growth year by year
- **Final Corpus**: Total accumulated amount at retirement
- **Monthly Salary**: Detailed monthly breakdown
- **Contribution History**: Employee + government contributions

### 3. Retirement Benefits
- **Monthly Pension**: Starting pension amount
- **Lumpsum (UPS)**: One-time payment at retirement
- **Total Withdrawal**: Corpus + lumpsum + gratuity
- **Future Pension**: Pension growth over retirement years

### 4. Performance Metrics
- **NPV**: Net Present Value (inflation-adjusted)
- **XIRR**: Extended Internal Rate of Return
- **10-year Pension Total**: Cumulative pension over first decade

### 5. Comparison & Recommendation
- **Side-by-Side Charts**: Bar charts for key metrics
- **Weighted Scoring**: 
  - Monthly Pension: 35%
  - 10-year Pension Total: 25%
  - Total Withdrawal: 15%
  - Final Corpus: 15%
  - NPV: 5%
  - XIRR: 5%
- **Clear Recommendation**: Winner with top reasons

## 🔧 Configuration Files

### `default_constants.py`
- Pay levels, service options, default rates
- Pay commission years and fitment factors
- Taper periods and pension duration
- Investment option definitions

### `data/` Directory
- **7th_CPC.csv**: Main pay matrix
- **6th_CPC_DA.csv**: Historical DA data (2006-2015)
- **7th_CPC_DA.csv**: Historical DA data (2016-2025)
- **Generated CPCs**: Future pay matrices with fitment factors

## 📈 Key Algorithms

### Career Progression
```python
# Half-year simulation with mid-year increments and year-end promotions
if year % 1 == 0.5:  # July 1st - annual increment
    apply_annual_increment()
if year % 1 != 0.5:  # January 1st - promotion + pay commission
    if is_pay_commission_year(): apply_fitment_factor()
    if is_promotion_year(): apply_promotion()
```

### DA Calculation
```python
# Historical data + projected inflation with PC resets
if year <= 2025.5: use_historical_da()
else: 
    current_da += inflation_rate / 2
    if year == pay_commission_year: current_da = 0
```

### Investment Allocation
```python
# Age-based glide path (example: Auto_LC50)
if age <= 35: E:50%, C:30%, G:20%
elif age >= 55: E:10%, C:10%, G:80%
else: linear_transition()
```

## 🎨 UI Features

### Layout
- **Wide Layout**: Optimized for dashboard view
- **Expanded Sidebar**: Easy access to all options
- **Responsive Columns**: Organized input sections
- **Expandable Sections**: Optional parameters hidden by default

### Visualizations
- **Line Charts**: Career progression, corpus growth, pension projection
- **Bar Charts**: Metric comparisons (Altair)
- **Data Tables**: Formatted currency and compact displays
- **Metrics**: Key performance indicators

### User Experience
- **Real-time Validation**: Input validation and error messages
- **Auto-calculation**: Derived values and suggestions
- **Session State**: Remembers user preferences
- **Responsive Design**: Works on different screen sizes

## 🚨 Error Handling

### Validation Checks
- Basic pay must match valid level/year combination
- Early retirement requires custom date input
- Existing corpus mode requires current basic pay
- Promotion schedule validation

### Graceful Failures
- Safe session state access with `.get()` method
- Default values when inputs are missing
- Clear error messages and warnings
- App continues with reasonable defaults

## 🔍 Troubleshooting

### Common Issues
1. **Port Already in Use**: Change port with `--server.port 8502`
2. **Missing Dependencies**: Ensure all packages from `requirements.txt` are installed
3. **Data File Errors**: Check `data/` directory for required CSV files
4. **Memory Issues**: Large career spans may require more RAM

### Debug Mode
```bash
streamlit run streamlit_app.py --logger.level debug
```

## 📚 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Altair**: Statistical visualization
- **Babel**: Internationalization and formatting
- **pyxirr**: Extended Internal Rate of Return calculation

### Performance
- **Caching**: CSV loading and data processing
- **Efficient Algorithms**: O(n) complexity for most operations
- **Memory Management**: Streaming data processing for large careers

### Extensibility
- **Modular Design**: Easy to add new features
- **Configuration Driven**: Constants and defaults easily modifiable
- **Plugin Architecture**: New investment strategies can be added

## 🤝 Contributing

### Code Structure
- Follow existing naming conventions
- Add comprehensive docstrings
- Include type hints where possible
- Test with various input combinations

### Adding Features
- New investment strategies in `invest_options.py`
- Additional pay commission logic in `pay_commissions.py`
- Extended financial metrics in `pension.py`

## 📄 License

This project is provided as-is for educational and planning purposes. Please consult with financial advisors for actual retirement planning decisions.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages in the terminal
3. Verify all data files are present
4. Ensure Python version compatibility

---

**Note**: This calculator provides estimates based on current government policies and assumptions. Actual benefits may vary based on policy changes, market conditions, and individual circumstances.