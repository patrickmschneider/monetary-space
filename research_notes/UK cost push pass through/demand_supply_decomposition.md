# Decomposing inflation into demand- and supply-driven components: Shapiro-style category decompositions vs sign-identified SVARs, and their use in central-bank dashboards (UK focus)

Research date: 29 Sep 2026. Primary sources fetched and read unless flagged. Where a PDF was read in full, page-level details are quoted.

---

## Q1. Shapiro (2022/2026) method: details, sensitivity, the FRBSF monthly series, and critiques

### Takeaway
Shapiro labels each of ~124–136 PCE categories each month as demand- or supply-driven, according to whether the unexpected parts of its price and quantity move in the same or opposite directions. The residuals come from category-by-category regressions with 12 lags. He then sums expenditure-weighted inflation within each label. The results hold up to changes in lags, rolling windows, smoothing and probability weighting. The main critique is Read (RBA 2024/2026): sign restrictions only set-identify these decompositions, and for aggregate inflation the identified set is very wide.

### Cited Findings
**Citation and publication**
- Shapiro, Adam Hale (2022), "Decomposing Supply and Demand Driven Inflation", FRBSF Working Paper 2022-18, dated 12 Oct 2022, doi 10.24148/wp2022-18. [FRBSF WP PDF](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf); [FRBSF landing page](https://www.frbsf.org/research-and-insights/publications/working-papers/2022/10/decomposing-supply-and-demand-driven-inflation/)
- Later published as "Decomposing Supply- and Demand-Driven Inflation", *Journal of Money, Credit and Banking*, 2026, doi 10.1111/jmcb.13209. [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jmcb.13209). The page returned 403, so I could not confirm volume, issue or pages.
- Companion non-technical piece: FRBSF Economic Letter 2022-15, "How Much Do Supply and Demand Drive Inflation?" (21 Jun 2022). [FRBSF EL 2022-15](https://www.frbsf.org/wp-content/uploads/sites/4/el2022-15.pdf)

**Method (from the WP text)**
- **Data.** BEA PCE at the fourth level of disaggregation: 136 categories in headline PCE and 124 in core PCE. Monthly data, generally available from 1988. [Shapiro WP 2022-18, sec. 2](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)
- **Regressions.** Separate price and quantity regressions for each category i: log price and log quantity on lags of both. "My main specification uses 12 lags of price and quantity as controls". The robustness checks use 3 and 24 lags. The lags are meant to absorb existing trends, so the residual is the unexpected component. [Shapiro WP](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)
- **Labelling.** Same-sign price and quantity residuals mean demand. Opposite signs mean supply. This gives four types: dem(+), dem(−), sup(+), sup(−). The justification is Jump & Kohler (2022): restrictions on the slopes of supply and demand curves imply these signs. [Shapiro WP](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)
- **Aggregation.** Demand-driven inflation is Σ ω_i,t · π_i,t · 1{demand}. Supply-driven inflation is defined the same way. ω is a Laspeyres expenditure weight, the same weight used to build aggregate PCE inflation, so the components add up to headline. [Shapiro WP](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)
- **Shares.** Over 1990–2022, about 60% of PCE by expenditure weight is labelled as having a supply shock in a typical month. [Shapiro WP](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)
- **"Ambiguous" category.** A category is relabelled ambiguous if its price or quantity residual is within 0.025 category-specific standard deviations of zero. This affects about 15% of category-month observations. Raising the cutoff to 0.10 SD (about 25% of observations) still gives correlations of 0.97–0.98 with the baseline. [Shapiro WP, Table 1 notes and fn. 10](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)
- **Robustness (Table 1).** Variants tested:
  - Smooth-1/2/3: summing current and 1–3 lagged residuals.
  - AR-3 and AR-24.
  - 10-year rolling windows: the first window starts Jan 1988, so the rolling series starts Jan 1998.
  - Parametric and Bayesian probability weights in place of 0/1 labels.
  - The precision cutoff.

  Correlations of the variants with the baseline 12-month series are mostly 0.85–0.99. [Shapiro WP, Table 1](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)
- **Validation.**
  - A monetary policy tightening lowers demand-driven inflation by a cumulative 1.5 pp over 24 months. It raises supply-driven inflation by a smaller 0.5 pp.
  - A 10% rise in the oil price raises supply-driven inflation by about 15 bp. The effect on demand-driven inflation is small.

  Shocks used: Bauer–Swanson/Barnichon–Mesters monetary shocks; Baumeister–Hamilton and Känzig oil shocks. [Shapiro WP, sec. 4](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)
- **2021–22 US narrative.** Demand-driven inflation "began to surge in the Spring of 2021, coinciding with the re-opening". It stayed strong into 2022, when supply-driven inflation also rose, likely because of food and energy disruptions linked to the invasion of Ukraine. [Shapiro WP](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)

**FRBSF monthly updated series (dashboard)**
- URL: [Supply- and Demand-Driven PCE Inflation](https://www.frbsf.org/research-and-insights/data-and-indicators/supply-and-demand-driven-pce-inflation/)
  - Updated monthly, a few days after the BEA PCE release.
  - Uses 10-year rolling-window regressions.
  - Shows supply-driven (green), demand-driven (blue) and ambiguous contributions.
  - Four charts: annualized monthly and year-over-year (12-month trailing sums), each for headline and core PCE.
  - Data are downloadable.
- A related FRBSF follow-up estimates a Phillips-curve-type equation on the demand and supply components, Jan 2000–Feb 2025:
  - The equation explains 96% of PCE inflation movements.
  - Supply forces mostly drove the below-target inflation of 2009–2020.
  - Demand forces were the main driver of the 2021–22 surge; PCE inflation peaked at 7.25% in June 2022.

  [FRBSF Economic Letter, June 2025, "Is Demand or Supply More Important for Inflation?"](https://www.frbsf.org/research-and-insights/publications/economic-letter/2025/06/is-demand-or-supply-more-important-for-inflation/); underlying [FRBSF WP 2025-08](https://www.frbsf.org/wp-content/uploads/wp2025-08.pdf)

**Critiques**
- Read (RBA RDP 2024-05; arXiv 2609.06907, Sept 2026) argues:
  - Sign restrictions on supply and demand slopes "only identify decompositions up to a set".
  - They give "sharp conclusions about the drivers of inflation in some expenditure categories" but "tend to yield uninformative decompositions of aggregate inflation".
  - A bottom-up decomposition is *less* informative than one that uses aggregate data directly.

  [RBA RDP 2024-05](https://www.rba.gov.au/publications/rdp/2024/2024-05.html); [RBA PDF](https://www.rba.gov.au/publications/rdp/2024/pdf/rdp2024-05.pdf)
- Read's quantitative US results:
  - At the 2022:Q2 peak, a 7.7 pp inflation forecast error could have a supply contribution anywhere between 0.2 and 7.3 pp.
  - The posterior correlation between price and quantity innovations is only 0.23 [0.13, 0.33].
  - Across PCE categories, |ρ| exceeds 0.2 in only about half of categories and is below 0.4 in about 80%.
  - Identification sharpens only when |ρ| is large and the realised forecast errors fit the historical pattern.
  - Recommendation: report identified sets, not point estimates.

  [arXiv 2609.06907 (Read, Sept 2026)](https://arxiv.org/html/2609.06907)
- Shapiro's labels are 0/1. The ECB adaptation notes that the approach "cannot quantify how large the supply and demand contributions are for each component". A whole category's inflation is assigned to one label. [ECB Economic Bulletin 7/2022 box](https://www.ecb.europa.eu/press/economic-bulletin/focus/2022/html/ecb.ebbox202207_07~8b71edbfcf.en.html)
- An RBA 2023 conference discussion of Shapiro exists: [RBA conference 2023 Shapiro discussion PDF](https://www.rba.gov.au/publications/confs/2023/pdf/rba-conference-2023-shapiro-discussion.pdf). I did not read it.

### Inferences
- The method's appeal for a dashboard is that it is transparent, cheap, needs little theory and adds up to headline. Its weakness is that the 0/1 label assigns a whole category's inflation to one side even when both shocks hit, so it is not a structural decomposition. Read's result means the demand/supply split should carry an uncertainty caveat or a probability-weighted variant.
- Shapiro's own robustness table shows internal stability. It does not address set identification. The two findings are compatible: the labels are stable across specifications, but they may still be only one member of a wide identified set.

### Gaps
- The JMCB published version (volume and pages, and any changes from the WP, e.g. to the lag or window choice) could not be verified; the page returned 403.
- I did not retrieve the latest values of the FRBSF series (the page does not state them in text).

---

## Q2. Applications to the UK and other countries: what they found for 2021–24

### Takeaway
There is no official UK Shapiro-style series. The UK appears in cross-country applications: the OECD (Economic Outlook 2022/2), IMF WP 23/205 (Firat & Hao), and BIS (Hofmann, Manea & Mojon 2024). These use quarterly household final consumption by COICOP. They find that around half of UK headline inflation in 2022Q2 came from demand-driven items. The ONS's 2023 UK analysis is **not** Shapiro-style; it uses an ECB-style reopening/bottleneck item classification. The euro area (ECB), Canada (BoC 2026) and the US have their own applications.

### Cited Findings
**UK**
- **OECD (Economic Outlook 2022 Issue 2; Ecoscope blog, 14 Feb 2023).** Shapiro-style VARs on price and volume residuals, 10-year rolling windows, with an "ambiguous" category covering about 20% of movements. Eight economies: US, Canada, UK, France, Australia, Korea, Denmark, Sweden.
  - UK data: **110 COICOP categories** from quarterly national accounts household consumption.
  - In 2022Q2, the demand-driven share of annual headline inflation ranged "from less than one-quarter in Korea to around half in the United Kingdom and Canada".
  - The UK demand-driven contribution was about 4 pp higher than in 2019.

  [OECD Ecoscope blog](https://oecdecoscope.blog/2023/02/14/if-its-not-one-thing-its-another-supply-and-demand-factors-driving-rising-inflation/)
- **IMF WP/23/205, Firat & Hao, "Demand vs. Supply Decomposition of Inflation: Cross-Country Evidence with Applications" (Sept/Oct 2023).**
  - Method: quarterly Shapiro/Sheremirov decomposition for 32 countries using sectoral PCE (household consumption) data from Haver and Eurostat. The per-item VAR is in first differences with **4 lags**.
  - Robustness: 8 lags, AIC lag length, sample ending 2019Q4, 10-year rolling window, one-step-ahead forecast errors, and small-residual "ambiguous" relabelling.
  - **UK input: Haver, 41 sectors, 1988Q1–2023Q1, seasonally adjusted by the authors (X-13).** Correlation of UK CPI with the PCE deflator is 0.927.
  - Findings:
    - Demand-driven inflation was negative through 2020 and then surged through end-2022 across regions.
    - Supply-driven inflation's relative contribution was small in 2021 and rose after 2022Q1.
    - Supply-chain pressure (GSCPI) raises only supply-driven inflation.
    - Monetary policy shocks (Deb et al. 2023) mainly lower demand-driven inflation.
  - Country-level results are shown only as regional averages ("available upon request"), so there is **no published UK-specific chart**.

  [IMF WP 23/205 PDF](https://www.imf.org/-/media/Files/Publications/WP/2023/English/wpiea2023205-print-pdf.ashx); [IMF eLibrary](https://www.elibrary.imf.org/view/journals/001/2023/205/article-A001-en.xml)
- **BIS Quarterly Review, Dec 2024, Hofmann, Manea & Mojon, "Targeted Taylor rules: monetary policy responses to demand- and supply-driven inflation".**
  - Uses the Shapiro method for Australia, Canada, Korea, Sweden, **UK (sample from 2000Q1)** and the US, and Eickmeier–Hofmann for the euro area.
  - Estimated policy-rate responses: 3.26 to demand-driven inflation vs 0.77 to supply-driven inflation, i.e. "more than fourfold".
  - In 2021–23, "policy rates were initially slow to respond" and then caught up with the targeted-rule predictions.

  [BIS QR Dec 2024](https://www.bis.org/publ/qtrpdf/r_qt2412d.pdf)
- **ONS, "Demand and supply factors in CPI inflation, UK: 2021 to 2022" (9 Mar 2023).** This is not Shapiro-style: it replicates an ECB classification of the 85 CPI classes into reopening-affected and bottleneck-affected items, against a 2012–19 baseline.
  - In 2022, CPI averaged about 9%. Contributions:
    - food and energy: about 4.44 pp, roughly half;
    - reopening items: about 1.56 pp, roughly a sixth;
    - supply-bottleneck items: about 1.06 pp, roughly a tenth.
  - Core CPI reached 8.5% in Dec 2022.

  [ONS article](https://www.ons.gov.uk/economy/inflationandpriceindices/articles/demandandsupplyfactorsincpiinflation/2021to2022)
- A Megan Greene speech (Feb 2024, "Worlds apart? UK inflation and monetary policy in an international context") cites Shapiro (2022) on US fiscal stimulus stoking demand. I found no evidence of a BoE Shapiro-style UK series. [BoE speech](https://www.bankofengland.co.uk/speech/2024/february/megan-greene-fireside-chat-with-brian-coulton-chief-economist-fitch-ratings)

**Euro area**
- **ECB Economic Bulletin 7/2022, Box by Eduardo Gonçalves & Gerrit Koester, "The role of demand and supply in underlying inflation – decomposing HICPX inflation into components".**
  - Uses 72 HICPX components with price and activity VARs, and an ambiguous class.
  - Findings:
    - The rise in HICPX from 2021Q3 "was initially mainly supply-driven", with demand's importance rising gradually. By mid-2022 the two contributed roughly equally.
    - Non-energy industrial goods were mostly supply-driven (cars, appliances).
    - Services were increasingly demand-driven (travel, hospitality).

  [ECB EB box](https://www.ecb.europa.eu/press/economic-bulletin/focus/2022/html/ecb.ebbox202207_07~8b71edbfcf.en.html)
- Eickmeier & Hofmann, "What drives inflation? Disentangling demand and supply factors" (BIS WP 1047 / Bundesbank DP 46/2022 / CEPR DP18378).
  - Method: a structural factor model with sign restrictions on the factor loadings of many price and activity series; this is an alternative to Shapiro.
  - US: the surge since mid-2021 came from "extraordinarily expansionary demand conditions and tight supply conditions".
  - Euro area: similar, with a greater role for supply because of energy exposure.

  [BIS WP 1047](https://www.bis.org/publ/work1047.pdf); [SUERF brief](https://www.suerf.org/publications/suerf-policy-notes-and-briefs/what-drives-inflation-disentangling-demand-and-supply-factors/)

**Canada**
- Bank of Canada Staff Analytical Paper 2026-33 (Kang, Sekkel, Taskin & Yang, July 2026) applies the method to detailed Canadian PCE data. Findings:
  - Both forces raised post-pandemic inflation, "with supply-side pressures accounting for the larger share".
  - Demand-driven inflation is more cyclical.
  - Contractionary monetary shocks lower demand-driven inflation but have little effect on supply-driven inflation.
  - The BoC responds more strongly to demand-driven inflation.

  [BoC SAP 2026-33](https://www.bankofcanada.ca/2026/07/staff-analytical-paper-2026-33/)
- Note the conflict: the OECD put Canada's demand-driven share at about half in 2022Q2 ([OECD](https://oecdecoscope.blog/2023/02/14/if-its-not-one-thing-its-another-supply-and-demand-factors-driving-rising-inflation/)), while BoC SAP 2026-33 finds supply larger over the episode. Different windows and data may explain this.

**Australia**
- RBA: Read (RDP 2024-05) is mainly a critique; see Q1. [RBA RDP 2024-05](https://www.rba.gov.au/publications/rdp/2024/2024-05.html)

### Inferences
- For the UK, the most citable Shapiro-style number is the OECD's: around half of 2022Q2 headline inflation was demand-driven, about 4 pp above 2019. This sits oddly next to the ONS finding that food and energy directly accounted for about half of 2022 CPI. The difference in method matters: Shapiro-type labels can call energy "demand-driven" in a quarter where energy volumes rose with prices.
- A UK replication is feasible with free data. ONS publishes quarterly household final consumption expenditure by COICOP in current prices and chained volume measures, so implied deflators can be computed; the OECD used 110 UK categories and the IMF used 41 via Haver. Using monthly CPI alone is not possible, because the method needs matching quantities.

### Gaps
- I found no Bank Underground post, NIESR or Resolution Foundation publication applying Shapiro's method to UK data, and no UK-specific chart of 2023–24 demand/supply shares.
- The OECD Economic Outlook 2022/2 box/annex reference was not retrieved directly (only via the blog).
- Japan and ECB 2023–24 updates of the Gonçalves–Koester decomposition were not checked.

---

## Q3. Sign-identified (and other structural) VARs producing historical decompositions of inflation

### Takeaway
The standard toolkit is a Bayesian VAR with a Minnesota or sum-of-coefficients prior. Shocks are identified with sign restrictions and, where needed, zero restrictions, using Rubio-Ramírez–Waggoner–Zha (2010) and Arias–Rubio-Ramírez–Waggoner (2018). The usual shocks are demand, supply, energy/oil and monetary policy. The BoE now documents exactly such a model (Brignone & Piffer, MTP No. 3, July 2025). It attributes 2022 UK CPI inflation to *all* identified shocks, with a particularly strong role for global demand, but stresses high uncertainty. Bergholt et al. show that historical decompositions can swing wildly unless the deterministic component is pinned down with priors.

### Cited Findings
**BoE structural VAR: Brignone & Piffer (2025), "A structural VAR model for the UK economy", Macro Technical Paper No. 3, July 2025**

Source for everything in this block: [BoE MTP No. 3 PDF](https://www.bankofengland.co.uk/-/media/boe/files/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy.pdf); [landing page](https://www.bankofengland.co.uk/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy).
- **Variables** (quarterly, 100×log unless noted):
  - global: real world GDP and world CPI (both UK-trade-weighted), real oil price in sterling;
  - UK: Bank Rate (level), sterling ERI, UK CPI (SA), UK CPI energy, real UK GDP.
  - CPI energy is included to capture gas as well as oil.
- **Sample.** 1992Q1–2023Q2 for estimation; data run to 2024Q2 (August 2024 MPR vintages). The last year is excluded from estimation because of data revisions.
- **Covid.** Dummies for 2020Q1–2021Q2 using Cascaldi-Garcia's (2022) "pandemic prior".
- **Prior.** Minnesota plus sum-of-coefficients, following Giannone, Lenza & Primiceri (2015).
- **Algorithm.** Arias et al. (2018) draws of Q for zero plus sign restrictions, with accept/reject. It is sped up with Chan et al. (2025), which searches over column orderings of B, to reach 10,000 accepted draws.
- **Identification** (six shocks plus two unidentified):
  - World demand: + world and UK GDP, + world and UK CPI.
  - World energy (expansionary): + world and UK GDP, − world and UK CPI, − oil price, − CPI energy.
  - World supply (expansionary): + GDP, − CPI, and zero impact on CPI energy, which separates it from energy.
  - UK shocks have zero impact on global variables (small open economy, following Cesa-Bianchi et al. 2021).
  - UK supply: + GDP, − CPI.
  - UK demand: + GDP, + CPI, + Bank Rate.
  - UK monetary tightening: + Bank Rate, − CPI, − GDP.
  - The two unidentified shocks are one global and one UK residual.
- **Variance decomposition.** One year after the shocks, world supply-side and demand shocks explain about 40% of UK GDP and about 50% of UK CPI variation. Domestic shocks explain about 40% of each, with monetary policy the largest domestic shock.
- **Historical decomposition for 2021–24:**
  - "In 2022, y-o-y UK CPI inflation was pushed up by all the shocks identified in the model."
  - Strongest role: global demand, plus persistent Covid-dummy effects until end-2023.
  - These were exacerbated by contractionary world energy and world supply shocks and by domestic shocks.
  - "UK monetary policy shocks turn negative in mid-2023, contributing to the decrease in inflation."
  - Estimated shocks include a large contractionary world supply shock in 2022Q1, contractionary energy shocks in 2022 and negative UK demand shocks around 2023.
  - The results are robust to ending estimation in 2019Q4.
  - The authors stress that "estimation uncertainty remains high around the decomposition … around 2022".
  - They say the finding that compounded demand shocks played the main role is consistent with Bergholt et al. (2024), Ascari et al. (2023) and Giannone & Primiceri (2024).
- **Use in the policy process:**
  - The model is part of the MPC toolkit and "has featured in various recent speeches" (Pill 2024; Taylor 2025; Breeden 2025).
  - Novel use: a structural decomposition of **forecast revisions** (May vs August 2024 unconditional SVAR forecasts). New shocks at time T explain about half of the revision; data revisions explain the rest.
- Other BoE structural VARs cited in the paper:
  - Brandt & Burr (2024), "A new medium-scale proxy-SVAR for the UK economy";
  - Braun, Miranda-Agrippino & Saha (2025, JME) on UK monetary policy shocks;
  - Albuquerque et al. (2025), MTP No. 1, for DSGE-based decompositions.
- Megan Greene's Sept 2025 speech ("The supply side demands more attention") uses a chart of the Bank's SVAR variance decomposition over 1992Q1–2024Q2, grouping UK supply, world supply and world energy shocks. I did not read the chart text directly; the detail comes from a search snippet. [BoE speech](https://www.bankofengland.co.uk/speech/2025/september/megan-greene-university-of-glasgow-business-school)
- BoE also has a newer staff paper, Staff WP 1,165 (Jan 2026), "Structural forecast analysis". [BoE SWP 1165](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2026/structural-forecast-analysis.pdf). Not read.
- There is a 2026 BoE macro technical paper on a threshold VAR for oil-shock transmission in the UK. [BoE MTP 2026](https://www.bankofengland.co.uk/macro-technical-paper/2026/inflation-thresholds-and-oil-shock-transmission-in-the-uk). Not read.

**Long-run UK history**
- A study in *European Economic Review* (2022) gives a history of UK aggregate demand and supply shocks for 1900–2016, using sign restrictions from a Keynesian model. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S001449832200016X); [RePEc WP](https://ideas.repec.org/p/gpe/wpaper/30959.html)

**Critique of historical decompositions**
- Bergholt, Canova, Furlanetto, Maffei-Faccioli & Ulvedal, "What Drives the Recent Surge in Inflation? The Historical Decomposition Roller Coaster" (Norges Bank WP 7/2024; CEPR DP19005; AEJ: Macro, forthcoming/2025):
  - Historical decompositions in standard VARs are "whimsical" because the deterministic component is imprecisely estimated.
  - A single-unit-root prior "massively shrinks" that uncertainty.
  - Once it is used, **demand shocks are the main drivers of the surge in the US, euro area and four small open economies**.

  [Norges Bank WP 7/2024](https://www.norges-bank.no/en/news-events/publications/Working-Papers/2024/wp-72024/); [AEA](https://aeaweb.org/articles?amp=&amp=&from=f&id=10.1257%2Fmac.20240209)

**Standard references for the method**

The following are bibliographic references. Arias et al. and Baumeister & Hamilton appear in the BoE MTP reference list; the others I cite from standard bibliographic knowledge and did not fetch.
- Uhlig (2005), "What are the effects of monetary policy on output? Results from an agnostic identification procedure", *JME* 52(2), 381–419. [doi](https://doi.org/10.1016/j.jmoneco.2004.05.007)
- Rubio-Ramírez, Waggoner & Zha (2010), "Structural Vector Autoregressions: Theory of Identification and Algorithms for Inference", *REStud* 77(2), 665–696. [doi](https://doi.org/10.1111/j.1467-937X.2009.00578.x)
- Arias, Rubio-Ramírez & Waggoner (2018), *Econometrica* 86(2), 685–720; listed in the [BoE MTP references](https://www.bankofengland.co.uk/-/media/boe/files/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy.pdf).
- Baumeister & Hamilton (2015), "Sign restrictions, structural vector autoregressions, and useful prior information", *Econometrica* 83(5), 1963–1999; listed in the [BoE MTP references](https://www.bankofengland.co.uk/-/media/boe/files/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy.pdf). Their point is that uniform-Haar priors on Q are informative about the objects of interest, so explicit priors on elasticities are needed.
- ECB WP 2875 (Bańbura, Bobeica & Martínez Hernández, 2023), "What drives core inflation? The role of supply shocks"; listed in the BoE MTP references.

### Inferences
- **Standard minimal scheme for a small open economy like the UK,** following the BoE:

  | Shock | GDP | CPI | Policy rate | Energy/oil price |
  |---|---|---|---|---|
  | Demand | + | + | + | |
  | Supply | + | − | | |
  | Energy, adverse | − | + | | + |
  | Monetary tightening | − | − | + | |

  Global variables are made block-exogenous to UK shocks.
- A cost-push/energy shock is distinguished from a generic supply shock by the sign on the energy price, or by a zero restriction on CPI energy.
- The BoE SVAR and the OECD Shapiro-style numbers agree that demand was significant in the UK in 2022. The BoE SVAR assigns the demand to the *global* side and energy/supply to the rest. The ONS item-based analysis puts more weight on food and energy directly.

### Gaps
- I did not verify quantitative bar sizes from the BoE MTP Figure 6: the text gives only qualitative attributions.
- Not verified: Haskel speeches (Nov 2023, Jul 2024) using Bernanke–Blanchard models rather than SVARs; ECB Economic Bulletin 2023 BVAR boxes; Bank of Canada SVARs; Giannone & Primiceri (2024).

---

## Q4. Do central banks publish such decompositions or sign-identified VAR forecasts on dashboards or in regular reports? Pros and cons

### Takeaway
Only the FRBSF publishes a regularly updated, public, monthly demand/supply inflation decomposition, and it is Shapiro-style. I found no central bank publishing a sign-identified SVAR historical decomposition or SVAR forecast on a regularly updated public dashboard. SVAR outputs appear in one-off technical papers, speeches and staff analyses. The BoE's SVAR is documented (MTP 3, 2025) and used internally round by round, in response to the Bernanke Review (Apr 2024). The Review treats VARs as statistical cross-checks within a model suite, not as published forecasts.

### Cited Findings
- **FRBSF.** Monthly updated public dashboard of supply-, demand- and ambiguous-driven PCE inflation, headline and core, with downloadable data. [FRBSF data page](https://www.frbsf.org/research-and-insights/data-and-indicators/supply-and-demand-driven-pce-inflation/)
- **Cleveland Fed.** Publishes daily inflation nowcasts and median CPI/PCE, but no demand/supply decomposition. [Cleveland Fed indicators](https://www.clevelandfed.org/indicators-and-data); [nowcasting](https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting)
- **BoE:**
  - The SVAR is "part of a wider modelling toolkit used to inform monetary policymaking". It is intended "for use on a quarterly basis" and gives "a structural narrative for forecast revisions".
  - It appears in MPC speeches, but there is no regular public series.
  - Estimation deliberately stops a year before the data end because of revisions.

  [BoE MTP 3](https://www.bankofengland.co.uk/-/media/boe/files/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy.pdf)
- **BoE Macro Technical Paper series.** The foreword (Clare Lombardelli) says it is "part of the Bank's response to Dr Bernanke's recommendations" and that "no MTP will provide definitive answers". [BoE MTP 3](https://www.bankofengland.co.uk/-/media/boe/files/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy.pdf)
- **Bernanke Review (12 Apr 2024), "Forecasting for monetary policy making and communication at the Bank of England: a review":**
  - VARs "provide useful checks on the forecasts of macroeconomic models", being "typically unconstrained by economic theory".
  - Staff "use a suite of models, both economic and purely statistical".
  - COMPASS's role "has diminished considerably".
  - Rec 1: modernise software and automate data input "to the suite of economic and statistical models".
  - Rec 2: ongoing model maintenance.
  - Rec 5: highlight forecast errors and their sources.
  - Rec 7: augment the central forecast with alternative scenarios, including ones that "can be used to decompose historical" forecast errors.
  - Rec 8: publish selected scenarios in the MPR.
  - Rec 11: eliminate the fan charts.
  - The Review does not recommend publishing VAR forecasts.

  [Bernanke Review PDF](https://www.bankofengland.co.uk/-/media/boe/files/independent-evaluation-office/2024/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review.pdf); [BoE news release](https://www.bankofengland.co.uk/news/2024/april/forecasting-for-monetary-policy-making-and-communication-a-review)
- The BoE now publishes a periodic Forecast Evaluation Report (e.g. January 2026). [BoE FER Jan 2026](https://www.bankofengland.co.uk/paper/2026/forecast-evaluation-report-january-2026). Not read in detail.
- **Evidence on revision and specification risk (relevant to dashboards):**
  - Read: the identified sets for aggregate inflation are very wide, 0.2–7.3 pp of a 7.7 pp error. [arXiv 2609.06907](https://arxiv.org/html/2609.06907)
  - Bergholt et al.: historical decompositions are a "roller coaster" that depends on the treatment of the deterministic component. [Norges Bank WP 7/2024](https://www.norges-bank.no/en/news-events/publications/Working-Papers/2024/wp-72024/)
  - The BoE MTP: "estimation uncertainty remains high" for 2022. [BoE MTP 3](https://www.bankofengland.co.uk/-/media/boe/files/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy.pdf)
  - Shapiro's rolling-window design means past labels change as windows roll; the correlation of the rolling version with the baseline is 0.88–0.96. [Shapiro WP Table 1](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)

### Inferences
**Arguments for a public dashboard:**
- The FRBSF precedent shows a Shapiro-style series can be run as a low-maintenance monthly product.
- It is additive, so it reconciles to headline, and it is intuitive.
- The BIS "targeted Taylor rule" result gives a policy-relevant reason to track the split.

**Arguments against, or reasons to caveat heavily:**
- Set identification and wide bands (Read).
- Sensitivity of historical decompositions to priors and the deterministic component (Bergholt et al.).
- Real-time revisions: rolling windows, data revisions and re-estimation. The BoE itself withholds the final year from estimation.
- Shapiro's 0/1 labelling.
- Differences between UK CPI and household final consumption deflator (HHFCE) data.
- An SVAR *forecast* on a public dashboard is a forecast. It is subject to model and specification uncertainty and could be read as competing with the MPR. That is out of scope for an explanatory dashboard, and no central bank I found does it.

**Practical recommendation, as an inference:**
- Show historical decompositions with credible bands or identified-set ranges.
- Label them clearly as "model-based illustration".
- Freeze vintages.
- Avoid publishing unconditional VAR forecasts.

### Gaps
- I did not verify the NY Fed Multivariate Core Trend (a dynamic factor model of sectoral trend inflation, not a demand/supply decomposition), Atlanta Fed dashboards, or ECB/BoC regular publication practices.
- I did not confirm whether the BoE publishes SVAR historical decompositions in the MPR itself after 2025, e.g. in the April or July 2026 MPRs.

---

## Q5. Practical implementation with free data in Python

### Takeaway
Both approaches are feasible in Python with free UK data. The Shapiro-style approach needs ONS HHFCE by COICOP (current prices and CVM, quarterly) and ~100 small OLS VARs, which takes seconds. A BoE-style sign/zero-restricted BVAR needs about 8 quarterly series from ONS, BoE, OECD, IMF and FRED. An open-source Python replication of the BoE MTP 3 model exists (PolicyEngine/boe-var-model). The R package bsvarSIGNs is the most complete reference implementation for sign, zero and narrative restrictions.

### Cited Findings
- **PolicyEngine/boe-var-model (GitHub, MIT licence).**
  - Python replication of BoE MTP No. 3: eight quarterly variables, six shocks, Minnesota/NIW prior, Arias–Rubio-Ramírez–Waggoner (2018) algorithm.
  - Outputs: IRFs, FEVDs, shocks and historical decompositions.
  - Data are free OECD and IMF series, with proxies for the Bank's unpublished UK-trade-weighted world aggregates.
  - It is a qualitative match; "no official replication package exists".

  [GitHub PolicyEngine/boe-var-model](https://github.com/PolicyEngine/boe-var-model)
- **puremacro (GitHub).** Pure-Python macro-econometrics that implements SVAR sign restrictions (Rubio-Ramírez–Waggoner–Zha) and sign plus zero restrictions (Arias–Rubio-Ramírez–Waggoner). [GitHub isamagana/puremacro](https://github.com/isamagana/puremacro)
- **R: bsvarSIGNs (CRAN).** Bayesian SVARs with sign, zero and narrative restrictions (RRWZ 2010; ARW 2018). [bsvarSIGNs](https://bsvars.org/bsvarSIGNs/); [CRAN/rdrr](https://rdrr.io/cran/bsvarSIGNs/)
- **R: VARsignR (Uhlig-style).** [GitHub VARsignR](https://github.com/chrstdanne/VARsignR)
- **Compute cost.** The BoE combined Arias et al. with the Chan et al. (2025) permutation search, which "significantly reduces the computational burden needed to generate accepted 10,000 draws". This implies naive accept/reject is costly with 6 identified shocks in 8 variables. [BoE MTP 3](https://www.bankofengland.co.uk/-/media/boe/files/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy.pdf)
- **Shapiro-style inputs:**
  - Shapiro uses 12 lags on monthly data.
  - Firat & Hao use 4 lags on quarterly data. Their UK input was 41 sectors from 1988Q1 (via Haver), with X-13 seasonal adjustment.
  - The OECD used 110 UK COICOP categories from quarterly national accounts.

  [Shapiro WP](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf); [IMF WP 23/205](https://www.imf.org/-/media/Files/Publications/WP/2023/English/wpiea2023205-print-pdf.ashx); [OECD blog](https://oecdecoscope.blog/2023/02/14/if-its-not-one-thing-its-another-supply-and-demand-factors-driving-rising-inflation/)

### Inferences
**Shapiro-style UK pipeline:**
1. Get quarterly ONS HHFCE by COICOP in current prices (CP) and chained volume measures (CVM), ideally seasonally adjusted.
2. Compute the implied deflator as CP/CVM.
3. For each category, run OLS of Δlog p and Δlog q on 4 lags of both, over a 10-year (40-quarter) rolling window. statsmodels OLS or VAR is enough.
4. Label each category by the signs of its residuals, with an ambiguous band of ±0.025–0.10 SD.
5. Aggregate using lagged nominal expenditure shares.

Cost: trivial.

Caveats:
- This decomposes the HHFCE deflator, not CPI. The IMF reports a UK CPI–PCE correlation of 0.93.
- It is quarterly, not monthly.
- Rolling-window revisions.

**BoE-style SVAR pipeline:**
- Minimal free UK set:
  - Bank Rate (BoE database);
  - UK CPI and CPI energy (ONS series D7BT and its energy subcomponent — series IDs from general knowledge, not verified here);
  - UK real GDP (ONS);
  - sterling ERI (BoE);
  - real Brent oil price in GBP (FRED/EIA plus the exchange rate);
  - world GDP and CPI proxies (OECD/IMF).
- Sample 1992Q1 onward, 4 lags, Minnesota prior, Covid dummies.
- Implementation: statsmodels for the reduced form plus custom Gibbs/NIW draws and ARW rotations, or the PolicyEngine code. Expect minutes rather than seconds for 10k accepted draws.
- To avoid "roller coaster" historical decompositions, use a sum-of-coefficients or single-unit-root prior.

**Shock-to-deliverable mapping for the four shocks the objective asks for:**
- demand: the UK and world demand shocks;
- supply: the UK and world supply shocks;
- cost-push/energy: the world energy shock;
- monetary policy: the UK monetary policy shock.

### Gaps
- I did not test PolicyEngine code quality or runtime, or check whether BEAR (ECB, MATLAB) or Cesa-Bianchi's VAR Toolbox (MATLAB) have Python ports.
- The exact ONS series IDs for the COICOP HHFCE tables were not verified in this session.
