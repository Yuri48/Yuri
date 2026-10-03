# Doom Talk and the AI Trade: AI Sentiment vs. AI Equity Returns, 8–30 September 2026

Course project (NYU Tandon, MS Financial Engineering). Event window opens 8 September 2026, when Anthropic
researcher Jacob Coxon resigned via a viral X thread and alignment lead Evan Hubinger replied that he puts
">10%" odds on AI killing all humans within a decade.

## Deliverables
| Path | What it is |
|---|---|
| `report/AI_Sentiment_Report_Sep2026.docx` / `.pdf` | The 5–6 page written analysis |
| `figures/` | Figures used in the report |
| `data/` | All inputs and outputs (see below) |
| `code/` | Reproducible pipeline (run in numeric order) |

## Pipeline
```
pip install pandas numpy statsmodels scipy matplotlib python-docx vaderSentiment
python3 code/01_prices.py      # prices_raw.json -> prices.csv, returns.csv, basket_summary.csv
python3 code/02_sentiment.py   # data/corpus/*.jsonl -> corpus_scored.csv, sentiment_daily_{calendar,trading}.csv
python3 code/03_granger.py     # ADF, Granger F-tests (both directions, lags 1-3), HAC OLS, cross-correlations
python3 code/04_bias.py        # Sacerdote-Sehgal-Cook style negativity tables and tests
python3 code/05_figures.py     # figures/*.png
python3 code/06_report.py      # report/*.docx (+ .pdf via LibreOffice)
```

## Data
* **Prices** (`data/prices_raw.json`): daily closes for NVDA, AVGO, AMD, TSM, META, MSFT, GOOGL, AMZN, ORCL, PLTR,
  the S&P 500, Nasdaq Composite and VIX, 1–30 Sep 2026, transcribed on 3 Oct 2026 from stockanalysis.com /
  investing.com / StatMuse / FRED pages as returned by web search. Three AVGO closes (24, 25, 29 Sep) and one
  PLTR close (29 Sep) were taken from same-day market reports; residual gaps on 1 Sep are interpolated and
  listed in `data/price_gaps_interpolated.json`.
* **Media corpus** (`data/corpus/*.jsonl`, 447 deduplicated items, 1–30 Sep 2026): headline, snippet, outlet,
  outlet type, topic and URL of every dated news article, blog post, newsletter or social-media post surfaced by
  systematic web searches (per-day query sets run by five research agents on 3 Oct 2026, plus items compiled by
  hand from the same search results and from dated newsletter digests). Direct API access (GDELT, X, Reddit,
  Yahoo Finance) was not available in the research environment, so this is a search-indexed sample, not an
  exhaustive scrape. Coverage is thin on 10–13 Sep and 17–20 Sep.
* **Sentiment**: VADER compound score on headline + snippet, with a small documented domain augmentation
  (`code/02_sentiment.py`). Daily series: mean score, share negative (≤ −0.05), share of risk/safety-topic
  items, composite index (AISI). Weekend/holiday items are assigned to the next trading day for the Granger tests.

## Branch
`claude/ai-sentiment-market-analysis-r51919`
