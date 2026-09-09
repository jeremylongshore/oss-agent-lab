# Knowledge Graph runtime contract

## Contents

- [Implemented flow](#implemented-flow)
- [Input rules](#input-rules)
- [Persistence and evidence](#persistence-and-evidence)

## Implemented flow

`build_graph` hashes the source string, derives synthetic node and edge counts, and creates a random
graph UUID. `query_graph` constructs placeholder labels from the first query word and a seed.
`find_relationships` constructs artificial paths and coupling scores. No graph library is called.

## Input rules

Graph type is `code`, `document`, or `mixed`; depth and maximum results must be at least one. The
specialist passes a single per-call graph ID through the three operations. Source and query strings
must be non-empty at the skill boundary because `query_graph` indexes the first split word.

## Persistence and evidence

There is no graph store, latest-graph state, source reader, clone, parser, embedding model, GitNexus,
or cognee runtime. A returned graph ID identifies only this response. Counts, entities, relevance
scores, paths, and relationship strengths cannot support claims about the supplied source.
