# Deer Flow prototype runtime contract

## Contents

- [Implemented stages](#implemented-stages)
- [Accepted values](#accepted-values)
- [Artifact boundary](#artifact-boundary)

## Implemented stages

`research_topic` produces numbered placeholder findings and caller-supplied or `auto-source-N` labels.
`generate_code` emits a Python `NotImplementedError` skeleton or comment-only non-Python stub.
`create_artifact` wraps dictionaries with a SHA-1-derived identifier and UTC timestamp. The specialist
runs all three by default because `generate_code` defaults truthy.

## Accepted values

Depth is `shallow`, `standard`, or `deep`; style is `clean`, `verbose`, or `minimal`; artifact type is
`report`, `notebook`, `package`, or `summary`; format is `markdown`, `json`, or `html`. Unsupported
values and empty required content raise `ValueError`.

## Artifact boundary

No source is consulted and no model generates code. Format is metadata only: the returned object is
not rendered or written to disk. The identifier is content-derived but is not a storage address,
signature, provenance proof, or guarantee that the stub is correct.
