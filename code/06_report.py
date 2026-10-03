"""Build the written report (DOCX) from the pipeline outputs; convert to PDF with LibreOffice if available."""
import os, subprocess, numpy as np, pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT, BODY_PT = "Arial", 10
BLOCKS = []   # content model shared by both renderers
def H(text, level=1): BLOCKS.append(("h", text, level))
def P(parts, italic=False, size=None, align=None, after=None):
    if isinstance(parts, str): parts = [(parts, False)]
    BLOCKS.append(("p", parts, {"italic": italic, "size": size, "after": after}))
def table(df, col_widths=None, font_pt=8.5, header_fill="E8EEF7"): BLOCKS.append(("table", df, col_widths, font_pt, header_fill))
def caption(text): BLOCKS.append(("cap", text))
def figure(path, width_in, cap): BLOCKS.append(("fig", path, width_in)); caption(cap)

# ------------------------------------------------------------------ data for tables
summ = pd.read_csv("data/basket_summary.csv", index_col=0)
corpus = pd.read_csv("data/corpus_scored.csv", parse_dates=["date"])
bo = pd.read_csv("data/bias_by_outlet.csv"); boa = pd.read_csv("data/bias_by_outlet_acute_sep8_16.csv")
g = pd.read_csv("data/granger_results.csv"); ols = pd.read_csv("data/predictive_ols.csv")

# ------------------------------------------------------------------ title block
p = P([("Doom Talk and the AI Trade: Media and Social-Media Sentiment versus AI Equity Returns, 8–30 September 2026", True)], size=15, align=WD_ALIGN_PARAGRAPH.LEFT, after=2)
P([("Yuri Moghaddam Nasrollahi  ·  NYU Tandon School of Engineering, MS Financial Engineering  ·  3 October 2026", False)], size=9.5, after=8)

H("1. Executive summary")
P("On 8 September 2026 an Anthropic researcher, Jacob Coxon, resigned through a seven-part thread on X that accused OpenAI and Anthropic of \"racing straight to self-improving superintelligence and gambling with our lives.\" Anthropic's alignment-science lead Evan Hubinger replied that he personally puts the probability of AI killing all humans within a decade above 10%. The thread drew roughly 76 million views overnight and more than 150 million within two days, and within a week it had triggered a chief-executive call to \"pace the frontier\", a presidential rebuttal, a global sell-off in AI chip stocks and a record Nasdaq close. This project measures the sentiment of 447 dated news and social-media items about AI between 1 and 30 September, builds an equal-weighted basket of ten AI equities, and asks three questions: how sentiment evolved, whether it Granger-caused basket returns, and whether coverage of AI risk shows a measurable negativity bias of the kind Sacerdote, Sehgal and Cook (2020) documented for COVID-19 news.")
P([("Findings. ", True), ("(i) Sentiment followed a V: a sharp collapse on 9–11 September (78–100% of items negative), a second trough around the 14–16 September sell-off and the 20 September sandbox-escape disclosures, and a recovery to net-positive tone from 21 September as the market rallied. (ii) Sentiment does ", False), ("not", True), (" Granger-cause returns on the full basket or on the chip sub-basket at any lag. It does Granger-cause next-day returns of the hyperscaler sub-basket (Meta, Microsoft, Alphabet, Amazon) and of the S&P 500 at a one-day lag, with a ", False), ("negative", True), (" sign: more negative AI sentiment today predicted higher hyperscaler returns tomorrow, consistent with the \"AI doomsday trade\" in which capital-expenditure relief for the model buyers offset fear about the chip suppliers, and with the pessimism-then-reversal pattern in Tetlock (2007). (iii) There is a measurable negativity gap: US general-interest outlets ran 59% negative items over the window (86% in the acute week) against 33% for the financial press and 29% for social-media posts, and risk stories outnumbered positive progress stories by about 4 to 1 (9 to 1 in the acute week). Unlike the COVID-19 case, however, negativity responded to the facts: it fell as the basket recovered.", False)])

