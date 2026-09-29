# Time-series and trend-cycle r* estimators robust to the ELB and weak identification (for a UK dashboard complementing HLW)

Scope note: research conducted 29 Sep 2026. Primary texts were read in full where marked "(read)": DGGT 2017 BPEA, DGGT 2019 NBER WP (global), Johannsen–Mertens FEDS 2016 WP, Kiley IJCB 2020, Hamilton–Harris–Hatzius–West 2015/16 WP, Han–Ma 2023 WP. Other items are from abstracts, repo READMEs or summaries and are flagged accordingly.

---

## 1. Del Negro, Giannone, Giannoni & Tambalotti (DGGT) trend-cycle VAR: 2017 BPEA (US) and 2019 JIE (global, incl. UK)

### Takeaway
DGGT is a Bayesian "VAR with common trends": observables are split into random-walk trends and a stationary VAR cycle. Very tight priors on the trend-innovation variance do the work of identification. The ELB is handled by treating the short rate as **missing** during the ZLB and leaning on long yields and survey expectations. The 2019 global version already contains a UK trend, built from annual Jordà–Schularick–Taylor (JST) data, 1870–2016. The authors publish Matlab code under a BSD-3 licence, and the Kalman/Durbin–Koopman Gibbs sampler is simple enough to port to Python. For a UK dashboard this is the most implementable, best-documented "robust" complement to HLW.

