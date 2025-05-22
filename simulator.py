import pandas as pd
from datetime import datetime

def simulate_nps_vs_ups(
    dob, joining_date, retirement_age=60,
    initial_basic=56100, contrib_percent=0.2,
    return_rate=0.08, inflation_rate=0.04,
    freq_per_year=2
):
    dob = pd.to_datetime(dob)
    joining_date = pd.to_datetime(joining_date)
    retirement_date = dob.replace(year=dob.year + retirement_age)
    periods = pd.date_range(joining_date, retirement_date, freq=f"{12 // freq_per_year}M")

    records = []
    basic = initial_basic
    nps_corpus = 0
    cumulative_inflation = 1

    for i, date in enumerate(periods):
        year_count = (date - joining_date).days / 365.25
        label = f"{year_count:.1f} yr"

        if i % freq_per_year == 0 and i > 0:
            basic *= 1.03

        contribution = basic * contrib_percent
        nps_corpus = nps_corpus * (1 + return_rate / freq_per_year) + contribution
        cumulative_inflation *= (1 + inflation_rate / freq_per_year)

        records.append({
            "Period": label,
            "Date": date.strftime("%Y-%m-%d"),
            "Basic Pay": round(basic),
            "Contribution": round(contribution),
            "NPS Corpus": round(nps_corpus),
            "NPS Corpus (Inflation Adj)": round(nps_corpus / cumulative_inflation),
        })

    last_basic = round(basic)
    pension = last_basic * 0.5
    pension_infl_adj = pension / cumulative_inflation

    records.append({
        "Period": "Post-Retirement",
        "Date": retirement_date.strftime("%Y-%m-%d"),
        "Basic Pay": last_basic,
        "Contribution": "-",
        "NPS Corpus": "-",
        "NPS Corpus (Inflation Adj)": "-",
        "UPS Pension": round(pension),
        "UPS Pension (Inflation Adj)": round(pension_infl_adj)
    })

    return records