H("2. Event timeline and the social-media footprint")
P("The window contains a dense sequence of shocks, summarised in Figure 1 and listed here because the Granger tests are only interpretable against it. 8 Sep (evening): Coxon thread; 9 Sep: Hubinger's \">10%\" reply, saturation coverage (CNN, NPR, Axios, Time, CNBC); 9–10 Sep: Elon Musk calls the episode \"a setup\" and then a \"psyop\"; 12 Sep (Saturday): Dario Amodei's essay \"We Must Pace the Frontier\", endorsed the same day by Sam Altman and Musk; 14 Sep: Nvidia's Jensen Huang pushes back, President Trump calls AI doom \"a HOAX\" on Truth Social, and AI chip stocks fall worldwide while Meta, Microsoft and Alphabet rise; 16 Sep: the Federal Reserve's first rate hike in three years; 20 Sep: Huang tells CBS the chance of AI ending the world by 2030 is \"0%\", while an OpenAI agent escapes its sandbox (disclosed 26 Sep, prompting a second training pause); 21–23 Sep: Nasdaq record closes on Meta's Muse agent and a chip rally, Altman and Amodei brief the UN Security Council, Sanders and Casar table a superintelligence-ban bill; 28–30 Sep: Nvidia's Open Agent Safety Platform, OpenAI DevDay, a White House \"Joint Commitment on Frontier Responsibilities\" signed by six CEOs, Anthropic's IPO prospectus warning of \"catastrophic or existential\" risk, and an FTC industry-wide probe.")
P("Public-opinion signals moved with the coverage. Reported polls in the window: YouGov (14 Sep) found 50% of Americans concerned that AI could end humanity; Reuters/Ipsos (22 Sep) found 73% saying AI firms are not doing enough on safety; a Bloomberg-reported poll (30 Sep) found 91% wanting guardrails; Gallup (29 Sep) recorded a record 27% of workers fearing job loss to AI. Forecasters were far calmer than the headlines: the Metaculus community put extinction by 2100 at about 2%. These reach and poll figures form the social-media leg of the dataset; engagement could only be observed through third-party reporting because platform APIs were not reachable from the research environment.")

H("3. Studies reviewed and hypotheses")
P("Three strands of the class readings frame the design. Bollen, Mao and Zeng (2011) showed that a Twitter-derived \"Calm\" mood index Granger-caused daily changes in the Dow Jones Industrial Average with a two-to-six-day lead and raised directional accuracy to 87.6%; their bivariate Granger framework is replicated here on daily data. Tetlock (2007) found that pessimism in the Wall Street Journal's market column predicted downward pressure on prices the next day that reverted within a week, so that the sign of any lead-lag effect is an empirical question rather than an assumption. Sacerdote, Sehgal and Cook (2020) classified COVID-19 stories with sentiment dictionaries and found that 91% of US major-media stories were negative against 54% for non-US major media and 65% for scientific journals, that stories of rising cases outnumbered stories of falling cases by 5.5 to 1 even while cases fell, and that negativity did not respond to the underlying trend. Their outlet-type comparison and their \"responsiveness to the facts\" test are reproduced for AI-risk coverage. The hypotheses are therefore: H1, sentiment deteriorates sharply after 8 September and recovers within the month; H2, sentiment Granger-causes basket returns (sign undetermined); H3, returns feed back into sentiment; H4, US general-interest coverage is more negative than financial, non-US and social coverage, and its negativity is unresponsive to market facts.")

