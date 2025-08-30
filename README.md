# NPS vs UPS Pension Calculator

A comprehensive pension scheme comparison tool for Indian government employees to evaluate **National Pension System (NPS)** vs **Unified Pension Scheme (UPS)**.

## 🎯 Overview

This application helps government employees make informed decisions about their pension schemes by providing detailed calculations, comparisons, and visualizations of retirement benefits under both NPS and UPS systems.

## ✨ Key Features

### 🔢 **Comprehensive Calculations**
- **Corpus Growth**: Year-by-year investment growth projections
- **Monthly Pension**: Post-retirement monthly income calculations
- **Financial Metrics**: NPV (Net Present Value) and XIRR (Extended Internal Rate of Return)
- **Withdrawal Options**: Lumpsum and monthly pension combinations
- **Inflation Adjustments**: Real-time inflation impact on future benefits

### 🎨 **Advanced Visualizations**
- **Interactive Charts**: Plotly-based corpus growth and comparison charts
- **Comparison Tables**: Side-by-side NPS vs UPS benefit analysis
- **Metric Cards**: Key performance indicators with visual appeal
- **Responsive Design**: Optimized for desktop and mobile devices

### ⚙️ **Flexible Configuration**
- **Career Progression**: Customizable promotion timelines and pay levels
- **Investment Strategies**: Multiple allocation options (Equity, Corporate Bonds, Government Bonds)
- **Financial Parameters**: Adjustable inflation rates, interest rates, and contribution percentages
- **Service Options**: Support for IAS, IPS, IFS, and other central services

## 🏗️ Architecture

### **Core Modules**
```
nps_vs_ups/
├── streamlit_app.py          # Main Streamlit application (core logic only)
├── app.py                    # Alternative simplified app
├── all_data.py              # Central calculation orchestrator
├── pay_commissions.py       # Career progression and pay matrix
├── rates.py                 # DA, inflation, and interest rate management
├── salary.py                # Salary calculations and breakdowns
├── contribution.py          # Employee and government contributions
├── invest_options.py        # Investment allocation strategies
├── pension.py               # Retirement benefit calculations
├── default_constants.py     # Configuration and constants
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── PROJECT_STRUCTURE.md     # Detailed structure overview
├── .gitignore               # Git ignore rules
│
├── 📁 helpers/              # Helper functions and utilities
│   ├── helper_functions.py  # Legacy helper functions
│   ├── utils/               # Utility modules (date, formatting, validation)
│   └── core/                # Core calculation modules (future)
│
├── 📁 styles/               # CSS and styling
│   └── main.css             # Main stylesheet (dark theme)
│
└── 📁 assets/               # Static assets
    ├── data/                # CSV data files
    │   ├── 7th_CPC.csv      # Pay matrix data
    │   ├── 6th_CPC_DA.csv   # Historical DA data
    │   └── 7th_CPC_DA.csv   # Current DA data
    └── images/               # Image files
```

### **Data Flow**
1. **User Input** → Streamlit UI collects parameters
2. **Validation** → Input validation and default value assignment
3. **Career Progression** → Pay level and promotion calculations
4. **Salary Matrix** → Basic pay + DA calculations
5. **Contributions** → Monthly contribution and corpus growth
6. **Investment Returns** → ECG allocation and return calculations
7. **Retirement Benefits** → Pension, lumpsum, and withdrawal amounts
8. **Financial Metrics** → NPV, XIRR, and future projections
9. **Results Display** → Interactive charts and comparison tables

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.8+
- pip package manager

