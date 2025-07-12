# app.py
from flask import Flask, render_template, send_file, jsonify, request
import matplotlib.pyplot as plt
from io import BytesIO
from my_stocks import get_portfolio_data
import time
import pandas as pd


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

@app.route("/")
def index():
    return "Backend API is running. Please use the frontend dashboard.", 200

@app.route('/api/analyze-portfolio', methods=['POST'])
def analyze_portfolio():
    portfolio_data = request.get_json()
    df = pd.DataFrame(portfolio_data)
    analysis = get_portfolio_data_from_df(df)
    return jsonify(analysis)


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