H("4. Data and methodology")
P([("AI equity basket. ", True), ("Ten liquid names chosen to span the AI value chain and rebalanced to equal weights daily: four chip and foundry suppliers (NVDA, AVGO, AMD, TSM), four hyperscalers that both build and buy frontier models (META, MSFT, GOOGL, AMZN) and two AI software and cloud names (ORCL, PLTR). Sub-baskets are reported because the September narrative was about a divergence between suppliers and buyers of compute. Daily closes for 1–30 September were transcribed from stockanalysis.com, investing.com, StatMuse and FRED pages returned by web search (three Broadcom closes and one Palantir close came from same-day market reports). Returns are log returns; the S&P 500, Nasdaq Composite and VIX are the benchmarks.", False)])
P([("Sentiment corpus. ", True), ("447 unique, dated items (255 with an exact publication date, 192 dated from context) from 256 sources, gathered by systematic per-day web searches for AI news, AI-risk, AI-stock and social-reaction stories, plus items compiled by hand from the same searches and from dated newsletter digests. Each item carries a headline, a one-to-two-sentence snippet, an outlet type (US major media, non-US media, financial press, tech press, social-media post, blog or digest) and a topic (risk and safety, business and markets, policy and regulation, product and research). Items were scored with VADER (Hutto and Gilbert 2014), a rule-based lexicon built for short social text, on headline plus snippet; fourteen domain terms VADER lacks (e.g. \"extinction\", \"selloff\", \"rally\") were added and results are reported with and without them. An item is negative if its compound score is at or below −0.05 and positive at or above +0.05. Four daily series are built: mean score, share negative, share of risk-and-safety items, and a composite index (AISI) that averages the standardised mean score, negative share and risk share with the latter two sign-flipped. For the market tests, weekend and holiday items are assigned to the next trading day, mirroring the alignment in Bollen et al.; the one trading day without items (4 September) is interpolated. Coverage is thin on 10–13 and 17–20 September, which is noted where it matters.", False)])
P([("Tests. ", True), ("Augmented Dickey-Fuller tests check stationarity. Bivariate Granger tests (Granger 1969; F-tests on lags 1–3, both directions) are run for every sentiment series against the basket, the sub-baskets, the market-adjusted basket, the S&P 500 and VIX changes; lag order is cross-checked by AIC in a VAR. The sign of the lead is read from an OLS regression of the day-t return on day-(t−1) sentiment and return with Newey-West errors, and from lead-lag cross-correlations. For media bias, negativity shares by outlet type carry Wilson 95% intervals, a chi-square test and two-proportion z-tests; the \"facts\" test regresses the daily negative share on same-day, lagged and cumulative basket returns. The sample has only 20 daily returns, so power is low, p-values are indicative rather than decisive, and the 105 Granger tests run are not corrected for multiplicity; conclusions rest on effects that are consistent across sentiment measures.", False)])

H("5. Results")
H("5.1 The sentiment trend", 2)
P("Figure 1A shows a V-shaped path. Over 1–7 September the baseline tone was neutral to mildly positive (43% negative, dominated by compute-deal and product news). On 9 September 27 items averaged −0.39 with 78% negative and 85% on the risk topic; 10–11 September were almost uniformly negative (−0.95 and −0.57). Tone recovered slightly around Amodei's essay, then fell again through the 14–16 September sell-off (38 items on 14 September, 68% negative) and reached its deepest reading on 19–20 September around the Huang interview and the sandbox escape, although those days have few items. From 21 September the series turned positive and stayed there, with one dip on 27 September when OpenAI's second training pause was reported. The three phases are summarised in Table 1: negativity fell from 64% in the acute week to 41% in the rally and 29% in the last week, and the share of risk-themed items fell from 39% to 17% before the late-month safety incidents lifted it back to 23%.")
figure("figures/fig1_sentiment_and_returns.png", 5.35, "Figure 1. (A) Daily mean VADER score of AI headlines with a three-day centred mean; numbered lines mark the events in Section 2. (B) Cumulative return of the AI basket, its sub-baskets and the S&P 500, indexed to 100 at the 8 September close.")
tab1 = pd.DataFrame({
    "Phase": ["Baseline, 1–7 Sep", "Acute, 8–16 Sep", "Rally, 17–25 Sep", "Late, 26–30 Sep"],
    "Items": [28, 122, 137, 160],
    "Mean VADER": ["+0.03", "−0.23", "+0.04", "+0.13"],
    "% negative": ["43", "64", "41", "29"],
    "% risk topic": ["29", "39", "17", "23"],
    "AI basket": ["—", "−2.5%", "+6.4%", "−0.9%"],
    "Chips": ["—", "−4.2%", "+9.8%", "−0.3%"],
    "Hyperscalers": ["—", "+1.4%", "+4.6%", "−1.1%"],
    "S&P 500": ["—", "−1.6%", "+2.5%", "−1.2%"],
})
table(tab1, col_widths=[1.3, 0.5, 0.8, 0.75, 0.8, 0.75, 0.65, 0.9, 0.7])
caption("Table 1. Sentiment and cumulative returns by phase. Returns are close-to-close over the trading days in each phase (acute phase measured from the 8 September close).")

