# Looking Through Cost-Push Shocks: Theory and Central-Bank Practice (UK focus, to Sept 2026)

Notes for weighting a "cost-push" block in a UK inflation-pressure score. Items marked **[verified this session]** were read or confirmed from a fetched or searched primary source during this research. Items marked **[from literature; not re-fetched]** are standard citations whose bibliographic details are well established, but I did not re-open the source this session. The report writer should treat quotes in the second category as paraphrase unless checked.

**Big context:** a new energy shock is under way in 2026. Conflict involving Iran has effectively closed the Strait of Hormuz and led to attacks on Gulf energy infrastructure, including Qatar's Ras Laffan. It is the live test case for the look-through doctrine. As of the MPC decision of 17 Sept 2026, Bank Rate was held at 3.75% on a **6–3 vote, with three members voting to hike to 4%**. ([BoE MPS Sept 2026](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026)) [verified this session]

---

## Q1. What do the canonical models imply?

### Takeaway
In the baseline one-sector New Keynesian model, policy should look through an energy or productivity shock only if it moves the efficient level of output and creates no inefficient cost-push wedge. That is "divine coincidence". Real-wage rigidity (Blanchard–Galí), sectoral heterogeneity in price stickiness (Aoki; Rubbo), and production networks or sectoral reallocation (La'O–Tahbaz-Salehi; Guerrieri et al.) each break divine coincidence. In those models the optimal policy:
- stabilises a sticky-price, core-like or "divine-coincidence" index rather than headline CPI;
- accepts some first-round headline inflation; and
- trades off any remaining cost-push component against the output gap.

The models support responding to core and domestic inflation, not headline, but only partial look-through of the cost-push wedge itself.

### Cited Findings

**Textbook cost-push trade-off (Clarida–Galí–Gertler 1999; Woodford 2003; Galí 2008/2015)**
- In the canonical NK model, an exogenous cost-push shock (u_t) in the Phillips curve creates a genuine output–inflation trade-off. Optimal discretionary policy "leans against the wind" and splits the shock between inflation and a negative output gap, in proportion to the relative weight on output (λ) and the Phillips-curve slope (κ).
- Under commitment, the optimal policy keeps the price level or inflation response more muted and more persistent ("history dependence"), which stabilises expectations. — Clarida, Galí & Gertler (1999), "The Science of Monetary Policy", *JEL* 37(4) ([NBER w7147](https://www.nber.org/papers/w7147)); Woodford (2003), *Interest and Prices*, ch. 7; Galí (2015), *Monetary Policy, Inflation, and the Business Cycle*, ch. 5. [from literature; not re-fetched]
- The BoE's own 2026 exposition of its remit uses exactly this loss function, L = E Σ β^s[(π−π*)² + λ(y−y*)²]. It argues that the remit's "trade-off" language is "arguably too passive: to achieve the best feasible outcome ... requires a tightening of monetary policy to balance the incidence of losses". — Harrison & Waldron, "The MPC's remit and trade-off management", *Bank Insights*, 29 May 2026 ([BoE](https://www.bankofengland.co.uk/bank-insights/2026/the-mpcs-remit-and-trade-off-management)) [verified this session]

**Blanchard & Galí**
- **"Real Wage Rigidities and the New Keynesian Model"** (*JMCB* 2007, Supplement 39(1); [NBER w11806](https://www.nber.org/papers/w11806)). This paper coined "divine coincidence": in the standard NK model, stabilising inflation also stabilises the welfare-relevant output gap, so supply shocks pose no trade-off. Adding real-wage rigidity breaks this. Oil and productivity shocks then generate an endogenous cost-push term, and the central bank faces a real trade-off. [from literature; not re-fetched]
- **"The Macroeconomic Effects of Oil Price Shocks: Why are the 2000s so different from the 1970s?"** (NBER w13368, 2007; in Galí & Gertler (eds.), *International Dimensions of Monetary Policy*, NBER/U. Chicago Press 2010; [NBER w13368](https://www.nber.org/papers/w13368)). Oil shocks in the 2000s had much smaller effects on inflation and output than in the 1970s. The paper attributes this to three factors, which are exactly the "look-through works" conditions:
  1. lower real-wage rigidity (weaker wage indexation);
  2. greater monetary-policy credibility (better-anchored expectations);
  3. a smaller oil share in consumption and production.

  It also found that 1970s shocks coincided with other large adverse shocks (commodities, etc.). [from literature; not re-fetched]

**Aoki (2001)**
- "Optimal monetary policy responses to relative-price changes", *Journal of Monetary Economics* 48(1): 55–80 ([ScienceDirect](https://doi.org/10.1016/S0304-3932(01)00069-1)). In a two-sector model with one flexible-price sector (e.g. energy or food) and one sticky-price sector:
  - optimal policy fully stabilises **sticky-price (core) inflation**;
  - it lets flexible-price relative-price movements pass into headline;
  - this also closes the welfare-relevant output gap.

  This is the formal basis for "target core, not headline". Benigno (2004, *JIE*) generalises the result: weight each sector by its degree of price stickiness. [from literature; not re-fetched]
- Related: Mankiw & Reis (2003), "What Measure of Inflation Should a Central Bank Target?", *JEEA* 1(5). Their optimal "stability price index" puts high weight on sectors that have sticky prices, are cyclically sensitive, and have small idiosyncratic shocks. Energy scores near zero on all three. [from literature; not re-fetched]

**Rubbo (2023)**
- "Networks, Phillips Curves, and Monetary Policy", *Econometrica* 91(4): 1417–1455 ([Wiley](https://onlinelibrary.wiley.com/doi/full/10.3982/ECTA18654); [Econometric Society](https://www.econometricsociety.org/publications/econometrica/2023/07/01/Networks-Phillips-Curves-and-Monetary-Policy)). [verified this session]
  - With input–output linkages, the slope of sectoral and aggregate Phillips curves falls as intermediate-input shares rise. Productivity fluctuations then endogenously generate an inflation–output trade-off, **"except when inflation is measured according to the novel divine coincidence index"** (DCI).
  - The DCI weights sectors by price stickiness and network position. It gives a Phillips curve with a 2–4× larger R² than CPI specifications, and a slope that is stable and correctly signed in 20-year rolling windows. CPI-based slopes are often insignificant or wrongly signed, because CPI "suffer[s] from productivity-driven cost-push shocks".
  - The constrained-optimal policy "must tolerate relative price distortions across firms and sectors in order to stabilize the output gap". It can be implemented via a Taylor rule on the DCI.

**La'O & Tahbaz-Salehi (2022)**
- "Optimal Monetary Policy in Production Networks", *Econometrica* 90(3): 1295–1336 ([NBER w27464](https://www.nber.org/papers/w27464)).
  - Optimal policy stabilises a price index that puts more weight on sectors that are larger, stickier, and (importantly) **more upstream** in the network.
  - The optimal target is therefore not core CPI: upstream input sectors (which can include energy-intensive intermediates) may deserve weight even if their consumer prices are flexible. This qualifies a naive "strip out energy" rule. [from literature; not re-fetched]

**Guerrieri, Lorenzoni, Straub & Werning (2021)**
- "Monetary Policy in Times of Structural Reallocation", Jackson Hole Symposium proceedings, Aug 2021 ([KC Fed PDF](https://www.kansascityfed.org/documents/8322/JH_Guerrieri.pdf); [BFI WP 2021-111](https://bfi.uchicago.edu/wp-content/uploads/2021/09/BFI_WP_2021-111.pdf)). [verified this session]
  - Asymmetric sectoral shocks with downward nominal-wage rigidity act as an **endogenous cost-push shock, breaking divine coincidence**.
  - Optimal policy lets inflation exceed target **"despite elevated unemployment"**, which facilitates reallocation.
  - This theory supports *tolerating* first-round relative-price-driven inflation.

**Bernanke, Gertler & Watson (1997)**
- "Systematic Monetary Policy and the Effects of Oil Price Shocks", *Brookings Papers on Economic Activity* 1997(1): 91–157 ([Brookings](https://www.brookings.edu/articles/systematic-monetary-policy-and-the-effects-of-oil-price-shocks/)).
  - VAR counterfactuals suggest much of the output decline after postwar US oil shocks came from the endogenous Fed tightening, not the oil shock itself.
  - Critique: Hamilton & Herrera (2004, *JMCB*) argued the counterfactual violates the Lucas critique and understates oil effects. Kilian & Lewis (2011, *Economic Journal*) found no evidence that Fed responses to oil shocks amplified output declines after 1987. [from literature; not re-fetched]

### Inferences
- Theory gives three distinct objects, and a UK dashboard should keep them separate:
  1. **the flexible-price first-round level effect** (energy in CPI), which theory says to look through almost entirely (Aoki);
  2. **the cost-push wedge from rigidities or networks** (Blanchard–Galí; Rubbo; La'O–Tahbaz-Salehi), which calls for a *partial* response, with weight rising in κ and falling in λ;
  3. **expectations and second-round effects**, which call for a full response.
- The network literature implies energy is not "zero weight". Its indirect pass-through into core and services via intermediate inputs is the part that matters. A cost-push block should weight **upstream and pipeline prices** (PPI inputs, wholesale gas/electricity), not the retail energy CPI component.

### Gaps
- I did not re-fetch Blanchard–Galí, Aoki, La'O–Tahbaz-Salehi or BGW this session, so no verbatim quotes are given for them.
- I found no paper that gives a single numerical "optimal weight on headline energy" for the UK. The DCI weights are country-specific, and Rubbo estimates them for the US.

---

## Q2. When does look-through fail?

### Takeaway
Look-through is regime-dependent. It works when:
- inflation starts low (the "low-inflation regime");
- expectations are anchored;
- the labour market is slack;
- the shock is small and short-lived;
- policy is not already stimulative.

It fails, or becomes costly, when shocks are large, persistent or successive, starting inflation is high, labour markets are tight, and agents have "lived experience" of inflation. In that case expectations turn backward-looking and wage–price feedback strengthens. The 2021–23 episode is the main evidence. Official judgement (BIS, Reis, ECB, BoE) is that look-through was over-applied then.

### Cited Findings

**BIS Annual Economic Report 2022, ch. II, "Inflation: a look under the hood"** ([PDF](https://www.bis.org/publ/arpdf/ar2022e2.pdf); [AER 2022](https://www.bis.org/publications/aer-2022)) [verified this session]
- There are two regimes. In a low-inflation regime inflation "mainly reflects changes in sector-specific prices and exhibits certain self-equilibrating properties". Salient price changes (energy, food, housing) "tend to leave only a temporary imprint".
- Sectoral price spillovers explain about **20% of inflation variance post-1986, versus over 45% in 1965–85**. Pass-through of oil and exchange-rate shocks, and of wages to prices, "becomes more muted at lower inflation rates".
- Transitions to high inflation are **self-reinforcing**: price increases move out of the zone of "rational inattention", workers try to recoup real income, and firms protect margins.
- "Monetary policy can afford to be more flexible in a low-inflation regime ... and it needs to be especially timely and decisive during transitions". Also: "waiting until signals are unequivocal heightens the risk that inflation will become entrenched". ([BIS overview](https://www.bis.org/publ/arpdf/ar2022e_ov.htm))
- Borio's related work (Borio, Lombardi, Yetman & Zakrajšek, "The two-regime view of inflation", BIS Papers No 133, 2023) develops the same framework. [from literature; not re-fetched]

**Reis (2022)**, "The Burst of High Inflation in 2021–22: How and Why Did We Get Here?" (BIS WP 1060 / CEPR DP17514; [BIS](https://www.bis.org/publ/work1060.htm); [LSE PDF](https://personal.lse.ac.uk/reisr/papers/22-whypi.pdf)) [verified this session]
- Four hypotheses for central-bank failure:
  1. misdiagnosis of the shocks;
  2. **neglect of expectations data**, due to "a strong belief that inflation expectations were firmly anchored and that inflation increases would thus be temporary";
  3. over-reliance on past credibility;
  4. strategy revisions that tolerated higher inflation.
- Conclusion: "inflation rose because central banks allowed it to rise". Reis stresses that the *tails and dispersion* of household expectations drift before the median does. His Annual Review piece (2025, "Why Did Inflation Rise and Fall in 2021–2024?", [Annual Reviews](https://www.annualreviews.org/content/journals/10.1146/annurev-economics-051624-072332)) extends this.

**IMF World Economic Outlook**
- **Oct 2022, ch. 2, "Wage Dynamics Post–COVID-19 and Wage-Price Spiral Risks"** ([PDF](https://www.imf.org/-/media/files/publications/weo/2022/october/english/ch2.pdf); [blog](https://www.imf.org/en/blogs/articles/2022/10/05/wage-price-spiral-risks-appear-contained-despite-high-inflation)) [verified this session]
  - The IMF found **22 episodes over 50 years** in advanced economies resembling 2021. On average these did *not* produce wage–price spirals.
  - Risks were contained because the shocks came from outside the labour market, real wages were falling, and central banks were tightening. Note the conditionality: containment was attributed partly to tightening, not to look-through.
- **Oct 2023, ch. 2, "Managing Expectations: Inflation and Monetary Policy"** ([PDF](https://www.imf.org/-/media/Files/Publications/WEO/2023/October/English/ch2.ashx); [blog](https://www.imf.org/en/Blogs/Articles/2023/10/04/how-managing-inflation-expectations-can-help-economies-achieve-a-softer-landing)) [verified this session]
  - There is an **increasing role of near-term inflation expectations** in inflation dynamics.
  - "Inflationary supply shocks are long-lasting and monetary policy is less effective when expectations are backward-looking". Better frameworks and communication lower the output cost of disinflation.
- IMF blog, Sept 2022: "Energy Shocks Amid Rapid Inflation Could Fuel Faster Wage Gains" ([IMF](https://www.imf.org/en/blogs/articles/2022/09/12/cotw-energy-shocks-amid-rapid-inflation-could-fuel-faster-wage-gains)). This argues state dependence: energy shocks feed wages more when inflation is already high. [title verified; content not fetched]

**Federal Reserve Board, FEDS Note (15 Dec 2023)**, "Second-Round Effects of Oil Prices on Inflation in the Advanced Foreign Economies" ([Fed](https://www.federalreserve.gov/econres/notes/feds-notes/second-round-effects-of-oil-prices-on-inflation-in-the-advanced-foreign-economies-20231215.html)). This is directly relevant evidence on state-dependent second-round effects. [title verified; content not fetched]

**ECB (2026) on non-linearity and state dependence** ([Lagarde, 25 Mar 2026](https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260325~ac2916a211.en.html); [BIS review](https://www.bis.org/review/r260407d.htm)) [verified this session]
- ECB research: "the relationship between energy price shocks and inflation can be non-linear: while small increases trigger no significant reaction in prices, larger shocks have disproportionately stronger effects".
- Pass-through is stronger when capacity utilisation is high, unemployment is low and expectations are elevated. People now have "lived experiences of inflation".

**Powell (26 Aug 2022, Jackson Hole)** ([Fed](https://www.federalreserve.gov/newsevents/speech/powell20220826a.htm)) [verified via search snippet]
- "Supply shocks that drive inflation high enough for long enough can affect the longer-term inflation expectations of households and businesses."
- On expectations being self-fulfilling: if people expect low, stable inflation it likely will be, "absent major shocks", and "The same is true of expectations of high and volatile inflation."

**ECB 2021 lesson (Lane, 2026)**. When the 2022 shock hit, ECB policy was highly accommodative (deposit rate −0.5%, net asset purchases continuing), which "exacerbated the inflationary effects". "In the absence of demand pressures, the impact of supply-side shocks on inflation would have been considerably lower." ([Lane 13 May 2026](https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260513~5b14c78806.en.html); press reports via [FXStreet](https://www.fxstreet.com/news/ecbs-lane-even-if-initial-energy-shock-begins-to-ease-second-round-effects-will-persist-202605280029)) [verified this session]

### Inferences
Failure conditions for look-through, each usable as a state variable that *scales up* the dashboard weight on the cost-push block:

| Condition | Evidence |
|---|---|
| Starting inflation above ~3% or recent overshoot history | BIS two regimes; Greene's "7 of past 10 years" (see Q3) |
| Tight labour market (low unemployment, high V/U) | BIS; ECB; Aikman/NIESR; BoE 2026 contrast with 2022 |
| Large shock (non-linearity) | ECB 2026 |
| Persistent or successive shocks | BoE minutes 2026, "the longer higher energy prices persist"; Lombardelli "risk is cumulative" |
| Short-term or household expectations rising, tails fattening | Reis; IMF 2023; Mann 2022 |
| Loose starting policy stance | Lane 2026 |
| Depreciating currency amplifying import prices | Mann 2022 |

### Gaps
- I found no consensus quantitative threshold for the regime switch. The BIS uses the post-1986 vs 1965–85 split rather than a sharp inflation cut-off. Other BIS work sometimes cites roughly 5%, but I did not verify that figure this session.
- I did not fetch the IMF WEO April 2022/2023 chapters beyond the two above.

---

## Q3. What has the Bank of England said?

### Takeaway
The BoE remit has explicitly allowed temporary look-through of supply shocks since the 1997–2013 era of flexible inflation targeting. The 2013 and later remits add an explicit "trade-off" clause. MPC practice has swung:
- **2008–11 (King): looked through.** VAT, energy and sterling pushed CPI to 5.2%, and Bank Rate stayed at 0.5%.
- **2016–17 (Carney): tolerated an overshoot.** Sterling pass-through after the referendum was explicitly traded off against output.
- **2021–23: did not look through.** Tight labour market, rising expectations, successive shocks. Mann, Pill, Greene and Haskel pushed hardest. The Bernanke Review (2024) then criticised the forecasting machinery (COMPASS), which assumed expectations were anchored.
- **2026: conditional, vigilant look-through**, with a growing hawkish minority. The vote moved from 9–0 (Mar) through 8–1 (Apr) and 7–2 (Jun) to 6–3 (Sep).

### Cited Findings

**Remit / doctrine**
- The remit states that attempts to keep inflation at target in the face of shocks "may cause undesirable volatility in output due to the short-term trade-offs involved". The MPC "may wish to allow inflation to deviate from the target temporarily". — Harrison & Waldron, *Bank Insights*, 29 May 2026 ([BoE](https://www.bankofengland.co.uk/bank-insights/2026/the-mpcs-remit-and-trade-off-management)) [verified this session]
- BoE framing, as stated in 2026 MPC material and summarised in search: if lags imply policy mainly affects inflation beyond the initial-shock horizon, "it may be appropriate for monetary policy to look through those effects". However, the effect beyond that horizon "depends on both the persistence of the increase in energy prices and on the size of any second-round effects via price and wage setting, which in turn is likely to depend on prevailing conditions in the economy." ([BoE MPS April 2026](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/april-2026)) [search snippet; exact source paragraph not confirmed]

**King era (2008–11)**
- Open letters from Governor Mervyn King to the Chancellor, for example **16 May 2011** (CPI 4.5% in April) and **15 Aug 2011** (CPI 4.4% in July). They attributed the overshoot to the VAT rise to 20%, world commodity and energy prices, and import prices ex-energy up "by over 20%" after sterling's 2007–09 depreciation. The MPC expected inflation to fall back as these temporary factors unwound, and held Bank Rate at 0.5%. ([May 2011 letter](https://www.bankofengland.co.uk/-/media/boe/files/letter/2011/governor-letter-160511.pdf); [Aug 2011 letter](https://www.bankofengland.co.uk/-/media/boe/files/letter/2011/governor-letter-150811); [May 2010 letter](https://www.bankofengland.co.uk/-/media/boe/files/letter/2010/chancellor-letter-180510.pdf); [Aug 2010 letter](https://www.bankofengland.co.uk/-/media/boe/files/letter/2010/chancellor-letter-170810.pdf)) [letter existence and CPI figures verified via search; full text not extracted, since the PDFs were unreadable to the fetch tool]
- MPC members in 2026 now use 2011 as the benign template. Taylor (March 2026 minutes): the MPC "might look through a milder shock, as in 2011 when the MPC faced an energy shock against the backdrop of a weak labour market". ([BoE minutes Mar 2026](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/march-2026)) [verified this session]

**Carney era (2016–18): sterling depreciation**
- Post-referendum, sterling fell sharply and CPI peaked at 3.1% (Nov 2017), triggering open letters. The MPC's stated judgement, reported in search results from the 2016–18 letters: "fully offsetting the persistent effects of sterling's depreciation on inflation would require exerting further downward pressure on domestic costs, implying even more lost output and a total disregard for higher unemployment. Such outcomes would be undesirable in themselves and would be unlikely to generate a sustainable return of inflation to the target." The MPC described this as the remit's trade-off, with "limits to the extent to which above-target inflation can be tolerated". ([BoE letters index, e.g. Dec 2016 remit exchange](https://www.bankofengland.co.uk/-/media/boe/files/letter/2016/chancellor-letter-151216.pdf); [TSC oral evidence 25 Oct 2016](https://committees.parliament.uk/oralevidence/6172/html/)) [quote verified via search snippet; **which exact letter (Feb/Nov 2017 or Feb 2018) it comes from is not confirmed**]
- Carney, "[De]Globalisation and inflation", Sept 2017 ([BIS review](https://www.bis.org/review/r170920a.pdf)), gives the related argument on imported inflation. [title verified; not fetched]

**2021–23: why the MPC did not look through**
- **Broadbent, "Lags, trade-offs and the challenges facing monetary policy"**, Leeds University Business School, **6 Dec 2021** (not 2022) ([BoE](https://www.bankofengland.co.uk/speech/2021/december/ben-broadbent-speech-at-leeds-university-during-an-agency-visit-to-yorkshire-and-humber); [BIS review](https://bis.org/review/r211208b.htm)). The speech stresses that transmission lags mean policy cannot affect near-term inflation from energy and tradable goods, so the MPC must focus on the medium-term domestic picture. [existence/date verified; PDF text unreadable, no verbatim quote]
- **Broadbent, "The inflationary consequences of real shocks"**, Imperial College, **Oct 2022** ([BoE](https://www.bankofengland.co.uk/speech/2022/october/ben-broadbent-speech-at-imperial-college-the-inflationary-consequences-of-real-shocks)). [verified this session]
  - "monetary policy cannot undo the hit to real income. Nor could it ever have done." Policy can only prevent persistent inflation.
  - Numbers: real household income more than 3% lower, real non-North Sea income down over 5% since end-2019, and import prices up about 20% more than output prices over two years.
  - "it's unavoidable that we are having to learn about these [second-round] effects, and to respond to them, as they emerge."
- **Mann, "Inflation expectations, inflation persistence, and monetary policy strategy"**, MMF conference, **Sept 2022** ([BoE](https://www.bankofengland.co.uk/speech/2022/september/catherine-l-mann-53rd-annual-conference-of-the-money-macro-and-finance-society)). [verified this session] Mann rejects looking through external shocks because they "mean-revert". Her reasons:
  - short-term expectations risk becoming **adaptive**;
  - firms show "me-too-ism" and anticipatory price overshoots, producing a "persistent rise in desired mark-ups";
  - prices are downwardly rigid, so disinflation is asymmetric;
  - **sterling depreciation** amplifies imported inflation.

  She concludes that forceful tightening is the "robust" policy. See also her April 2022 speech "A monetary policymaker faces uncertainty" ([BoE](https://www.bankofengland.co.uk/speech/2022/april/catherine-l-mann-speech-at-a-boe-webinar-monetary-policy-decision-making-facing-uncertainties)): if 2021 wage settlements and price hikes repeated in 2022, inflation would stay above target longer, the "ratchet effect".
- Other 2022–23 speeches (titles verified, not fetched):
  - Pill, "Monetary policy with a steady hand" (Feb 2022, [BIS](https://bis.org/review/r220211g.htm)) and "Returning inflation to target" (Jul 2022, [BIS](https://bis.org/review/r220707a.htm));
  - Mann, "Expectations, lags, and the transmission of monetary policy" (Feb 2023, [BoE](https://www.bankofengland.co.uk/speech/2023/february/catherine-l-mann-speech-resolution-foundation));
  - Tenreyro, "The path to 2 per cent" (Nov 2022, [BoE](https://www.bankofengland.co.uk/speech/2022/november/silvana-tenreyro-keynote-speech-at-the-society-of-professional-economists-annual-conference)) and "Monetary policy in the face of large shocks" (Jun 2023, [PDF](https://www.bankofengland.co.uk/-/media/boe/files/speech/2023/june/monetary-policy-in-the-face-of-large-shocks-speech-by-silvana-tenreyro.pdf)). Tenreyro was the dovish counterpoint: energy shocks are contractionary and policy lags mean overtightening risks.
- **Bailey, "Reflecting on recent times"**, Jackson Hole, **Aug 2024** ([BoE](https://www.bankofengland.co.uk/speech/2024/august/andrew-bailey-speech-federal-reserve-bank-of-kansas-annual-jackson-hole-economic-policy-symposium)). This is Bailey's retrospective on 2021–23 persistence and second-round effects. [title verified; not fetched]

**Bernanke Review (12 Apr 2024)**, "Forecasting for monetary policy making and communication at the Bank of England: a review" ([Economics Observatory summary](https://www.economicsobservatory.com/why-did-the-bank-of-england-need-a-review-of-its-forecasting-record); [TSC evidence 15 May 2024](https://committees.parliament.uk/oralevidence/14819/html/); [arXiv discussion](https://arxiv.org/pdf/2501.07386)) [verified via search]
- The BoE "seriously underestimated" the inflationary impact of the 2022 energy shock and initially judged it transitory.
- The COMPASS model has the property that long-run inflation expectations are always anchored at target, so inflation always returns to 2% in the model.
- Recommendations: replace the fan chart, make more systematic use of **alternative scenarios**, de-emphasise the market-curve-conditioned central forecast, and overhaul models and software.
- **Relevance:** the review institutionalised scenario analysis for energy shocks, which the MPC used in 2026 (Taylor's scenarios; the July 2026 adverse scenario).

**2026 energy shock**
- **MPS 18 Mar 2026** (9–0 hold at 3.75%) ([BoE](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/march-2026)). [verified this session]
  - Bailey: policy cannot influence global energy prices but "must respond to the risk of a more persistent effect on UK CPI inflation".
  - Minutes: "The MPC was alert to the increased risk of domestic inflationary pressures through second-round effects in wage and price-setting, the risk of which would be greater the longer higher energy prices persist."
  - CPI projected to reach about 3½% vs 3% before the shock. Q2 2026 CPI about 3% vs 2.1%. Energy's direct contribution to Q3 is "around ¾ percentage points".
  - Greene: households are "more sensitive to upside surprises" after five years above target.
  - Mann: "sustained pressure on energy prices could re-embed the inflation persistence of the last few years".
  - Pill cited pay settlements of 3.6% for 2026.
  - Breeden and Ramsden would otherwise have voted to cut.
- **MPS 29 Apr 2026** (8–1 hold) ([BoE](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/april-2026)). The shock differs from 2022 because the energy-price increase was smaller, policy started more restrictive, and the labour market was weaker. Future pay demands "could come up against firms' margin constraints, a softer labour market and firms' caution about passing on cost increases". [verified via search snippet]
- **Taylor, "Stopping for gas"**, 26 Mar 2026 ([BoE](https://www.bankofengland.co.uk/speech/2026/march/alan-taylor-exante-datas-10-year-anniversary-macro-conference)). The UK is very sensitive to gas and oil prices, the starting point differs from past shocks, and scenario analysis shows "difficult trade-offs could lie ahead". [summary verified; PDF text unreadable]
- **Greene, "Here we go again? Assessing the inflation risks of the recent energy shock"**, Univ. of Derby, **2 Jun 2026** ([BoE](https://www.bankofengland.co.uk/speech/2026/june/megan-greene-speech-at-university-of-derby-business-school); [Derby report](https://www.derby.ac.uk/news/2026/the-case-for-hiking-rates-grows-as-iran-conflict-wears-on/)). [verified this session]
  - She contrasts 2011 (MENA unrest; energy up, limited second-round effects) with 2022 (persistent inflation).
  - "Inflation has exceeded our target in seven of the past 10 years."
  - "Should inflation remain above target now, there is a risk that households and firms come to see this as a 'new normal'."
  - "The risk of acting, even if inflation proves to be less persistent, is less severe than the risk of failing to act."
- **MPS 17 Jun 2026:** 7–2 hold, with two members voting to hike to 4%. ([BoE](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/june-2026)) [verified via search]
- **MPS 17 Sept 2026:** 6–3 hold. ([BoE](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026)) [verified this session]
  - Brent was up 36% and UK wholesale gas up 78% since July. Spot prices are near the July **adverse scenario**.
  - CPI was 3.1% in August, of which about **0.7pp of the 1.1pp overshoot was direct energy effects**, mostly motor fuels. CPI is projected to be "slightly above 4%" in early 2027.
  - Services inflation 3.4%. Private regular pay 2.9% (3m annualised), underlying about 3.5%.
  - There was "little evidence so far of material second-round effects", though these typically emerge with longer lags. Risk judged higher than in July.
  - Food-inflation moderation suggests delayed rather than diminished indirect effects.
- **Lombardelli (Deputy Governor), "The outlook for inflation"**, **24 Sept 2026** ([BoE](https://www.bankofengland.co.uk/speech/2026/september/clare-lombardelli-speech-at-the-sixth-biennial-conference-poland)). [verified this session]
  - "Monetary policy cannot prevent the initial rise in inflation caused by higher energy prices. Rather, its role is to ensure that temporary increases in inflation do not become persistent inflationary pressure."
  - "The key judgement for monetary policy is whether emerging evidence suggests inflation may become persistent. This risk is cumulative."
  - "The longer energy prices remain high and volatile, the greater the risk for pass-through more widely into domestic wages and prices."
  - "Food prices have an outsized effect on households' inflation perceptions and expectations."
  - Indirect effects have so far been smaller than expected, with firms absorbing costs.
- Pill, "Homophones", Edinburgh Chamber of Commerce, **Sept 2026** ([BoE](https://www.bankofengland.co.uk/speech/2026/september/remarks-at-the-edinburgh-chamber-of-commerce)). [title verified; not fetched]
- External view: **Aikman (NIESR), 19 Mar 2026** ([NIESR](https://niesr.ac.uk/blog/how-should-monetary-policy-respond-energy-price-shock)). [verified this session]
  - Brent about $115 (from about $60 at the start of the year), UK gas futures about 175p/therm (from about 70p).
  - Direct CPI impact "a little over one percentage point".
  - Under an aggressive rule, unemployment rises substantially "for a negligible reduction in inflation".
  - Lessons: second-round spirals depend on labour-market tightness, not the shock itself; **target domestic inflation, not headline CPI**; pair patience with scenario-based communication.

### Inferences
- The BoE's revealed reaction function treats first-round energy effects (about 0.7pp of CPI in 2026) as outside policy's reach. It reacts to the *interaction* of shock persistence with domestic conditions: pay settlements, services CPI, household expectations, and food prices as an expectations channel.
- The drift from 9–0 to 6–3 as energy prices persisted matches the "cumulative risk" doctrine. A dashboard should let the cost-push block's weight rise with the **duration** of the shock, not just its size.
- 2011 is the MPC's reference case for successful look-through (slack labour market). 2022 is the reference failure (tight labour market, loose policy, successive shocks).

### Gaps
- No verbatim text was extracted from the King 2008–11 or Carney 2016–18 open letters (the PDFs were unreadable to the fetch tool), and the Carney quote is not tied to a specific letter.
- Not fetched: Haskel speeches 2022–23; Bailey 2022 speeches; the Bernanke Review PDF itself.
- The Greene and Taylor 2026 speech PDFs were unreadable. Only summaries and quotes via secondary pages are included.

---

## Q4. ECB, Fed and other central banks

### Takeaway
All major central banks formally share a state-contingent look-through doctrine: look through small, temporary supply shocks, and respond as persistence and second-round risk rise. After 2022 the ECB formalised a graduated three-tier response, which is now the clearest official statement of the rule.

### Cited Findings
- **ECB three-tier framework**, Lagarde, "Navigating energy shocks: risks and policy responses", **25 Mar 2026** ([ECB](https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260325~ac2916a211.en.html)). [verified this session]
  1. **Small, short-lived shocks: look through.** "Transmission lags mean that a monetary policy response would arrive too late and risk being counterproductive."
  2. **Large but temporary: "some measured adjustment of policy could be warranted".**
  3. **Significant and persistent deviation: policy must be "appropriately forceful or persistent".**
  - Lagarde called the 2026 disruption "the largest supply disruption in the history of the global oil market". The ECB monitors firms' selling-price expectations and wage trackers for "tit-for-tat inflation".
- **Lane, "Analytical perspectives on energy supply shocks"**, **13 May 2026** ([ECB](https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260513~5b14c78806.en.html)). [verified this session]
  - First-round effects are direct energy plus indirect costs on non-energy goods. Second-round effects are when "the initial inflationary impulse feeds into wage-setting, the pricing and margin decisions of firms and inflation expectations".
  - Energy shocks also lower activity in energy-using sectors ("more slack ... putting downward pressure on inflation over the medium term").
  - Bayesian VAR: a geopolitical oil supply shock raising the real oil price by **10%** lowers euro-area GDP growth by about **0.2–0.3pp in each of the first three years**. Global shocks do more damage than regional ones via value chains.
  - Later (28 May 2026, press reports): second-round effects "would persist even after shock reversal". ([investingLive](https://investinglive.com/centralbank/ecb-policymaker-lane-says-second-round-effects-would-persist-even-after-shock-reversal-20260528/))
- **Lane, "Monetary policy after the energy shock"**, **16 Feb 2023** ([ECB](https://www.ecb.europa.eu/press/key/date/2023/html/ecb.sp230216~a297a41feb.en.html)). This is Lane's 2023 retrospective on the energy shock. [title verified; not fetched]
- **ECB 2021 strategy statement**: the appropriate response to deviations from target "is context-specific and depends on the origin, magnitude and persistence of the deviation". Medium-term orientation allows looking through supply shocks. ([ECB strategy statement](https://www.ecb.europa.eu/home/search/review/html/ecb.strategydocument202107~58864f0a7a.en.html)) [from literature; not re-fetched, so wording is approximate]
- **Fed:** Powell, 26 Aug 2022, Jackson Hole ([Fed](https://www.federalreserve.gov/newsevents/speech/powell20220826a.htm)); see Q2. Traditionally the Fed looks through supply shocks when expectations are anchored. In 2022, supply shocks "high enough for long enough" threatened expectations. Press reports from 31 Mar 2026 say Powell called the 2026 energy shock "manageable for now" while flagging deeper inflation risks ([Malay Mail](https://www.malaymail.com/news/money/2026/03/31/us-fed-chief-says-energy-shock-manageable-for-now-but-flags-deeper-inflation-risks/214525)). [secondary source]
- **Bank of Canada and RBNZ:** their frameworks traditionally direct the bank to look through first-round effects of relative-price and supply shocks (energy, indirect taxes) while guarding medium-term expectations. The pre-2019 RBNZ Policy Targets Agreements listed supply shocks, commodity prices and indirect-tax changes as events whose first-round effects the bank could accommodate if second-round effects were avoided. The BoC's operational guides (CPI-trim, CPI-median, CPIX) exclude volatile components. [from literature; not re-fetched, and no primary URL verified this session]

### Inferences
- The ECB three-tier rule maps cleanly onto a dashboard. The cost-push block's contribution should rise non-linearly in shock **size × persistence**, gated by domestic second-round indicators.

### Gaps
- No primary BoC or RBNZ documents were fetched. The 2021 BoC framework renewal and the current RBNZ remit wording are unverified.
- Powell's 2026 comments are secondary-source only.

---

## Q5. Is there a standard rule of thumb for weighting first-round energy shocks?

### Takeaway
No single number. The practical consensus rule is:
1. give **approximately zero weight to direct (first-round) energy and flexible-price effects** on headline;
2. give **partial weight to indirect pass-through into core goods, food and services**, via input costs and networks;
3. give **full weight to second-round indicators**: wages and settlements, services and domestic inflation, firms' price expectations, household and short-term expectations;
4. scale the whole block up **state-contingently** when inflation starts high, the labour market is tight, the shock is large or persistent, or expectations move.

The models provide theoretical weights: Aoki gives zero weight to flexible-price sectors; Rubbo's DCI and La'O–Tahbaz-Salehi weight by stickiness and upstreamness.

### Cited Findings
- "Respond to core/sticky-price inflation": Aoki (2001, *JME*) and Mankiw–Reis (2003) (see Q1); Rubbo (2023): a Taylor rule on the divine-coincidence index implements constrained-optimal policy ([Econometrica](https://onlinelibrary.wiley.com/doi/full/10.3982/ECTA18654)).
- "Respond to domestic inflation, not headline": Aikman/NIESR 2026 ([NIESR](https://niesr.ac.uk/blog/how-should-monetary-policy-respond-energy-price-shock)). BoE MPC practice tracks services CPI, private regular pay and settlements ([MPS Sept 2026](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026)).
- "Respond when expectations move": Powell 2022 ([Fed](https://www.federalreserve.gov/newsevents/speech/powell20220826a.htm)); Reis 2022 ([BIS](https://www.bis.org/publ/work1060.htm)); IMF WEO Oct 2023 ([IMF](https://www.imf.org/-/media/Files/Publications/WEO/2023/October/English/ch2.ashx)).
- "Size and persistence tiers": ECB three-tier framework ([Lagarde 2026](https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260325~ac2916a211.en.html)); BoE "risk is cumulative" ([Lombardelli 2026](https://www.bankofengland.co.uk/speech/2026/september/clare-lombardelli-speech-at-the-sixth-biennial-conference-poland)).
- "Regime-dependence": BIS AER 2022 ([BIS](https://www.bis.org/publ/arpdf/ar2022e2.pdf)). The 20% vs 45% spillover variance share quantifies how much more sectoral shocks propagate in high-inflation regimes.

### Inferences (suggested dashboard design, derived from the above)
- **Split the cost-push block into three tiers:**
  - (a) **direct energy CPI contribution** (e.g. the 0.7pp in Aug 2026): low weight, informational only;
  - (b) **pipeline and indirect pressure**: PPI input prices, import prices ex-energy, sterling ERI changes, food CPI; moderate weight;
  - (c) **second-round transmission**: services CPI, pay settlements, household one-year expectations (with dispersion), DMP firm price expectations; high weight. Tier (c) arguably belongs in the domestic block.
- **Apply a state multiplier** that raises weights on (a) and (b) when:
  - CPI has been above target for most of the past 12–24 months;
  - labour-market tightness is high (V/U, unemployment gap);
  - the shock is large (non-linearity) or has lasted more than about two quarters (the 2026 MPC vote drift);
  - short-term household expectations or their upper tail rise;
  - sterling is depreciating.
- **Treat food separately from energy.** BoE 2026 (Lombardelli) singles out food as an expectations-salient channel.
- **UK specifics:** the UK is highly exposed to gas prices (Taylor 2026). The Ofgem price cap lags wholesale gas, so the direct CPI effect is predictable from wholesale futures one to two quarters ahead. [Ofgem lag mechanism from general knowledge; not verified this session]

### Gaps
- No official BoE or academic source gives an explicit numerical weight, such as "x% of the energy shock should enter the policy rule". The weights above are my synthesis, not a published rule.
- I did not verify any empirical estimate of UK second-round elasticities (e.g. BoE staff estimates of wage response to energy-driven CPI). This is worth a separate search: BoE Staff Working Papers on energy pass-through; the BoE MPR Nov 2022 and Feb 2023 boxes on second-round effects.