### **Installation Steps**
```bash
# Clone the repository
git clone https://github.com/your-username/nps-vs-ups.git
cd nps-vs-ups

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

### **Dependencies**
```
streamlit>=1.28.0          # Web application framework
plotly>=5.17.0             # Interactive visualizations
pandas>=2.0.0              # Data manipulation
babel>=2.12.0              # Number and currency formatting
altair>=5.0.0              # Statistical visualizations
```

## 📊 Configuration Options

### **Personal Information**
- **Date of Birth**: Affects retirement age and career duration
- **Date of Joining**: Determines service length and promotion eligibility
- **Early Retirement**: Option to specify custom retirement date
- **Service Type**: IAS, IPS, IFS, or other central services

### **Career Configuration**
- **Starting Level**: Initial pay level (7th CPC system)
- **Starting Year**: Year within the starting level
- **Promotion Periods**: Customizable years between promotions
- **Fitment Factors**: Salary increase percentages at each CPC

### **Financial Parameters**
- **Investment Strategy**: 
  - Standard/Benchmark (15% equity)
  - Auto_LC25 (25% max equity)
  - Auto_LC50 (50% max equity) - **Default**
  - Auto_LC75 (75% max equity)
  - Active (manual allocation)
- **Inflation Rates**: Initial and final rates with tapering
- **Interest Rates**: Equity, Corporate, and Government bond returns
- **Contribution Percentages**: Employee (10%) and Government (14%)

### **Retirement Options**
- **Withdrawal Percentage**: Corpus amount to withdraw (1-60%)
- **Annuity Rate**: NPS corpus to pension conversion rate
- **Pension Duration**: Years to project post-retirement benefits
- **Existing Corpus**: Include previous NPS investments

<<<<<<< Updated upstream
#### Service Type
- **Options**: 
  - `IFS (AIS)` - Indian Forest Service (All India Service)
  - `IAS` - Indian Administrative Service
  - `IPS` - Indian Police Service
  - `Other Central Services`
- **Default**: `IFS (AIS)`
- **Impact**: 
  - IAS: Special promotion rules (skips levels 13A, 16); On promotion, granted extra increments in initial career, etc
  - AIS: Starts from Pay Level 10 minimum
  - Other: Full pay level range available

## 🎮 Usage Guide

### **Basic Usage**
1. **Open Application**: Launch `streamlit run streamlit_app.py`
2. **Configure Inputs**: Set personal, career, and financial parameters
3. **Calculate Results**: Click "Calculate Pension Comparison" button
4. **Review Results**: Analyze metrics, charts, and comparisons
5. **Make Decision**: Choose between NPS and UPS based on results

### **Advanced Configuration**
1. **Custom Promotion Timeline**: Modify promotion duration array
2. **Investment Allocation**: Adjust ECG percentages manually
3. **Financial Scenarios**: Test different inflation and interest rate combinations
4. **Early Retirement**: Analyze impact of retiring before standard age

### **Result Interpretation**
- **Final Corpus**: Total accumulated amount at retirement
- **Monthly Pension**: Starting monthly pension amount
- **XIRR**: Investment return rate over the career period
- **NPV**: Present value of future benefits adjusted for inflation
- **Withdrawal Amount**: Lumpsum available at retirement

## 🔧 Customization

### **Adding New Services**
1. Update `SERVICES` list in `default_constants.py`
2. Modify promotion rules in `pay_commissions.py`
3. Add service-specific logic in relevant modules

### **Modifying Financial Parameters**
1. Update rate constants in `default_constants.py`
2. Adjust tapering logic in `rates.py`
3. Modify investment allocation in `invest_options.py`

### **Extending Calculations**
1. Add new functions to appropriate modules
2. Update `all_data.py` to orchestrate new calculations
3. Integrate results into Streamlit UI

## 📈 Performance & Scalability

### **Optimization Features**
- **Lazy Loading**: Data loaded only when needed
- **Caching**: Streamlit session state for user inputs
- **Efficient Calculations**: Vectorized operations where possible
- **Memory Management**: Minimal data duplication

### **Scalability Considerations**
- **Modular Design**: Easy to add new calculation modules
- **Configuration-Driven**: Constants file for easy parameter changes
- **Extensible Architecture**: Support for additional pension schemes

## 🐛 Troubleshooting

### **Common Issues**
1. **Import Errors**: Ensure all dependencies are installed
2. **Data File Errors**: Check CSV files exist in `assets/data/` directory
3. **Calculation Errors**: Verify input parameters are within valid ranges
4. **UI Issues**: Clear browser cache and restart Streamlit
5. **CSS Issues**: Verify `styles/main.css` file exists and is readable

### **Debug Mode**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug info
streamlit run streamlit_app.py --logger.level=debug
```

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit pull request with detailed description

### **Code Standards**
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include type hints for functions
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Government of India**: For pension scheme documentation
- **7th CPC**: Pay commission data and structure
- **Open Source Community**: For the tools and libraries used

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join community discussions
- **Documentation**: Check this README and inline code comments
- **Contributors**: See GitHub Contributors page

---

**Note**: This calculator provides estimates based on current government policies and assumptions. Actual benefits may vary based on policy changes, market conditions, and individual circumstances.

**Version**: 2.0  
**Last Updated**: December 2024  
**Maintainer**: Pension Calculator Team