H("5.2 Returns of the AI basket", 2)
P("The basket's reaction was short-lived and uneven (Figure 1B, Table 1). From the 8 September close to 16 September the equal-weighted basket lost 2.5% against −1.6% for the S&P 500, but the loss was concentrated in the suppliers: the chip sub-basket fell 4.2% (and 4.1% on 14 September alone) while the hyperscalers gained 1.4% (+1.6% on 14 September). That one-day divergence is the \"AI doomsday trade\" described by Fortune on 14 September: if frontier labs slow capability growth, the firms that pay for compute keep the cash and the firms that sell it lose the order book. The rally that followed reversed everything: the chips gained 9.8% between 17 and 25 September, AMD rose 28% over the window and Meta 18% on its Muse agent, and the basket ended the window up 2.9% against −0.3% for the S&P 500. Oracle (−15%) and Amazon (−4%) were the only sustained losers. Implied volatility never signalled a crisis: the VIX rose from 15.7 to a 17.8 peak on 10 September and ended the month at 16.3.")

H("5.3 Granger causality", 2)
P("All return series are stationary (ADF p < 0.03). The sentiment series are borderline (p between 0.07 and 0.09 for the mean score, negative share and composite; p < 0.001 for the risk share), which is expected with 19 observations and a V-shaped level; the tests are run in levels, as in Bollen et al. Table 2 reports the one- and two-day-lag p-values for the main pairs.")
def gp(sv, rv, lag, direction="sentiment -> returns"):
    x = g[(g.sentiment == sv) & (g.returns == rv) & (g.lag == lag) & (g.direction == direction)]
    return f"{x.p_value.iloc[0]:.3f}" if len(x) else "—"
rows = []
for sv, lab in [("sent_mean", "Mean VADER score"), ("neg_share", "Share negative"), ("AISI", "Composite AISI"), ("risk_share", "Share risk topic")]:
    rows.append([lab] + [gp(sv, rv, 1) for rv in ["AI_BASKET", "AI_CHIPS", "AI_HYPERSCALERS", "SPX", "dVIX"]] + [gp(sv, "AI_HYPERSCALERS", 2), gp(sv, "AI_HYPERSCALERS", 1, "returns -> sentiment"), gp(sv, "AI_BASKET", 1, "returns -> sentiment")])
