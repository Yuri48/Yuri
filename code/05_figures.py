"""Figures for the report (static PNGs; palette and mark specs follow the dataviz reference instance)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
                     "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
                     "axes.titleweight": "semibold", "axes.titlesize": 10, "axes.titlecolor": INK,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})

def style(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.tick_params(length=0)

px = pd.read_csv("data/prices.csv", index_col=0, parse_dates=True)
r = pd.read_csv("data/returns.csv", index_col=0, parse_dates=True)
cal = pd.read_csv("data/sentiment_daily_calendar.csv", index_col=0, parse_dates=True)
td = pd.read_csv("data/sentiment_daily_trading.csv", index_col=0, parse_dates=True)

EVENTS = [("2026-09-08", "Coxon resigns /\nHubinger >10%"), ("2026-09-12", "Amodei:\n'Pace the Frontier'"),
          ("2026-09-14", "Chip selloff;\nTrump 'hoax'"), ("2026-09-16", "Fed hike"),
          ("2026-09-21", "Nasdaq record;\nMuse rally"), ("2026-09-28", "Nvidia agent-\nsafety platform")]

# ---------- Figure 1: sentiment (top) and indexed cumulative returns (bottom), one x-axis, no dual axis ----------
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.6), sharex=True, gridspec_kw={"height_ratios": [1, 1.15], "hspace": 0.12})
s = cal["sent_mean"].copy()
s3 = s.rolling(3, min_periods=1, center=True).mean()
a1.plot(s.index, s.values, color=BLUE, lw=1.2, alpha=0.45, label="Daily mean VADER")
a1.plot(s3.index, s3.values, color=BLUE, lw=2, label="3-day centred mean")
a1.scatter(s.index, s.values, s=14, color=BLUE, edgecolor=SURF, linewidth=1, zorder=3)
a1.axhline(0, color=AXIS, lw=0.8); a1.set_ylim(-1.0, 0.75)
a1.set_ylabel("Headline sentiment\n(VADER compound, -1 to +1)")
a1.set_title("A. AI news & social-media sentiment, 1-30 September 2026 (calendar days)")
a1.legend(loc="lower right", frameon=False, fontsize=7.5, ncol=2)
style(a1)
for i, (d, lab) in enumerate(EVENTS, 1):
    a1.axvline(pd.Timestamp(d), color=AXIS, lw=0.8)
    a1.text(pd.Timestamp(d), 0.70, str(i), fontsize=7.5, color=SURF, ha="center", va="center", fontweight="bold",
            bbox=dict(boxstyle="circle,pad=0.25", fc=INK2, ec="none"))

base = pd.Timestamp("2026-09-08")
idx = {}
for name, col, c in [("AI basket (10, eq-wt)", "AI_BASKET", BLUE), ("AI chips (NVDA, AVGO, AMD, TSM)", "AI_CHIPS", ORANGE),
                     ("Hyperscalers (META, MSFT, GOOGL, AMZN)", "AI_HYPERSCALERS", AQUA), ("S&P 500", "SPX", RED)]:
    cum = np.exp(r[col].loc[base + pd.Timedelta(days=1):].cumsum()) * 100
    cum = pd.concat([pd.Series([100.0], index=[base]), cum])
    idx[name] = cum
    a2.plot(cum.index, cum.values, color=c, lw=2, label=name)
    a2.scatter([cum.index[-1]], [cum.values[-1]], s=22, color=c, edgecolor=SURF, linewidth=1.2, zorder=3)
    off = {"AI chips (NVDA, AVGO, AMD, TSM)": 0.45, "Hyperscalers (META, MSFT, GOOGL, AMZN)": -0.45}.get(name, 0)
    a2.text(cum.index[-1] + pd.Timedelta(days=0.4), cum.values[-1] + off, f"{cum.values[-1]-100:+.1f}%", fontsize=7.5, color=INK2, va="center")
a2.axhline(100, color=AXIS, lw=0.8)
a2.set_ylabel("Cumulative return\n(8 Sep close = 100)")
a2.set_title("B. AI equity basket vs. S&P 500 after the 8 September posts")
a2.legend(loc="upper left", frameon=False, fontsize=7.5)
style(a2)
for d, _ in EVENTS: a2.axvline(pd.Timestamp(d), color=AXIS, lw=0.8)
a2.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1,4,7,10,13,16,19,22,25,28])); a2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
a2.set_xlim(pd.Timestamp("2026-08-31 12:00"), pd.Timestamp("2026-10-02"))
fig.text(0.125, 0.04, "Events: " + "   ".join(f"({i}) {lab.replace(chr(10), ' ')}" for i, (_, lab) in enumerate(EVENTS, 1)), fontsize=7, color=INK2, ha="left", va="top", wrap=True)
fig.savefig("figures/fig1_sentiment_and_returns.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 2: negativity by outlet type (single series, with Wilson CIs) ----------
bo = pd.read_csv("data/bias_by_outlet.csv")
labels = {"us_major_media": "US major media", "non_us_media": "Non-US media", "financial_press": "Financial press",
          "tech_press": "Tech press", "social_media": "Social media posts", "blog_other": "Blogs / digests / other"}
bo = bo[bo["n"] >= 5].sort_values("neg_share")
fig, ax = plt.subplots(figsize=(6.4, 3.0))
y = np.arange(len(bo))
ax.barh(y, bo["neg_share"] * 100, height=0.5, color=BLUE)
ax.errorbar(bo["neg_share"] * 100, y, xerr=[(bo["neg_share"] - bo["neg_ci_lo"]) * 100, (bo["neg_ci_hi"] - bo["neg_share"]) * 100],
            fmt="none", ecolor=INK2, elinewidth=1, capsize=2)
for yi, (v, n) in enumerate(zip(bo["neg_share"], bo["n"])):
    ax.text(bo["neg_ci_hi"].iloc[yi] * 100 + 1.5, yi, f"{v*100:.0f}%  (n={n})", va="center", fontsize=8, color=INK2)
ax.axvline(91, color=RED, lw=1.2); ax.axvline(54, color=AQUA, lw=1.2)
fig.text(0.125, -0.02, "Vertical lines: COVID-19 benchmark from Sacerdote, Sehgal & Cook (2020) - US major media 91% negative (red), non-US major media 54% (green).", fontsize=7, color=INK2, ha="left", va="top")
ax.set_yticks(y); ax.set_yticklabels([labels.get(k, k) for k in bo["outlet_type"]], color=INK)
ax.set_xlim(0, 115); ax.set_xlabel("Share of AI stories classified negative, 8-30 Sep 2026 (%, 95% Wilson CI)")
ax.set_title("Negativity of AI coverage by outlet type vs. the COVID-19 benchmark")
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
fig.savefig("figures/fig2_negativity_by_outlet.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 3: lead-lag cross-correlation, sentiment(t-k) vs basket return(t) ----------
cc = pd.read_csv("data/crosscorr.csv")
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7), sharey=True)
for ax, sv, title in [(axes[0], "sent_mean", "Mean headline sentiment"), (axes[1], "risk_share", "Share of risk/safety stories")]:
    x = cc[(cc.sentiment == sv) & (cc.returns == "AI_BASKET")]
    k = x["k (sent leads by k days)"].values; v = x["corr"].values
    ax.bar(k, v, width=0.55, color=[BLUE if kk > 0 else (ORANGE if kk < 0 else MUTED) for kk in k])
    n = len(td.dropna(subset=["sent_mean"]))
    ax.axhline(2 / np.sqrt(n), color=AXIS, lw=0.8); ax.axhline(-2 / np.sqrt(n), color=AXIS, lw=0.8); ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(k); ax.set_xlabel("k  (k>0: sentiment leads returns by k days)"); ax.set_title(title); style(ax)
axes[0].set_ylabel("corr( sentiment t-k , basket return t )")
fig.text(0.5, -0.12, f"Blue = sentiment leads returns; orange = returns lead sentiment. Grey lines: ±2/√n (n={n}).", ha="center", fontsize=7.5, color=INK2)
fig.savefig("figures/fig3_crosscorr.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("figures written")
