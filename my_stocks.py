import yfinance as yf
import pandas as pd
from datetime import datetime
from collections import Counter

TFSA_LIMIT = 7000  # hardcoded for now

def get_portfolio_data_from_df(df):
    try:
        # Ensure numeric columns
        df['shares'] = pd.to_numeric(df['shares'], errors='coerce').fillna(0)
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)

        # Simulate current price +10% (since you don’t have live price here)
        df['current_price'] = df['buy_price'] * 1.1

        # Calculate initial and current values
        df['initial_value'] = df['shares'] * df['buy_price']
        df['current_value'] = df['shares'] * df['current_price']

        total_initial = df['initial_value'].sum()
        total_current = df['current_value'].sum()
        growth = ((total_current - total_initial) / total_initial * 100) if total_initial else 0

        # Build holdings summary
        holdings = []
        for _, row in df.iterrows():
            holdings.append({
                "ticker": str(row['ticker']),
                "shares": int(row['shares']),
                "buy_price": float(round(row['buy_price'], 2)),
                "current_price": float(round(row['current_price'], 2)),
                "change_percent": float(round((row['current_price'] - row['buy_price']) / row['buy_price'] * 100, 2))
            })

        return {
            "latest_value": float(round(total_current, 2)),
            "initial_value": float(round(total_initial, 2)),
            "growth": float(round(growth, 2)),
            "holdings": holdings
        }

    except Exception as e:
        return {"error": f"Backend processing error: {str(e)}"}


def get_portfolio_data_from_df_old(df):
    try:
        # Ensure numeric columns
        df['shares'] = pd.to_numeric(df['shares'], errors='coerce').fillna(0)
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)

        # Simulate current price +10% (since you don’t have live price here)
        df['current_price'] = df['buy_price'] * 1.1

        # Calculate initial and current values
        df['initial_value'] = df['shares'] * df['buy_price']
        df['current_value'] = df['shares'] * df['current_price']

        total_initial = df['initial_value'].sum()
        total_current = df['current_value'].sum()
        growth = ((total_current - total_initial) / total_initial * 100) if total_initial else 0

        # Build holdings summary
        holdings = []
        for _, row in df.iterrows():
            holdings.append({
                "ticker": row['ticker'],
                "shares": row['shares'],
                "buy_price": round(row['buy_price'], 2),
                "current_price": round(row['current_price'], 2),
                "change_percent": round((row['current_price'] - row['buy_price']) / row['buy_price'] * 100, 2)
            })

        return {
            "latest_value": round(total_current, 2),
            "initial_value": round(total_initial, 2),
            "growth": round(growth, 2),
            "holdings": holdings
        }

    except Exception as e:
        return {"error": f"Backend processing error: {str(e)}"}