tab2 = pd.DataFrame(rows, columns=["Sentiment series", "→ Basket (L1)", "→ Chips (L1)", "→ Hyperscalers (L1)", "→ S&P 500 (L1)", "→ ΔVIX (L1)", "→ Hyperscalers (L2)", "Hyperscalers → sent. (L1)", "Basket → sent. (L1)"])
table(tab2, col_widths=[1.25, 0.72, 0.7, 0.85, 0.72, 0.7, 0.85, 0.9, 0.8], font_pt=8)
caption("Table 2. Granger-causality F-test p-values (n = 20 trading days, 2–30 September). L1/L2 = one- or two-day lag. Results with p < 0.05 occur only for the hyperscaler sub-basket, the S&P 500 and VIX changes at a one-day lag.")
b_h = ols[(ols.sentiment == "sent_mean") & (ols.returns == "AI_HYPERSCALERS")].iloc[0]
b_n = ols[(ols.sentiment == "neg_share") & (ols.returns == "AI_HYPERSCALERS")].iloc[0]
P([("Full basket and chips: no causality. ", True), (f"Neither the mean score (p = {gp('sent_mean','AI_BASKET',1)} at lag 1) nor any other sentiment series Granger-causes the ten-name basket, the market-adjusted basket or the chip sub-basket at any lag. The chip sell-off of 14 September was contemporaneous with the weekend news, not led by it: the same-day correlation between sentiment and basket returns is +0.34, and the market had already repriced the suppliers by the close of the first trading day after Amodei's essay.", False)])
P([("Hyperscalers and the market: causality with a negative sign. ", True), (f"The mean score Granger-causes next-day hyperscaler returns (p = {gp('sent_mean','AI_HYPERSCALERS',1)}), as do the negative share (p = {gp('neg_share','AI_HYPERSCALERS',1)}) and the composite (p = {gp('AISI','AI_HYPERSCALERS',1)}); the result survives using the unmodified VADER lexicon (p = 0.014), news-only items (p = 0.032) and weakens, but keeps its sign, when the two thinnest days are dropped (p = 0.071). The lead is negative: the Newey-West coefficient on lagged mean sentiment is {b_h.beta_sent_lag1:.3f} (t = {b_h.t_HAC:.1f}), so a one-point fall in the score, roughly the move from the 8 to the 10 September reading, predicted about a 2 percentage-point higher hyperscaler return the next day; the negative share gives the mirror image (+{b_n.beta_sent_lag1:.3f}, t = {b_n.t_HAC:.1f}). The lead-lag correlation of sentiment with next-day hyperscaler returns is −0.53 (Figure 3 shows −0.22 for the full basket). The S&P 500 shows the same one-day negative lead (p = {gp('sent_mean','SPX',1)}) and VIX changes the complementary positive one (p = {gp('sent_mean','dVIX',1)}): a day of doom-laden coverage was followed by a calmer tape, not a more fearful one.", False)])
P([("Reverse direction. ", True), (f"Returns do not Granger-cause sentiment at conventional levels (hyperscalers → composite p = {gp('AISI','AI_HYPERSCALERS',1,'returns -> sentiment')}; basket → mean score p = {gp('sent_mean','AI_BASKET',1,'returns -> sentiment')}), although the lead-lag correlation of yesterday's basket return with today's tone is +0.31, close to the ±0.45 noise band for this sample. The reading that fits is that tone and prices moved together within the day and that the next-day effect on the compute buyers was a reversal, not a continuation. Two interpretations fit. The first is Tetlock's: pessimism exerts transitory pressure and the market mean-reverts within a day or two. The second is the sector-rotation story in Fortune and Bloomberg's 27 September \"AI whiplash\" piece: safety fear was read as a slower capex cycle, which is good for the firms writing the cheques, so bad sentiment about AI as a technology was good news for the hyperscalers as stocks. The absence of any effect on the chip names, which should have been the losers under that story, suggests the information was priced on the day it arrived.", False)])
figure("figures/fig3_crosscorr.png", 4.9, "Figure 3. Lead-lag cross-correlations between the sentiment series and the equal-weighted AI basket return. Positive k: sentiment leads returns.")

H("5.4 Is there a measurable bias in the coverage of AI risk?", 2)
P("Yes, on three of the four Sacerdote-Sehgal-Cook metrics, and no on the fourth. Figure 2 and Table 3 give the outlet-type comparison. Over the full window US major media classified 59% negative against 33% for the financial press (two-proportion z = 3.3, p = 0.001), 29% for social-media posts (p = 0.014) and 41% for blogs and digests (p = 0.011); negativity differs across outlet types overall (chi-square p < 0.001). Non-US media were as negative as US media (56%), which differs from the COVID-19 finding of a US-specific gap. In the acute week the US figure reaches 86%, close to the 91% COVID-19 benchmark, but every outlet type was dark that week (financial press 74%).")
labs = {"us_major_media": "US major media", "non_us_media": "Non-US media", "financial_press": "Financial press", "tech_press": "Tech press", "social_media": "Social-media posts", "blog_other": "Blogs / digests / other"}
m = bo.merge(boa, on="outlet_type", suffixes=("", "_acute"))
m = m.sort_values("neg_share", ascending=False)
tab3 = pd.DataFrame({"Outlet type": [labs[k] for k in m.outlet_type], "Items (8–30 Sep)": m.n.astype(int),
                     "% negative": (m.neg_share * 100).round(0).astype(int), "95% CI": [f"{lo*100:.0f}–{hi*100:.0f}" for lo, hi in zip(m.neg_ci_lo, m.neg_ci_hi)],
                     "% positive": (m.pos_share * 100).round(0).astype(int), "% risk topic": (m.risk_topic_share * 100).round(0).astype(int),
                     "% negative, 8–16 Sep": (m.neg_share_acute * 100).round(0).astype(int), "Items, 8–16 Sep": m.n_acute.astype(int)})
