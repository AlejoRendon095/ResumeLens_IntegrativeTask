# ResumeLens — Formal Language-Based Resume Screening

Integrative Task 1 · Computación y Estructuras Discretas III · Universidad Icesi · 2026-2

ResumeLens processes plain-text résumés and decides, for each of four professional
profiles, whether the qualifications explicitly written in the résumé satisfy a
formally defined qualification pattern. It does **not** rank candidates or make
hiring decisions.

| Stage | Formal model | Library | Module |
|---|---|---|---|
| 1. Extraction | Regular expressions | `re` | `extraction.py` |
| 2. Normalization | Finite-state transducers | `pyformlang` | `normalization.py` |
| 2b. Sorting / filtering | Profile canonical order | — | `sorting.py` |
| 3. Recognition | Finite automata (DFA / NFA / ε-NFA) | `pyformlang` | `recognition.py` |
| 4. Candidate language | Context-free grammar (EBNF) | `textX` | `dsl.py`, `candidate.tx` |
| 4b. Visualization | HTML / Markdown | — | `render.py` |

Supported profiles: Full Stack Developer, Machine Learning Engineer, DevOps Engineer
(team-defined, software engineering) and Data Engineer (team-defined, AI/data).
Profiles are JSON files in `profiles/` processed by the same engine.

## Team

| Member | Responsibility |
|---|---|
| Alejandro Rendón Garzón | Stage 1 (extraction) and Stage 2 (normalization) |
| Juan Diego Balanta Molina | Profiles, Stage 2b (sorting) and Stage 3 (recognition) |
| Edwar Estacio | Stage 4 (DSL and visualization), pipeline and UI |

The interface between stages is defined in [`docs/contracts.md`](docs/contracts.md).

## Requirements and setup

* Python 3.10 or newer
* Recommended IDE: Visual Studio Code (any Python 3.10+ environment works)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Running the tests

From the repository root:

```bash
pytest
```

`pyproject.toml` adds `src/` to the import path, so no installation is needed.

## Regenerating the automata diagrams

```bash
python scripts/export_diagrams.py --svg
```

Writes the Mermaid (`.mmd`), Graphviz (`.dot`) and SVG diagrams of the four profile
automata, plus the index [`docs/diagrams/automata.md`](docs/diagrams/automata.md).
The `--svg` option needs Graphviz installed.

## Repository layout

```
docs/          design documents (contract, formalization, profiles, test cases, IAG log)
profiles/      JSON configuration of the four professional profiles
samples/       example résumés
src/resumelens/  source code (one module per stage + shared models/vocabulary)
tests/         pytest test suite
```

## Notes

* Line endings are normalized to LF by `.gitattributes`.
* The use of generative AI is documented in [`docs/iag_log.md`](docs/iag_log.md).
