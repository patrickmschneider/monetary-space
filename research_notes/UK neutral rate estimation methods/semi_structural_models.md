# Semi-structural (filter-based) estimation of r*: HLW family, alternatives, pathologies, UK applications

Scope note: research conducted 29 Sep 2026. Primary texts read in full or in large part: HLW (2023) NY Fed Staff Report 1063; Buncic (arXiv 2103.16452, v. 29 Apr 2022); BoE MPR Feb 2025 Box A; Alan Taylor LSE speech (4 Jul 2025); BoE April 2026 Minutes. Other items were checked only through abstracts or search snippets, and are marked that way.

---

## 1. HLW (2017) and HLW (2023): equations, 3-stage MUE, restrictions, UK status, code

### Takeaway
HLW is a 2-equation (IS + Phillips curve) Kalman-filter model with three random-walk latent states (y*, g, z) and r* = c·g + z. It is estimated in three stages, and median-unbiased estimation (MUE) pins the two signal-to-noise ratios λg and λz. The NY Fed stopped producing UK estimates with the 2023 COVID-adjusted update (Staff Report 1063, June 2023). The stated reason is that adding recent (pandemic-era) data weakened the output-gap/real-rate-gap link in UK data, which made r* "highly unreliable". Pre-COVID UK estimates were already "highly imprecise". Replication code (R) is free on the NY Fed website.

### Cited Findings
**Model equations (HLW 2023 notation, which nests HLW 2017)** — [HLW 2023, SR1063](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1063.pdf)
- IS curve: ỹ_t = a_y1·ỹ_{t-1} + a_y2·ỹ_{t-2} + (a_r/2)·Σ_{j=1}^{2}(r_{t-j} − r*_{t-j}) + ε_ỹ,t, with ỹ_t = 100·(y_t − y*_t).
- Phillips curve: π_t = b_π·π_{t-1} + (1 − b_π)·π_{t-2,4} + b_y·ỹ_{t-1} + ε_π,t, where π_{t-2,4} is the average of lags 2–4 of inflation.
- r*_t = c·g_t + z_t. HLW 2017 imposed c = 1. HLW 2023 estimates c, following LW 2003.
- y*_t = y*_{t-1} + g_{t-1} + ε_y*,t; g_t = g_{t-1} + ε_g,t; z_t = z_{t-1} + ε_z,t. All shocks are Gaussian and mutually and serially uncorrelated.
- Data definitions: y = log real GDP. π = annualised q/q core-type consumer price inflation, spliced with the all-items index where core is unavailable. Inflation expectations = 4-quarter moving average of past inflation. Real rate r_t = i_t − π^e_t. Short rates are on a 365-day annualised basis.

**Three-stage estimation and MUE** — [HLW 2023 Appendix A1](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1063.pdf)
- ML estimates of σg and σz "are likely to be biased towards zero due to the pile-up problem". Stock and Watson's (1998) median-unbiased estimator is therefore used for λg ≡ σg/σy* (after Stage 1) and λz ≡ a_r·σz/σ_ỹ (after Stage 2). These ratios are then imposed in later stages.
- Stage 1: states [y*_t, y*_{t-1}, y*_{t-2}]. Constant trend growth g. No interest-rate term. Parameters θ1 = [a_y1, a_y2, b_π, b_y, g, σ_ỹ, σ_π, σ_y*].
- Stage 2: adds g_t as a state and the real rate r_{t-1}, r_{t-2} plus a constant a_0 and a term a_g·g in the IS equation. θ2 = [a_y1, a_y2, a_r, a_0, a_g, b_π, b_y, σ_ỹ, σ_π, σ_y*].
- Stage 3: the full model with states y*, g, z (with lags). The IS equation loadings on g are −4c·a_r/2, because g is quarterly and annualised ×4.
- HLW 2023 also made "minor technical changes" to Stage 2. A second lag of g is added to the IS equation. The Stage-2 y* equation is corrected to y*_t = y*_{t-1} + g_{t-1} + ε, where it previously used g_{t-2} "in error". The paper explicitly cites Buncic (2021, 2022). HLW say these changes have "minor effects" on r*.

