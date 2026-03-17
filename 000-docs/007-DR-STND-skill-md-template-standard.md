# 007-DR-STND: SKILL.md Template Standard

**Category:** Design Record -- Standard
**Status:** Final
**Date:** 2026-03-16
**Author:** Jeremy Longshore

---

## Purpose

This document defines the SKILL.md specification for all specialists in OSS Agent Lab. Every specialist must include a SKILL.md file in its directory (`agents/specialists/<name>/SKILL.md`). The file serves as both machine-readable metadata (YAML frontmatter) and human-readable documentation (Markdown body). CI validates SKILL.md against this specification on every PR.

---

## Frontmatter Schema

The YAML frontmatter block is delimited by `---` lines and must appear at the top of the file. All fields marked `(required)` must be present. Missing required fields cause CI failure.

```yaml
---
name: string (required)
  # Specialist identifier. Must be snake_case. Must match the directory
  # name under agents/specialists/. Example: autoresearch

display_name: string (required)
  # Human-readable name. Title case. Example: AutoResearch

description: string (required)
  # One-line description of what the specialist does. Maximum 120
  # characters. Must start with a verb. Example: "Runs self-improving
  # research loops to produce paper-grade answers from natural language
  # questions."

version: string (required)
  # Semantic version (semver.org). Format: MAJOR.MINOR.PATCH.
  # Example: 0.1.0

source_repo: string (required)
  # GitHub owner/repo of the upstream project this specialist wraps.
  # Format: owner/repo. Example: karpathy/autoresearch
  # For meta-specialists (e.g., repo-scanner), use "META".

license: string (required)
  # SPDX license identifier of the upstream repo. Must be MIT-compatible.
  # Accepted values: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC,
  # Unlicense, 0BSD. Any other value is rejected.

tier: enum (required)
  # Quality tier. One of: core, verified, community, experimental.
  # See governance policy (008-PP-PLAN) for tier definitions and
  # promotion criteria.

capabilities: list[string] (required)
  # List of capability identifiers this specialist provides.
  # Each identifier must be snake_case. Must match the capabilities
  # registered in the specialist's agent.py class.
  # Example:
  #   - research_loop
  #   - literature_review
  #   - citation_generation

allowed_tools: list[string] (required)
  # List of tool names this specialist may invoke. Must match the
  # function names exported by the specialist's tools.py module.
  # This is a security boundary: any tool not listed here is prohibited.
  # Example:
  #   - search_papers
  #   - summarize_paper
  #   - generate_citations

output_formats: list[string] (required)
  # List of output formats this specialist supports. Must be a subset of:
  # python_api, cli, mcp_server, agent_skill, rest_api.
  # All five are expected for core and verified tier specialists.
  # Example:
  #   - python_api
  #   - cli
  #   - mcp_server
  #   - agent_skill
  #   - rest_api

dependencies: list[string] (optional)
  # Python package dependencies beyond the base oss-agent-lab requirements.
  # These are installed when the specialist is activated.
  # Example:
  #   - arxiv>=2.0
  #   - scholarly>=1.7

model_requirements: string (optional)
  # Required LLM model if the specialist needs a specific model.
  # Omit if the specialist works with the default Claude model.
  # Example: claude-sonnet-4-20250514
---
```

---

## Frontmatter Example

A complete frontmatter block for the `autoresearch` specialist:

```yaml
---
name: autoresearch
display_name: AutoResearch
description: Runs self-improving research loops to produce paper-grade answers from natural language questions.
version: 0.1.0
source_repo: karpathy/autoresearch
license: MIT
tier: core
capabilities:
  - research_loop
  - literature_review
  - citation_generation
  - knowledge_synthesis
allowed_tools:
  - search_papers
  - summarize_paper
  - generate_citations
  - synthesize_findings
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
dependencies:
  - arxiv>=2.0
  - scholarly>=1.7
---
```

---

## Body Structure

The Markdown body follows the frontmatter and must contain the following sections in order.

### 1. Title (H1)

The specialist's `display_name` as a level-1 heading.

```markdown
# AutoResearch
```

### 2. Overview

