# Estimating pass-through of external cost-push shocks into UK inflation (first vs second round): methods, identification, data

Research notes compiled 29 Sep 2026. Scope: specifications, identification, data needs, coefficient sizes, and recommendations for a small, reproducible, daily-rerunnable Python pipeline on free UK data (ONS, BoE, FRED, OECD). PDFs of the key papers were downloaded and text-extracted, so the coefficients below are quoted from the papers themselves unless marked otherwise.

Terminology used throughout:
- **First round (direct):** the mechanical effect of energy, food or import prices on the CPI through their basket weights.
- **Indirect first round:** pass-through via firms' input costs into core goods and services.
- **Second round:** wages, inflation expectations and markups responding to the higher price level (the "battle of mark-ups"). This is what persists.

---

## 1. Phillips curves augmented with import, energy and food prices (Gordon triangle; Ball-Mazumder; Ball-Leigh-Mishra; BoE practice)

### Takeaway
Two families of cost-push term dominate.
- **Relative-price growth terms (Gordon, Bernanke-Blanchard).** Energy, food or import inflation minus a numeraire (core inflation, headline inflation or wages) enters a backward-looking Phillips curve with long lags.
- **"Headline minus core" shocks (Ball-Leigh-Mishra).** Headline minus weighted-median inflation, averaged over 12 months, enters a core-inflation-gap equation. It is nonlinear and asymmetric: pass-through is large for positive shocks and negligible for negative ones.

For the UK, BoE staff found that separate non-energy, non-food import-price terms add little once relative energy and food are included, because they are collinear with food and with sterling.

### Cited Findings

