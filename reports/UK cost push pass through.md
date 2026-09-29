# Look through first rounds, then price the state

Build the dashboard around conditional look-through. Direct first-round energy, commodity and import-price effects on headline CPI should add almost nothing to the "is policy tight enough" pressure score. Pipeline and indirect pass-through into food, core goods and services should get a partial weight. Second-round signals (wages, services inflation, short-term and firm price expectations) should get a full weight. The whole cost-push block should then be scaled by a state multiplier that rises when inflation is above about 3%, the labour market is tight, expectations are drifting, and the shock is large or long-lasting. That is what the theory implies: Aoki-type models say stabilise sticky-price inflation, and network and real-wage-rigidity models say respond only partly to the cost-push wedge. It is also what current practice says. The ECB's 2026 three-tier rule and the Bank of England's "this risk is cumulative" doctrine both follow this pattern. The UK evidence says pass-through is small and slow in normal times: a typical energy shock adds under 0.2pp to annual CPI, and supply-chain pass-through into services reaches only about 0.4 in the long run over roughly 15 quarters. It becomes much larger when inflation is high and the labour market is tight. The BoE now estimates a threshold of about 3.1% headline CPI, above which household expectations become oil-sensitive. The 2026 energy shock is the live test. CPI is at that threshold and household expectations jumped. But the labour market is loose, and indirect pass-through has come in below forecast, so a well-built multiplier should currently sit well above 1 but below its 2022 level. That mirrors the MPC's drift from a 9–0 to a 6–3 hold. For estimation, the most useful free-data tools are:
- a UK Bernanke–Blanchard wage–price–expectations system;
- state-dependent local projections instrumented with Känzig oil-supply news shocks;
- a Ball–Leigh–Mishra "headline-shock" core equation.

A sign-identified BVAR belongs on the dashboard only as a banded historical decomposition, labelled as a model-based illustration. It should not be published as a forecast: no central bank found in this research publishes one, and the identification uncertainty is very large.

## Theory endorses partial look-through, not indifference

The canonical New Keynesian model gives three distinct objects, and a dashboard should keep them separate.

**The flexible-price first-round level effect.** In Aoki's two-sector model, optimal policy fully stabilises **sticky-price (core) inflation** and lets flexible-price relative-price movements pass into headline. Doing so also closes the welfare-relevant output gap ([Aoki 2001](https://doi.org/10.1016/S0304-3932(01)00069-1)). This is the formal basis for giving the direct energy contribution close to zero weight.

