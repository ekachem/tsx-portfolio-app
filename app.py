# app.py
from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
from io import BytesIO
from my_stocks import get_portfolio_data
import time

app = Flask(__name__)

portfolio_cache = {"timestamp": 0, "data": None}
CACHE_DURATION = 10

def get_cached_portfolio_data():
    current_time = time.time()
    if (current_time - portfolio_cache["timestamp"] > CACHE_DURATION) or portfolio_cache["data"] is None:
        portfolio_cache["data"] = get_portfolio_data()
        portfolio_cache["timestamp"] = current_time
    return portfolio_cache["data"]

@app.route("/ping")
def ping():
    return "OK", 200

@app.route("/api/analyze-portfolio", methods=["POST"])
def analyze_portfolio():
    portfolio_data = request.get_json()
    # process portfolio_data like you did with portfolio.csv
    # return analysis as JSON

@app.route("/")
def index():
    portfolio = get_cached_portfolio_data()
    return render_template("index.html",
                           current_value=round(portfolio["latest_value"], 2),
                           growth_percent=round(portfolio["growth"], 2),
                           initial_value=round(portfolio["initial_value"], 2),
                           timestamp=int(time.time()),
                           holdings=portfolio["holdings"],
                           upcoming_dividends=portfolio["upcoming_dividends"],
                           dividend_income=portfolio["dividend_income"],
                           total_dividend_income=round(portfolio["total_dividend_income"], 2),
                           investment_history=portfolio["investment_history"],
                           sector_allocation=portfolio["sector_allocation"],
                           tfsa_limit=round(portfolio["tfsa_limit"], 2),
                           total_contributed=round(portfolio["total_contributed"], 2),
                           risk_flags=portfolio["risk_flags"])

@app.route("/plot.png")
def plot_png():
    portfolio = get_cached_portfolio_data()
    growth_series = portfolio["growth_series"]
    target_growth_series = portfolio["target_growth_series"]
    investment_scaled = portfolio["investment_scaled"]

    fig, ax = plt.subplots(figsize=(10, 5))
    growth_series.plot(ax=ax, label="Growth (%)", linewidth=2)
    target_growth_series.plot(ax=ax, color='red', linestyle='--', label='5% FD Target')
    ax.bar(investment_scaled.index, investment_scaled.values, width=1,
           alpha=0.3, color='orange', label='Investment Activity (scaled)')

    ax.set_xlabel("Date")
    ax.set_title("TFSA Portfolio Growth Over Time")
    ax.set_ylabel("Growth (%)")
    ax.grid(True)
    ax.legend()

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run()
