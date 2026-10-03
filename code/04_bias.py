"""Media-negativity analysis in the spirit of Sacerdote, Sehgal & Cook (2020), 'Why is all COVID-19 news bad news?'

Input : data/corpus_scored.csv, data/returns.csv, data/sentiment_daily_trading.csv
Output: data/bias_by_outlet.csv, data/bias_by_topic.csv, data/bias_negativity_vs_facts.csv, data/bias_tests.txt
"""
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats

df = pd.read_csv("data/corpus_scored.csv", parse_dates=["date"])
ev = df[df["date"] >= "2026-09-08"].copy()          # event window
pre = df[df["date"] < "2026-09-08"].copy()           # baseline week

def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (c - h, c + h)

def table(g, by):
    rows = []
    for k, x in g.groupby(by):
        n = len(x); kneg = x["is_neg"].sum(); kpos = x["is_pos"].sum(); krisk = x["is_risk"].sum()
        lo, hi = wilson(kneg, n)
        rows.append({by: k, "n": n, "neg_share": kneg / n, "neg_ci_lo": lo, "neg_ci_hi": hi,
                     "pos_share": kpos / n, "risk_topic_share": krisk / n, "mean_vader": x["vader"].mean()})
    return pd.DataFrame(rows).sort_values("n", ascending=False)

by_outlet = table(ev, "outlet_type").round(3)
acute = ev[ev["date"] <= "2026-09-16"]
by_outlet_acute = table(acute, "outlet_type").round(3)
by_outlet_acute.to_csv("data/bias_by_outlet_acute_sep8_16.csv", index=False)
by_topic = table(ev, "topic").round(3)
by_outlet.to_csv("data/bias_by_outlet.csv", index=False)
by_topic.to_csv("data/bias_by_topic.csv", index=False)

lines = []
# Chi-square: negativity independent of outlet type?
ct = pd.crosstab(ev["outlet_type"], ev["label"])
chi2, p, dof, _ = stats.chi2_contingency(ct)
lines.append(f"Chi-square negativity x outlet_type: chi2={chi2:.2f}, dof={dof}, p={p:.4f}")
# Two-proportion z-tests: US major media vs each other group
def ztest(a, b):
    k1, n1 = a["is_neg"].sum(), len(a); k2, n2 = b["is_neg"].sum(), len(b)
    p1, p2 = k1 / n1, k2 / n2; pp = (k1 + k2) / (n1 + n2)
    se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se
    return p1, p2, z, 2 * (1 - stats.norm.cdf(abs(z)))
us = ev[ev.outlet_type == "us_major_media"]
for grp in ["non_us_media", "financial_press", "tech_press", "social_media", "blog_other"]:
    o = ev[ev.outlet_type == grp]
    if len(o) >= 5 and len(us) >= 5:
        p1, p2, z, pv = ztest(us, o)
        lines.append(f"US major media neg share {p1:.2f} vs {grp} {p2:.2f}: z={z:.2f}, p={pv:.3f}")
# Risk-vs-progress ratio (analogue of 'rising cases' vs 'falling cases' story ratio = 5.5 in SSC 2020)
n_risk = ev["is_risk"].sum()
n_prog_pos = ((ev["topic"] == "ai_product_research") & (ev["is_pos"] == 1)).sum()
n_prog = (ev["topic"] == "ai_product_research").sum()
lines.append(f"Risk/safety stories: {n_risk}; product/research stories: {n_prog} (positive-toned: {n_prog_pos}); ratio risk:positive-progress = {n_risk / max(n_prog_pos,1):.2f}")
# Pre vs post event negativity
lines.append(f"Negative share baseline (Sep 1-7): {pre['is_neg'].mean():.3f} (n={len(pre)}) vs event window (Sep 8-30): {ev['is_neg'].mean():.3f} (n={len(ev)})")
lines.append(f"Risk-topic share baseline: {pre['is_risk'].mean():.3f} vs event window: {ev['is_risk'].mean():.3f}")

# Negativity vs. 'the facts': does daily negativity respond to AI-basket returns?  (SSC: negativity unresponsive to case trends)
s = pd.read_csv("data/sentiment_daily_trading.csv", index_col=0, parse_dates=True)
r = pd.read_csv("data/returns.csv", index_col=0, parse_dates=True)
d = s.join(r, how="inner").loc["2026-09-08":]
d["cum_basket"] = d["AI_BASKET"].cumsum()
X = sm.add_constant(pd.DataFrame({"ret_same_day": d["AI_BASKET"], "ret_lag1": d["AI_BASKET"].shift(1),
                                  "cum_ret_to_date": d["cum_basket"].shift(1)}).dropna())
y = d.loc[X.index, "neg_share"]
m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
facts = pd.DataFrame({"coef": m.params, "t_HAC": m.tvalues, "p": m.pvalues}).round(4)
facts.to_csv("data/bias_negativity_vs_facts.csv")
lines.append("OLS neg_share_t on basket returns (HAC): " + "; ".join(f"{k}: b={v:.3f} (p={m.pvalues[k]:.3f})" for k, v in m.params.items()))
# Split: selloff phase (Sep 8-16) vs rally phase (Sep 17-25) vs late (Sep 28-30)
for name, lo, hi in [("selloff Sep 8-16", "2026-09-08", "2026-09-16"), ("rally Sep 17-25", "2026-09-17", "2026-09-25"), ("late Sep 26-30", "2026-09-26", "2026-09-30")]:
    x = ev[(ev.date >= lo) & (ev.date <= hi)]
    lines.append(f"{name}: n={len(x)}, neg_share={x['is_neg'].mean():.3f}, risk_share={x['is_risk'].mean():.3f}, mean_vader={x['vader'].mean():.3f}")
open("data/bias_tests.txt", "w").write("\n".join(lines))
print(by_outlet.to_string(index=False)); print("\nAcute phase Sep 8-16:\n", by_outlet_acute.to_string(index=False)); print(); print(by_topic.to_string(index=False)); print(); print("\n".join(lines))
