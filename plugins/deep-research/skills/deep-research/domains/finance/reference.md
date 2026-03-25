# Finance & Investment Research Reference

## Query Patterns

### Pattern 1: Regulatory Filing Targeting
```
"[company] 10-K annual report site:sec.gov"
"[company] 10-Q quarterly filing EDGAR"
"[company] proxy statement DEF 14A"
"[company] 8-K material event"
"[ETF/fund] prospectus N-1A site:sec.gov"
"[company] insider transactions Form 4 site:sec.gov"
```

### Pattern 2: Data-Driven Queries
```
"[asset/index] historical performance total return [period]"
"[metric] FRED economic data"
"[index] price-to-earnings ratio historical average"
"[country] inflation rate CPI [year]"
"[topic] OECD data statistics"
"[industry] market size revenue growth"
"[asset class] risk-adjusted return Sharpe ratio"
"[bond/credit] yield spread historical"
```

### Pattern 3: Budgeting and Personal Finance
```
"[strategy] evidence effectiveness personal finance"
"[topic] consumer price index impact"
"[product type] fee comparison total expense ratio"
"[retirement strategy] safe withdrawal rate research"
"[savings method] behavioral economics nudge"
"[insurance type] coverage comparison consumer guide"
"[debt strategy] avalanche vs snowball evidence"
```

### Pattern 4: Risk and Fraud Detection
```
"[entity/product] scam warning SEC enforcement"
"[entity] complaints CFPB consumer"
"[entity] FINRA BrokerCheck"
"[crypto project] audit security review"
"[entity] regulatory action fine penalty"
"[scheme type] FTC warning consumer alert"
"[product] hidden fees total cost analysis"
```

### Pattern 5: Stock Fundamental Analysis
```
"[company] earnings estimates consensus"
"[company] valuation PE PB EV/EBITDA"
"[company] dividend history yield payout ratio"
"[company] insider ownership Form 4 transactions"
"[company] competitive advantage moat analysis"
"[company] margin trend revenue growth"
"[company] analyst price target consensus"
"[company] balance sheet debt free cash flow"
"[company] ROE ROIC return on capital"
```

### Pattern 6: ETF / Fund Analysis
```
"[ETF ticker] tracking difference tracking error"
"[ETF ticker] total expense ratio total cost"
"[ETF ticker] holdings top 10 concentration"
"[ETF/fund] physical synthetic replication method"
"[ETF] bid-ask spread premium discount NAV"
"[ETF/fund] tax efficiency distributing accumulating"
"[ETF] overlap comparison [other ETF]"
"[fund] site:morningstar.com analysis"
"[ETF] site:justetf.com"
```

### Pattern 7: Portfolio and Asset Allocation
```
"[asset class] correlation matrix portfolio"
"[strategy] asset allocation model"
"[topic] sequence of returns risk withdrawal"
"[asset classes] diversification benefit"
"rebalancing strategy frequency evidence"
```

### Pattern 8: UCITS / European Investor Specifics
```
"[US ETF ticker] UCITS equivalent Europe"
"[index] UCITS ETF Ireland domicile"
"[ETF] accumulating distributing UCITS"
"[ETF] EUR hedged share class"
"[ETF] Sparplan Trade Republic Scalable"
"[country] withholding tax US dividends treaty rate"
"[fund] Meldefonds Teilfreistellung steuerlich"
"[ETF] site:justetf.com UCITS"
"[ETF] KID PRIIPs available Europe"
"Ireland domicile vs Luxembourg ETF tax"
```

### Pattern 9: Comparative Analysis
```
"[product A] vs [product B] comparison [year]"
"[strategy A] vs [strategy B] historical performance"
"[broker A] vs [broker B] fees comparison"
"[country A] vs [country B] tax treatment [topic]"
"best [product type] [year] Morningstar rating"
```

