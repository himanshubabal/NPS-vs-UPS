from flask import Flask, render_template, request
from simulator import simulate_nps_vs_ups

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        dob = request.form['dob']
        joining_date = request.form['joining_date']
        contrib_percent = float(request.form['contrib']) / 100
        return_rate = float(request.form['return']) / 100
        inflation_rate = float(request.form['inflation']) / 100

        results = simulate_nps_vs_ups(
            dob=dob,
            joining_date=joining_date,
            contrib_percent=contrib_percent,
            return_rate=return_rate,
            inflation_rate=inflation_rate
        )
        return render_template('compare.html', data=results)

    return render_template('compare.html', data=None)

if __name__ == "__main__":
    app.run(debug=True)