A paragraph explaining what the specialist does, which upstream repo it wraps, and what problem it solves. Should be 2-5 sentences.

```markdown
## Overview

AutoResearch wraps [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
to provide self-improving research loops. Feed it a natural language question and it
produces a paper-grade answer with citations, iterating on its own output until quality
thresholds are met.
```

### 3. Capabilities

A bulleted list matching the `capabilities` frontmatter field. Each bullet contains the capability identifier in bold followed by a description.

```markdown
## Capabilities

- **research_loop**: Executes iterative research cycles, refining answers with each pass
- **literature_review**: Searches and summarizes relevant academic papers
- **citation_generation**: Produces properly formatted citations for all referenced works
- **knowledge_synthesis**: Combines findings across multiple sources into coherent analysis
```

### 4. Tools

A table listing every tool declared in `allowed_tools`. Columns: Tool (code-formatted name), Description, Side Effects (None, Network, File I/O, etc.).

```markdown
## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `search_papers` | Queries ArXiv and Semantic Scholar for relevant papers | Network |
| `summarize_paper` | Extracts key findings from a paper given its URL or ID | Network |
| `generate_citations` | Formats citations in APA/BibTeX from paper metadata | None |
| `synthesize_findings` | Merges multiple paper summaries into a unified analysis | None |
```

### 5. Usage

Two subsections: Python API and CLI. Each contains a minimal working example.

```markdown
## Usage

### Python API
\```python
from agents.specialists.autoresearch.agent import AutoResearchSpecialist

specialist = AutoResearchSpecialist()
result = await specialist.execute({
    "query": "What are the latest advances in test-time compute?",
    "max_iterations": 3,
})
print(result.summary)
\```

### CLI
\```bash
oss-lab run autoresearch "What are the latest advances in test-time compute?"
\```
```

### 6. Source

A single line linking to the upstream repository.

```markdown
## Source

Wraps [karpathy/autoresearch](https://github.com/karpathy/autoresearch).
```

### 7. Changelog (optional)

Per-specialist change history. Only required after the first release. Uses Keep a Changelog format scoped to this specialist.

```markdown
## Changelog

### [0.1.0] - 2026-03-16
#### Added
- Initial specialist implementation
- Core research loop with configurable iteration depth
```

---

## Validation Rules

CI enforces the following rules on every SKILL.md in the repository:

### Frontmatter Validation

1. **All required fields present.** A missing required field fails the build.
2. **`name` matches directory name.** The `name` field must exactly match the parent directory name under `agents/specialists/`.
3. **`name` is snake_case.** Must match the pattern `^[a-z][a-z0-9_]*$`.
4. **`version` is valid semver.** Must match `^\d+\.\d+\.\d+$`.
5. **`license` is MIT-compatible.** Must be one of: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense, 0BSD.
6. **`tier` is a valid enum.** Must be one of: core, verified, community, experimental.
7. **`output_formats` values are valid.** Each must be one of: python_api, cli, mcp_server, agent_skill, rest_api.
8. **`description` starts with a verb.** First word must not be a noun or article.
9. **`description` is 120 characters or fewer.**

### Cross-File Validation

10. **`capabilities` match agent.py.** Every capability listed in SKILL.md must correspond to a capability registered in the specialist's `agent.py` class. No undeclared capabilities. No unregistered capabilities.
11. **`allowed_tools` match tools.py exports.** Every tool listed in SKILL.md must correspond to a function exported by the specialist's `tools.py` module. No undeclared tools. No unexported tools.
12. **`dependencies` are installable.** Every dependency listed must be a valid pip package specifier.

### Body Validation

13. **All required sections present.** Title (H1), Overview, Capabilities, Tools, Usage, and Source sections must exist.
14. **Capabilities count matches.** The number of capability bullets in the body must match the length of the `capabilities` frontmatter list.
15. **Tools table rows match.** The number of tool rows in the body table must match the length of the `allowed_tools` frontmatter list.

---

## Template Reference

The canonical template lives at `agents/specialists/_template/SKILL.md`. All new specialists should start by copying this template and filling in the values. The template contains placeholder values that will fail validation, forcing authors to replace every field.