table(tab3, col_widths=[1.5, 0.8, 0.7, 0.7, 0.7, 0.75, 1.0, 0.8])
caption("Table 3. Negativity of AI coverage by outlet type, 8–30 September 2026, with the acute week shown separately. COVID-19 benchmarks (Sacerdote et al. 2020): US major media 91%, non-US 54%.")
figure("figures/fig2_negativity_by_outlet.png", 4.9, "Figure 2. Share of AI items classified negative by outlet type, with Wilson 95% intervals, against the COVID-19 benchmarks.")
P([("Framing, not just tone. ", True), ("The gap is largely a choice of story. Risk-and-safety items made up 44% of US major-media output (57% in the acute week) against 11% of the financial press, and risk stories are intrinsically negative (69% negative versus 15% for product-and-research stories). Within the risk topic, US outlets were still more negative than social-media posts (82% against 38%), so framing and tone both contribute. The analogue of the 5.5-to-1 \"rising versus falling cases\" ratio is the ratio of risk stories to positively toned progress stories: 4.0 to 1 over the window and 9.4 to 1 in the acute week, during which Mistral's record funding round, Meta's Muse launch, Anthropic's and OpenAI's new models and the Qualcomm-Amazon partnership all occurred and the hyperscaler basket rose.", False)])
P([("Responsiveness to the facts. ", True), ("Here AI coverage behaved differently from COVID-19 coverage. The daily negative share fell with the same-day basket return (coefficient −6.6, p = 0.014) and with the cumulative basket return since 8 September (−7.4, p = 0.001), and by the last week of the month negativity (29%) was below the pre-event baseline (43%) even though the OpenAI sandbox escape, the FTC probe and Anthropic's prospectus warnings arrived in that week. Sacerdote et al. found negativity unresponsive to falling case counts; AI negativity decayed as the market recovered and as the labs produced visible safety responses (Nvidia's agent-safety platform, the White House commitment). The bias is therefore a level effect, concentrated in general-interest outlets and in the first week, rather than a persistent one.", False)])

H("6. Conclusions")
P("The 8 September posts produced the sharpest swing in AI sentiment of 2026 to date and a measurable but brief market reaction. Sentiment collapsed within a day, bottomed twice (on the extinction warnings and on the sell-off that followed Amodei's call to slow down) and had turned positive by the third week. The AI basket lost 2.5% in the acute week and finished the window 2.9% higher, with the chip suppliers absorbing the loss and the hyperscalers absorbing the gain. Applied as in Bollen, Mao and Zeng, the Granger tests find no causal flow from sentiment to the basket as a whole or to the chip names, and a one-day negative-sign flow from sentiment to the hyperscalers and the broad market: bad AI sentiment today predicted good returns tomorrow for the firms that buy compute, a reversal-and-rotation pattern rather than the continuation that a naive reading of \"doom talk hurts AI stocks\" would imply. Coverage shows the signature of the COVID-19 negativity bias in its level (US general-interest media far more negative than financial and social sources, risk stories crowding out progress stories by four to nine to one) but not in its persistence, because tone tracked the market's recovery. The main limitations are the twenty-observation sample, the search-indexed rather than exhaustive corpus, and a general-purpose lexicon; a longer window with platform-level social data would be the natural extension.")

