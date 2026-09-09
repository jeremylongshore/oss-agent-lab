# Browser AI runtime contract

## Contents

- [Implemented flow](#implemented-flow)
- [Accepted inputs](#accepted-inputs)
- [Side-effect boundary](#side-effect-boundary)

## Implemented flow

The tools parse URL text and synthesize results. `navigate` derives a title, latency, redirect, and
status from the string. `extract_content` recognizes only `body`, `main`, `article`, `#content`, and
`.content`, then returns placeholder text. `take_screenshot` validates dimensions and constructs a
timestamped path.

## Accepted inputs

Navigation requires a non-empty HTTP(S) URL. Extraction formats are `text`, `html`, and `markdown`.
Viewport syntax is positive integer `WIDTHxHEIGHT`. A path containing `/404` yields a synthetic 404;
all other valid URL strings yield a synthetic 200.

## Side-effect boundary

No DNS lookup, HTTP request, redirect, DOM parse, browser launch, directory creation, or PNG write
occurs. A screenshot path is not a file receipt. Never use these results to claim a site is reachable,
to quote page content, or to prove how a page renders.