**Parameter restrictions in the code**
- b_y ≥ 0.025 in all stages. a_r ≤ −0.0025 in Stages 2 and 3. In the R code these are `b2.constraint` and `a3.constraint` — [search summary of HLW code / rStar port](https://rdrr.io/github/JannesRed/rStar/src/R/run.hlw.estimation.R). I verified this only through a search snippet, not by opening the R file. Check it in `HLW_2023_Replication_Code.zip` before relying on it.

**COVID adjustments (HLW 2023)** — [SR1063](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1063.pdf)
- Time-varying volatility: the measurement-error covariance becomes R_t = diag((κ_t σ_ỹ)², (κ_t σ_π)²). κ takes separate values for 2020Q2–Q4, 2021 and 2022, and κ = 1 otherwise. The state-shock variances are *not* scaled. This follows Lenza and Primiceri (2022).
- Estimated values: κ2020 is "sizable" and significant. For the US and EA, κ2021 ≈ 2 and κ2022 ≈ 1.5. For Canada, κ2021 ≈ 1 and κ2022 ≈ 1.5.
- Persistent COVID supply shock: y*_t,COVID = y*_t + (φ/100)·d_t, so the gap becomes ỹ_t = 100(y_t − y*_t) − φ·d_t. Here d_t is the quarterly-average Oxford COVID-19 Government Response Tracker Stringency Index (0–100). d_t = 0 up to 2019Q4. Because OxCGRT stopped at end-2022, d_t is assumed to decline linearly from 2023Q1 to zero in 2024Q4.
- Without the adjustments, standardised auxiliary IS residuals in 2020Q2 were 9–10× the outlier threshold in the US and Canada and 17× in the EA. The adjustments remove these outliers.
- Estimated r* in 2022 is "within a few tenths of a percentage point" of 2019 in the US, Canada and EA. The main lasting COVID effect is lower y*: the US natural output level in 2022 is about 4% below the pre-pandemic projection.
- Pre-COVID parameter table (sample to 2019Q4, current vintage). λg = 0.053 / 0.052 / 0.036 and λz = 0.031 / 0.016 / 0.032 for US / Canada / EA. a_r = −0.067 / −0.065 / −0.037. b_y = 0.076 / 0.047 / 0.062. c = 1.198 / 1.130 / 0.816. The average standard error of r* is 1.24 / 1.63 / 3.48 pp, rising to 1.66 / 1.84 / 4.82 pp at the final observation.

**UK dropped**
- Quote: "In HLW (2017), the model was also estimated using data from the United Kingdom. Extending the sample to include the most recent years has weakened the estimated relationship between the output gap and real interest rates in the UK data, making estimates of the natural rate of interest highly unreliable. For that reason, we no longer estimate the model for the United Kingdom." — [SR1063, June 2023](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1063.pdf)
- Williams (19 May 2023): the NY Fed no longer produces UK HLW estimates because "the model does not provide a good fit for the data". Even before the pandemic "estimates for the UK were highly imprecise". Post-2023 data use Oxford Stringency to 2023–24 and a time-varying variance for 2020Q2–2022Q4 — [Williams speech](https://www.newyorkfed.org/newsevents/speeches/2023/wil230519)
- The NY Fed r* page currently covers the US, Canada and Euro Area only. Its latest data are as of Aug 27/28 2026 — [NY Fed r* page](https://www.newyorkfed.org/research/policy/rstar)

**Code**
- R replication code: [HLW_2023_Replication_Code.zip](https://www.newyorkfed.org/medialibrary/media/research/economists/williams/data/HLW_2023_Replication_Code.zip) and [LW_2023_Replication_Code.zip](https://www.newyorkfed.org/medialibrary/media/research/economists/williams/data/LW_2023_Replication_Code.zip) — [NY Fed r* page](https://www.newyorkfed.org/research/policy/rstar)
- Buncic's corrected R/Matlab code: [GitHub 4db83/Issues-with-HLWs-natural-rate-Code](https://github.com/4db83/Issues-with-HLWs-natural-rate-Code)

### Inferences
- A Python port is straightforward. It needs: a state-space model (statsmodels `MLEModel` or a hand-written Kalman filter plus `scipy.optimize` with bounds for the two constraints); the Stock–Watson (1998) Table 3 look-up values for the MW/EW/QLR/L statistics (interpolation); and a 3-stage driver.
- The OxCGRT UK stringency index is free, so the full HLW-2023 COVID treatment is replicable for the UK.
- UK series needed, all free: ONS real GDP (CVM, SA); CPI, ideally core CPI spliced with headline for pre-1989 history; and BoE Bank Rate or 3-month rate, quarterly-averaged. The exact series codes (e.g. ONS ABMI for real GDP) are from my own knowledge and not verified in this session.
- When the IS slope a_r goes to the −0.0025 bound, the model has almost no information on r*. The IS equation cannot tell a gap in r from a gap in r*. σz = λz·σ_ỹ/a_r then becomes very large, because the implied z variance scales with 1/a_r. That is the "z explodes" pathology. The UK breakdown the NY Fed describes (a weakened output-gap/real-rate link) is exactly this case.

### Gaps
- I did not retrieve HLW (2017) JIE Table 1 UK parameter values or the UK r* path. Buncic's replication gives UK r* ≈ 1.35% at 2019Q4 under HLW's implementation (see §2).
- I found no document saying exactly which NY Fed release last carried UK numbers. SR1063 (June 2023) is the first to state it was dropped. UK estimates were presumably published with the 2017-model updates through early 2020, before the COVID suspension, but this is unconfirmed.
- The a_r/b_y bounds are confirmed via search snippets only. Verify them in the zip.

---

## 2. Critiques and pathologies

### Takeaway
There are four main problems:
- **MUE errors**: HLW's Stage-2 MUE was misspecified and implemented differently from Stock–Watson. It inflates λz and so the downward trend in z. Corrected, λz = 0 exactly for the UK, EA and Canada, and UK r* is about 45 bp higher at 2019Q4.
- **Imprecision and revisions**: estimates are very imprecise and revise heavily in real time.
- **Weak identification**: identification collapses when the IS or Phillips curve is flat.
- **Pile-up**: variance ratios pile up at zero.
Together these mean a naive UK HLW run is likely to be fragile.

### Cited Findings
**Buncic (2020/2022, arXiv 2103.16452; SSRN 3725151)** — [arXiv](https://arxiv.org/abs/2103.16452), [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3725151)
- MUE theory requires the Stage-2 local-level model to have the same output-gap equation as the full model with z removed: a_y(L)ỹ_t = a_r(L)[r_t − 4g_t] + ε. HLW instead use a_y(L)ỹ_t = a_0 + a_r(L)r_t + a_g·g_{t-1} + ε. Here a_g is not restricted to −4a_r and a constant is added.
- Under HLW's version, MUE recovers λz = a_r·σz / (σ_ỹ + a_g·σg/2), not a_r·σz/σ_ỹ, so it is inconsistent with how λz is used in Stage 3.
- HLW's Stage-2 y* equation also wrongly used g_{t-2}, which makes the trend error MA(1). HLW 2023 has since corrected this.
- Structural-break regressions: Stock and Watson AR(4)-filter the series once and regress it on a constant plus a break dummy only. HLW add "extra regressors" (lagged gaps, the r terms and g) inside the break regressions. This inflates the F(τ) sequence: on SW's own trend-growth example, the MW/EW/QLR statistics are {0.4461, 0.3426, 0.2342} under the HLW form against {0.1103, 0.0987, 0.0250} under the SW form. Because the look-up tables were simulated under the SW form, λz is spuriously large. HLW also use break-date trimming τ0 = 4, τ1 = T − 4, where SW used 15%/85%.
- The intercept a_0 is not supported by the data. Adding it raises the log-likelihood by 0.3847 for the US (p = 0.38) and by 0.0146 for the UK.
- Results (sample to 2019Q4):
  - US: λz falls from 0.040 to 0.013 and is insignificant. r* is ≈ 1.5% against 0.48%.
  - EA: λz = 0 and r* is 1.03% against 0.24%.
  - UK: λz = 0 and r* is 1.80% against 1.35%, i.e. +45 bp.
  - Canada: λz = 0 and r* is 1.73% against 1.46%.
  - With λz = 0, z for the UK and Canada "is essentially a horizontal line at 0". UK r* then equals (4×) trend growth, which is unaffected by the correction.
- ML estimation of σg (full model, US recursive samples to 2019Q4) never piles up at zero. ML of σz did pile up at zero in every sample up to mid-2018. For the EA, UK and Canada, the ML and MUE estimates of σz are both zero.
- Related Bayesian work cited by Buncic:
  - Berger and Kempa (2019), using a non-centred parameterisation, find the σz posterior centred at zero.
  - Lewis and Vazquez-Grande find z should be AR(1) with transitory shocks, not a random walk.
  - Kiley (2020) finds "little information in the data" about the r* process.
- Buncic also has an earlier LW-focused paper, "Econometric issues with Laubach and Williams' estimates" — [arXiv 2002.11583](https://arxiv.org/pdf/2002.11583)

**Beyer and Wieland (2019, JIMF 94:1–14)**: "popular estimation methods deliver imprecise and unstable results". The observed decline "is not a reliable indicator" of the need for easy policy. If used, r* should be paired with consistent potential-output estimates. They cover the US, EA and Germany using LW — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0261560618303851), [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2941513)

**Fiorentini, Galesi, Pérez-Quirós and Sentana (2018, "The Rise and Fall of the Natural Interest Rate")**: the LW model "cannot estimate r* accurately when either the IS curve or the Phillips curve is flat". Adding a local-level specification for the observed interest rate restores precise estimation in those empirically relevant cases. r* rises from the 1960s, peaks around the end of the 1980s, then falls — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3214487), [CEPR DP13042](https://cepr.org/publications/dp13042), [RCEA WP](http://www.rcea.org/RePEc/pdf/wp18-29.pdf). A 2026 follow-up, "Unobservable no more: estimating the natural rate of interest under flat IS and Phillips curves", exists per a search snippet. I did not read it.

**Lewis and Vazquez-Grande (2019, JAE 34(3):425–436)**: estimated with Bayesian methods and loose priors, r* is subject to both permanent and transitory shocks. With transitory shocks, US r* is more procyclical, shows a less marked secular decline, and is higher after the GFC than most estimates — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1002/jae.2671), [FEDS version](https://www.federalreserve.gov/econres/feds/measuring-the-natural-rate-of-interest-a-note-on-transitory-shocks.htm), [replication data](https://journaldata.zbw.eu/dataset/measuring-the-natural-rate-of-interest-a-note-on-transitory-shocks)

**Kiley (2019/2020, "The Global Equilibrium Real Interest Rate: Concepts, Estimates, and Challenges")**, FEDS 2019-076 / Annual Review of Financial Economics — [FEDS pdf](https://www.federalreserve.gov/econres/feds/files/2019076pap.pdf), [Annual Reviews](https://www.annualreviews.org/content/journals/10.1146/annurev-financial-012820-012703)

### Inferences
- For the UK, a Buncic-corrected Stage 2 is likely to return λz = 0. r* then collapses to c·g (trend growth). The model becomes "r* = 4 × trend GDP growth", which is informative about growth but not about the saving/investment or convenience-yield wedge. Any UK implementation should report results under both HLW's and Buncic's Stage 2, and an ML/Bayesian σz alternative.
- Diagnostics to report: whether a_r sits at the −0.0025 bound; the size of b_y; λz and the MUE confidence interval (SW tables give intervals such as [0, 0.07]); smoothed against filtered r*; standard errors (HLW's own pre-COVID US r* s.e. is ≈ 1.2–1.7 pp); and recursive real-time vintages.

### Gaps
- I did not retrieve primary text for Clark and Kozicki (2005, "Estimating equilibrium real interest rates in real time", North American Journal of Economics and Finance). Their known result is that real-time LW-type estimates are heavily revised and one-sided estimates are unreliable. This comes from my own knowledge and is not re-verified here.
- I found no published UK-specific pile-up or a_r-bound diagnostics beyond Buncic's tables. The UK Stage-2 parameter values sit in his Table 7 (or 10), which I did not extract line by line.

---

## 3. Handling the ZLB/ELB and QE: shadow rates, long yields, Johannsen–Mertens

### Takeaway
Free UK shadow rates exist but are stale:
- Wu–Xia UK runs monthly from Jan 1990 to Feb 2022, is not updated, and the authors say to splice it with Bank Rate.
- Krippner's UK SSR from January 1995 is free on ljkmfa.com.

Johannsen–Mertens (2021) is the cleanest ELB-robust filter approach. Its US r* is very stable (1.7–2.2%). Macro-finance models that use the whole gilt curve (Davis et al. 2024) sidestep the ELB and are now the approach favoured by a BoE MPC member.

### Cited Findings
- Wu–Xia shadow rates: a UK series is available (Matlab/Excel), monthly, Jan 1990–Feb 2022. "we are not currently updating the shadow rate and will continue updating it when ZLB returns". Users may "splice the shadow rate with the policy rate" — [Cynthia Wu shadow rates](https://sites.google.com/view/jingcynthiawu/shadow-rates); also [Fan Dora Xia page](https://sites.google.com/site/fandoraxia/wx-data)
- Krippner: two-factor SSR for 8 economies including the UK, from Jan 1995, free to use subject to the site's disclaimer — [LJKmfa](https://www.ljkmfa.com/), [Visitors page](https://www.ljkmfa.com/visitors/). A cross-country comparison is in [Anderl (2023), SJPE](https://onlinelibrary.wiley.com/doi/full/10.1111/sjpe.12343). There is a caution on shadow-rate sensitivity (model-dependence) in "A Note of Caution on Shadow Rate Estimates", JMCB 2020 — [RePEc](https://ideas.repec.org/a/wly/jmoncb/v52y2020i4p951-962.html)
- BoE Staff WP 864 (2020), "A shadow rate without a lower bound constraint", is a BoE-authored UK-relevant alternative — [BoE WP 864](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2020/a-shadow-rate-without-a-lower-bound-constraint.pdf). I did not read the contents.
- Johannsen and Mertens (2021, JMCB 53(5):1005–1046):
  - A shadow rate equals the actual rate except when the ELB binds. It is embedded in a trend-cycle decomposition of interest rates and macro variables.
  - It gives competitive interest-rate forecasts.
  - US r* is "substantially more stable than alternative estimates, remaining between 1.7 percent and 2.2 percent", with only a modest, insignificant decline.
  - Sources: [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jmcb.12771), [BIS WP 715](https://www.bis.org/publ/work715.pdf), [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2772897)
- Richmond Fed comparison (Q2 2024, US): Lubik–Matthes 2.6%, Johannsen–Mertens 1.8%, HLW 0.8%. The differences reflect definitions: LM uses a 5-year-ahead forecast of the real rate, while JM uses the permanent (infinite-horizon) component. HLW's residual z may pick up the Treasury convenience yield — [Richmond Fed EB 24-36](https://www.richmondfed.org/publications/research/economic_brief/2024/eb_24-36)

### Inferences
- In practice for the UK, the ELB mattered most for 2009Q1–2021Q4 (Bank Rate 0.1–0.5%) plus large-scale QE. Three options:
  - Splice Wu–Xia (to 2022) or Krippner (updated) into the HLW real-rate variable.
  - Replace Bank Rate with a 2–5-year gilt or OIS yield from the free BoE yield-curve data, noting this adds term premia.
  - Move to a JM-style censored-shadow-rate model, which needs Gibbs/particle methods and is harder in Python but feasible.
- Shadow rates are model-dependent and can move a lot, e.g. Wu–Xia UK going deeply negative. Using them in the IS curve can distort a_r. Show sensitivity across the options.

### Gaps
- I did not verify Krippner UK's latest update date.
- I found no JM application to the UK.

---

## 4. Alternatives within the filter family and robustness ranking

### Takeaway
The alternatives that impose less structure (JM, Lubik–Matthes) or add financial-market information (DGGT trend VARs with long yields and survey expectations; Davis et al. 2024 macro-finance) give more stable and plausible r* paths than HLW. They are the ones BoE staff and MPC members actually use for the UK. The BoE's staff suite explicitly includes a DGGT (Del Negro et al. 2019)-based semi-structural model and a Davis et al. (2024) macro-finance model.

### Cited Findings
- **Del Negro, Giannone, Giannoni and Tambalotti (2019, "Global Trends in Interest Rates", JIE; NY Fed SR 866)**: a trend-cycle VAR across advanced economies. The world real-rate trend for safe and liquid assets was ≈ 2% for over a century, then fell sharply over three decades, converging across countries. The drivers are a higher convenience yield for safety and liquidity plus lower global growth — [NY Fed SR866](https://www.newyorkfed.org/research/staff_reports/sr866.html), [NBER w25039](https://www.nber.org/papers/w25039). The companion Brookings paper (2017) is "Safety, Liquidity, and the Natural Rate of Interest" — [Brookings pdf](https://www.brookings.edu/wp-content/uploads/2017/08/delnegrotextsp17bpea.pdf)
- **Davis, Fuenzalida, Huetsch, Mills and Taylor (2024, JIE 149, "Global natural rates in the long run: Postwar macro trends and the market-implied r* in 10 advanced economies")**: a unified no-arbitrage macro-finance model with two trend factors (π* and r*) for 10 AEs including the UK. It addresses the "natural rate puzzle" — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0022199624000436), [NBER w31787](https://www.nber.org/papers/w31787)
  - Taylor's description: the macro block models low-frequency trends in inflation and r*. The finance block links the average gilt yield to them: ȳ_t = a_y + b_π·π*_t + b_r·r*_t + ε^cyc_t, where the cyclical term includes risk factors. It uses a two-sided Kalman filter. 95% bands are "about 50 to 150 basis points" — [Taylor, "The end of the road", 4 Jul 2025](https://www.bankofengland.co.uk/-/media/boe/files/speech/2025/july/the-end-of-the-road-speech-by-alan-taylor.pdf)
- **Lubik–Matthes**: a flexible TVP-VAR statistical model where r* is the 5-year-ahead forecast of the real rate. The Richmond Fed maintains it: 2.6% for the US in 2024Q2 — [Richmond Fed EB 24-36](https://www.richmondfed.org/publications/research/economic_brief/2024/eb_24-36). Taylor also cites Lubik and Matthes (2023) and Ferreira and Shousha (2023) as HLW-tradition variants — [Taylor speech](https://www.bankofengland.co.uk/-/media/boe/files/speech/2025/july/the-end-of-the-road-speech-by-alan-taylor.pdf)
- **Fiorentini et al.**: add a local-level equation for the observed real rate to fix weak identification (see §2).
- **Lewis and Vazquez-Grande**: model z as AR(1) and estimate with Bayesian methods (see §2).

### Inferences
Suggested robustness ranking for a small UK Python project. This is my synthesis:
1. HLW-2023 with the Buncic-corrected Stage 2, as the benchmark. Expect a_r near the bound and λz ≈ 0.
2. A Fiorentini-style local-level r equation added to the same state space, which is cheap to implement.
3. A DGGT-style common-trend model on Bank Rate/shadow rate, 10-year gilt yields, index-linked gilt real yields and long-run inflation expectations. Everything except Consensus surveys is free from BoE yield curves; Consensus is paid, but market breakevens are free.
4. A Davis et al.-type two-trend macro-finance filter using the average gilt yield.

JM is the most ELB-robust option but the heaviest to code.

### Gaps
- Mertens and Zhang: I found no source in this session. Cannot confirm the paper's title or content.
- I did not retrieve UK-specific numbers from DGGT (2019).
- I did not verify whether Davis et al. or DGGT publish UK code or data.

---

## 5. UK-specific estimates and ranges (2023–2026)

### Takeaway
BoE Box A (MPR Feb 2025) says staff macro models show UK R* up 25–75 bp since the 2018 assessment. The 2018 assessment was 2–3% nominal in the long run, i.e. roughly 0–1% real. Within that:
- The Davis et al. model shows about +25 bp and the DGGT-based model about +75 bp.
- Market-based 10-year forward real rates show about +90 bp.
- The Market Participants Survey shows +150 bp.
- Consensus 6–10-year-ahead forecasts show less than +25 bp.

MPC member Alan Taylor puts UK real r* at ≈ 0.75% (2025Q1). That gives a nominal neutral of 2.75%, with a 2.25–3.25% range. By April 2026 he cited "neutral at 3%".

### Cited Findings
- MPR Feb 2025 Box A, "The long-run equilibrium interest rate" — [BoE MPR Feb 2025](https://www.bankofengland.co.uk/monetary-policy-report/2025/february-2025) ([pdf](https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2025/february/monetary-policy-report-february-2025)):
  - The August 2018 Inflation Report put the equilibrium rate "in the 2%–3% range in nominal terms in the long run".
  - "Macroeconomic models monitored by Bank staff suggest a modest increase in R* of around 25 to 75 basis points relative to the estimates published in the August 2018 Inflation Report."
  - "a macrofinance model with two trend factors based on Davis et al (2024) finds only a small increase in R* in recent years of around 25 basis points, while a semi-structural model based on Del Negro et al (2019) points to a larger increase of around 75 basis points." Staff models "estimates have diverged to some extent since the pandemic".
  - Market-based measures (10-year UK forward real rates from nominal yields adjusted by survey inflation expectations) show "over 90 basis points since 2018". The Box warns these may overstate the rise because long yields are oversensitive to short yields and term premia are uncertain.
  - The Market Participants Survey neutral Bank Rate is up 150 bp. Consensus 6–10-year-ahead expectations imply a rise of less than 25 bp.
  - Conclusion: "R* is likely to have increased modestly"; Bank Rate is "unlikely to fall back to its pre-pandemic lows" absent new disinflationary shocks. For a small open economy, R* is ultimately determined globally, per Bailey et al. (2022).
  - HLW/LW is not named among the staff models. This is consistent with the NY Fed dropping the UK.
- Taylor, "The end of the road" (LSE, 4 Jul 2025) — [BoE pdf](https://www.bankofengland.co.uk/-/media/boe/files/speech/2025/july/the-end-of-the-road-speech-by-alan-taylor.pdf):
  - "The point estimate of r* for the UK is about 0.75% per annum for Q1 2025, similar to the levels that were seen in the UK in 2015-2016."
  - Adding 2% gives a nominal neutral of 2.75%, with a range of 2.25–3.25%, based on the ~100 bp 95% posterior interval at the end of the UK series.
  - The estimate is an updated Davis et al. (2024) model covering the G5 (US, UK, Japan, France, Germany). He prefers it to HLW.
- Taylor at the ECB Sintra forum (2 Jul 2025, "Unexpected curves") used the one-sided nominal neutral from Davis et al. (2024) to test whether r* predicts policy rates — [BoE speech page](https://www.bankofengland.co.uk/speech/2025/july/alan-taylor-panellist-at-ecb-forum-on-central-banking-2025), [appendix pdf](https://www.bankofengland.co.uk/-/media/boe/files/speech/2025/unexpected-curves-remarks-by-alan-taylor-appendix.pdf)
- April 2026 MPC Minutes: Bank Rate held at 3.75% on an 8–1 vote, with Pill voting for 4%. Taylor's rationale: "Given neutral at 3%, it makes sense to hold..." — [BoE Minutes April 2026](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/april-2026). Bank Rate was still 3.75% in September 2026 — [Sept 2026 Summary](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026)
- Buncic's UK HLW replication (sample to 2019Q4): r* is 1.35% under HLW's implementation and 1.80% under the corrected one — [arXiv 2103.16452](https://arxiv.org/abs/2103.16452)
- Kaykhusraw (Economica 2025, "Longer-run equilibrium interest rates: evidence from the United Kingdom") adapts a semi-structural NK/Kalman model to UK annual data from 1700 onwards (the EHS draft covers 1700–1950). r* rose through the 18th–19th centuries and declined from around 1900 — [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/ecca.12566), [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5072873), [EHS draft](https://files.ehs.org.uk/wp-content/uploads/2024/03/07144045/Kaykhusraw-NR-Paper-2024.pdf). A GitHub repo "kaykhosrow/adapted.hlw" appeared in search results but returned a 404.

### Inferences
- A reasonable consensus range for UK real r* in 2025–26 from filter/macro-finance methods is ≈ 0.5–1.25%. That is a nominal neutral of ≈ 2.5–3.25% (Taylor 2.75–3%). This is my inference from Box A applied to the 2018 baseline of 2–3% nominal, plus Taylor's figures.
- A plain UK HLW run will likely give a lower number with very wide bands, or fail (a_r at the bound). The Buncic-corrected version gives a trend-growth-driven r*, which is likely below 1% given weak UK productivity growth.

### Gaps
- I did not search for NIESR r* estimates, Bank Underground posts on r*, Rachel and Smith (2015, BoE SWP 571), or speeches by Mann, Greene, Lombardelli or Pill specifically on r*, beyond the search that found Lombardelli's Sept 2026 "outlook for inflation" speech (not read).
- I did not check whether MPRs after Feb 2025 (Aug 2025, 2026 editions) updated the R* box.
- Cesa-Bianchi, Lloyd, Sajedi and Sampaolesi, "The Natural Rate of Interest in Small-Open Economies" (forthcoming, cited by Taylor), is not reviewed.