### Cited Findings
**General state-space form (both papers)** (read) — [NBER WP 25039](https://www.nber.org/system/files/working_papers/w25039/w25039.pdf)
- Measurement: y_t = Λ ȳ_t + ỹ_t. Trends follow a random walk, ȳ_t = ȳ_{t−1} + e_t. Cycles follow a VAR, Φ(L) ỹ_t = ε_t. Trend and cycle shocks are orthogonal, with e ~ N(0, Σ_e) and ε ~ N(0, Σ_ε). Initial cycle states are drawn from the VAR's unconditional variance. The paper describes this as essentially Villani (2009) with a stochastic rather than deterministic trend. It notes that "the procedure straightforwardly accommodates missing observations".
- Estimation: Gibbs sampler using the Durbin–Koopman (2002) simulation smoother, with 10,000 draws of which the first 5,000 are burn-in (global paper).
- Priors:
  - VAR coefficients get a Minnesota prior with overall tightness 0.2 and own-lag mean **0** (cycles are stationary), truncated to non-explosive draws.
  - Σ_ε ~ IW with κ_ε = n+2 and diagonal prior mean. Prior SD is 2 for each cycle and 4 for inflation cycles (global paper; the BPEA values were half these).
  - Σ_e ~ IW with **κ_e = 100** (tight). The mode is diagonal with **1/100** per real trend (global, annual data), which implies a 1pp SD of the change in the trend over a century. Inflation trends get 1/50.
  - Loadings λ get independent Gaussian priors.
  - Initial trend means are 0.5 for the real rate, 2 for inflation, 1 for the term spread, 1 for the convenience yield and 1.5 for consumption growth. Country-specific trends start at mean 0 with half the SD of the world trend.
- Robustness to the trend-variance prior: moving from a "one century" horizon to half a century, a quarter century or a decade barely changes the results (Online Appendix Fig. A3). Only an extreme 1-year horizon, which reproduces the decadal moving average, changes them, and it gives 50% bands about 10pp wide in 2016 — [NBER WP 25039](https://www.nber.org/system/files/working_papers/w25039/w25039.pdf)

**2017 BPEA US model ("Safety, liquidity, and the natural rate of interest")** (read) — [BPEA text](https://www.brookings.edu/wp-content/uploads/2017/08/delnegrotextsp17bpea.pdf)
- Equations (quarterly):
  - R_{1,t} = r̄_t + π̄_t + R̃_{1,t}
  - π_t = π̄_t + π̃_t, and π^e_t = π̄_t + π̃^e_t (Stock–Watson-style use of surveys)
  - R_{80,t} = r̄_t + π̄_t + tp̄_t + R̃_{80,t} (20-year yield with a trend term premium)
  - Survey long-run expected short rate: R^e_{1,t} = r̄_t + π̄_t + R̃^e_{1,t}
  - Observables are y_t = (π, π^e, R_1, R_80, R^e_1) and trends are (r̄, π̄, tp̄). Only two cointegrating restrictions are imposed: inflation with its expectations, and the short rate with its expectations.
- Data (FRED mnemonics):
  - PCE inflation: DPCERD3Q086SBEA
  - 3-month T-bill: TB3MS
  - 20-year Treasury: GS20, averaged with GS10/GS30 for 1987–93
  - 10-year PCE inflation expectations: SPF from 2007, FRB/US PTR-type series for 1970–2006
  - SPF 10-year average T-bill expectations: annual, from 1992
  - Sample 1960Q1–2016Q4, with 1954–59 as presample. VAR has 5 lags.
- Trend-variance prior: diagonal **1/400** for r̄ (1pp change per century at quarterly frequency) and 1/200 for inflation, with κ_e = 100. Initial trends are 2, 0.5 and 1 for π̄, r̄ and tp̄, with V_0 = I.
- **ELB handling:** "we do not use data on R_{1,t} after 2008:Q3"; the short rate is treated as unobservable from 2008Q4 onward. As a robustness check, using the short-rate data through the ZLB gives "essentially the same" results (Table A2, col. 5).
- Results:
  - The median decline in r̄ from 1998Q1 to 2016Q4 is about 1.3pp.
  - The r̄ bands narrow sharply once SPF short-rate expectations become available, then "become somewhat wider again in the ZLB period".
  - A looser prior (κ_e = 8) lets the trend pick up higher-frequency movement, but the substantive conclusions hold.
  - The convenience-yield decomposition uses Baa/Aaa spreads, with the 20-year yield chosen to match corporate maturities; "results obtained using the 10-year yield are very similar".
- Discussant criticism (in the same BPEA volume): "The present paper lacks proper treatment for the zero lower bound (ZLB) period" — [BPEA text](https://www.brookings.edu/wp-content/uploads/2017/08/delnegrotextsp17bpea.pdf)

**2019 JIE global model ("Global trends in interest rates"; NBER WP 25039, NY Fed SR 866)** (read) — [NBER WP 25039](https://www.nber.org/system/files/working_papers/w25039/w25039.pdf); [NY Fed SR866](https://www.newyorkfed.org/research/staff_reports/sr866.html)
- Baseline, for each country i:
  - R_{i,t} = r^w_t + r^i_t + λ^π_i π^w_t + π^i_t + R̃_{i,t}
  - R^L_{i,t} = r^w_t + r^i_t + ts^w_t + ts^i_t + λ^π_i π^w_t + π^i_t + R̃^L_{i,t}
  - π_{i,t} = λ^π_i π^w_t + π^i_t + π̃_{i,t}
  - No-arbitrage sets the loading of each country's real rate on the world real trend r^w to 1. Inflation loadings are free.
  - Dimensions: n = 21 observables and τ = 24 trends for 7 countries. The model has **1 lag** (annual data).
- Data: JST Macrohistory Database, annual 1870–2016, for Canada, Germany, France, Italy, Japan, the **UK** and the US.
  - Variables are short rates (bills or money market), long government bond yields, CPI inflation and real consumption per capita, plus Moody's Baa from FRED (from 1919).
  - Observations above 30pp in absolute value are treated as missing.
  - There are **no survey expectations** in the global model, unlike the BPEA US model.
- Results:
  - r^w was about 1.5% for roughly a century, peaked near 2.5% around 1980, and was about 0.5% in 2016.
  - The declines are about 2pp since 1980, more than 150bp since 1990 and more than 1pp over the last 20 years. All 90% bands exclude zero.
  - "The uncertainty on the level of the trend at any point in time is large", but the decline is precisely estimated.
  - The convenience yield explains about half of the 171bp decline since 1980 and close to 60% of the decline since 1997.
- **UK-specific results:**
  - Country-specific trends have shrunk since the late 1970s, so each country's trend is now close to the world trend.
  - "U.K. government paper yielded greater convenience than U.S. Treasuries for the first century of the sample, but this ranking has been reversed over the last fifty years."
  - In the free-loading variant, the UK loading on r^w has a 68% credible interval below one, but the 90% interval covers one.
  - Regressing the UK trend on the middle-aged/young (MY) demographic ratio gives R² = 81%, the highest of the countries (range 26–81%).
- **Code:** GitHub [FRBNY-TimeSeriesAnalysis/rstarGlobal](https://github.com/FRBNY-TimeSeriesAnalysis/rstarGlobal)
  - Matlab R2017b, BSD-3-Clause licence. Run `estimateAll.m`; 100,000 MCMC draws take about 20 hours.
  - `Rstar_Vintages.xlsx` holds original and updated US and world r* for 1870–2016.
- BPEA code: [FRBNY-DSGE/rstarBrookings2017](https://github.com/FRBNY-DSGE/rstarBrookings2017) (Matlab `MainModelX.m`). The accompanying Excel file holds original and updated trend estimates.

### Inferences
- **UK substitutions for a quarterly BPEA-style UK model:**

  | Variable | UK substitute | Caveats |
  |---|---|---|
  | R_1 (short rate) | Bank Rate or 3-month gilt/T-bill (GLC short end) | Short-rate data from about 2009Q1 to 2016 (Bank Rate 0.5% then 0.25%, and 0.1% in 2020–21) would be treated as missing, as DGGT do |
  | R_80 (long yield) | BoE nominal GLC 20-year spot yield, or the 10-year | |
  | π (inflation) | CPI | RPI or a CPI back-cast is needed before 1989/1996 |
  | π^e (long-run inflation expectations) | BoE/Ipsos Inflation Attitudes Survey 5-year-ahead expectations; HMT "Comparison of independent forecasts" medium-term CPI; market-implied 5y5y from the BoE inflation curve | The Ipsos series is a household survey and noisy. The market measure is RPI-based and includes an RPI–CPI wedge and inflation risk premium |
  | R^e_1 (survey long-run expected short rate) | No long-history UK analogue of the SPF 10-year T-bill expectation found | Candidates are BoE Market Participants Survey responses and Consensus long-term forecasts. Otherwise drop this observable, which the paper shows widens the bands |

  Alternatively, a real-yield observable could be added directly: the BoE real (index-linked) GLC 5y5y or 10-year real yield, loaded on r̄ plus a real term-premium trend. DGGT do not do this.
- The published global model already gives a UK trend (r̄_UK = r^w + r^UK), but only annually to 2016. A dashboard would need to re-estimate on updated JST data, or on a quarterly panel of UK, US and euro-area data, to extend it.
- A UK-plus-world panel variant is attractive because the paper finds idiosyncratic trends have "been vanishing since the late 1970s". It pins the UK trend down largely through the common world trend, which reduces UK-specific weak-identification problems.

### Gaps
- No UK-specific point estimate for 2016 was extracted from figures or tables; UK results are shown graphically (Fig. 3). The updated `Rstar_Vintages.xlsx` holds only US and world series, so UK numbers would need a code run.
- It is unclear whether DGGT or the NY Fed have updated the global model beyond 2016. No post-2019 vintage was found.
- The published JIE version (2019, vol. 118, pp. 248–262) was not checked for changes versus the NBER WP. I believe the citation is J. Int. Econ. 118:248–262, but did not verify it.

---

## 2. Johannsen & Mertens (2021 JMCB): shadow rate plus trend real rate

### Takeaway
Johannsen–Mertens (JM) is a Bayesian unobserved-components model:
- random-walk trends for inflation (with stochastic volatility) and the real rate (constant variance);
- a stationary VAR(2) with stochastic volatility for the gaps in inflation, the unemployment gap, the shadow rate and a medium-term yield;
- the observed short rate = max(shadow rate, ELB).

Explicitly modelling the ELB stops the model reading the long spell at zero as a fall in trend. As a result, JM's r̄ declines less than LW or Lubik–Matthes. Replication code is public (Fortran/Matlab/R). The model is heavier to port to Python than DGGT, but for a UK ELB sample (2009–21) it is the most principled treatment.

### Cited Findings
(read, FEDS 2016-033 WP version) — [FEDS 2016-033](https://www.federalreserve.gov/econresdata/feds/2016/files/2016033pap.pdf); published version [JMCB 53(5):1005–1046, 2021](https://onlinelibrary.wiley.com/doi/abs/10.1111/jmcb.12771); [BIS WP 715](https://www.bis.org/publ/work715.pdf)
- Equations:
  - i_t = max(s_t, ELB), with ELB = 0 for the US. Quarters with a 0–25bp target range count as at the ELB.
  - Each series x_t = x̄_t + x̃_t, where x̄_t = lim_{h→∞} E_t x_{t+h} (Beveridge–Nelson-style).
  - π̄_t = π̄_{t−1} + σ_{π̄,t} ε, with stochastic volatility.
  - s̄_t = π̄_t + r̄_t, with r̄_t = r̄_{t−1} + σ_r̄ ε (constant variance: "cautions us against fitting a stochastic volatility process for changes in this trend").
  - Medium-term yield trend: ȳ_t = s̄_t + p̄_0, a constant average term premium, so spreads are stationary.
  - Gaps: A(L)[π̃, ũ, s̃, ỹ]' = B Σ_t ε_t, with B unit lower-triangular and diagonal SV following log σ²_{j,t} − μ_j = ρ_j(log σ²_{j,t−1} − μ_j) + φ_j η_{j,t}. There are 2 lags.
  - Inflation has measurement error with SV.
- **ELB sampling:** first treat rates at the ELB as missing and draw states with the standard simulation smoother. Then **reject draws until s_t < ELB** in ELB quarters, generalising Park et al. (2007) and Hopke et al. (2001). Other parameters follow Primiceri (2005) and Cogley–Sargent (2005).
- Data (FEDS version):
  - PCE headline inflation, effective fed funds rate, 5-year Treasury (GS5), unemployment minus CBO NROU.
  - Sample 1960Q1–2015Q4, all from FRED.
  - The FEDS version uses **no survey data**. The JMCB replication README lists SPF only for forecast comparisons, and adds TB3MS, GS2, GS10, GDPC1 and GDPPOT — [GitHub replication](https://github.com/elmarmertens/JohannsenMertensJMCBtimeseriesELB)
- Results:
  - Quasi-real-time (filtered) and smoothed r̄ both show declines starting "well before the onset of the Great Recession". Bands are "wide", consistent with Hamilton et al., Kiley and Lubik–Matthes.
  - r̄ does "not dip nearly as much" as LW or Lubik–Matthes. The reasons given are stochastic volatility in the gaps and explicit ELB modelling.
  - **Ignoring the ELB (treating zero as data) yields a lower trend nominal rate**, because the model must explain the flat rate by a trend shift rather than a large negative shadow-rate gap.
  - Including the medium-term yield sharply tightens the shadow-rate posterior at the ELB.
- BIS WP abstract: "estimates of the longer-run level of the real rate have edged down somewhat in recent decades, but not significantly so"; forecasts are competitive — [BIS WP 715](https://www.bis.org/publ/work715.pdf) (via summary)
- **Code:** [elmarmertens/JohannsenMertensJMCBtimeseriesELB](https://github.com/elmarmertens/JohannsenMertensJMCBtimeseriesELB)
  - Fortran (Intel + MKL, OpenMP) does the MCMC; Matlab handles figures; there is some R.
  - Variants: `spectre2018.f90` (baseline SV), `spectre2018rbarSV.f90` (SV in all shocks, including r̄), `spectre2018constvar.f90` (no SV), `nomas2018.f90` (no long yields).
  - Forecast comparisons against a random walk, SPF and Wu–Xia (`jm_vs_rw.m`, `jm_vs_spf.m`, `jm_vs_wx.m`).
  - No licence stated.

### Inferences
- **UK substitutions:**
  - Bank Rate or SONIA for i_t, with the ELB set to 0.5% (2009–16), 0.25% (2016–17) and 0.1% (2020–21). A time-varying ELB is trivial to add.
  - A 5-year nominal gilt (BoE GLC) for y_t.
  - CPI inflation.
  - An unemployment gap using an OBR or BoE equilibrium unemployment estimate.
  - Adding a survey long-run inflation observable (BoE/Ipsos 5-year, or HMT medium-term) is a natural extension.
- The Python port is feasible:
  - the linear-Gaussian state space with missing data can use a custom Durbin–Koopman smoother, or statsmodels' `simulation_smoother`;
  - SV can use a Kim–Shephard–Chib mixture sampler (Python implementations exist);
  - the ELB step is a rejection or accept–resample loop. Rejection can be slow over long ELB spells; the UK had about 50 quarters at or near the ELB, so block sampling or the Carriero–Clark–Marcellino–Mertens shadow-rate sampler may be needed.
- JM's finding that ignoring the ELB biases r̄ down is directly relevant to UK HLW-style estimates over 2009–21.

### Gaps
- The JMCB published version may differ from the FEDS WP in data and specification, e.g. adding the 10-year and 2-year yields. The repository lists GS2, GS5, GS10 and TB3MS, but I could not confirm the final baseline observable set or the final r̄ numbers.
- Search snippets mentioned updated JM r̄ estimates "through 2024:Q3", but the author's homepage and repo README did not show values. Unverified.
- No UK application of JM was found (see section 6 for related UK work).

---

## 3. Lubik–Matthes TVP-VAR, Kiley (2020), Hamilton–Harris–Hatzius–West (2016), Lunsford–West (2019), Bauer–Rudebusch (2020)

### Takeaway
- **Kiley** shows the data barely move the prior on r* variance: the posterior of the r* shock SD moves one-for-one with its prior. Any r* model's time variation is largely a prior choice, which argues for reporting several prior settings.
- **Hamilton et al.** use backward moving averages and a VECM linking the US real rate to a "world" long-run rate. They conclude real rates are non-stationary, the link to growth is weak and uncertainty is very large; they give a range of about 0–2% for 2015.
- **Lubik–Matthes** (TVP-VAR) had to restrict parameter drift in 2023 after post-COVID volatility.
- **Lunsford–West** find demographics, but not productivity, correlate with low-frequency real rates.
- **Bauer–Rudebusch** show that shifting-endpoint yield models (r* + π*) improve forecasts and term-premium estimates.

### Cited Findings
**Kiley (2020), "What can the data tell us about the equilibrium real interest rate?", IJCB 16(3):181–209** (read) — [IJCB](https://www.ijcb.org/journal/v16n3/what-can-data-tell-us-about-equilibrium-real-interest-rate); [PDF](https://www.ijcb.org/sites/default/files/journal/v16n3/ijcb-v16n3-what-can-data-tell-us-about-equilibrium-real-interest-rate.pdf)
- Uses a Bayesian semi-structural (LW-type) model to confront the "pile-up" problem of maximum-likelihood estimation. Cyclical parameters get N(0,2) priors; trend-shock SD priors have mean 0.25 and SE 0.25.
- "The posterior distribution of the r* process lies very close to its prior." Doubling the prior mean of the SD from 0.25 to 0.5 gives Δposterior/Δprior = **1.00 for r***, versus 0.24 for g and 0.04 for trend unemployment, so "the posterior moves with the prior".
- Conditional on a prior of gradual r* variation, r* declines to 0–1% at end-2017 (about 2% from the early 1960s through the 1980s).
- Kiley is **not** a moving-average paper. Its lesson for robustness is that the trend-variance prior should be reported and varied.

**Hamilton, Harris, Hatzius & West (2016), IMF Economic Review 64(4):660–707** (read, Hutchins WP #16 version) — [JSTOR](https://www.jstor.org/stable/45212125); [WP PDF](https://www.brookings.edu/wp-content/uploads/2016/07/WP16-Hamilton-et-al-equilibrium-real-funds-rate-1.pdf); [NBER w21476](https://www.nber.org/papers/w21476)
- Ex-ante real rates:
  - nominal policy/safe rate minus expected inflation from rolling AR forecasts of inflation;
  - annual data go back up to two centuries across 17 countries including the UK;
  - quarterly data use an AR(4) on a 40-quarter rolling window.
- Moving averages: 40-quarter or 10-year **backward** moving averages serve as "(noisy) measures of the equilibrium rate", "at best a noisy indicator of the theoretical construct".
- Weak growth link: the correlation between 10-year averages of US GDP growth and the real rate is −0.25 in annual data. The cross-country correlation of average growth and average real rates is positive but flips sign if one country (Australia) is dropped.
- Econometrics:
  - They reject that the real rate reverts to a constant; there are Bai–Perron breaks.
  - A "world long-run rate" is built as ℓ_t = median over countries n of b̂_{nt}/(1−ψ̂_{nt}), from AR(1)-ARCH(2) fits on **30-year rolling windows** of each country's ex-ante real rate. This is a robust, simple benchmark.
  - The US rate minus ℓ_t is stationary: r_US − ℓ = −0.174 + 0.935(lag 1) − 0.357(lag 2), with a DF t-stat of −4.89. This gives a VECM with cointegrating vector (1,−1).
  - The VECM forecasts US and world long-run rates settling "around a half a percent within about three years". Confidence intervals widen with horizon because ℓ_t itself is non-stationary. The narrative range is 1–2%.
- Summary: plausible central estimates run "from a little over 0% to the pre-crisis consensus of 2%". Uncertainty argues for more policy inertia.

**Lubik & Matthes (2015), Richmond Fed Economic Brief 15-10** — [EB 15-10](https://www.richmondfed.org/publications/research/economic_brief/2015/eb_15-10); [PDF](https://www.richmondfed.org/-/media/richmondfedorg/publications/research/economic_brief/2015/pdf/eb_15-10.pdf); methodology in [Economic Quarterly 101(4) 2015](https://www.richmondfed.org/-/media/richmondfedorg/publications/research/economic_quarterly/2015/q4/pdf/lubik.pdf); tracker [Richmond Fed r* page](https://www.richmondfed.org/research/national_economy/natural_rate_interest)
- The model is a TVP-VAR with time-varying lag coefficients and stochastic volatility. It is described as imposing fewer theoretical restrictions than LW/HLW and is updated quarterly — [Richmond Fed](https://www.richmondfed.org/research/national_economy/natural_rate_interest)
- 2023 update: the authors restricted parameter variability because of "excessive specification flexibility" and real-time data measurement error after the pandemic. The result is "a less volatile r* series that reflects more closely our prior belief". The 2023Q2 estimate is 2.28% (range 2.28–2.65% across specifications), up from 0.44% in 2020Q2 — [EB 23-32](https://www.richmondfed.org/publications/research/economic_brief/2023/eb_23-32) (via page summary)

**Lunsford & West (2019), "Some evidence on secular drivers of US safe real rates", AEJ: Macro 11(4):113–39** — [AEA](https://www.aeaweb.org/articles?id=10.1257/mac.20180005); [NBER w25288](https://www.nber.org/papers/w25288)
- Low-frequency (long-run) correlations of US safe real rates with 30+ candidate drivers, using annual data mostly 1890–2016.
- Correlations with demographics have the expected signs: positive with labour-force hours growth, negative with the 40–64 population share.
- **Productivity is not positively correlated** with real rates (abstract).

**Bauer & Rudebusch (2020), "Interest rates under falling stars", AER 110(5):1316–54** — [AEA](https://www.aeaweb.org/articles?id=10.1257%2Faer.20171822); [author page](https://www.michaeldbauer.com/publication/falling-stars/); [code/data, openICPSR 115622](https://www.openicpsr.org/openicpsr/project/115622/version/V1/view)
- An arbitrage-free term-structure model with shifting endpoints: the long-run level of rates = r* + π*.
- Time variation in these trends is "crucial for understanding the dynamics of Treasury yields and predicting excess bond returns". It gives more plausible term premia and accurate out-of-sample yield forecasts.
- A replication package is provided.

### Inferences
- For a UK dashboard, Hamilton et al.'s "median of rolling-AR long-run means" and the 10-year backward moving average of the ex-ante real Bank Rate are cheap, transparent benchmarks. They should be labelled as noisy, backward-looking indicators.
- DGGT show formally that moving averages behave like a trend model with an extremely loose prior (1-year horizon) and give very wide implied uncertainty.
- Kiley's result argues for publishing r̄ under 2–3 trend-variance priors (e.g. DGGT's 1/400 versus 4× looser) as a sensitivity fan.
- The Lubik–Matthes post-COVID instability is a warning against unrestricted TVP-VARs on UK 2020–23 data.

### Gaps
- The Lubik–Matthes variable list and r* definition could not be confirmed from a fetched primary source; the Richmond Fed summary did not list variables. From memory, it uses real GDP growth, PCE inflation and a real short rate, with r* defined as a long-horizon conditional forecast of the real rate; **unverified**.
- The components of Bauer–Rudebusch's r* proxy could not be confirmed. From memory it is an average of several published r* estimates, with the Fed's perceived target rate (PTR) as π*; **unverified**. Han & Ma (2023), below, confirm the use of PTR for π* "following Bauer and Rudebusch (2020)".
- No formal forecast horse-race of moving averages versus UC models for r* itself was found. r* is unobserved, so evaluations are of real-rate or yield forecasts. JM's repo includes comparisons against a random walk, SPF and Wu–Xia, but results were not extracted.

---

## 4. Simple robust benchmarks (moving averages, local-level UC with survey expectations) and forecasting comparisons

### Takeaway
The simplest defensible UK benchmarks are:
- **(a) a 10-year (40-quarter) one-sided moving average of the ex-ante real Bank Rate**, using survey or model-based expected inflation (Hamilton et al.);
- **(b) a rolling-window long-run mean from an AR(1)**, possibly as a cross-country median (Hamilton et al.'s ℓ_t);
- **(c) a local-level UC model** of the real rate, or of nominal short and long rates less survey inflation expectations, with a tight trend-variance prior (a stripped-down DGGT).

Moving averages mix cycle into trend (DGGT). UC models with tight priors are smoother but prior-driven (Kiley).

### Cited Findings
- Hamilton et al. use 40-quarter/10-year backward averages as a "noisy indicator". Ex-ante inflation comes from rolling AR forecasts; alternative expectation measures give a 0.98 correlation — [Hutchins WP #16](https://www.brookings.edu/wp-content/uploads/2016/07/WP16-Hamilton-et-al-equilibrium-real-funds-rate-1.pdf)
- DGGT: "unlike moving averages, our trend-cycle decomposition attributes much of the decline in rates in the interwar period to cyclical fluctuations … decadal moving averages conflate trends with cyclical variations". The cross-country average of moving averages "rises to almost 5 percent in the 1980s" and falls lower than today around the World Wars — [NBER WP 25039](https://www.nber.org/system/files/working_papers/w25039/w25039.pdf)
- A local-level UC for inflation with surveys (π_t = π̄_t + π̃_t; π^e_t = π̄_t + π̃^e_t) is exactly the DGGT BPEA inflation block, following Stock–Watson (1999) — [BPEA](https://www.brookings.edu/wp-content/uploads/2017/08/delnegrotextsp17bpea.pdf)
- JM: forecasts are "competitive"; the repo has random-walk and SPF comparisons — [BIS WP 715](https://www.bis.org/publ/work715.pdf); [GitHub](https://github.com/elmarmertens/JohannsenMertensJMCBtimeseriesELB)
- Han & Ma (2023) report their shifting-endpoint shadow-rate term-structure model gives "better yield forecasts than existing models" for the US, UK and Germany — [Han & Ma WP](https://economics.ucr.edu/wp-content/uploads/2023/05/5-26-Ma.pdf)

### Inferences
- **Suggested UK benchmark set (all Python, free data):**
  1. 10-year one-sided MA of (Bank Rate − 1-year-ahead expected CPI inflation). Expected inflation can come from BoE/Ipsos 1-year expectations or an AR forecast.
  2. 10-year one-sided MA of the 10-year real gilt yield from the BoE real GLC curve, or of the 5y5y real forward.
  3. A local-level UC: (Bank Rate, 10-year nominal gilt, CPI, long-run inflation expectation) → trends r̄, π̄, tp̄, estimated with DGGT priors and the ELB period set to missing. This is feasible in statsmodels `UnobservedComponents`/`MLEModel`, or with a small Gibbs sampler.
- Because r* is unobservable, "forecasting performance" should be judged on out-of-sample forecasts of real rates and yields at 5–10-year horizons, and on revision size (section 5).

### Gaps
- I found no published, systematic out-of-sample comparison of MA benchmarks versus UC/VAR r* for the UK.
- Kiley (2020) does not contain an MA-versus-model forecasting comparison; the brief's premise that it does appears incorrect based on my reading.

---

## 5. Real-time versus smoothed reliability, revisions, and recommended uncertainty bands

### Takeaway
All sources agree the **level** of the trend is highly uncertain while **changes over decades** can be precisely estimated. JM report both quasi-real-time (filtered) and smoothed r̄, and the qualitative picture is the same. Tight-prior trend models (DGGT, JM) are much less revision-prone than MA or loose-prior models, by construction. Recommended practice is to show 68% and 90/95% posterior bands, filtered alongside smoothed estimates, and prior sensitivity.

### Cited Findings
- DGGT: "the uncertainty on the level of the trend at any point in time is large … However, the decline over the past few decades is statistically significant". They report 68% and 95% bands and 90% bands on changes — [NBER WP 25039](https://www.nber.org/system/files/working_papers/w25039/w25039.pdf)
- DGGT BPEA: bands narrow when survey short-rate expectations enter and widen again when the short rate is dropped at the ZLB, so survey and long-rate observables are key to precision — [BPEA](https://www.brookings.edu/wp-content/uploads/2017/08/delnegrotextsp17bpea.pdf)
- JM: "quasi real-time estimates … conditioned solely on data through period t" versus smoothed. Bands are wide in both, and the downward trend is visible in both before the GFC — [FEDS 2016-033](https://www.federalreserve.gov/econresdata/feds/2016/files/2016033pap.pdf)
- Kiley: the posterior of the r* variance equals the prior, so the amount of time variation, and hence the revision behaviour, is prior-determined — [IJCB](https://www.ijcb.org/sites/default/files/journal/v16n3/ijcb-v16n3-what-can-data-tell-us-about-equilibrium-real-interest-rate.pdf)
- Hamilton et al.: forecast confidence intervals for the long-run rate are 1–2pp wide within two years and widen further at longer horizons — [Hutchins WP #16](https://www.brookings.edu/wp-content/uploads/2016/07/WP16-Hamilton-et-al-equilibrium-real-funds-rate-1.pdf)
- Lubik–Matthes had to re-specify in 2023 because real-time measurement error and flexible parameters produced volatile r* — [EB 23-32](https://www.richmondfed.org/publications/research/economic_brief/2023/eb_23-32)

### Inferences
- Dashboard recommendations:
  - Plot the filtered (one-sided) estimate as the headline, since it is what was knowable in real time, and overlay the smoothed estimate.
  - Show 68% and 90% bands.
  - Report the change since, e.g., 1998 or 2007 with its band, because changes are better identified than levels.
  - Include a "prior sensitivity" toggle for the trend variance.
- Track vintages: store each quarterly run's filtered path to measure revisions empirically.

### Gaps
- No quantified revision statistics (e.g. mean absolute revision of r̄ between real-time and final) were found for DGGT or JM. The literature quantifying HLW revisions is outside this scope.

---

## 6. UK applications, and code availability (Python/R/Matlab)

### Takeaway
UK-specific work is thin:
- DGGT (2019) estimate a UK trend within the global model (annual, to 2016).
- Han & Ma (2023; later JMCB) estimate a UK real-rate trend from a shadow-rate shifting-endpoint term-structure model on BoE forward rates, 1983–2022.
- A 2025 *Economica* paper, "Longer-run equilibrium interest rates: evidence from the United Kingdom" (Kaykhusraw), exists, but I could not access it.

All public code for the key models is **Matlab or Fortran**; I found no Python implementations. DGGT is the easiest to port.

### Cited Findings
- **Han & Ma (2023 WP)**, "Estimating the interest rate trend in a shadow rate term structure model" — [WP PDF](https://economics.ucr.edu/wp-content/uploads/2023/05/5-26-Ma.pdf); published in [JMCB](https://onlinelibrary.wiley.com/doi/10.1111/jmcb.70004) (read, WP)
  - UK data: BoE forward rates at 1–10-year maturities (sub-1-year dropped for liquidity reasons) and OECD core CPI, January 1983 to March 2022.
  - The UK ELB is fixed at **0**, following Andreasen & Meldrum (2015).
  - π* is the UK inflation target: 2.5% for 1998–2003 and 2% from 2004, treated as missing before 1998.
  - Results:
    - The UK shadow rate was below zero from 2009 to the end of 2017, fell below zero again in COVID, and turned positive at the end of 2021.
    - The UK real-rate trend "climbed to around 10% in the early 90s" and then "declined persistently". It "did not fall below zero until the end of 2014" and stayed negative post-GFC.
    - It co-moves with the US and Germany, and the US trend explains much UK variation (Cholesky VAR).
  - The inflation trend is extracted with a DGGT/JM-style trend-cycle model (per the paper).
- **Kaykhusraw (2025)**, *Economica*, "Longer-run equilibrium interest rates: evidence from the United Kingdom" — [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/ecca.12566) (access blocked, 403; content unknown)
- UK LW-type application: search snippets describe a UK Laubach–Williams application finding large declines in trend growth and r* over 25 years. The primary source was not identified here, so this belongs to the HLW workstream.
- BoE working papers on UK real-rate drivers:
  - [SWP 701 Demographic trends and the real interest rate](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2017/demographic-trends-and-the-real-interest-rate.pd)
  - [SWP 845 Eight centuries of global real interest rates](https://www.bankofengland.co.uk/working-paper/2020/eight-centuries-of-global-real-interest-rates-r-g-and-the-suprasecular-decline-1311-2018)
  - [SWP 837 UK house prices and the decline in the risk-free real rate](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2019/uk-house-prices-and-three-decades-of-decline-in-the-risk-free-real-interest-rate.pdf)
  - BoE real/nominal yield-curve methodology: [WP 126](https://wwwtest.bankofengland.co.uk/working-paper/2001/new-estimates-of-the-uk-real-and-nominal-yield-curves)
- **Code inventory:**

  | Model | Repo | Language | Licence |
  |---|---|---|---|
  | DGGT global (incl. UK) | [FRBNY-TimeSeriesAnalysis/rstarGlobal](https://github.com/FRBNY-TimeSeriesAnalysis/rstarGlobal) | Matlab | BSD-3 |
  | DGGT BPEA (US, surveys) | [FRBNY-DSGE/rstarBrookings2017](https://github.com/FRBNY-DSGE/rstarBrookings2017) | Matlab | (not checked) |
  | Johannsen–Mertens | [elmarmertens/JohannsenMertensJMCBtimeseriesELB](https://github.com/elmarmertens/JohannsenMertensJMCBtimeseriesELB) | Fortran + Matlab + R | none stated |
  | Bauer–Rudebusch | [openICPSR 115622](https://www.openicpsr.org/openicpsr/project/115622/version/V1/view) | (not checked) | AEA |
  | Shadow-rate VAR toolkit (related) | [shawcharles/srvar-toolkit](https://github.com/shawcharles/srvar-toolkit) | (appears Python; not verified) | — |

### Inferences
- **Recommendation for a small team (Python, free UK data):**
  1. **Primary complement to HLW: a UK DGGT-BPEA-style trend-cycle VAR.**
     - Observables: Bank Rate or 3-month rate treated as missing at the ELB; the 10-year and/or 20-year nominal GLC yield; CPI; a long-run inflation-expectations proxy; optionally the 10-year real GLC yield.
     - Priors: DGGT's (trend variance 1/400 quarterly, κ = 100, Minnesota 0.2).
     - Implementation: about 300–500 lines of numpy (Durbin–Koopman simulation smoother plus conjugate draws).
     - Optionally add US and euro-area blocks with a common world trend, following DGGT 2019, to sharpen UK identification.
  2. **Second: a JM-style shadow-rate UC**, or simply augment (1) with a censored shadow short rate using the JM rejection step and a time-varying UK ELB (0.5/0.25/0.1). Include stochastic volatility in the gaps if resources allow; JM show SV plus the ELB treatment keep r̄ from being dragged down post-GFC.
  3. **Always show benchmarks:** a 10-year one-sided MA of the ex-ante real Bank Rate, a 10-year real gilt MA, and a Hamilton-style rolling-AR long-run mean.
- **Free UK data sources** (URLs not re-verified in this session):
  - BoE Database: Bank Rate and SONIA;
  - BoE yield curves (nominal, real and implied inflation GLC; daily from 1979/1985);
  - ONS CPI/CPIH;
  - BoE/Ipsos Inflation Attitudes Survey (quarterly, 5-year-ahead from 2009);
  - HMT "Forecasts for the UK economy" (medium-term CPI);
  - JST Macrohistory for long annual history.

### Gaps
- The Kaykhusraw (2025) *Economica* methods and results were inaccessible (HTTP 403).
- The DGGT UK trend values were not extracted numerically.
- I found no UK-specific survey of long-run expected short rates comparable to the SPF 10-year T-bill forecast. Whether the BoE Market Participants Survey provides a long-horizon Bank Rate expectation with a usable history was not verified.
- No Python implementations of DGGT or JM were found. The srvar-toolkit language and content were not checked.
- Coverage through September 2026: no 2024–26 updates of the DGGT or JM UK or global estimates were found.