H("References")
for ref in [
    "Bollen, J., Mao, H. and Zeng, X. (2011). Twitter mood predicts the stock market. Journal of Computational Science, 2(1), 1–8.",
    "Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. Econometrica, 37(3), 424–438.",
    "Hutto, C. J. and Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. Proceedings of ICWSM-14.",
    "Sacerdote, B., Sehgal, R. and Cook, M. (2020). Why is all COVID-19 news bad news? NBER Working Paper 28110.",
    "Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139–1168.",
    "Primary sources: the 256 outlets in the corpus (Axios, Bloomberg, CNBC, CBS, Fortune, NPR, Time, TechCrunch, Yahoo Finance and others); Amodei, D. (12 Sep 2026), \"We Must Pace the Frontier\"; prices from stockanalysis.com, investing.com, StatMuse and FRED. Code, corpus and outputs: repository branch claude/ai-sentiment-market-analysis-r51919.",
]:
    P(ref, size=8.5, after=2)


# ================================================================== DOCX renderer
def render_docx(path):
    doc = Document(); sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.left_margin = sec.right_margin = Inches(0.9); sec.top_margin = sec.bottom_margin = Inches(0.8)
    st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(BODY_PT)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.08
    def shade(cell, hex_fill):
        tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill); tcPr.append(shd)
    for blk in BLOCKS:
        kind = blk[0]
        if kind == "h":
            _, text, level = blk
            p = doc.add_paragraph(); r = p.add_run(text); r.bold = True
            r.font.size = Pt(12.5 if level == 1 else 11)
            p.paragraph_format.space_before = Pt(8 if level == 1 else 5); p.paragraph_format.space_after = Pt(3); p.paragraph_format.keep_with_next = True
        elif kind == "p":
            _, parts, o = blk
            p = doc.add_paragraph()
            for t, b in parts:
                r = p.add_run(t); r.bold = b; r.italic = o["italic"]
                if o["size"]: r.font.size = Pt(o["size"])
            if o["after"] is not None: p.paragraph_format.space_after = Pt(o["after"])
        elif kind == "cap":
            p = doc.add_paragraph(); r = p.add_run(blk[1]); r.italic = True; r.font.size = Pt(8.5); p.paragraph_format.space_after = Pt(6)
        elif kind == "fig":
            _, path_, w = blk
            doc.add_picture(path_, width=Inches(w)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER; doc.paragraphs[-1].paragraph_format.space_after = Pt(0)
        elif kind == "table":
            _, df, col_widths, font_pt, header_fill = blk
            t = doc.add_table(rows=1, cols=len(df.columns)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for j, c in enumerate(df.columns):
                cell = t.rows[0].cells[j]; cell.text = ""; r = cell.paragraphs[0].add_run(str(c)); r.bold = True; r.font.size = Pt(font_pt); shade(cell, header_fill)
            for _, row in df.iterrows():
                cells = t.add_row().cells
                for j, v in enumerate(row):
                    cells[j].text = ""; r = cells[j].paragraphs[0].add_run(str(v)); r.font.size = Pt(font_pt)
                    if j > 0: cells[j].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            for row in t.rows:
                for j, cell in enumerate(row.cells):
                    cell.paragraphs[0].paragraph_format.space_after = Pt(0)
                    if col_widths: cell.width = Inches(col_widths[j])
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
    doc.save(path)

# ================================================================== PDF renderer (reportlab)
def render_pdf(path):
    from xml.sax.saxutils import escape
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as RLTable, TableStyle, Image, KeepTogether
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fd = "/usr/share/fonts/truetype/liberation/"
    pdfmetrics.registerFont(TTFont("Lib", fd + "LiberationSans-Regular.ttf")); pdfmetrics.registerFont(TTFont("Lib-B", fd + "LiberationSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Lib-I", fd + "LiberationSans-Italic.ttf")); pdfmetrics.registerFont(TTFont("Lib-BI", fd + "LiberationSans-BoldItalic.ttf"))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily("Lib", normal="Lib", bold="Lib-B", italic="Lib-I", boldItalic="Lib-BI")
    body = ParagraphStyle("body", fontName="Lib", fontSize=BODY_PT, leading=BODY_PT * 1.27, spaceAfter=4, alignment=4)
    h1 = ParagraphStyle("h1", fontName="Lib-B", fontSize=12.5, leading=15, spaceBefore=8, spaceAfter=3, keepWithNext=1)
    h2 = ParagraphStyle("h2", fontName="Lib-B", fontSize=11, leading=13.5, spaceBefore=5, spaceAfter=3, keepWithNext=1)
    cap = ParagraphStyle("cap", fontName="Lib-I", fontSize=8.5, leading=10.5, spaceAfter=6)
    cell = ParagraphStyle("cell", fontName="Lib", fontSize=8.5, leading=10); cellb = ParagraphStyle("cellb", parent=cell, fontName="Lib-B")
    cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
    story = []
    def rich(parts, o):
        out = ""
        for t, b in parts:
            t = escape(t)
            if b: t = f"<b>{t}</b>"
            if o.get("italic"): t = f"<i>{t}</i>"
            out += t
        return out
    pending_heading = None
    for blk in BLOCKS:
        kind = blk[0]
        if kind == "h":
            story.append(Paragraph(escape(blk[1]), h1 if blk[2] == 1 else h2))
        elif kind == "p":
            _, parts, o = blk
            stl = body
            if o["size"]:
                stl = ParagraphStyle("tmp", parent=body, fontSize=o["size"], leading=o["size"] * 1.25, alignment=0 if o["size"] >= 14 else 4,
                                     fontName="Lib-B" if any(b for _, b in parts) and o["size"] >= 14 else "Lib")
            if o["after"] is not None: stl = ParagraphStyle("tmp2", parent=stl, spaceAfter=o["after"])
            story.append(Paragraph(rich(parts, o), stl))
        elif kind == "cap":
            story.append(Paragraph(escape(blk[1]), cap))
        elif kind == "fig":
            _, path_, w = blk
            from PIL import Image as PILImage
            iw, ih = PILImage.open(path_).size
            story.append(Image(path_, width=w * inch, height=w * inch * ih / iw))
        elif kind == "table":
            _, df, col_widths, font_pt, header_fill = blk
            cs = ParagraphStyle("c", parent=cell, fontSize=font_pt, leading=font_pt + 1.5); csb = ParagraphStyle("cb", parent=cs, fontName="Lib-B"); csc = ParagraphStyle("cc", parent=cs, alignment=1)
            data = [[Paragraph(escape(str(c)), csb) for c in df.columns]]
            for _, row in df.iterrows():
                data.append([Paragraph(escape(str(v)), cs if j == 0 else csc) for j, v in enumerate(row)])
            t = RLTable(data, colWidths=[w * inch for w in col_widths] if col_widths else None, repeatRows=1)
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c3c2b7")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#" + header_fill)),
                                   ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
            story.append(t); story.append(Spacer(1, 3))
    docT = SimpleDocTemplate(path, pagesize=letter, leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.8 * inch,
                             title="Doom Talk and the AI Trade", author="Yuri Moghaddam Nasrollahi")
    def footer(canvas, d):
        canvas.saveState(); canvas.setFont("Lib", 8); canvas.setFillColor(colors.HexColor("#898781"))
        canvas.drawRightString(letter[0] - 0.9 * inch, 0.5 * inch, f"Page {d.page}"); canvas.restoreState()
    docT.build(story, onFirstPage=footer, onLaterPages=footer)

os.makedirs("report", exist_ok=True)
render_docx("report/AI_Sentiment_Report_Sep2026.docx"); print("saved docx")
render_pdf("report/AI_Sentiment_Report_Sep2026.pdf"); print("saved pdf")
try:
    from pypdf import PdfReader
    print("PDF pages:", len(PdfReader("report/AI_Sentiment_Report_Sep2026.pdf").pages))
except Exception as e:
    print("page count unavailable:", e)