### Pattern 6: Macroeconomic Context
```
"[central bank] interest rate decision [year]"
"[country] GDP growth forecast IMF"
"[region] economic outlook [year]"
"yield curve inversion recession indicator"
"[currency pair] exchange rate forecast"
"[commodity] supply demand outlook"
```

## Preferred Source Tiers

### Tier 1 -- Regulatory and official data (always search first)
- SEC EDGAR (sec.gov/cgi-bin/browse-edgar)
- Federal Reserve / FRED (fred.stlouisfed.org)
- BLS / BEA (bls.gov, bea.gov)
- ECB Statistical Data Warehouse (sdw.ecb.europa.eu)
- Eurostat (ec.europa.eu/eurostat)
- IMF Data (data.imf.org)
- OECD Data (data.oecd.org)

### Tier 2 -- Institutional analysis
- Bloomberg (bloomberg.com)
- Reuters (reuters.com)
- Morningstar (morningstar.com)
- S&P Global (spglobal.com)
- World Bank data (data.worldbank.org)
- CFPB (consumerfinance.gov)

### Tier 3 -- Quality financial journalism
- Financial Times (ft.com)
- Wall Street Journal (wsj.com)
- The Economist (economist.com)
- Barron's (barrons.com)

### Tier 4 -- Academic and research
- NBER Working Papers (nber.org)
- SSRN (ssrn.com) -- label as working paper
- Journal of Finance, Journal of Financial Economics, Review of Financial Studies
- Brookings Institution, Peterson Institute

### Tier 5 -- Qualified secondary
- Investopedia (verify all claims against higher tiers)
- Bogleheads wiki (passive investing context)
- Khan Academy finance courses (educational fundamentals)
- NerdWallet, Bankrate (product comparisons, verify independently)
- justETF (justetf.com) — European ETF screener, comparison data, UCITS availability
- extraETF (extraetf.com) — German ETF analysis, savings plan availability
- Trackinsight (trackinsight.com) — ETF analytics, tracking difference data

## WebFetch Prompts by Source Type

### For SEC filings (10-K, 10-Q)
```
"What are the key financial metrics: revenue, net income, operating margin,
free cash flow, debt-to-equity? What risk factors does the company disclose?
What are management's forward-looking statements? What significant accounting
policies or changes are noted? What related-party transactions exist? What is
the auditor's opinion?"
```

### For economic data pages (FRED, BLS, Eurostat)
```
"What is the current value of this indicator? What is the historical trend
(1-year, 5-year, 10-year)? When was this data last updated? What is the
methodology or definition used? Are there any revisions to prior data noted?
What is the seasonal adjustment method?"
```

### For investment product pages (ETF, fund)
```
"What is the total expense ratio / management fee? What is the investment
objective and strategy? What are the top holdings and sector allocation? What
is the benchmark index? What are the 1-year, 3-year, 5-year, 10-year returns
(total return)? What is the fund size (AUM)? What is the tracking error (for
index funds)? Are there any sales loads or redemption fees?"
```

### For financial journalism
```
"What specific data or sources does this article cite? What are the key claims
with their supporting evidence? Does the article disclose any conflicts of
interest? Is there a distinction between factual reporting and opinion/analysis?
What is the date of the data referenced (not just the article date)? Are
alternative viewpoints or risks mentioned?"
```

### For budgeting and personal finance articles
```
"What specific strategy or product is discussed? What evidence or data supports
the recommendations? Are fees, costs, and tax implications addressed? Are
alternative approaches mentioned? Is the advice jurisdiction-specific? Does the
source have any commercial affiliations? What assumptions underlie any
projections or calculations?"
```

### For stock analysis / equity research pages
```
"What are the key valuation metrics (P/E, P/B, EV/EBITDA, PEG)? What is the
analyst consensus rating and price target range? What are the revenue and earnings
growth rates? What are the profitability metrics (ROE, ROIC, margins)? What is
the dividend yield and payout ratio? What is the insider ownership? Are there
recent insider transactions? What are the key competitive advantages? What are
the main risks and catalysts identified?"
```

