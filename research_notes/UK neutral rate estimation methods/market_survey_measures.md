# Market-based and survey-based measures of r* (UK focus)

Research date: 29 September 2026. "Own calculation" means the researcher computed the figure from the Bank of England's free yield-curve files (downloaded 29 Sep 2026). Everything else is cited to its source.

## 1. Long-horizon real forwards (index-linked gilts, TIPS 5y5y, AFNS, shifting endpoints) and UK caveats

### Takeaway
A UK 5y5y real forward can be built in a few lines from the BoE's free daily "GLC Real" curve. It has risen from about -1.5% (2018 average) to about +2.7% (late Sep 2026). That rise is far larger than the MPR's ">90bp" market-based r* increase. Most of the gap is probably term premium, ILG-specific demand (LDI) and the RPI-basis wedge, not r* itself. A raw ILG forward is a credible component only if it is clearly labelled as an upper-bound or "market-implied" signal. The academic best practice (Christensen–Rudebusch AFNS with a liquidity factor) is not published for the UK.

### Cited Findings
**BoE data (free)**
- The BoE publishes daily UK yield curves from gilts: nominal, real and implied inflation. Real curves are fitted from index-linked gilt prices. The nominal curve also uses GC repo rates at the short end. — [BoE Yield curves](https://www.bankofengland.co.uk/statistics/yield-curves); [Further details about yields data](https://www.bankofengland.co.uk/statistics/details/further-details-about-yields-data)
- Download URLs:
  - Latest month: `https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/latest-yield-curve-data.zip`. It contains "GLC Real daily data current month.xlsx", "GLC Nominal…", "GLC Inflation…" and "OIS daily data current month.xlsx".
  - Daily archives: `glcrealddata.zip`, `glcnominalddata.zip`, `glcinflationddata.zip`.
  - Month-end archives: `glcrealmonthedata.zip` (files split 1979–2015, 2016–2024, 2025–present) and the equivalent nominal and inflation files.
  - All are under `/-/media/boe/files/statistics/yield-curves/`.
  - The BoE targets publishing curves by noon on the following business day. — [BoE Yield curves](https://www.bankofengland.co.uk/statistics/yield-curves); structure verified by download
- Each workbook has the sheets `info`, `1. fwds, short end`, `2. fwd curve`, `3. spot, short end` and `4. spot curve`:
  - Row 4 holds the maturities in years. The real whole-curve sheet runs from 2.5y in 0.5y steps; the month-end file lists maturities up to 40y.
  - Dates are in column A.
  - Rates are continuously compounded, in percent.
  - One daily file had a "#VALUE!" placeholder row, so parsers must handle it. — own inspection of the downloaded files
  - The BoE page describes the fitting as a spline-based (variable roughness penalty / adjusted Waggoner) method, following Anderson & Sleath (2001, BoE WP 126). — [BoE Yield curves](https://www.bankofengland.co.uk/statistics/yield-curves); [Anderson & Sleath WP](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2001/new-estimates-of-the-uk-real-and-nominal-yield-curves.pdf)
  - Note: a WebFetch summary said real curves extend "to approximately 25 years". The downloaded month-end file lists columns to 40y, though long maturities may be sparsely populated.

**Current UK values (own calculation from the BoE GLC real spot curve; 5y5y = (10·s10 − 5·s5)/5)**

| Period | UK 5y5y real forward (RPI-linked ILGs) |
|---|---|
| 2018 average (MPC's previous r* assessment) | -1.52% (range -1.78 to -1.38) |
| 2019 / 2020 / 2021 avg | -2.26% / -2.81% / -2.46% |
| 2022 avg | -0.92% (Jan -2.35% → Sep +0.17%, Oct +0.50% during LDI crisis) |
| 2023 avg | +0.56% |
| 2024 avg | +1.02% (Dec-24: 1.61%) |
| 2025 avg | +2.07% (range 1.63–2.36) |
| 2026 avg to Aug | +2.37% (Feb-26 low 1.93%; Jul-26 2.65%) |
| 28 Sep 2026 (daily) | **2.71%** |

- Also on 28 Sep 2026 (own calculation): 10y real spot 1.97%; 10y instantaneous real forward (Aug-26 month end) 2.99%; nominal 5y5y 5.85%; implied RPI inflation 5y5y 3.14%.

**MPR February 2025, Box A (market measure)**
- The Box A market-based measure is not an ILG measure. It is "based on 10-year UK forward expected real interest rates, which can be extracted from nominal bond yields adjusted for survey measures of inflation expectations". It rose "by over 90 basis points since 2018".
- Caveats in the Box: market measures "may overstate the true increase in R* because long-term yields have historically been oversensitive to short-term yields", and "long-term yields reflect both expectations of future interest rates and a term premium, and estimates of term premia are uncertain." — [BoE MPR Feb 2025, Box A (PDF pp.22–27)](https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2025/february/monetary-policy-report-february-2025.pdf)

**RPI reform**
- "From 2030, UK RPI will be aligned with the CPIH measure of consumer prices". The BoE adjusts its 5y5y inflation-compensation measure by adding a scaled estimate of the reform effect. That estimate is the difference between the 4y1y and 6y1y forwards on a 3-month rolling average. — [MPR Feb 2025, Chart 2.28 note](https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2025/february/monetary-policy-report-february-2025.pdf)
- Alan Taylor likewise uses "the 5y5y inflation swap rate adjusted for estimated effects of the RPI reform". — [Taylor, "Stopping for gas" (2026)](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/stopping-for-gas.pdf)

**LDI crisis**
- In Sep–Oct 2022, gilt sales were larger in index-linked gilts, which make up only about a quarter of the market, and were spread more evenly across maturities than sales of conventional gilts. — [BoE SWP 1,019 "An anatomy of the 2022 gilt market crisis"](https://www.bankofengland.co.uk/working-paper/2023/an-anatomy-of-the-2022-gilt-market-crisis)
- The BoE bought £19.3bn of gilts (28 Sep–14 Oct 2022), including £7.2bn of index-linked gilts. — [BoE QB 2023, "Financial stability buy/sell tools: a gilt market case study"](https://www.bankofengland.co.uk/quarterly-bulletin/2023/2023/financial-stability-buy-sell-tools-a-gilt-market-case-study)
- A secondary source says long-dated ILG real yields rose from about -1% to +0.5% within days. — [fi-desk](https://www.fi-desk.com/bank-of-england-releases-detail-on-index-linked-gilt-purchases-as-ldi-woes-continue/) (secondary; consistent with the own-calculated 5y5y jump from -0.58% in Aug-22 to +0.50% in Oct-22)

**Christensen & Rudebusch (2019)**
- Full reference: "A New Normal for Interest Rates? Evidence from Inflation-Indexed Debt", *Review of Economics and Statistics* 101(5): 933–949; FRBSF WP 2017-07.
- r* is defined as "the average expected real short rate over a five-year period starting five years ahead" (5yr5yr), consistent with Laubach–Williams.
- The model is an AFNS model estimated from individual TIPS prices, with and without a TIPS liquidity factor (T-O-L vs T-O models). The average estimated TIPS liquidity premium is 34bp.
- Estimates "gradually decline from around 2 to 3 percent in 2000 to near zero" by the end of the sample (2016). They conclude r* "has fallen about 2 percentage points and appears unlikely to rise quickly."
- The paper also shows 5yr5yr real term premium estimates, which is how the model separates expectations from the raw forward. — [FRBSF WP PDF](https://www.frbsf.org/wp-content/uploads/wp2017-07.pdf); [REStat](https://direct.mit.edu/rest/article-abstract/101/5/933/58554/A-New-Normal-for-Interest-Rates-Evidence-from)
- In that paper, an alternative six-factor model (AACMY) gives a negative r* for almost the whole sample. The authors attribute this to poorly pinned-down P-dynamics. Estimates are therefore model-sensitive. — same source
- The WebFetch summary gave figures for the term premium (0.5–1.0%) and liquidity premium (0.3–0.5%). These did not match the paper text and have been excluded. Only the 34bp average liquidity premium is verified.

**Bauer & Rudebusch (2020)**
- Full reference: "Interest Rates under Falling Stars", *AER* 110(5): 1316–54.
- Trend inflation and the equilibrium real rate are fundamental determinants of the yield curve. Term-structure models that assume constant long-run means (fixed endpoints) mis-measure term premia. Allowing shifting endpoints yields "more plausible estimates of the term premium" and accurate out-of-sample yield forecasts. — [AEA](https://www.aeaweb.org/articles?id=10.1257%2Faer.20171822); [Bauer page](https://www.michaeldbauer.com/publication/falling-stars/)
- Replication code and data are available. — [openICPSR 115622](https://www.openicpsr.org/openicpsr/project/115622/version/V1/view?path=/openicpsr/115622/fcr:versions/V1/data&type=folder)

### Inferences
- **RPI basis in 2026.** The 5y5y window from Sep 2026 covers roughly 2031–2036, which is entirely after the 2030 reform. So an RPI-linked real forward there is approximately a CPIH-real forward, and the RPI/CPI basis matters little for the current reading. For historical comparison it matters a lot. In 2018 the 5y5y window (2023–2028) was pre-reform, when RPI ran well above CPI, so RPI-real forwards were depressed relative to CPI-real ones. Part of the roughly 4.2pp rise in the ILG 5y5y since 2018 is therefore a basis artefact. A dashboard should either:
  - start a consistent series around 2020–21, when the reform window began to be priced, or
  - present a CPI-adjusted series (nominal forward minus survey or RPI-reform-adjusted inflation expectations, as in the MPR), rather than the raw ILG real forward for pre-2020 comparisons.
- **Size of the gap.** The contrast between the ILG real forward rise (~+4.2pp since 2018) and the MPR's nominal-minus-survey-inflation measure (">90bp" to early 2025) shows the scale of term premium, ILG-specific demand and basis effects. A raw real forward is not a credible stand-alone r* estimate for the UK.
- **Implementability.** A raw 5y5y real (or 10y instantaneous real) forward is trivially implementable daily with free data. A Christensen–Rudebusch style AFNS with liquidity factor on individual ILG prices is feasible in principle, since DMO publishes gilt prices and details. But it is a substantial research build, and no public UK version was found.
- **Crisis flags.** Episodes of market dysfunction should be shaded or flagged on the dashboard, notably Sep–Oct 2022 and possibly the Feb 2026 Iran-war shock.

### Gaps
- No free, regularly published term-premium-adjusted UK real forward (UK AFNS/C&R-type r*) was found.
- The exact series and chart behind the MPR's ">90bp" measure were not located. The text says 10y forward real rates from nominal yields minus survey inflation expectations, probably Consensus, but the maturity construction and data are not published.
- No quantitative estimates of the ILG liquidity premium or LDI-demand premium for the 2023–2026 period were found.
- The own calculations have not been cross-checked against an official BoE-published 5y5y real series, because none is published.

## 2. UK term-premium models: are UK term-premium estimates published or free?

### Takeaway
The BoE's UK term-structure work is methodological, not a data service. The main papers are Malik & Meldrum (JBF 2016; SWP 518), long-run priors for term-structure models (2015), and a 2026 Bank Insights OIS+MaPS model. No regularly updated, free UK term-premium series was found. A dashboard would need to estimate an ACM-style model itself (feasible with the free GLC nominal curve) or rely on the BoE's occasional charts.

### Cited Findings
- **Malik & Meldrum (2016).** "Evaluating the robustness of UK term structure decompositions using linear regression methods", BoE SWP 518 (Dec 2014); *Journal of Banking & Finance* 67: 85–102 (2016).
  - They estimate UK affine term-structure models using linear-regression (ACM-type) methods and find they pass standard specification tests.
  - Term premia are countercyclical and positively related to inflation uncertainty, and are robust to small-sample bias correction and to adding unspanned macro factors. — [BoE SWP 518 page](https://www.bankofengland.co.uk/working-paper/2014/evaluating-the-robustness-of-uk-term-structure-decompositions-using-linear-regression-methods); [PDF](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2014/evaluating-the-robustness-of-uk-term-structure-decompositions-using-linear-regression-methods.pdf); [JBF/IDEAS](https://ideas.repec.org/a/eee/jbfina/v67y2016icp85-102.html)
- **Related BoE work.** "Long run priors for term structure models" (BoE SWP, 2015) is relevant to the shifting-endpoint problem. — [PDF](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2015/long-run-priors-for-term-structure-models.pdf). SWP 914 (2021) covers monetary policy surprises and transmission through term premia versus expected rates. — [PDF](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2021/monetary-policy-surprises-and-their-transmission-through-term-premia-and-expected-interest-rates.pdf)
- **Bank Insights (2026), "Bank Rate expectations in the UK curve following the war in Iran".**
  - BoE staff use "a term structure model designed to separate near-term risk premia from central expectations for Bank Rate", using OIS rates and MaPS survey expectations.
  - After stripping risk premia, "the model-implied expected path for Bank Rate was broadly flat over the next year", even though the forward curve sloped upward after Feb 2026.
  - Short-end risk premia were "unusual by historical standards, albeit not unprecedented". The short-end OIS/survey gap has a historical mean of -17bp with a standard deviation of 27bp.
  - This is a one-off analysis; no downloadable series was found. — [Bank Insights 2026](https://www.bankofengland.co.uk/bank-insights/2026/bank-rate-expectations-uk-curve-following-the-war-in-iran)
- **Taylor (July 2025).** In "Unexpected curves", Alan Taylor's model-based analysis uses a term premium from "a macro-finance term structure model using government bond yields". Recursive model-based neutral-rate forecasts "have actually been better at predicting future short rates than the bond market on average over recent decades", compared with 3-year-ahead instantaneous forwards. — [Taylor, ECB Forum 2025](https://www.bankofengland.co.uk/speech/2025/july/alan-taylor-panellist-at-ecb-forum-on-central-banking-2025); [appendix](https://www.bankofengland.co.uk/-/media/boe/files/speech/2025/unexpected-curves-remarks-by-alan-taylor-appendix)
- **Free OIS data.** A BoE OIS curve file is free and is included in the latest-yield-curve zip ("OIS daily data current month.xlsx"). — own inspection of the [BoE download](https://www.bankofengland.co.uk/statistics/yield-curves)

### Inferences
- **Build route.** For the dashboard, the realistic free route is to estimate an ACM-style (Adrian–Crump–Moench linear regression) or Bauer–Rudebusch shifting-endpoint model on the GLC nominal curve. Survey inflation expectations can then be subtracted, or the model extended to the real curve. Both need maintenance and add model risk.
- **Simpler alternative.** Subtract an assumed or averaged term premium. This is weaker, but transparent.

### Gaps
- No evidence was found that the BoE publishes a UK term-premium time series (unlike the NY Fed ACM or Kim–Wright series for the US). Not definitively confirmed.
- No UK ACM replication with public data was found in this search.

## 3. Surveys: MaPS perceived neutral Bank Rate, Consensus, SPF-type, Fed SEP

### Takeaway
MaPS asks for the neutral Bank Rate in nominal terms in every round. It has been published since February 2022, is free in HTML and XLSX, and runs eight times a year. The median was 3.0% in 2023–24, peaked at 3.5% in March 2025, fell to 3.0% in late 2025, and is 3.25% in 2026 (latest: September 2026, 3.25%, IQR 3.00–3.50). It is the most implementable UK survey measure. Consensus Economics long-run forecasts are licensed. The Fed SEP longer-run dot is the US analogue (3.2% median, Sep 2026, as reported).

### Cited Findings
- **Launch.** The BoE announced on 14 Jan 2022 that it would publish aggregate MaPS results from February 2022; the survey had previously run in pilot form. It runs eight times a year, aligned with MPC meetings. — [BoE news, Jan 2022](https://www.bankofengland.co.uk/news/2022/january/bank-of-england-to-publish-results-of-market-participants-survey)
- **Question wording.** "where do you see the level of Bank Rate at which monetary policy is neither expansionary nor contractionary (often referred to as the neutral, natural or equilibrium rate) (%)?" — [MaPS Feb 2023](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/market-participants-survey-results-february-2023)
- **Nominal neutral Bank Rate by round (25th / median / 75th):**

| Survey (fielded) | Respondents | 25th | Median | 75th | Source |
|---|---|---|---|---|---|
| Feb 2023 (18–20 Jan 2023) | 56 | 2.50 | 3.00 | 3.50 | [link](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/market-participants-survey-results-february-2023) |
| Feb 2024 (17–19 Jan 2024) | 79 | 3.00 | 3.00 | 3.50 | [link](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/2024/market-participants-survey-results-february-2024) |
| Mar 2025 (5–7 Mar 2025) | 79 | 3.00 | 3.50 | 3.75 | [link](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/2025/market-participants-survey-results-march-2025) |
| Nov 2025 (22–24 Oct 2025) | 88 | 3.00 | 3.00 | 3.50 | [link](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/2025/market-participants-survey-results-november-2025) |
| Mar 2026 (4–6 Mar 2026) | 83 | 3.00 | 3.25 | 3.50 | [link](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/2026/market-participants-survey-results-march-2026) (via [secondary summary](https://service.betterregulation.com/document/839413)) |
| Sep 2026 (2–4 Sep 2026) | 92 | 3.00 | 3.25 | 3.50 | [link](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/2026/market-participants-survey-results-september-2026) |

- **Where the data are.** Each results page has an XLSX download (e.g. "Market Participants Survey results – September 2026 (XLSX 0.1MB)"). The URL pattern is `bankofengland.co.uk/markets/market-intelligence/survey-results/{year}/market-participants-survey-results-{month}-{year}`; 2022–23 pages sit without the year folder. — [MaPS Sep 2026](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/2026/market-participants-survey-results-september-2026)
- **MPR Feb 2025 on MaPS.**
  - The MaPS neutral measure "has increased by 150 basis points in recent years". But "it is difficult to judge the extent to which these responses reflect perceptions of long-run R*… the question asked does not clearly distinguish between the long-term equilibrium real rate and shorter-term concepts affected by cyclical factors."
  - The MPR also uses MaPS to compute real-rate gaps: each respondent's weighted mean Bank Rate expectation, deflated by their CPI expectation, minus their r* perception, over a 3-year horizon. — [MPR Feb 2025 PDF](https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2025/february/monetary-policy-report-february-2025.pdf); [MPR Feb 2025 page](https://www.bankofengland.co.uk/monetary-policy-report/2025/february-2025)
- **MPR Feb 2025 on Consensus.** Its "6 to 10 year ahead forecasts for 10-year yields and inflation based on Consensus Economics' survey of professional forecasters imply that expectations of the long-term real interest rate in the UK may have picked up by less than 25 basis points since 2018." Consensus Economics data are commercially licensed. — [MPR Feb 2025 PDF](https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2025/february/monetary-policy-report-february-2025.pdf)
- **ECB analogues.** The ECB's survey-based r* uses:
  - the Survey of Monetary Analysts (SMA): median expected deposit facility rate minus long-run inflation expectations, available from Q2 2021;
  - Consensus Economics: 3-month interbank rate expectations 10 years ahead minus long-run inflation expectations. — [ECB Economic Bulletin 1/2024, Brand, Lisack & Mazelis](https://www.ecb.europa.eu/press/economic-bulletin/focus/2024/html/ecb.ebbox202401_07~72edc611d3.en.html)
- **Fed SEP (Sep 2026).** Longer-run federal funds rate median 3.2%, central tendency 3.0–3.6%, range 2.9–3.9%; longer-run PCE inflation 2.0%. That implies a real longer-run rate of about 1.2%. — [Fed SEP 16 Sep 2026](https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm); history on [FRED FEDTARMDLR](https://fred.stlouisfed.org/series/FEDTARMDLR). The 3.2% figure comes from a WebFetch extraction and should be double-checked against the PDF.

### Inferences
- **Real-terms conversion.** MaPS is nominal. To express it as a real r*, subtract 2% (the inflation target) or respondents' long-run CPI expectations. On that basis the current MaPS-implied real neutral rate is about 1.25% (3.25% − 2%).
- **Reconciling the "+150bp".** The MPR's "+150bp in recent years" must compare with a pre-2023 round (probably around 2022, when the median would have been about 2%), not with the 2023 median of 3.0%. The published rounds shown above only move within 3.0–3.5%.
- **Contamination by the policy cycle.** The drop from 3.5% (Mar 2025) to 3.0% (Oct 2025) and back to 3.25% suggests MaPS responses move with the rate cycle. That supports the MPR caveat, so the measure should be labelled "medium-run neutral as perceived by markets".

### Gaps
- The 2022 MaPS neutral medians (the base for "+150bp") were not retrieved. The pages exist (e.g. [May 2022](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/market-participants-survey-results-may-2022), [Sep 2022](https://www.bankofengland.co.uk/markets/market-intelligence/survey-results/market-participants-survey-results-september-2022)) but were not fetched.
- The complete MaPS time series for every round was not compiled. It would be scraped from the per-round XLSX files; no single consolidated history file was found.
- No UK equivalent of an SPF long-run policy-rate question was found. The BoE's own Survey of External Forecasters asks about Bank Rate over 3 years, not the neutral rate; this was not verified in this search.

## 4. MPC and central-bank use of market-based r* (MPR Feb 2025 Box A, speeches, ECB/Fed papers)

### Takeaway
The MPC formally uses three lenses: macro models (+25 to 75bp since 2018), market-based measures (>+90bp) and surveys (MaPS +150bp; Consensus <+25bp). It concluded that R* "is likely to have increased modestly" and is "not used by the MPC as a direct guide to setting policy". The ECB similarly reports a median across macro, finance and survey measures. Taylor explicitly argues against "outsourcing" r* to market forwards.

### Cited Findings
**MPR February 2025, Box A**
- Headline conclusion: "Overall, the evidence suggests that R* is likely to have increased modestly, but that there is significant uncertainty…". Absent new disinflationary shocks, Bank Rate "is unlikely to fall back to its pre-pandemic lows."
- The 2018 benchmark was the August 2018 Inflation Report view of neutral Bank Rate at 2–3% nominal in the long run.
- Macro models: "a modest increase in R* of around 25 to 75 basis points". A Davis et al (2024) two-trend macro-finance model gives about 25bp; a Del Negro et al (2019) semi-structural model gives about 75bp.
- Market-based: ">90bp" (construction and caveats as in section 1).
- Surveys: MaPS +150bp; Consensus <25bp.
- "Because R* is a theoretical concept and cannot be directly observed, it is not used by the MPC as a direct guide to setting policy". It acts as "a long-term anchor for the policy rate".
- The Box also lists drivers in Table 1:
  - weighing on R*: demographics, trade fragmentation, higher risk;
  - pushing up: financial fragmentation, expansionary fiscal policy, AI;
  - climate change: net effect uncertain. — [MPR Feb 2025 PDF, pp.22–27](https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2025/february/monetary-policy-report-february-2025.pdf)

**Taylor (July 2025, "Unexpected curves")**
- UK and US forward curves over 20 years show "the market was wrong for much of the 2010s".
- He advocates model-based neutral-rate analysis with a term-premium adjustment from a macro-finance term-structure model. — [Taylor 2025](https://www.bankofengland.co.uk/speech/2025/july/alan-taylor-panellist-at-ecb-forum-on-central-banking-2025)
- Taylor's "The end of the road" (July 2025) also addresses neutral and is available as a PDF. — [link](https://www.bankofengland.co.uk/-/media/boe/files/speech/2025/july/the-end-of-the-road-speech-by-alan-taylor.pdf) (content not extracted)

**ECB**
- **Economic Bulletin 1/2024 (Brand, Lisack & Mazelis).**
  - Finance and term-structure estimates draw on Geiger & Schupp (2018), Joslin–Singleton–Zhu (2011)-type models, Ajevskis (2020) shadow-rate and Brand, Goy & Lemke (2021, ECB WP 2612 "Natural rate chimera and bond pricing reality").
  - Survey measures come from SMA and Consensus.
  - Since H2 2023, estimates range "between about minus three-quarters of a percentage point to around half a percentage point" (real).
  - The range "only accounts for model uncertainty and does not take account of much larger statistical uncertainty." — [ECB EB 1/2024](https://www.ecb.europa.eu/press/economic-bulletin/focus/2024/html/ecb.ebbox202401_07~72edc611d3.en.html)
- **ECB Economic Bulletin 1/2025.**
  - Updated range as of Q4 2024: real about -0.5% to +0.5%, nominal about 1.75%–2.25%; "such ranges should be viewed as merely indicative".
  - It notes term-structure measures carry uncertainty over whether yield movements reflect r* or risk compensation. — [ECB EB 1/2025](https://www.ecb.europa.eu/press/economic-bulletin/focus/2025/html/ecb.ebbox202501_08~3be5a005f9.en.html)
- Christensen & Mouabbi apply the AFNS/inflation-indexed method to the euro area. — [SUERF Policy Brief 980](https://www.suerf.org/wp-content/uploads/2024/09/SUERF-Policy-Brief-980_Christensen_Mouabbi.pdf); [FRBSF Economic Letter 2025 "A Rising Star"](https://www.frbsf.org/research-and-insights/publications/economic-letter/2025/05/rising-star-natural-interest-rate-in-euro-area/) (not fetched)

### Inferences
- The BoE's own framing is a "suite" of macro, market and survey measures with explicit caveats, which is the model for the dashboard. Presenting a range or median across approaches mirrors both the BoE Box A and the ECB EB practice.

### Gaps
- Speeches by Greene, Mann, Pill and Lombardelli specifically discussing market-based r* were not found in this search (limited tool budget). Their views are not covered here.
- MPC minutes references to r* measures after February 2025 were not reviewed.
- The IMF WP 2025/123 on euro-area equilibrium rates surfaced in search but was not read.

## 5. Why the dashboard spec excluded market proxies, and how best practice addresses term premia

### Takeaway
The spec's objection ("forward rates include term premia") is correct and is the BoE's own caveat. Best practice does not discard market measures. It either (a) models the term premium explicitly (AFNS with liquidity factor; ACM; shifting-endpoint models; OIS+survey hybrids), or (b) shows the market measure alongside macro and survey measures with caveats. For a free UK dashboard, the defensible option is a clearly labelled "market-implied long-horizon real rate (includes term premium)", shown next to the MaPS median, with an optional in-house ACM/AFNS-adjusted version later.

### Cited Findings
- The BoE says market-based measures "may overstate the true increase in R*", that long yields are "oversensitive to short-term yields", and that "estimates of term premia are uncertain." — [MPR Feb 2025](https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2025/february/monetary-policy-report-february-2025.pdf)
- Christensen & Rudebusch strip time-varying real term premia and TIPS liquidity premia with an AFNS model on individual bond prices, so r* is the model-implied expected 5y5y real short rate. — [FRBSF WP 2017-07](https://www.frbsf.org/wp-content/uploads/wp2017-07.pdf)
- Bauer & Rudebusch show that fixed-endpoint term-structure models give implausible term premia when r* and trend inflation drift, and that shifting-endpoint models correct this. — [AER 2020](https://www.aeaweb.org/articles?id=10.1257%2Faer.20171822)
- BoE staff combine OIS forwards with MaPS survey expectations to separate risk premia from expected Bank Rate. — [Bank Insights 2026](https://www.bankofengland.co.uk/bank-insights/2026/bank-rate-expectations-uk-curve-following-the-war-in-iran)
- The ECB reports finance-based estimates inside a multi-model range and warns about term premia and statistical uncertainty. — [ECB EB 1/2024](https://www.ecb.europa.eu/press/economic-bulletin/focus/2024/html/ecb.ebbox202401_07~72edc611d3.en.html); [ECB EB 1/2025](https://www.ecb.europa.eu/press/economic-bulletin/focus/2025/html/ecb.ebbox202501_08~3be5a005f9.en.html)
- Taylor finds market forwards were poorer predictors of future short rates than model-based neutral-rate forecasts over recent decades. — [Taylor 2025](https://www.bankofengland.co.uk/speech/2025/july/alan-taylor-panellist-at-ecb-forum-on-central-banking-2025)

### Inferences
**Implementability ranking for a free UK dashboard**

| Measure | Free? | Effort | Credibility as r* | Recommendation |
|---|---|---|---|---|
| MaPS neutral Bank Rate median (nominal, −2% for real) | Yes (XLSX per round, 8×/yr, since 2022) | Low (scrape) | Medium: contaminated by cycle | Include |
| Raw ILG 5y5y real forward (GLC real curve) | Yes (daily) | Very low | Low–medium: includes term, liquidity and LDI premia; RPI basis pre-2030 | Include, clearly labelled as upper-bound/market-implied; flag 2022 LDI episode; start ~2021 or add basis caveat |
| Nominal 5y5y (GLC nominal/OIS) minus 5y5y inflation expectations (RPI-reform-adjusted, or target 2%) | Yes | Low | Medium–low: same term-premium issue; closest to MPR's ">90bp" measure | Optional alternative to ILG measure |
| Term-premium-adjusted forward (in-house ACM or Bauer–Rudebusch on GLC nominal; or AFNS on ILG prices) | Data free; no published series | High | Higher, but model-dependent (C&R vs AACMY divergence) | Phase 2 |
| Consensus Economics 6–10y ahead real rate | No (licensed) | n/a | Medium | Exclude; cite MPR's "<25bp since 2018" as context |
| Fed SEP longer-run dot / ECB range | Yes | Low | Benchmarks only (US/EA) | Optional comparators |

- **Level check (own calculation, approximate).**
  - Raw ILG 5y5y real forward: about 2.7%.
  - MaPS-implied real neutral: about 1.25%.
  - Fed SEP implied real: about 1.2%.
  - The roughly 1.5pp gap between the ILG forward and the survey measures is a rough upper-bound indication of the UK long-horizon real term premium plus ILG-specific premia today.
  - This supports the spec's concern: the raw forward should not be averaged into a central r* estimate without adjustment.

### Gaps
- No published estimate of the current UK 5y5y real term premium was found to validate the ~1.5pp inference.
- No UK study was found evaluating whether ILG-based r* signals have predictive content comparable to the US TIPS evidence.
