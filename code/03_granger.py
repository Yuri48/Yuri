"""Granger-causality and lead-lag analysis: AI sentiment vs AI-basket returns (Sept 2026).

Input : data/returns.csv, data/sentiment_daily_trading.csv
Output: data/granger_results.csv, data/crosscorr.csv, data/adf.csv, data/predictive_ols.csv
"""
import warnings, numpy as np, pandas as pd, statsmodels.api as sm
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")

r = pd.read_csv("data/returns.csv", index_col=0, parse_dates=True)
s = pd.read_csv("data/sentiment_daily_trading.csv", index_col=0, parse_dates=True)
d = r.join(s, how="inner").dropna(subset=["AI_BASKET", "sent_mean"])
print("Sample:", d.index.min().date(), "->", d.index.max().date(), "| n =", len(d))

SENT = ["sent_mean", "neg_share", "risk_share", "AISI", "social_sent", "sent_headline"]
RET = ["AI_BASKET", "AI_BASKET_ABN", "AI_CHIPS", "AI_HYPERSCALERS", "AI_SOFTWARE", "SPX", "dVIX"]

# --- Stationarity (ADF, constant, lag chosen by AIC with a small cap) ---
adf = []
for c in SENT + RET:
    x = d[c].dropna()
    if len(x) < 10:
        continue
    stat, p, used, nobs, crit, _ = adfuller(x, regression="c", autolag="AIC", maxlag=2)
    adf.append({"series": c, "adf_stat": stat, "p_value": p, "lags": used, "nobs": nobs})
adf = pd.DataFrame(adf).round(4)
adf.to_csv("data/adf.csv", index=False)
print("\nADF tests:\n", adf.to_string(index=False))

# --- Granger tests, both directions, lags 1..3 (F-test on SSR) ---
out = []
for sv in SENT:
    for rv in RET:
        x = d[[rv, sv]].dropna()
        if len(x) < 12:
            continue
        for direction, cols in [("sentiment -> returns", [rv, sv]), ("returns -> sentiment", [sv, rv])]:
            try:
                res = grangercausalitytests(x[cols], maxlag=3)
            except Exception as e:
                print("granger failed", sv, rv, direction, repr(e)); continue
            for lag, (tests, _) in res.items():
                f, p = tests["ssr_ftest"][0], tests["ssr_ftest"][1]
                out.append({"sentiment": sv, "returns": rv, "direction": direction, "lag": lag,
                            "F": f, "p_value": p, "n": len(x)})
g = pd.DataFrame(out).round(4)
g.to_csv("data/granger_results.csv", index=False)

# --- VAR lag selection and sign of the predictive coefficient (HAC SE) ---
ols = []
for sv in SENT:
    for rv in RET:
        x = d[[rv, sv]].dropna()
        if len(x) < 12:
            continue
        try:
            sel = VAR(x).select_order(maxlags=3)
            aic_lag = int(sel.aic)
        except Exception:
            aic_lag = np.nan
        y = x[rv].iloc[1:]
        X = sm.add_constant(pd.DataFrame({"sent_lag1": x[sv].shift(1), "ret_lag1": x[rv].shift(1)}).iloc[1:])
        m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
        ols.append({"sentiment": sv, "returns": rv, "var_aic_lag": aic_lag,
                    "beta_sent_lag1": m.params["sent_lag1"], "t_HAC": m.tvalues["sent_lag1"],
                    "p_HAC": m.pvalues["sent_lag1"], "R2": m.rsquared, "n": int(m.nobs)})
ols = pd.DataFrame(ols).round(4)
ols.to_csv("data/predictive_ols.csv", index=False)

# --- Lead/lag cross-correlations: corr(sent_{t-k}, ret_t) for k = -3..3 ---
cc = []
for sv in SENT:
    for rv in ["AI_BASKET", "AI_BASKET_ABN", "AI_CHIPS", "AI_HYPERSCALERS"]:
        x = d[[rv, sv]].dropna()
        for k in range(-3, 4):
            cc.append({"sentiment": sv, "returns": rv, "k (sent leads by k days)": k,
                       "corr": x[rv].corr(x[sv].shift(k))})
cc = pd.DataFrame(cc).round(3)
cc.to_csv("data/crosscorr.csv", index=False)

pd.set_option("display.width", 200)
print("\nGranger p-values (sentiment -> returns), lag 1 / 2:")
piv = g[g.direction == "sentiment -> returns"].pivot_table(index="sentiment", columns=["returns", "lag"], values="p_value")
print(piv.round(3).to_string())
print("\nGranger p-values (returns -> sentiment), lag 1 / 2:")
piv2 = g[g.direction == "returns -> sentiment"].pivot_table(index="sentiment", columns=["returns", "lag"], values="p_value")
print(piv2.round(3).to_string())
print("\nPredictive OLS (sign of lagged sentiment):\n", ols.to_string(index=False))
print("\nCross-correlations (AI_BASKET):\n", cc[cc.returns == "AI_BASKET"].pivot(index="sentiment", columns="k (sent leads by k days)", values="corr").to_string())
