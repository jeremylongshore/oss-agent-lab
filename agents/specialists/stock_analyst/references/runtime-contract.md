# Stock Analyst runtime contract

## Contents

- [Implemented flow](#implemented-flow)
- [Inputs and outputs](#inputs-and-outputs)
- [Financial-use boundary](#financial-use-boundary)

## Implemented flow

Each tool sums ticker characters and derives fixture values. Fundamentals synthesize price, market
capitalization, P/E, sector, and recommendation. Indicators synthesize RSI, MACD, and moving averages.
News sentiment synthesizes article counts, themes, and a score. No provider or model is called.

## Inputs and outputs

Ticker must be non-empty and news days at least one. Period is currently echoed without runtime
validation. Unknown indicator names are ignored while known names are computed. The specialist merges
the three dictionaries and derives a summary signal from their synthetic values.

## Financial-use boundary

The output has no timestamp, exchange, currency verification, filing provenance, article provenance,
or market-data receipt. It is fixture data only. Preserve the risk note and never use price,
recommendation, confidence, or stance fields for trading, valuation, advice, or reporting.