**Gordon triangle model**
- Specification: p_t = a(L)p_{t-1} + b(L)(U_t − U^N_t) + c(L)z_t + e_t, with a time-varying NAIRU U^N_t = U^N_{t-1} + η_t. [Gordon 2013, NBER WP 19390](https://www.nber.org/system/files/working_papers/w19390/w19390.pdf)
  - The constant is suppressed, and the lagged-inflation coefficients are constrained to sum to 1 so that a "natural rate" exists.
  - Long lags on inflation (the paper's Table 1 uses up to 24 quarters).
- Supply-shock vector z_t:
  - relative food-energy: headline PCE inflation minus core PCE inflation;
  - relative import prices: non-food non-oil import deflator inflation minus the dependent-variable inflation;
  - 8-quarter change in trend productivity (HP filter, λ=6400);
  - Nixon price-control dummies. — [Gordon 2013](https://www.nber.org/system/files/working_papers/w19390/w19390.pdf)
- The food-energy coefficient has fallen over time. It is allowed to change between halves of the sample, following Blanchard & Galí (2010). [Gordon 2013](https://www.nber.org/system/files/working_papers/w19390/w19390.pdf)
  - In the core-inflation equation it averages 0.62 for regressions starting in 1962–75 and 0.43 for regressions starting in 1976–83.
  - The net food-energy coefficient is 0.25 for samples ending 1996, 0.16 ending 2006 and 0.08 ending 2013.
- Unemployment-gap slope ≈ −0.5 in the triangle version, against ≈ −0.1 to −0.2 in NKPC versions. [Gordon 2013](https://www.nber.org/system/files/working_papers/w19390/w19390.pdf)

**Ball, Leigh & Mishra (2022), Brookings Papers on Economic Activity / NBER WP 30613 / IMF WP 2022/208**
- Headline = core + headline shocks. Core is the Cleveland Fed weighted-median CPI, and H = headline minus median. [NBER w30613](https://www.nber.org/system/files/working_papers/w30613/w30613.pdf)
- Core equation: (median inflation − 10-year SPF expected inflation) = f(V/U) + g(H), where V/U and H are 12-month (or 4-quarter) averages and f and g are cubic polynomials. [NBER w30613](https://www.nber.org/system/files/working_papers/w30613/w30613.pdf)
  - Long-run expectations enter with a coefficient of 1.
- Table 1, monthly data 1985–2022, Newey-West standard errors. [NBER w30613](https://www.nber.org/system/files/working_papers/w30613/w30613.pdf)
  - V/U 9.140, V/U² −10.328, V/U³ 4.241.
  - H 0.058 (not significant), H² 0.089\*\*\*, H³ 0.031\*\*.
  - Constant −2.654; R² 0.575.
  - The pre-pandemic quarterly sample (1985–2019) gives H² 0.155 and H³ 0.054.
- Pass-through of headline shocks is asymmetric: "negligible for shocks that reduce headline inflation but strong for shocks that increase headline inflation." [NBER w30613](https://www.nber.org/system/files/working_papers/w30613/w30613.pdf)
- With core measured as ex-food-and-energy (XFE), they "find almost no evidence of a pass-through from past headline shocks". The weighted median is critical. [NBER w30613](https://www.nber.org/system/files/working_papers/w30613/w30613.pdf)
- Headline shocks are themselves explained by three terms. [NBER w30613](https://www.nber.org/system/files/working_papers/w30613/w30613.pdf)
  - Energy price inflation minus median (adjusted R² 0.646 alone).
  - IHS Markit backlogs of orders. This is licensed data; a free UK proxy would be needed.
  - Auto-price shocks.
  - The decomposition splits H into energy, backlogs, autos and a residual using the headline-shock regression coefficients.

**Bernanke-Blanchard UK application (Haskel, Martin & Brandt 2023, BoE)**
- Energy and food enter relative to wages. [Haskel, Martin & Brandt 2023](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/november/recent-uk-inflation-an-application-of-the-bernanke-blanchard-model-paper.pdf)
  - grpe = q/q annualised log growth of (CPI energy / wages).
  - grpf = the same for CPI food and non-alcoholic beverages.
  - Energy and food are expressed relative to wages "to avoid inflation being on both sides of the equation."
- On adding import prices (section 6.2): trialled non-energy non-food import prices, CPI–GVA and CPI–GDP deflator wedges, and the sterling exchange rate. [Haskel, Martin & Brandt 2023](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/november/recent-uk-inflation-an-application-of-the-bernanke-blanchard-model-paper.pdf)
  - All improved fit slightly, and contemporaneous coefficients were significant.
  - Sums of coefficients were insignificant.
  - Relative non-energy non-food import prices co-move with relative food prices, "we cannot disentangle their effects sufficiently precisely."
- A useful benchmark: long-run energy and food coefficients should be close to the CPI basket shares if there are no indirect effects. Coefficients above the shares imply indirect or second-round effects. [Haskel, Martin & Brandt 2023](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/november/recent-uk-inflation-an-application-of-the-bernanke-blanchard-model-paper.pdf)

**Current BoE toolkit, as described in Greene (2 June 2026)**
- **Energy BVAR (Copeland et al. 2025).** Oil supply shocks have "more immediate but short-lived effects on UK inflation", while gas supply shocks have "broader and more persistent effects". [Greene speech, 2 Jun 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)
- **Instruments and restrictions.** The Bank's energy BVAR uses Känzig (2021) oil supply shocks and Alessandri & Gazzani (2025) gas supply shocks as proxies, combined with zero and sign restrictions (Arias et al. 2021). [BoE-related search summary; see Greene speech and MPRs](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)
  - Only the Känzig part is confirmed in the speech's Figure 5 notes. The Alessandri-Gazzani detail comes from a search snippet and should be verified.
- **Boosted Inflation Model (BIM; Buckmann, Potjagailo & Schnattinger 2025, SWP 1,143).** A machine-learning decomposition whose "trend" block (expectations, past services inflation, wage growth) is used to approximate second-round effects. [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf); [SWP 1,143](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2025/blockwise-boosted-inflation-non-linear-determinants-of-inflation-using-machine-learning.pdf)
- **Phillips-curve convexity (BoE SWP 1,107, Oct 2025).** Across 38 countries over 1990–2024, the Phillips-curve slope is about 0.34 for positive output gaps against 0.12 for negative gaps. [BoE SWP 1,107 "How curvy is the Phillips curve?"](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2025/how-curvy-is-the-phillips-curve.pdf)

### Inferences
- **Recommended cost-push terms on UK data**, all free from ONS. For a dashboard, (a) and (b) are the most transparent.
  - (a) Relative energy CPI inflation (energy index / AWE, or energy minus core), q/q annualised.
  - (b) Relative food CPI inflation, constructed the same way.
  - (c) An optional BLM-style H_t = headline CPI − UK weighted-median or trimmed-mean CPI. This can be computed from ONS CPI item or class indices and weights. The ONS does not publish a weighted median to my knowledge, so it must be built.
  - (d) Non-energy import prices would add little over (a) and (b), per the Haskel-Martin-Brandt finding.
- **Weighting a cost-push term in a pressure score:** use the long-run multiplier Σβ_k / (1 − Σα_k) from the price equation as the weight on the 4-quarter moving sum of the relative-price term.
  - For the UK BB estimates that is 0.02 (energy) and 0.44 (food) on relative-to-wage growth.
  - Alternatively, use share-weighted direct effects plus the estimated excess over the share as the "indirect/second-round" component.
- **Headline-shock pass-through should be nonlinear and asymmetric.** A linear pressure score will understate pass-through in big upswings and overstate it in downswings.
  - Implement with max(H,0), or H and H² terms, as in BLM.

### Gaps
- I did not retrieve Ball & Mazumder (2019, "A Phillips Curve with Anchored Expectations and Short-Term Unemployment", JMCB) or Ball & Mazumder (2021, euro-area Phillips curve) text in this session. Their median-CPI plus anchored-expectations specifications are the precursor to BLM (2022), but no coefficients were verified here.
- I found no recent public BoE staff Phillips curve paper (2024–26) with explicit import-price coefficients. BoE MPR boxes use suites of models whose coefficients are rarely published.
- No official UK weighted-median CPI series was found. This needs verifying on the ONS site; the ONS may have experimental measures.

---

## 2. Bernanke & Blanchard (2023) and the 11-economy project, including the UK chapter

### Takeaway
- **Model.** Four equations (wage, price, 1-year expectations, long-run expectations), estimated by OLS with homogeneity restrictions on quarterly data. It is easy to replicate in Python with statsmodels.
- **UK chapter.** Written by Jonathan Haskel, Josh Martin and Lennart Brandt (BoE, November 2023), estimated on 1990Q1–2023Q2.
- **UK results.** 2021 inflation was driven by energy (1.6pp of 4.8% q/q annualised; 33%) and shortages (1.3pp; 27%). Food and V/U mattered more in 2022–23. The UK looked to be overheating before COVID.
- **Code.** A replication package for the 11-economy paper is on PIIE.

### Cited Findings
- **Paper and authors.** "An Analysis of Pandemic-Era Inflation in 11 Economies", Bernanke & Blanchard, NBER WP 32532 / PIIE WP 24-11 / Hutchins Center WP 91 (May 2024). [NBER](https://www.nber.org/papers/w32532); [PIIE](https://www.piie.com/publications/working-papers/2024/analysis-pandemic-era-inflation-11-economies); [Brookings PDF](https://www.brookings.edu/wp-content/uploads/2024/05/WP91_Bernanke-Blanchard.pdf)
  - Built with 10 central banks (Belgium, Canada, France, Germany, Italy, Japan, Netherlands, Spain, UK and the ECB), plus the US.
  - The UK team was Haskel, Martin & Brandt. [Brookings summary](https://www.brookings.edu/articles/an-analysis-of-pandemic-era-inflation-in-11-economies/)
- **Replication package:** https://www.piie.com/sites/default/files/2024-05/wp24-11.zip (stated on the paper's front page). [NBER w32532 PDF](https://www.nber.org/system/files/working_papers/w32532/w32532.pdf)
  - An independent replication of the US BB (2023) paper is on Zenodo. [Zenodo 20272539](https://zenodo.org/records/20272539)
- **Cross-country conclusion.** Pandemic-era inflation came mainly from supply disruptions and food and energy price rises, but these effects "have not been persistent, in part due to the credibility of central bank inflation targets". Tight labour markets became relatively more important later. [NBER w32532](https://www.nber.org/system/files/working_papers/w32532/w32532.pdf)
  - The estimated effect of energy and food shocks, including lags, "is only slightly larger than the share of energy or food" in the CPI, i.e. weak price-price feedback.
- **The UK was already overheating in 2019Q4.** "The main exception is the United Kingdom, where the effect on inflation of the initial conditions increases, suggesting that the UK economy was already overheating to some degree in 2019Q4." [NBER w32532](https://www.nber.org/system/files/working_papers/w32532/w32532.pdf)
- **Energy contributions varied with subsidies.** Summed energy contributions in the first three quarters of 2022 were 5.6pp for France, 12.1pp for Germany and 9.9pp for Italy, with the differences reflecting energy subsidies and caps. [NBER w32532](https://www.nber.org/system/files/working_papers/w32532/w32532.pdf) This is relevant to the UK Energy Price Guarantee and Ofgem cap timing.

**UK chapter equations (Haskel, Martin & Brandt 2023)**
- All growth rates are q/q annualised log changes, with 4 lags.
- Homogeneity is imposed: coefficients on the endogenous variables sum to 1 in each equation.
- 2020Q2 and 2020Q3 dummies are included.
- Source for everything in this block: [Haskel, Martin & Brandt 2023](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/november/recent-uk-inflation-an-application-of-the-bernanke-blanchard-model-paper.pdf)

The four equations:
- Wage: gw_t = Σ_{1..4} gw_{t-k} + Σ_{1..4} iesr_{t-k} + Σ_{1..4} vu_{t-k} + Σ_{1..4} catchup_{t-k} + gpty_{t-1} + u
- Price (eq. 11): gp_t = Σ_{1..4} gp_{t-k} + Σ_{0..4} gw_{t-k} + Σ_{0..4} grpe_{t-k} + Σ_{0..4} grpf_{t-k} + Σ_{0..4} shortage_{t-k} + gpty_{t-1} + u
- Short-run expectations (eq. 12): iesr_t = Σ_{1..4} iesr + Σ_{0..4} ielr + Σ_{0..4} gp + u
- Long-run expectations (eq. 13): ielr_t = Σ_{1..4} ielr + Σ_{0..4} gp + u

UK data used:
- CPI (seasonally adjusted by the authors).
- CPI food and non-alcoholic beverages.
- CPI energy (electricity, gas, vehicle fuels).
- AWE private-sector regular pay, adjusted for furlough and composition. The adjustment is a BoE staff series, not public.
- V/U: ONS vacancies from 2000, spliced to Jobcentre vacancies before 2000, over unemployment aged 16+.
- Shortages: Google Trends "shortage" for the UK. The GSCPI was also considered.
- Composite 1-year and long-run expectations from households, professional forecasters and markets.
- Catch-up = annual inflation − 1-year expectations from a year earlier.

UK coefficient sums, 1990Q1–2023Q2, 134 observations:

| Equation | Coefficient sums | Fit | Long-run effect |
|---|---|---|---|
| Wage | lagged gw 0.602; V/U 2.364 (p=0.016); catch-up 0.088 (n.s.); iesr 0.398; productivity 0.210 | R² 0.597 | V/U +0.5 raises wage growth by 0.5×2.364/(1−0.602) = 3.0pp |
| Price | lagged gp 0.703; gw 0.297; energy 0.005 (sum n.s., jointly significant); food 0.131 (p=0.013); shortage 0.036; productivity −0.221 | R² 0.888 | Energy 0.018, food 0.441 |
| 1-year expectations | own lags 0.841; ielr 0.143; gp 0.015 (contemporaneous gp 0.07) | R² 0.831 | — |

- Contemporaneous price-equation coefficients are energy 0.08 and food 0.18, close to the CPI basket shares.
- **UK vs US comparison** (the US figures are as reported in the same paper):
  - Price equation: wage coefficient 0.30 (US 0.67); inflation persistence 0.70 (US 0.34).
  - Long-run energy effect 0.02 (US 0.09); long-run food effect 0.44 (US 0.19).
  - Shortage sum 0.04 (US 0.03).
  - Wage elasticity to V/U at the mean: short-run 0.81 (US 0.40), long-run 2.04 (US 0.75).
- **Impulse responses:**
  - A 1 SD pre-pandemic food shock adds about 0.3pp to annual inflation at 4 quarters and about 0.05pp after 4 years.
  - A shortage shock peaks at 0.04pp.
  - A 1 SD (0.27) permanent rise in V/U raises inflation about 1.7pp after 4 years.
- **Decomposition:**
  - 2021: energy 1.6pp (33%) and shortages 1.3pp (27%) of 4.8% q/q annualised CPI.
  - 2022: energy was lumpy, driven by the April 2022 Ofgem cap rise; food mattered from 2022Q3; V/U grew in importance.
  - H1 2023: energy turned negative.
  - The V/U contribution over 2022–2023H1 is 0.5pp in the baseline, with a plausible range of 0.5–1.8pp depending on initial conditions.
  - V/U contributed 1.6pp to wage growth in 2022; energy and shortages contributed about 1pp to wages via expectations and catch-up.

### Inferences
- **The UK BB model is the most directly usable "first vs second round" framework.** Direct effects come through grpe and grpf in the price equation. Second-round effects come through gw, catch-up and expectations.
- **Implementation risks for a public dashboard:**
  - The furlough- and composition-adjusted AWE is a BoE staff series. Use raw ONS AWE private regular pay plus dummies instead.
  - The composite expectations series needs to be assembled from free sources: BoE/Ipsos Inflation Attitudes Survey (quarterly), market breakevens (BoE yield-curve data) and the BoE Survey of External Forecasters. This is the hardest free-data step.
  - Google Trends has no official API. pytrends is unofficial, rate-limited and re-normalised on each query, so it is not robust for daily automation. Consider the NY Fed GSCPI (free download) or dropping shortages.
- **Very small UK energy coefficient.** The Ofgem cap creates lagged, lumpy energy CPI changes, so an energy term with longer lags or cap-announcement timing may be needed.
- **Re-estimation cadence.** The model is quarterly. Re-running daily only changes results when ONS releases land, so re-estimation can be event-triggered while the dashboard refreshes daily.

### Gaps
- I did not open the BB (2023) US paper (NBER WP 31417) directly. The US coefficients above come from the UK paper's comparison text.
- I did not confirm the contents of the PIIE replication zip (e.g. whether UK data or only code is included, and which software: likely EViews or Stata, unverified).
- I found no published UK update after 2023Q2, and no BoE-published Python code. The BB model is also used in the BoJ (WP 24-E-1) and ECB (Occasional Paper 343) applications. [BoJ](https://www.boj.or.jp/en/research/wps_rev/wps_2024/data/wp24e01.pdf); [ECB OP 343](https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op343~ab3e870d21.en.pdf)

---

## 3. Local projections vs VARs for energy/oil pass-through to headline and core

### Takeaway
- **Standard approach:** use LPs (Jordà 2005) of CPI, core CPI, wages and expectations on an external shock series (LP-IV or a shock-as-regressor LP). Both are straightforward in Python.
- **The LP vs VAR trade-off.** In population, LPs and VARs estimate the same impulse responses (Plagborg-Møller & Wolf 2021). In finite samples LPs have lower bias but much higher variance at medium and long horizons (Li, Plagborg-Møller & Wolf 2024). Shrinkage (BVAR or penalised/smoothed LP) is recommended unless bias is the overriding concern.
- **Recent magnitudes.** A euro-area gas supply shock that raises gas prices 10% lifts headline HICP about 0.6pp after a year, and about 75% of the cumulative 3-year effect is indirect.

### Cited Findings
- **Li, Plagborg-Møller & Wolf (2024)**, "Local projections vs. VARs: Lessons from thousands of DGPs", Journal of Econometrics 244(2), 105722. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S030440762400068X); [NBER w30207](https://www.nber.org/papers/w30207)
  - LP estimators have lower bias than VARs but substantially higher variance at intermediate and long horizons.
  - "Unless researchers are overwhelmingly concerned with bias, shrinkage via Bayesian VARs or penalized LPs is attractive."
- **Primer.** Montiel Olea, Plagborg-Møller, Qian & Wolf (2025), "Local Projections or VARs? A Primer for Macroeconomists", NBER WP 33871. [arXiv 2503.17144](https://arxiv.org/pdf/2503.17144); [RePEc](https://ideas.repec.org/p/nbr/nberwo/33871.html)
- **ECB WP 2968 (López, Odendahl, Párraga Rodríguez & Silgado-Gómez; revised March 2026):** BSVAR on January 1997–December 2024. [ECB WP 2968](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2968~e514c92723.en.pdf)
  - A gas supply shock that raises gas prices 10% raises euro-area headline inflation about 0.6pp after a year.
  - Känzig (2021) oil supply news shocks enter as exogenous controls.
  - A companion instrument uses daily changes in 1-month TTF futures.
  - The NK-DSGE part attributes about 75% of the 3-year cumulative headline response to indirect effects.
- **Oil vs gas shocks.** Oil supply shocks have immediate but short-lived effects and gas supply shocks broader and more persistent ones. Pass-through is stronger when energy or core inflation is elevated. [CEPR VoxEU](https://cepr.org/voxeu/columns/different-effects-oil-and-gas-supply-shocks-euro-area-inflation); [ScienceDirect: Gas price shocks and euro area inflation](https://www.sciencedirect.com/science/article/abs/pii/S0261560624001700)
  - These are search-snippet summaries; the full text was not read.
- **Känzig, Stock & Zanotti (BPEA conference draft, 24–25 Sep 2026), "From Importer to Exporter: Oil Shocks and the U.S. Economy".** [Brookings PDF](https://www.brookings.edu/wp-content/uploads/2026/09/1_KanzigStockZanotti.pdf)
  - Uses OPEC-announcement oil supply news shocks in a time-varying model plus state-dependent LPs.
  - The US contractionary effects of oil shocks have weakened, and even become expansionary, as the US became a net exporter.
  - Relevance for the UK: effects depend on energy trade position, and the UK is a net energy importer, especially of gas.
- **Canonical references** (bibliographic details from standard citations; full texts not fetched in this session):
  - Jordà (2005), "Estimation and Inference of Impulse Responses by Local Projections", AER 95(1):161–182. https://doi.org/10.1257/0002828053828518
  - Plagborg-Møller & Wolf (2021), "Local Projections and VARs Estimate the Same Impulse Responses", Econometrica 89(2):955–980. https://doi.org/10.3982/ECTA17813

### Inferences
- **Recommended UK LP specification** (monthly):
  - π^{x}_{t+h} − π^{x}_{t−1} (or cumulative log price change p_{t+h} − p_{t−1}) = α_h + β_h·shock_t + Σ_{j=1..12} γ_j'X_{t−j} + ε_{t+h}, for h = 0..36.
  - x ∈ {CPI, CPI energy, CPI ex-energy-food-alcohol-tobacco (core), services, AWE}.
  - X includes lags of the shock, Brent in sterling, the sterling ERI, the unemployment rate and the dependent variable.
  - Use Newey-West or Eicker-Huber-White standard errors with lag augmentation.
  - Normalise to a 10% rise in the sterling oil price (LP-IV: instrument Δlog oil price with the Känzig shock).
- **First vs second round:** read direct effects off the CPI-energy response times its weight. Indirect and second-round effects are the core and services and wage responses at h=12–36.
- **Variance at long horizons.** Given LP variance at long horizons on about 30 years of UK monthly data, report smoothed LP or BVAR as the headline estimate and raw LP as a robustness check.

### Gaps
- I found no published UK-specific LP study of oil or gas shock pass-through to core CPI with public code. The BoE's Copeland et al. (2025) energy BVAR is referenced but its publication and code status was not confirmed.

---

## 4. External instruments: Känzig (2021), Baumeister-Hamilton (2019), Kilian (2009)

### Takeaway
All three are free.
- **Känzig oil supply news shock:** updated about every 6 months on GitHub (latest vintage 2025M12, 4–5 month lag). Good for LP-IV but not a real-time daily input.
- **Baumeister-Hamilton supply and demand shocks:** updated on Christiane Baumeister's site (coverage 1975M2–2026M3).
- **Kilian (2009):** can be self-computed from free data.
- **Where BoE uses them:** the Känzig series is used directly in current BoE UK work (the threshold BVAR in Greene 2026).

### Cited Findings
- **Känzig (2021)**, "The Macroeconomic Effects of Oil Supply News: Evidence from OPEC Announcements", AER 111(4):1092–1125. [AEA](https://www.aeaweb.org/articles?id=10.1257%2Faer.20190964)
  - Identified from oil futures price changes around OPEC announcements.
  - Negative supply news raises oil prices, lowers production, raises prices and inflation expectations, and appreciates the dollar.
  - Replication package: https://doi.org/10.3886/E122886V1 ([AEA page](https://www.aeaweb.org/articles?id=10.1257%2Faer.20190964)).
  - Code: [github.com/dkaenzig/replicationOilSupplyNews](https://github.com/dkaenzig/replicationOilSupplyNews)
- **Känzig shock series** at [github.com/dkaenzig/oilsupplynews](https://github.com/dkaenzig/oilsupplynews):
  - Vintages from 2017 to 2025, latest `oilSupplyNewsShocks_2025M12.xlsx`, naming pattern `oilSupplyNewsShocks_yyyyMmm.xlsx`.
  - Four sheets: daily surprises, monthly surprises plus VAR-based shocks, and pre-COVID versions of each.
  - "Updated approximately every six months", with a 4–5 month delay. Licensed CC-BY 4.0.
  - Data page: [diegokaenzig.com/data](https://www.diegokaenzig.com/data)
- **Baumeister & Hamilton (2019, AER)**, "Structural Interpretation of VARs with Incomplete Identification: Revisiting the Role of Oil Supply and Demand Shocks". [Baumeister datasets page](https://sites.google.com/site/cjsbaumeister/datasets); [NBER w24167](https://www.nber.org/papers/w24167)
  - Monthly structural oil supply and demand shocks, coverage 1975M2–2026M3, as Google Drive direct downloads:
    - supply: https://drive.google.com/uc?export=download&id=1OsA8btgm2rmDucUFngiLkwv4uywTDmya
    - demand: https://drive.google.com/uc?export=download&id=1neFXLrIvGwggebQRwjmtrWK-dfQZ9NH8
  - A world industrial production index (1958M1–2026M7) is also provided.
  - The fetched page reported "Last Update: October 2, 2026", which is after today's date (29 Sep 2026). This is probably a parsing error or a mislabelled date: treat it as unreliable and check the live page.
- **BoE use of the Känzig shock (Greene 2026, Figure 5).** [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)
  - Generalised impulse responses to "an oil supply news shock by Känzig (2021) that raises sterling oil prices by 10% on impact".
  - Estimated in a self-exciting threshold Bayesian VAR (following Gargiulo, Matthes & Petrova 2026, EER), on monthly UK data from January 1989 to June 2025.
  - The model has an endogenous inflation threshold and a labour-market-slack split, giving 4 regimes.
- **Känzig carbon-policy shocks.** "The Unequal Economic Consequences of Carbon Pricing" identifies EU ETS carbon policy shocks from high-frequency data. [NBER w31221](https://www.nber.org/papers/w31221)
  - This is an EU-level instrument; I found no UK-specific shock series.
- **Kilian (2009)**, "Not All Oil Price Shocks Are Alike", AER 99(3):1053–69, https://doi.org/10.1257/aer.99.3.1053. Bibliographic detail only, not fetched.
  - The recursive SVAR on (Δ global oil production, real activity index, real oil price) is replicable from free data.
  - Kilian's real activity index is on FRED as IGREA (unverified in this session).

### Inferences
- **For a daily pipeline:**
  - Pull the latest Känzig xlsx from GitHub's raw URL by globbing the highest `yyyyMmm`.
  - Pull the B-H CSVs from the Google Drive links.
  - Cache locally and fail gracefully, since Google Drive links can break.
  - Re-estimate LP-IV only when a new vintage appears.
  - Note that shocks end 4–9 months before today, so the dashboard's "current" cost-push pressure must come from observed prices (Brent/gas in sterling, CPI energy), not from shocks.
- **For gas, the UK's marginal fuel:** no free, maintained UK gas-shock series was found. The Alessandri & Gazzani (2025) TTF-based series and the ECB WP 2968 TTF-futures instrument are candidates; check their public availability.

### Gaps
- No verification of whether Alessandri & Gazzani gas supply shocks are publicly downloadable or updated.
- The UK responses from the Känzig shock in the BoE threshold BVAR were shown only as figures. No numerical values were extracted.

---

## 5. UK sample choices, state dependence, and translating estimates into dashboard weights

### Takeaway
- **Sample.** Use 1992/93 onwards (inflation targeting), or 1997 onwards (BoE independence), for level relationships. The BoE uses 1989–2025 for threshold VARs and HMB use 1990–2023.
- **COVID.** Handle 2020Q2–Q3 with dummies and report results with and without 2020–23.
- **Energy price cap.** Treat the Ofgem cap and Energy Price Guarantee as timing and dampening mechanisms. The UK energy CPI reflects cap changes with a lag, and support schemes muted energy CPI during 2022–23.
- **State dependence.** It is material: BoE staff find a 3.1% inflation threshold above which household expectations become more oil-sensitive, and stronger pass-through in tight labour markets.

### Cited Findings
- **Inflation threshold (BoE).** Household inflation expectations become more sensitive to global oil price shocks above an inflation threshold, so "the risk of second-round effects emerging increases when overall inflation rises to above 3.1% (Gaffney et al., 2026)". Gaffney, Petrova, Potjagailo & Sisko, "When inflation is high: Inflation thresholds and oil shock transmission in the UK", a forthcoming BoE Macro Technical Paper. [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)
  - A 3–3.2% threshold also appears in an extension of the SET-BVAR from November 2025 MPR Box C.
- **Labour-market state (BoE).** "Regardless of whether or not the shock occurs when inflation is above the 3.1% threshold, inflation responds more forcefully and persistently in a tight labour market than a loose one… The difference becomes more extreme when inflation is high." [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)
  - The slack measure is based on vacancy advertising costs (Stelmach et al. 2025). Results are robust to a filtered unemployment gap and a sample from 1976.
- **Expectations channel (BoE).** [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)
  - When media coverage of energy is high, household expectations rise by nearly 3pp in the short term and about 0.5pp in the longer term per 1pp of petrol-driven inflation.
  - A 1pp rise in headline inflation is associated with a 0.3pp rise in firms' expected year-ahead own-price growth (DMP; Yotzov et al. 2024).
  - Food prices matter most for household expectations (Anesti, Esady & Naylor 2025, BoE SWP 1,125).
- **2011 vs 2022 episodes.** Energy CPI inflation peaked at 18% in 2011 against 59% in 2022, and second-round effects (the BIM trend component) were larger and more persistent in 2022. [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)
- **Current context.** A 2026 energy shock linked to war in the Middle East and the Strait of Hormuz is under way. BoE MPC minutes through September 2026 note "little evidence so far" of second-round effects. [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf); [BoE MPS Sept 2026](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026) (the minutes characterisation is from a search summary)
- **Sample choice in the UK BB model.** HMB estimate on the full sample 1990Q1–2023Q2 with 2020Q2 and 2020Q3 dummies. BB estimate the wage and expectations equations pre-pandemic but the price equation on the full sample, to capture variation in the shortages variable. Appendix A gives pre-2019Q4 estimates. [Haskel, Martin & Brandt 2023](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/november/recent-uk-inflation-an-application-of-the-bernanke-blanchard-model-paper.pdf)
- **UK energy pricing features.** Energy CPI responds larger and with different lags because gas is the marginal source of supply and because of energy price regulation. [Haskel, Martin & Brandt 2023](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/november/recent-uk-inflation-an-application-of-the-bernanke-blanchard-model-paper.pdf)
- **Asymmetry.** BLM find strongly asymmetric pass-through of headline shocks (Section 1). BoE staff also find nonlinearities in the size of the energy shock on UK data (Greene 2026, footnote 1). [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)

### Inferences
**Recommended state-dependent LP** (implementable with statsmodels OLS):
- y_{t+h} − y_{t−1} = α_h + β_h^L·shock_t·(1−S_{t−1}) + β_h^H·shock_t·S_{t−1} + controls, with S_{t−1} = 1[12-month CPI inflation_{t−1} > 3%] or 1[V/U_{t−1} > median].
- Lag the state to avoid endogeneity.
- Expect few high-inflation observations: roughly 1990–92, 2008, 2011 and 2021–23 in the UK. Use wide bands and avoid a finely estimated threshold. A fixed 3% threshold, taken from BoE work, is defensible.

**Translating estimates into dashboard weights.** Four building blocks:
- (i) **Direct-effect component** = Σ_i w_i^{CPI}·π_i for energy and food, using ONS CPI weights. This is a mechanical contribution and needs no estimation. ONS publishes contributions to 12-month CPI inflation.
- (ii) **Indirect and second-round multiplier** = (long-run coefficient from the BB price equation, or cumulative LP response of core at h=24) − CPI share. This measures persistence beyond the direct effect.
- (iii) **Pressure score** = Σ_k ω_k·z_k, where z_k is the standardised deviation of each cost-push indicator (Brent in £, NBP/TTF gas in £, food commodity prices, import prices, sterling ERI), with ω_k ∝ |long-run pass-through coefficient|·SD(driver).
  - This is the "contribution per 1 SD shock" metric, the same scaling HMB use for their impulse responses.
- (iv) **State multiplier:** multiply the second-round component by β^H/β^L when the state is "high". Show both states transparently rather than hard-switching.

**Robustness for a public dashboard:**
- Freeze coefficients and re-estimate on a schedule (e.g. monthly after CPI release, or quarterly), not daily.
- Show rolling-window coefficient stability.
- Report the pre-COVID and full-sample estimates side by side.
- Version-control data vintages, since ONS revisions and the Känzig vintages change.

**Free data mapping.** The ONS series IDs below are from my knowledge and were NOT verified in this session; check each on ons.gov.uk before use.

| Series | Source and ID |
|---|---|
| CPI index | ONS D7BT (CPI index 2015=100) |
| CPI annual rate | ONS D7G7 |
| CPI COICOP class indices and weights (energy: 04.5 electricity and gas + 07.2.2 fuels; food: 01) | ONS MM23 dataset |
| Vacancies | ONS AP2Y |
| Unemployment 16+ | ONS MGSC |
| AWE private sector regular pay | ONS, via the Labour Market dataset |
| Import prices | ONS MM22 producer/import price dataset |
| Sterling ERI and gilt breakevens | BoE IADB |
| Brent | FRED DCOILBRENTEU (daily) |
| USD/GBP | FRED DEXUSUK |
| OECD CPI components | OECD SDMX API |
| Household expectations | BoE/Ipsos Inflation Attitudes Survey, quarterly, free xlsx |
| Supply-chain pressure | NY Fed GSCPI, free, replaces licensed PMI backlogs |

**Licensed data to avoid:**
- IHS/S&P Global PMI backlogs (used by BLM).
- Citi/YouGov expectations (used in the BoE threshold VAR).
- ICE/NBP gas futures, which are commercial; for daily data, look for a free proxy such as Ofgem cap levels or ONS system average price of gas.
- The BoE Decision Maker Panel is published in aggregate free form.
- The furlough-adjusted AWE is a BoE internal series.

### Gaps
- The Gaffney et al. (2026) BoE paper is forthcoming, so there are no published coefficients. The 3.1% threshold is from a speech.
- There is no verified free daily UK wholesale gas series. ONS publishes a "System Average Price of gas" experimental series, which is unverified in this session.
- No UK weighted-median CPI series was confirmed. A dashboard wanting BLM-style H must build one from ONS item-level indices and weights (published monthly in ONS CPI item indices files).
- The ONS series codes listed above were not verified in this session.
