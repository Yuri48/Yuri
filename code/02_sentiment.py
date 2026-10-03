"""Score the dated AI media corpus and build daily sentiment series.

Input : data/corpus/*.jsonl  (one JSON object per headline; fields documented in README)
Output: data/corpus_scored.csv, data/sentiment_daily_calendar.csv, data/sentiment_daily_trading.csv
"""
import glob, json, numpy as np, pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

rows = []
for f in sorted(glob.glob("data/corpus/*.jsonl")):
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
df = pd.DataFrame(rows)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date", "headline"])
df = df[(df["date"] >= "2026-09-01") & (df["date"] <= "2026-09-30")]
df["url"] = df["url"].fillna("").str.strip()
df = df.drop_duplicates(subset=["url"]).drop_duplicates(subset=["headline"]).reset_index(drop=True)
df["outlet_type"] = df["outlet_type"].fillna("blog_other").str.strip().str.lower()
df["topic"] = df["topic"].fillna("other").str.strip().str.lower()
df["snippet"] = df["snippet"].fillna("")

# --- VADER with a small, documented domain augmentation (only terms VADER lacks) ---
base = SentimentIntensityAnalyzer()
aug = SentimentIntensityAnalyzer()
DOMAIN = {"extinction": -3.0, "doomsday": -3.0, "existential": -2.0, "psyop": -2.0,
          "resigns": -1.5, "resignation": -1.5, "slowdown": -1.2, "ban": -1.5,
          "rally": 2.0, "rallies": 2.0, "record": 1.0, "breakthrough": 2.0, "surge": 1.5,
          "surges": 1.5, "tumble": -2.0, "tumbles": -2.0, "selloff": -2.0, "sell-off": -2.0}
added = {k: v for k, v in DOMAIN.items() if k not in aug.lexicon}
aug.lexicon.update(added)
print("Domain terms added to VADER lexicon:", added)

text = (df["headline"].astype(str) + ". " + df["snippet"].astype(str)).str.strip()
df["vader_base"] = [base.polarity_scores(t)["compound"] for t in text]
df["vader"] = [aug.polarity_scores(t)["compound"] for t in text]
df["vader_headline"] = [aug.polarity_scores(t)["compound"] for t in df["headline"].astype(str)]
df["label"] = np.select([df["vader"] <= -0.05, df["vader"] >= 0.05], ["negative", "positive"], "neutral")
df["is_neg"] = (df["label"] == "negative").astype(int)
df["is_pos"] = (df["label"] == "positive").astype(int)
df["is_risk"] = (df["topic"] == "ai_risk_safety").astype(int)
df["is_social"] = (df["outlet_type"] == "social_media").astype(int)
df.to_csv("data/corpus_scored.csv", index=False)

def agg(g):
    soc = g[g["is_social"] == 1]
    return pd.Series({
        "n_items": len(g),
        "sent_mean": g["vader"].mean(),
        "sent_mean_base": g["vader_base"].mean(),
        "sent_headline": g["vader_headline"].mean(),
        "neg_share": g["is_neg"].mean(),
        "pos_share": g["is_pos"].mean(),
        "risk_share": g["is_risk"].mean(),
        "n_risk": g["is_risk"].sum(),
        "social_sent": soc["vader"].mean() if len(soc) else np.nan,
        "n_social": len(soc),
        "news_sent": g.loc[g["is_social"] == 0, "vader"].mean(),
    })

cal = df.groupby("date").apply(agg).reindex(pd.date_range("2026-09-01", "2026-09-30"))
cal["n_items"] = cal["n_items"].fillna(0)
cal.index.name = "date"
cal.to_csv("data/sentiment_daily_calendar.csv", float_format="%.4f")

# Align to the trading calendar: weekend/holiday items load onto the next trading day
trading = [d for d in pd.bdate_range("2026-09-01", "2026-09-30") if d != pd.Timestamp("2026-09-07")]
def next_td(d):
    for t in trading:
        if t >= d:
            return t
    return pd.NaT
df["tdate"] = df["date"].apply(next_td)
td = df.dropna(subset=["tdate"]).groupby("tdate").apply(agg).reindex(trading)
td.index.name = "date"
# Trading days with no scored items (e.g. 4 Sep, Labor-Day week) are linearly interpolated from neighbours and flagged.
td["n_items"] = td["n_items"].fillna(0)
td["interpolated"] = td["sent_mean"].isna().astype(int)
for c in ["sent_mean", "sent_mean_base", "sent_headline", "neg_share", "pos_share", "risk_share", "news_sent"]:
    td[c] = td[c].interpolate(limit_direction="both")
# Composite AI Sentiment Index: average of z-scored components (higher = more positive)
z = lambda s: (s - s.mean()) / s.std(ddof=0)
td["AISI"] = (z(td["sent_mean"]) - z(td["neg_share"]) - z(td["risk_share"])) / 3
td.to_csv("data/sentiment_daily_trading.csv", float_format="%.4f")

print("Items:", len(df), "| by outlet_type:\n", df["outlet_type"].value_counts().to_string())
print("\nBy topic:\n", df["topic"].value_counts().to_string())
print("\nLabel shares:", df["label"].value_counts(normalize=True).round(3).to_dict())
print("\nTrading-day series:\n", td[["n_items", "sent_mean", "neg_share", "risk_share", "AISI"]].round(3).to_string())
