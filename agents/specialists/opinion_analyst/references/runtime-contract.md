# Opinion Analyst runtime contract

## Contents

- [Implemented methods](#implemented-methods)
- [Inputs and fallbacks](#inputs-and-fallbacks)
- [Interpretation boundary](#interpretation-boundary)

## Implemented methods

Sentiment counts fixed positive and negative words. Stance searches fixed phrases containing the
target, then falls back to sentiment. Bias searches fixed phrase lists across requested dimensions and
adds flags for exclamation marks and all-caps tokens. All processing is local and deterministic.

## Inputs and fallbacks

Sentiment supports document behavior and optional aspect extraction; unknown granularity behaves like
document. Empty sentiment or stance input returns a neutral zero-confidence record. The default bias
dimensions are political, emotional, framing, source, and confirmation. Unknown dimensions receive a
zero score because they have no signal list.

## Interpretation boundary

Scores are uncalibrated heuristics, not model probabilities. They are sensitive to spelling,
tokenization, negation, sarcasm, dialect, and quoted language. Do not use output to infer protected
traits, mental state, voter intent, population opinion, or fitness for a consequential decision.