**The cost-push wedge.** Blanchard and Galí showed that real-wage rigidity breaks "divine coincidence". Oil shocks then generate an endogenous cost-push term and a genuine trade-off ([NBER w11806](https://www.nber.org/papers/w11806)). Production networks do the same:
- Rubbo finds that CPI-based Phillips curves "suffer from productivity-driven cost-push shocks". A **divine-coincidence index**, which weights sectors by stickiness and network position, gives a Phillips curve with a 2–4× larger R² ([Rubbo 2023](https://onlinelibrary.wiley.com/doi/full/10.3982/ECTA18654)).
- La'O and Tahbaz-Salehi show that the optimal target overweights **upstream** sectors ([NBER w27464](https://www.nber.org/papers/w27464)). Energy is therefore not zero-weight: its indirect path through intermediate inputs is exactly the part that matters.
- In the textbook discretionary solution, a cost-push shock is split between inflation and a negative output gap, in proportions set by the output weight and the Phillips-curve slope ([Clarida, Galí & Gertler](https://www.nber.org/papers/w7147)).

**Expectations and second-round effects.** These call for a full response, because they are what makes a relative-price shock persistent.

Bank staff now state the trade-off in the same loss-function terms. Harrison and Waldron argue that the remit's "trade-off" language is "arguably too passive", and that the best feasible outcome "requires a tightening of monetary policy to balance the incidence of losses" ([BoE Bank Insights, May 2026](https://www.bankofengland.co.uk/bank-insights/2026/the-mpcs-remit-and-trade-off-management)). Guerrieri, Lorenzoni, Straub and Werning give the strongest dovish case: with downward nominal-wage rigidity, reallocation shocks justify inflation above target "despite elevated unemployment" ([Jackson Hole 2021](https://www.kansascityfed.org/documents/8322/JH_Guerrieri.pdf)).

The honest summary is that theory tells a dashboard **what to weight**: sticky, upstream and expectations-sensitive prices. It does not give a UK-calibrated number for how much.

Practice has converged on a graduated, state-contingent version of the same idea.

**ECB.** Lagarde's March 2026 framework has three tiers ([ECB, 25 Mar 2026](https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260325~ac2916a211.en.html)):
- look through small, short-lived shocks, because "a monetary policy response would arrive too late";
- make "some measured adjustment" for large but temporary ones;
- be "appropriately forceful or persistent" when the deviation is significant and persistent.

**Bank of England.** Lombardelli: "Monetary policy cannot prevent the initial rise in inflation caused by higher energy prices… The key judgement… is whether emerging evidence suggests inflation may become persistent. This risk is cumulative" ([BoE, 24 Sept 2026](https://www.bankofengland.co.uk/speech/2026/september/clare-lombardelli-speech-at-the-sixth-biennial-conference-poland)).

**UK history.** The MPC's revealed record has three reference cases:

| Episode | What the MPC did | Conditions |
|---|---|---|
| 2008–11 | Looked through CPI of 4.5–5.2% with Bank Rate at 0.5% | VAT, commodity and sterling effects ([King open letter, May 2011](https://www.bankofengland.co.uk/-/media/boe/files/letter/2011/governor-letter-160511.pdf)) |
| 2016–17 | Tolerated the sterling overshoot as a remit trade-off | Post-referendum depreciation |
| 2021–23 | Did not look through | Tight labour market, successive shocks, loose starting stance |

The failure of 2021–23 is now the official lesson. Reis attributes central banks' errors partly to "a strong belief that inflation expectations were firmly anchored" ([BIS WP 1060](https://www.bis.org/publ/work1060.htm)). The Bernanke Review found the BoE "seriously underestimated" the 2022 energy shock, partly because COMPASS anchors long-run expectations at target by construction ([Economics Observatory](https://www.economicsobservatory.com/why-did-the-bank-of-england-need-a-review-of-its-forecasting-record)). Lane adds that ECB policy was highly accommodative when the shock hit, and that "in the absence of demand pressures, the impact of supply-side shocks on inflation would have been considerably lower" ([ECB, 13 May 2026](https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260513~5b14c78806.en.html)).

For a hybrid-NKPC dashboard, the implication is direct. The cost-push term should raise the required policy stance only through the portion that is likely to persist. That portion depends on the other two blocks: expectations and demand-driven slack.

## UK pass-through is small at first and slow, and runs mostly through wages

**Direct effects** are large, fast and mechanical. In October 2022, CPI hit 11.1% while core stayed at 6.5%. The ONS estimated that without the Energy Price Guarantee, household energy prices would have risen about 75% rather than 25%, putting CPI at about **13.8%** ([ONS, Oct 2022](https://ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/october2022)). The Ofgem cap turns wholesale gas moves into lagged, stepwise CPI jumps. In 2021, wholesale rises reached CPI mainly through the October 2021 and April 2022 cap resets. Oil reaches CPI within weeks ([Haskel, Martin & Brandt, ESCoE DP 2025-12](https://escoe-website.s3.amazonaws.com/wp-content/uploads/2025/09/24140421/ESCoE-DP-2025-12-2.pdf)).

For a dashboard, this makes the direct gas effect **predictable one to two quarters ahead** from wholesale futures and announced cap changes. That is useful for the headline nowcast, and irrelevant to whether policy is tight enough.

**Indirect (supply-chain) effects** are smaller, slower and incomplete. Bank staff estimate that energy and food cost pass-through lifted CPI by about **1pp at the 2022Q4 peak**. Most of it came through food (about 3pp of food inflation), with about 1pp each on transport services and restaurants ([Bank Underground, Aug 2023](https://bankunderground.co.uk/2023/08/24/how-do-firms-pass-energy-and-food-costs-through-the-supply-chain/)).

| Sector | Long-run pass-through coefficient | Time to reach 80% of pass-through |
|---|---|---|
| Manufacturing | **0.8** | 8 quarters |
| Services | **0.4** | 15 quarters |

Cost decreases take about two quarters longer to pass through than increases. The UK Bernanke–Blanchard model puts a typical pre-pandemic energy shock at "a little under **0.2pp**" on annual CPI, with little persistence. Food shocks are more persistent: a typical food shock peaks at about 0.3pp after four quarters ([ESCoE DP 2025-12](https://escoe-website.s3.amazonaws.com/wp-content/uploads/2025/09/24140421/ESCoE-DP-2025-12-2.pdf)). Bank BVAR work adds that oil supply shocks have "more immediate but short-lived effects on UK inflation, while gas supply shocks tend to have broader and more persistent effects" ([Greene, 2 Jun 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)). That matters for the UK, where gas sets the marginal price of electricity.

**Exchange-rate pass-through** follows a well-established rule of thumb: about **60% to import prices and 20% to CPI**. A 10% sterling fall raises import prices by about 6% within roughly a year, and the CPI level by about 2% over six to eight quarters or more ([Forbes, Hjortsoe & Nenova 2018](https://www.nber.org/system/files/working_papers/w24773/w24773.pdf)). The rule of thumb is an average over very different cases, because pass-through depends on the shock behind the move:

| Shock driving sterling | Pass-through to import prices |
|---|---|
| Domestic demand | below 40% after 5 quarters |
| Exogenous exchange-rate | 50% after 5 quarters |
| Monetary | about 85% by quarter 6 |

This explains why 2007–09 depreciation passed through at about 90% and why the model predicted only about 45% after the 2016 referendum.

Micro evidence complicates the aggregate story. Breinlich et al. find near-complete pass-through into import-intensive products after 2016, yet an aggregate ERPT of only **0.29**. The depreciation raised consumer prices by about 2.9% ([IER 2022](https://ideas.repec.org/a/wly/iecrev/v63y2022i1p63-93.html)). The ONS found that half of the rise in CPI inflation over 2015–17 came from items with more than 25% import intensity ([ONS, July 2019](https://www.ons.gov.uk/economy/nationalaccounts/uksectoraccounts/compendium/economicreview/july2019/exchangeratepassthroughandtransmissiontoconsumerpricesfollowingthe2015to2016depreciationofsterling/pdf)). The design lesson is that a sterling move is not a clean exogenous cost-push shock. A depreciation driven by weak domestic demand arrives with its own disinflationary offset, so the dashboard should not add the full rule-of-thumb pass-through on top of its slack block.

**Second-round effects** in the UK ran mainly through wages rather than de-anchored long-run expectations. In the UK Bernanke–Blanchard system ([Haskel, Martin & Brandt 2023](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/november/recent-uk-inflation-an-application-of-the-bernanke-blanchard-model-paper.pdf); [ESCoE 2025](https://escoe-website.s3.amazonaws.com/wp-content/uploads/2025/09/24140421/ESCoE-DP-2025-12-2.pdf)):
- Wage persistence is higher than in the US (lagged-wage sum **0.60** versus 0.46).
- Wages are far more sensitive to tightness: the long-run V/U elasticity is about 2.0, versus 0.75 in the US.
- Energy, food and supply-chain shocks together added about **1pp to wage growth** over 2022–23 through expectations and catch-up.
- Labour-market tightness added 0.5–1.8pp to inflation over 2022–23.
- Long-run expectations stayed close to anchored: own-lag 0.99, loading on current inflation 0.01.

The long-run price-equation multipliers show where UK cost-push persistence lives. The multiplier is **0.02 for relative energy** but **0.44 for relative food**, and both are measured relative to wages.

Expectations respond to salience rather than CPI weight:
- **Households.** When media coverage of energy is high, a 1pp petrol-driven rise in inflation moves household expectations by **nearly 3pp in the short term** and about 0.5pp in the longer term ([Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)).
- **Firms.** Their year-ahead own-price expectations rise about 0.3pp per 1pp of headline inflation, and they respond more strongly to rises than to falls ([Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)).
- **Food.** Lombardelli notes that food prices "have an outsized effect on households' inflation perceptions and expectations" ([BoE, Sept 2026](https://www.bankofengland.co.uk/speech/2026/september/clare-lombardelli-speech-at-the-sixth-biennial-conference-poland)).

That is why the dashboard should track food separately from energy, and treat petrol and utility bills as expectations shocks as well as price-level shocks.

## State dependence roughly doubles the stakes above 3% inflation and in tight labour markets

The evidence for regime dependence is now strong and UK-specific.

**The inflation threshold.** The BoE's November 2025 MPR found that shocks "tend to have a bigger impact on inflation when inflation is already above 3% to 4%" ([BoE MPR Nov 2025](https://www.bankofengland.co.uk/monetary-policy-report/2025/november-2025)). Bank staff then estimated a self-exciting threshold BVAR on monthly UK data from 1989 to 2025 ([Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)):
- Household expectations become oil-sensitive above a headline CPI threshold of about **3.1%**. About 70% of 100 specifications put the threshold below 3.6%.
- The wage-growth threshold is about **4.6%**. Wage growth was below it in 2011 and above it in 2022.
- Inflation "responds more forcefully and persistently in a tight labour market than a loose one", whether or not inflation is above 3.1%, and "the difference becomes more extreme when inflation is high". The shock used is a Känzig oil-supply news shock that raises sterling oil prices by 10%.

The underlying paper has not yet been published: it is forthcoming as a Macro Technical Paper. The 3.1% figure should therefore be treated as a speech-reported point estimate.

**Firm pricing.** The DMP shows a structural shift toward faster pass-through. State-dependent pricers rose from 44% of firms in 2019 to about 60% in 2023, and were still 54% in late 2025. These firms' prices "respond more strongly to cost shocks", and more so for bigger shocks ([BoE SWP 1166](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2026/state-and-time-dependent-pricing.pdf)).

**Cross-country evidence** agrees on the direction:
- BIS: sectoral price spillovers explain about **20% of inflation variance after 1986 versus over 45% in 1965–85**. Transitions to high inflation are "self-reinforcing" ([BIS AER 2022](https://www.bis.org/publ/arpdf/ar2022e2.pdf)).
- ECB: small energy increases "trigger no significant reaction in prices", while larger shocks "have disproportionately stronger effects" ([Lagarde 2026](https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260325~ac2916a211.en.html)).
- Ball, Leigh and Mishra: headline shocks pass into core strongly when positive and negligibly when negative ([NBER w30613](https://www.nber.org/system/files/working_papers/w30613/w30613.pdf)).

The main dissent is Alvarez and Kroen at the IMF. Across 30+ countries, advanced-economy non-linearities "were already present pre-Covid and did not strengthen significantly after 2020" ([IMF WP 2025/091](https://www.imf.org/-/media/files/publications/wp/2025/english/wpiea2025091-print-pdf.pdf)). The two views are compatible. Much of 2022's amplification can come from shock *size* meeting a convexity that was always there, plus labour-market tightness, without any structural break. For the dashboard, this argues for modelling size non-linearity and state interactions explicitly, rather than a regime-switching break.

**2011 versus 2022.** This is the UK's natural experiment, and it isolates the labour market as the binding condition ([Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)):

| | 2011 | 2022 |
|---|---|---|
| Headline and food inflation vs threshold | Above | Above |
| Energy CPI inflation peak | 18% | 59% |
| Unemployment | about 8% | about 4% |
| Output gap | Negative | Positive |
| Main output-price driver after the shock | Margin rebuilding | Unit labour costs |
| Second-round effects (BIM trend component) | Smaller | Larger and more persistent |

**2026.** The episode fits the same pattern ([BoE MPS Sept 2026](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026); [Lombardelli 2026](https://www.bankofengland.co.uk/speech/2026/september/clare-lombardelli-speech-at-the-sixth-biennial-conference-poland); [Greene 2026](https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/here-we-go-again-assessing-the-inflation-risks-of-the-recent-energy-shock-speech-by-megan-greene.pdf)):
- Brent is up 36% and UK wholesale gas up 78% since July.
- CPI was **3.1% in August**. About **0.7pp of the 1.1pp overshoot** was direct energy, mostly motor fuel. CPI is projected slightly above 4% in early 2027.
- Services inflation is 3.4%. Private regular pay is 2.9% on a three-month annualised basis, with underlying pay about 3.5%, well below the 4.6% wage threshold.
- Indirect pass-through has been "weaker than expected": the MPC projected about 0.3pp by August and saw less. Firms are absorbing costs.
- Household one-year expectations jumped from **3.3% to 5.4%** within a month of the shock.
- DMP firms' own-price expectations rose from 3.4% to 4.4%.

So the expectations channel has fired while the wage channel has not. The MPC vote has drifted from 9–0 (March) to 8–1, 7–2 and **6–3 (September)**, with the minority wanting 4%. This is the "cumulative risk" doctrine at work: weight on the cost-push block rises with the **duration** of the shock, not only its size.

The IMF's 2026 Article IV makes the dovish case: pass-through to core "should be more limited, given the weak labor market, slow wage growth, and a negative output gap" ([IMF 2026](https://www.imf.org/-/media/files/publications/cr/2026/english/1gbrea2026001.pdf)). Greene makes the hawkish one: "the risk of acting, even if inflation proves to be less persistent, is less severe than the risk of failing to act" ([BoE, Jun 2026](https://www.bankofengland.co.uk/speech/2026/june/megan-greene-speech-at-university-of-derby-business-school)). A dashboard cannot settle that disagreement. What it can do is show transparently which state variables have switched on.

## Three free-data estimators cover first versus second round

**The UK Bernanke–Blanchard system** is the most directly usable first-versus-second-round framework ([Haskel, Martin & Brandt 2023](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/november/recent-uk-inflation-an-application-of-the-bernanke-blanchard-model-paper.pdf)). It has four OLS equations:
- wages, on lagged wages, short-run expectations, V/U, catch-up and productivity;
- prices, on lagged prices, wages, relative energy, relative food, shortages and productivity;
- short-run expectations;
- long-run expectations.

The specification uses quarterly annualised log changes, four lags, homogeneity restrictions and 2020Q2–Q3 dummies, estimated on 1990Q1–2023Q2. Energy and food enter relative to wages "to avoid inflation being on both sides of the equation".

A useful diagnostic comes with it. Long-run energy and food coefficients near their CPI basket shares mean no indirect or second-round effects, and coefficients above the shares mean there are some. The cross-country project finds UK energy and food effects "only slightly larger than the share" ([Bernanke & Blanchard, NBER w32532](https://www.nber.org/system/files/working_papers/w32532/w32532.pdf)), with code at PIIE. Adding non-energy import prices or sterling improved fit slightly, but the summed coefficients were insignificant because they co-move with food.

Three free-data substitutions are needed:
- raw ONS AWE private regular pay instead of the Bank's furlough-adjusted series;
- a composite of the BoE/Ipsos Inflation Attitudes Survey, gilt breakevens and the Survey of External Forecasters instead of Citi/YouGov;
- the NY Fed GSCPI instead of Google Trends "shortage", which cannot be automated reliably.

**Local projections** on external oil shocks give horizon-specific pass-through into headline, core, services, wages and expectations. In population, LPs and VARs estimate the same impulse responses. In finite samples, LPs have lower bias but much higher variance at medium horizons, so "shrinkage via Bayesian VARs or penalized LPs is attractive" ([Li, Plagborg-Møller & Wolf 2024](https://www.sciencedirect.com/science/article/pii/S030440762400068X)).

The natural instrument is the Känzig oil-supply news shock. It is free (CC-BY) and updated about every six months with a lag of four to five months ([GitHub](https://github.com/dkaenzig/oilsupplynews)), and the BoE uses it in its threshold VAR. Baumeister–Hamilton supply and demand shocks run to 2026M3 and are a robustness alternative ([Baumeister data](https://sites.google.com/site/cjsbaumeister/datasets)).

Gas is the weak point: this research found no free, maintained UK gas-shock series. The closest benchmark is the ECB's BSVAR, where a 10% gas supply shock raises euro-area headline inflation by about 0.6pp after a year, with about 75% of the three-year effect indirect ([ECB WP 2968](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2968~e514c92723.en.pdf)).

**The Ball–Leigh–Mishra headline-shock equation** captures non-linear, asymmetric pass-through into underlying inflation. It regresses median inflation minus long-run expected inflation on cubic functions of 12-month-averaged V/U and H = headline minus median. The H² and H³ terms are significant, with coefficients of 0.089 and 0.031. Using ex-food-and-energy core instead of the weighted median gives "almost no evidence" of pass-through ([NBER w30613](https://www.nber.org/system/files/working_papers/w30613/w30613.pdf)). The ONS does not publish a UK weighted median, so it has to be built from item-level indices and weights.

Two further tools are optional. Sector-level error-correction models on supply-use tables and PPI/SPPI reproduce the Bank Underground pipeline estimates. Gordon-style triangle models are the historical precedent ([Gordon 2013](https://www.nber.org/system/files/working_papers/w19390/w19390.pdf)).

## Decompositions are useful, but no central bank publishes a sign-identified VAR forecast

There are two families of demand-versus-supply decomposition.

**Shapiro's category method** estimates small price-and-quantity VARs for each expenditure category. It labels a category-month "demand" when the unexpected parts of price and quantity move in the same direction, and "supply" when they move in opposite directions. It then sums expenditure-weighted inflation within each label, so the pieces add up to headline ([FRBSF WP 2022-18](https://www.frbsf.org/wp-content/uploads/sites/4/wp2022-18.pdf)). The method has been validated against external shocks:
- a monetary tightening lowers demand-driven inflation by 1.5pp over 24 months;
- a 10% oil rise raises supply-driven inflation by about 15bp.

The FRBSF publishes the only regularly updated public central-bank demand/supply inflation series, monthly on 10-year rolling windows ([FRBSF](https://www.frbsf.org/research-and-insights/data-and-indicators/supply-and-demand-driven-pce-inflation/)). The UK appears only in cross-country studies:
- The OECD, using 110 COICOP categories, found **around half of UK headline inflation in 2022Q2 was demand-driven**, about 4pp above 2019 ([OECD Ecoscope](https://oecdecoscope.blog/2023/02/14/if-its-not-one-thing-its-another-supply-and-demand-factors-driving-rising-inflation/)).
- BIS estimates of "targeted Taylor rules", including the UK, find policy rates respond **3.26 to demand-driven versus 0.77 to supply-driven inflation** ([BIS QR Dec 2024](https://www.bis.org/publ/qtrpdf/r_qt2412d.pdf)). That is the revealed-preference counterpart of look-through.
- The ONS's own 2023 split is a different, item-classification method. It attributes roughly half of 2022 CPI directly to food and energy ([ONS](https://www.ons.gov.uk/economy/inflationandpriceindices/articles/demandandsupplyfactorsincpiinflation/2021to2022)).

The critique is serious. Read shows that sign restrictions only set-identify these decompositions. For US aggregate inflation, the supply contribution to a 7.7pp forecast error at the 2022Q2 peak could lie anywhere between **0.2 and 7.3pp** ([Read 2026](https://arxiv.org/html/2609.06907)). A UK version would also decompose the quarterly household-consumption deflator rather than CPI, because monthly CPI has no matching quantities.

**Sign-identified structural VARs** are the second family, and the BoE now documents one ([Brignone & Piffer, MTP No. 3](https://www.bankofengland.co.uk/-/media/boe/files/macro-technical-paper/2025/a-structural-var-model-for-the-uk-economy.pdf)):
- **Variables:** eight quarterly series, namely world GDP, world CPI, real sterling oil price, Bank Rate, sterling ERI, UK CPI, UK CPI energy and UK GDP.
- **Sample and priors:** 1992Q1–2023Q2, a Minnesota plus sum-of-coefficients prior, and a pandemic prior on the Covid dummies.
- **Identification:** six shocks identified with Arias–Rubio-Ramírez–Waggoner sign and zero restrictions. The world energy shock is separated from world supply by the sign on the oil price and CPI energy, and the UK is treated as block-exogenous (a small open economy).
- **Results:** in 2022, UK CPI "was pushed up by all the shocks identified", with global demand strongest. The authors warn that "estimation uncertainty remains high".
- **Use:** internal to the MPC process and in speeches. The Bank deliberately excludes the final year of data from estimation because of revisions. Its novel output is a structural decomposition of **forecast revisions**, not a published forecast.

Bergholt et al. show that historical decompositions are a "roller coaster" unless the deterministic component is pinned down with a single-unit-root prior. With that prior, demand shocks dominate the recent surge in several economies ([Norges Bank WP 7/2024](https://www.norges-bank.no/en/news-events/publications/Working-Papers/2024/wp-72024/)). The Bernanke Review treats VARs as "useful checks" within a model suite and recommends scenarios, not published VAR forecasts ([Bernanke Review](https://www.bankofengland.co.uk/-/media/boe/files/independent-evaluation-office/2024/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review.pdf)). An open-source Python replication of the BoE model exists, built on free OECD and IMF proxies, and it matches the original qualitatively ([PolicyEngine/boe-var-model](https://github.com/PolicyEngine/boe-var-model)).

## Recommendations for the dashboard

### 1. Weight cost-push in three tiers, scaled by a capped state multiplier

The following design is a synthesis calibrated to the evidence above. No central bank or paper publishes an official numerical weight on first-round energy.

**Tiers and base weights.** Each weight is expressed as a share of a 1pp contribution to the inflation-pressure score.

| Tier | Indicators (free data) | Base weight | Rationale |
|---|---|---|---|
| A. Direct first-round | ONS contributions of energy (04.5 + 07.2.2) to 12-month CPI; Ofgem cap path | **0.1** | Aoki; outside policy's reach within lags; small weight only for salience-driven expectations |
| B. Pipeline and indirect | Input PPI, non-energy import prices, sterling ERI change (after any Forbes-type shock split), food CPI, energy-exposed core-goods and services components | **0.4** | UK services pass-through about 0.4 long run; network theory weights upstream prices |
| C. Second round | Services CPI, private regular pay and settlements, DMP own-price expectations, IAS/one-year household expectations including upper tail | **1.0**, but housed in the expectations and domestic-slack blocks | Theory and practice say respond fully; keep outside the cost-push block to avoid double counting |

Use relative prices (energy and food relative to wages or core), not raw levels, and weight positive shocks more than negative ones: for example, apply max(H, 0) plus an H² term, following Ball–Leigh–Mishra and the pass-through asymmetry.

**State multiplier.** Apply M_t = min(2.5, 1 + 0.5·S_π + 0.5·S_L + 0.3·S_E + 0.2·S_D) to tiers A and B, with each state entering as a smooth 0–1 logistic rather than a hard switch:
- **S_π:** 12-month CPI relative to a 3.1% threshold, with a transition band of about ±0.5pp.
- **S_L:** V/U relative to its pre-pandemic median, or private regular pay relative to 4.6%.
- **S_E:** the change in household one-year expectations or their upper tail, or DMP price expectations above their pre-shock level.
- **S_D:** shock duration beyond two quarters, reflecting the "cumulative risk" doctrine.

Sterling depreciation can enter as a further term, following Mann's argument for amplification.

The 2.5 cap roughly matches the BIS ratio of sectoral-spillover variance between the two regimes (45% vs 20%). Once estimated, the multiplier should be replaced by the high-state to low-state ratio of impulse responses (β^H/β^L) from the state-dependent LP below.

**Back-casts.** The multiplier gives about 2.5 for 2022, when every state was on. For 2011 it gives about 1.5–1.7: inflation was high but the labour market was loose. For September 2026 it gives about 1.6–1.8: CPI is at the threshold, expectations have jumped and the shock has lasted beyond two quarters, but the labour market is loose. This ordering matches the MPC's revealed judgement and the 6–3 split.

### 2. Estimate three core specifications on UK data

**(i) A UK Bernanke–Blanchard four-equation system.**
- Quarterly, 1990Q1 to latest, four lags, homogeneity imposed, 2020Q2–Q3 dummies.
- Report pre-2019Q4 and full-sample estimates side by side.
- Energy should enter with longer lags or aligned to Ofgem cap timing.
- Use its long-run multipliers, minus CPI shares, to set the tier-B weights.

**(ii) A monthly LP-IV of cumulative log price changes over h = 0–36.**
- Sample: 1993 or 1997 onward.
- Outcomes: CPI, CPI energy, core, services and AWE, plus quarterly expectations.
- Instrument: Δlog Brent in sterling instrumented with the Känzig shock, normalised to a 10% oil rise. Baumeister–Hamilton shocks as a robustness check.
- Controls: 12 lags of the ERI, unemployment and the dependent variable.
- State interaction: shock × lagged state, with the state defined as CPI > 3% or V/U above median.
- Report smoothed LP or BVAR as the headline and raw LP as robustness. Wide bands are unavoidable, because the UK has few high-inflation months: roughly 1990–92, 2008, 2011 and 2021–23.

**(iii) A Ball–Leigh–Mishra core equation** using a self-built UK weighted-median CPI, with cubic V/U and H terms.

Add an exchange-rate block benchmarked to the 60%/20% rule, adjusted downward when depreciation coincides with weak domestic demand.

**Operations.** Re-estimate after ONS releases, not daily. Freeze and version data vintages. Pull Känzig vintages from GitHub with graceful failure. Drive the "current" cost-push reading from observed prices (sterling Brent, gas and cap levels, CPI components), because the shock series end months in the past.

### 3. Include a sign-identified VAR as a historical decomposition only

Publish a quarterly, BoE-MTP-3-style BVAR:
- sample 1992Q1 onward;
- Minnesota plus sum-of-coefficients or single-unit-root prior, with pandemic dummies;
- demand, supply, energy and monetary shocks identified by sign and zero restrictions;
- estimation window ending about a year before the data end.

Present it as a stacked historical decomposition of recent CPI inflation with credible bands, labelled "model-based illustration". Use it as a cross-check on the pressure score. When the energy and world-supply shares dominate and the domestic-demand share is small, look-through is being validated. When the demand share grows during an energy shock, the multiplier logic is being validated.

Do **not** publish unconditional SVAR forecasts. No central bank found in this research does so, the Bernanke Review points toward scenarios instead, and a forecast would compete with the MPR while carrying identification uncertainty as wide as Read's 0.2–7.3pp range. The one defensible forward-looking use is a **conditional energy-shock scenario**: the model's energy impulse responses scaled to futures-implied oil and gas paths, shown next to the BoE's own scenarios. An optional quarterly Shapiro-style split of the household-consumption deflator (four lags, 40-quarter rolling window, ambiguous band) can sit alongside, with an explicit set-identification caveat.

## Conclusion

The main change in understanding since 2022 is that "look through or not" is the wrong binary for a dashboard. The useful question is how much of a cost-push shock the prevailing state converts into persistence. UK evidence identifies which states matter: headline inflation near 3%, wage growth near 4.6%, a tight labour market, and salient petrol and food prices. So the cost-push block becomes a small, mostly informational term when conditions are benign. When all the states are on, it becomes a leading indicator carrying roughly twice to two-and-a-half times its normal weight.

The 2026 shock is an uncomfortable middle case. Expectations have moved while wages have not, which is exactly why the MPC is split. A dashboard that shows its state switches openly will be more credible than one that returns a single verdict. The largest remaining uncertainties are the unpublished BoE threshold estimates, the lack of a free UK gas-shock instrument, and the thin sample of high-inflation UK months. Each is a reason to show bands and ranges alongside point scores.
