# Autoresearch runtime contract

## Contents

- [Implemented flow](#implemented-flow)
- [Inputs and outputs](#inputs-and-outputs)
- [Evidence boundary](#evidence-boundary)

## Implemented flow

`AutoresearchSpecialist.execute` selects the first of three fixed hypothesis templates, chooses a
canned finding list by method, and averages floating-point `strength` fields. The experiment ID is a
short random UUID. No filesystem, network, corpus, model, statistical package, or laboratory system
is used.

## Inputs and outputs

The topic comes from `intent.parameters.topic` or the raw query. Supported finding sets are
`literature_review`, `simulation`, and `ablation`; an unknown method currently uses the
`literature_review` findings while echoing the unknown method. Analysis counts `supporting` and
`refuting` entries and averages float strengths. Empty findings return zero confidence.

## Evidence boundary

Names such as `corpus_scan`, `meta_analysis`, and `monte_carlo_run` are fixture labels, not sources or
receipts. Returned confidence is arithmetic over those fixtures and is not calibrated. Preserve the
simulation disclosure whenever output leaves a test or demonstration context.
