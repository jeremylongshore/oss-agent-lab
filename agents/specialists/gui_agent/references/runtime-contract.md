# GUI Agent runtime contract

## Contents

- [Implemented flow](#implemented-flow)
- [Input rules](#input-rules)
- [Safety boundary](#safety-boundary)

## Implemented flow

`detect_elements` creates five login-form fixtures with random IDs and filters them by description
keywords. `interact_element` maps an ID and action to a synthetic state and latency. `fill_form` counts
fields and applies minimal token rules for fields named `email`, `url`, and `phone`.

## Input rules

Detection and form filling require a non-empty URL string. Actions are `click`, `type`, `hover`,
`focus`, and `clear`; `type` requires a value. Form data must be non-empty. Detection falls back to the
first two fixture elements when no description keyword matches.

## Safety boundary

No URL validation, HTTP request, browser, DOM, vision model, click, keystroke, or form submission
occurs. Random element IDs are not stable across calls. Never pass secrets as sample form values or
report `submit_ready` as evidence about a real page.
