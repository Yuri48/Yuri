"""Build the AI equity basket price/return panel for Sept 2026.

Input : data/prices_raw.json  (daily closes transcribed from stockanalysis.com /
        investing.com / statmuse / FRED summaries retrieved via web search, 2026-10-03)
Output: data/prices.csv, data/returns.csv, data/basket_summary.csv
"""
import json, numpy as np, pandas as pd

raw = json.load(open("data/prices_raw.json"))
px = pd.DataFrame({t: pd.Series(v) for t, v in raw.items()})
px.index = pd.to_datetime(px.index)
px = px.sort_index().loc["2026-09-01":"2026-09-30"]

# Trading calendar: Sept 1-4, 8-11, 14-18, 21-25, 28-30 (Labor Day Sept 7).
cal = [d for d in px.index if d.weekday() < 5 and d != pd.Timestamp("2026-09-07")]
px = px.reindex(cal)

# Any residual gaps are linearly interpolated in log price and flagged.
gaps = {t: [d.strftime("%Y-%m-%d") for d in px.index[px[t].isna()]] for t in px.columns}
gaps = {k: v for k, v in gaps.items() if v}
px_filled = np.exp(np.log(px).interpolate(limit_direction="both"))
px_filled.to_csv("data/prices.csv", float_format="%.4f")
json.dump(gaps, open("data/price_gaps_interpolated.json", "w"), indent=1)

BASKET = ["NVDA", "AVGO", "AMD", "TSM", "META", "MSFT", "GOOGL", "AMZN", "ORCL", "PLTR"]
CHIPS = ["NVDA", "AVGO", "AMD", "TSM"]
HYPER = ["META", "MSFT", "GOOGL", "AMZN"]
SOFT = ["ORCL", "PLTR"]

r = np.log(px_filled).diff().dropna(how="all")
r["AI_BASKET"] = r[BASKET].mean(axis=1)          # equal-weight, daily rebalanced
r["AI_CHIPS"] = r[CHIPS].mean(axis=1)
r["AI_HYPERSCALERS"] = r[HYPER].mean(axis=1)
r["AI_SOFTWARE"] = r[SOFT].mean(axis=1)
r["AI_BASKET_ABN"] = r["AI_BASKET"] - r["SPX"]    # market-adjusted (abnormal) return
r["AI_CHIPS_ABN"] = r["AI_CHIPS"] - r["SPX"]
r["AI_HYPER_ABN"] = r["AI_HYPERSCALERS"] - r["SPX"]
r["dVIX"] = np.log(px_filled["VIX"]).diff()
r.to_csv("data/returns.csv", float_format="%.6f")

# Summary: cumulative returns over the event window Sept 8 -> Sept 30 (close-to-close)
win = r.loc["2026-09-08":"2026-09-30"]
summ = pd.DataFrame({
    "cum_ret_Sep8_30_%": (np.exp(win.sum()) - 1) * 100,
    "daily_vol_%": win.std() * 100,
    "worst_day_%": win.min() * 100,
    "best_day_%": win.max() * 100,
}).round(2)
summ.to_csv("data/basket_summary.csv")
print(summ.loc[BASKET + ["AI_BASKET", "AI_CHIPS", "AI_HYPERSCALERS", "AI_SOFTWARE", "SPX", "IXIC"]])
print("Interpolated gaps:", gaps)