### For ETF / fund detail pages
```
"What is the total expense ratio? What is the replication method (physical/synthetic)?
What are the top 10 holdings and their weights? What is the sector and geographic
breakdown? What is the tracking difference and tracking error vs the benchmark?
What is the fund size (AUM)? What is the average bid-ask spread? Does it distribute
or accumulate? What is the fund domicile? What is the securities lending policy?
What are the 1/3/5/10-year returns vs the benchmark?"
```

### For crypto / digital asset content
```
"What is the project's stated purpose and mechanism? Is the team identified
and verifiable? Has the smart contract been independently audited? What are
the tokenomics (supply, distribution, vesting)? What is the regulatory status
in major jurisdictions? What risks does the source acknowledge? Are return
projections or guarantees made (red flag)?"
```

## Temporal Sensitivity

| Content Type | Freshness Requirement | Notes |
|---|---|---|
| Stock/crypto prices | Hours to days | Stale prices are misleading |
| Earnings data | Last quarter available | Quarterly cycle |
| Economic indicators | Last release | Monthly/quarterly cycle |
| Fund performance | Last quarter | Morningstar updates quarterly |
| Analyst ratings | Last 3-6 months | May be stale or revised |
| Tax rules | Current tax year | Annual changes common |
| Interest rates | Last central bank meeting | Can change at any meeting |
| Regulatory changes | Last 6 months | Check for recent amendments |
| Investment strategy research | 1-3 years | Foundational studies any age |
| Financial product comparisons | Last 6 months | Fees and features change |
| Macroeconomic analysis | Last 6-12 months | Cycle-dependent |
| Historical data series | Any age | But verify methodology consistency |

## Local-Language Query Patterns

### German (DACH Region)
```
"[Thema] site:bafin.de"                     (Bundesanstalt fur Finanzdienstleistungsaufsicht)
"[Thema] site:bundesbank.de"                (Deutsche Bundesbank)
"[Unternehmen] site:boerse-frankfurt.de"     (Deutsche Borse / Frankfurt Stock Exchange)
"[Thema] Finanztest Stiftung Warentest"      (independent consumer finance testing)
"[Anlageprodukt] Kosten TER Vergleich"       (total expense ratio comparison)
"[Thema] Finanztip"                          (non-profit financial advice)
"[Steuer] Einkommensteuer [Thema]"           (income tax)
"[Thema] site:destatis.de"                   (Federal Statistical Office)
```

German financial source tiers:
- **Tier 1**: BaFin, Bundesbank, Destatis, Deutsche Borse official data
- **Tier 2**: Finanztest (Stiftung Warentest), Handelsblatt, Borsen-Zeitung
- **Tier 3**: Finanztip (non-profit), WirtschaftsWoche
- **Tier 4**: Finanzfluss, justETF.com (verify against higher tiers)

### Swedish
```
"[amne] site:riksbank.se"                   (Sveriges Riksbank)
"[amne] site:fi.se"                         (Finansinspektionen -- financial supervisory)
"[amne] site:scb.se"                        (Statistiska centralbyran -- Statistics Sweden)
"[fond/produkt] site:avanza.se"             (largest Swedish broker, product data)
"[amne] site:konsumenternas.se"             (Konsumenternas Bank- och finansbyra)
"[amne] site:pensionsmyndigheten.se"        (Swedish Pensions Agency)
"[skatt] site:skatteverket.se"              (Swedish Tax Agency)
```

Swedish financial source tiers:
- **Tier 1**: Riksbanken, Finansinspektionen, SCB, Skatteverket
- **Tier 2**: Pensionsmyndigheten, Konsumenternas, Dagens Industri
- **Tier 3**: Avanza research, Nordnet research (note broker bias)

### EU-wide
```
"[topic] site:ecb.europa.eu"
"[topic] site:esma.europa.eu"              (European Securities and Markets Authority)
"[topic] site:eba.europa.eu"               (European Banking Authority)
"[topic] MiFID II regulation"
"[topic] UCITS fund regulation"
```
