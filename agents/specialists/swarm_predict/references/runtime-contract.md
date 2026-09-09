# Swarm Prediction runtime contract

## Contents

- [Implemented flow](#implemented-flow)
- [Aggregation rules](#aggregation-rules)
- [Prediction boundary](#prediction-boundary)

## Implemented flow

The specialist creates virtual model descriptors, derives numeric values and confidences from the
target string, aggregates them, and evaluates agreement. No model endpoint, statistical estimator,
database, or external evidence source runs. The swarm UUID is random; fixture values are target-based.

## Aggregation rules

Swarm size must be at least one. Methods are `weighted_vote`, `majority_vote`, and `mean`.
Caller-supplied numeric values use weighted or ordinary averaging; categorical values use majority
vote. Threshold must be between zero and one. Blended confidence averages agreement with input
confidence and is not calibrated accuracy.

## Prediction boundary

The end-to-end consensus is arithmetic over synthetic numbers near an arbitrary baseline of 50.
Recommendation strings are contract labels only. Even with caller-supplied predictions, provenance,
independence, calibration, and domain validity must be established elsewhere before interpretation.
