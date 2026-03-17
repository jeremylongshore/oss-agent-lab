# Template Specialist

> Copy this directory to create a new specialist.

## Quick Start

1. Copy `_template/` to `agents/specialists/your_name/`
2. Rename `TemplateSpecialist` class in `agent.py`
3. Implement tools in `tools.py`
4. Update `SKILL.md` frontmatter and documentation
5. Add tests: `tests/test_your_name.py`
6. Open a PR

## Required Files

| File | Purpose |
|------|---------|
| `agent.py` | Specialist class extending `BaseSpecialist` |
| `tools.py` | Tool implementations (pure functions preferred) |
| `SKILL.md` | Metadata, capabilities, allowed-tools declaration |
| `README.md` | Human-readable documentation |

## Quality Requirements

- 80%+ test coverage
- MIT-compatible license
- All network calls declared in SKILL.md `allowed-tools`
- Type hints on all public functions