def get_portfolio_data(csv_file='portfolio.csv'):
    portfolio = {}
    df = pd.read_csv(csv_file, parse_dates=['date'])

    start_date = df['date'].min().strftime('%Y-%m-%d')
    end_date = datetime.now().strftime("%Y-%m-%d")

    tickers = df['ticker'].unique().tolist()
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    if isinstance(data, pd.Series):
        data = data.to_frame()
    data.index = pd.to_datetime(data.index)

    today = pd.Timestamp(datetime.now().date())
    if today not in data.index:
        data.loc[today] = pd.Series([float('nan')] * len(data.columns), index=data.columns)

    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            live_price = t.info.get('regularMarketPrice')
            if live_price is not None:
                data.at[today, ticker] = live_price
        except:
            pass

    portfolio_value = pd.Series(0.0, index=data.index)
    initial_value_series = pd.Series(0.0, index=data.index)

    holdings = []
    dividend_income = []
    sector_counter = Counter()
    total_contributed = 0.0

    for _, row in df.iterrows():
        ticker = row['ticker']
        shares = row['shares']
        buy_price = row['buy_price']
        date = row['date']
        total_contributed += shares * buy_price

        if ticker in data.columns:
            mask = data.index >= date
            portfolio_value[mask] += data.loc[mask, ticker] * shares
            initial_value_series[mask] += shares * buy_price

        try:
            t = yf.Ticker(ticker)
            current_price = t.info.get("regularMarketPrice", 0)
            change_percent = 100 * (current_price - buy_price) / buy_price if buy_price else 0
            sector = t.info.get("sector", "Unknown")
            sector_counter[sector] += shares * buy_price
            holdings.append({
                "ticker": ticker,
                "shares": shares,
                "buy_price": round(buy_price, 2),
                "current_price": round(current_price, 2),
                "change_percent": round(change_percent, 2)
            })

            rate = t.info.get("dividendRate")
            if rate:
                income = round(rate * shares, 2)
                dividend_income.append({
                    "ticker": ticker,
                    "shares": shares,
                    "rate": round(rate, 2),
                    "annual_income": income
                })
        except:
            continue

    total_sector = sum(sector_counter.values())
    sector_allocation = {s: 100 * v / total_sector for s, v in sector_counter.items() if total_sector > 0}

    # Upcoming dividends
    upcoming_dividends = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            div_timestamp = info.get('dividendDate')
            if div_timestamp:
                div_date = datetime.fromtimestamp(div_timestamp).date()
                if div_date >= datetime.now().date():
                    div_history = t.dividends
                    amount = float(div_history.iloc[-1]) if not div_history.empty else None
                    upcoming_dividends.append({
                        "ticker": ticker,
                        "date": div_date,
                        "amount": amount
                    })
        except:
            continue
    upcoming_dividends.sort(key=lambda x: x["date"])

    investment_history = df.sort_values("date").to_dict(orient="records")

    max_growth = ((portfolio_value - initial_value_series) / initial_value_series * 100).max()
    investment_series = pd.Series(0.0, index=portfolio_value.index)
    grouped = df.groupby('date')[['shares', 'buy_price']].apply(lambda g: (g['shares'] * g['buy_price']).sum())
    total_investment = grouped.sum()
    for date, amount in grouped.items():
        if date in investment_series.index:
            investment_series.at[date] = amount / total_investment
    investment_scaled = investment_series * (max_growth / investment_series.max()) if investment_series.max() > 0 else investment_series

    days = (portfolio_value.index - portfolio_value.index.min()).days
    target_growth_series = pd.Series((5.0 / 365.0) * days, index=portfolio_value.index)

    latest_value = portfolio_value.iloc[-1]
    initial_value = initial_value_series.iloc[-1]
    growth = 100.0 * (latest_value - initial_value) / initial_value
    years_held = (datetime.now() - df['date'].min()).days / 365.0

    risk_flags = []
    if any(v > 40 for v in sector_allocation.values()):
        risk_flags.append("Over 40% concentration in one sector.")
    if not dividend_income:
        risk_flags.append("No dividend-generating stocks.")

  
    portfolio["growth_series"] = (portfolio_value - initial_value_series) / initial_value_series * 100
    portfolio["initial_value"] = initial_value
    portfolio["latest_value"] = latest_value
    portfolio["growth"] = growth
    portfolio["years_held"] = years_held
    portfolio["investment_scaled"] = investment_scaled
    portfolio["target_growth_series"] = target_growth_series
    portfolio["upcoming_dividends"] = upcoming_dividends
    portfolio["holdings"] = holdings
    portfolio["dividend_income"] = dividend_income
    portfolio["total_dividend_income"] = sum(i['annual_income'] for i in dividend_income)
    portfolio["investment_history"] = investment_history
    portfolio["sector_allocation"] = sector_allocation
    portfolio["tfsa_limit"] = TFSA_LIMIT
    portfolio["total_contributed"] = total_contributed
    portfolio["risk_flags"] = risk_flags


    return portfolio
