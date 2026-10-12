# Module Design Document

This document describes the architectural design, responsibilities, interfaces, inputs, and outputs of each module in ResumeLens, in alignment with `docs/contracts.md`.

---

## 1. Architectural Overview

ResumeLens follows a multi-stage sequential pipeline architecture based on formal computational models:

```
[Raw Résumé Text]
       │
       ▼ (Stage 1: Regex)
[ExtractionResult]
       │
       ▼ (Stage 2: FST)
[NormalizationResult]
       │
       ▼ (Stage 2b & 3: Sorting + FSA per profile)
[list[ProfileResult]]
       │
       ▼ (Stage 4: CFG / textX)
[Candidate DSL text & Validated AST]
       │
       ▼ (Stage 4b: Visualization)
[HTML / Markdown Reports]
```

---

## 2. Shared Core Modules

### 2.1 `models.py`
- **Owner:** Shared (Diego / Team)
- **Responsibility:** Declares the strongly typed dataclasses exchanged across pipeline stages.
- **Key Entities:**
  - `Candidate(name, emails, phones, links, education, experience)`
  - `Education(degree, institution, year)`
  - `Experience(years, description)`
  - `ExtractionResult(candidate, raw_skills)`
  - `NormalizationResult(tokens, mapping, unrecognized)`
  - `ProfileResult(profile_id, sequence, accepted)`
  - `PipelineResult(extraction, normalization, classifications, dsl_text, html, markdown)`

### 2.2 `errors.py`
- **Owner:** Shared (Diego / Team)
- **Responsibility:** Defines the centralized error hierarchy rooted at `ResumeLensError`.
- **Key Entities:**
  - `ExtractionError` (Stage 1)
  - `VocabularyError` (Vocabulary loader / Stage 2)
  - `ProfileConfigError` (Profile loader / Stage 3)
  - `DSLValidationError` (Stage 4, includes optional `line` and `column` attributes)

### 2.3 `vocabulary.py` and `vocabulary.json`
- **Owner:** Shared (Diego / Team)
- **Responsibility:** Single source of truth for the canonical token vocabulary (30 tokens). Provides `load_vocabulary`, `canonical_tokens`, `is_canonical`, `token_category`, and `alias_index`.

---

## 3. Pipeline Stage Modules

### 3.1 `extraction.py` (Stage 1)
- **Owner:** Alejandro Rendón Garzón (Alejo)
- **Formal Model:** Regular expressions (`re`).
- **Responsibility:** Extracts surface qualification strings and candidate contact/education/experience records from raw résumé text.
- **Input:** `text: str`.
- **Output:** `ExtractionResult`.

### 3.2 `normalization.py` (Stage 2)
- **Owner:** Alejandro Rendón Garzón (Alejo)
- **Formal Model:** Finite-State Transducers (FSTs via `pyformlang`).
- **Responsibility:** Preprocesses raw skill strings and maps accepted surface aliases to their canonical token representation in alphabet $\Gamma$.
- **Input:** `raw_skills: list[str]`.
- **Output:** `NormalizationResult`.

### 3.3 `profiles.py` (profile configuration)
- **Owner:** Juan Diego Balanta Molina (Diego)
- **Responsibility:** Loads the JSON files of `profiles/` and validates them against the rules of contract Section 7.3, so the four profiles are data processed by one engine.

| Function | Input | Output | Errors |
|---|---|---|---|
| `load_profiles(directory=None, vocabulary=None)` | Folder with `*.json` (default: `<repo>/profiles`, resolved from the package location) | `list[dict]` sorted by `order`, then file name | `ProfileConfigError` if the folder is missing or empty, a file is invalid or two ids repeat |
| `load_profile(path, vocabulary=None)` | One JSON file | Normalized profile `dict` | `ProfileConfigError` (missing file, invalid JSON, rule violation) |
| `validate_profile(raw, source, vocabulary=None)` | Decoded JSON object | Normalized copy with `id`, `display_name`, `order`, `slots` (input not mutated) | `ProfileConfigError`: bad id, no slots, token not in the vocabulary, overlapping `any_of`, every slot optional |
| `profile_alphabet(profile)` | Profile | Tokens in slot order (alphabet Σ of its automaton) | — |

### 3.4 `sorting.py` (Stage 2b)
- **Owner:** Juan Diego Balanta Molina (Diego)
- **Formal Model:** Profile-defined canonical ordering (filter + stable sort).
- **Responsibility:** Turns the normalized tokens into the word that a profile automaton reads: drops tokens that belong to no slot of the profile (decision D5) and sorts the rest by (slot index, position inside `any_of`).

| Function | Input | Output |
|---|---|---|
| `sort_for_profile(tokens, profile)` | Normalized tokens, profile | Filtered, deduplicated and sorted `list[str]`; depends only on the *set* of tokens |
| `filter_for_profile(tokens, profile)` | Tokens, profile | Tokens of the profile in their original order |
| `discarded_for_profile(tokens, profile)` | Tokens, profile | Tokens removed by the filter (used to explain a result) |
| `canonical_order(profile)` | Profile | `{token: (slot_index, position)}` sort keys |

### 3.5 `recognition.py` (Stage 3)
- **Owner:** Juan Diego Balanta Molina (Diego)
- **Formal Model:** Finite automata (`pyformlang`): one ε-NFA per profile built from its slots, with the equivalent DFA and minimal DFA derived for the formalization.
- **Responsibility:** Decides, for every profile, whether the sorted word of the résumé belongs to the profile language S1^k1 … Sn^kn (k = `+` mandatory, `*` optional).

| Function | Input | Output |
|---|---|---|
| `classify(tokens, profiles=None)` | Normalized tokens; profiles (default: `load_profiles()`) | `list[ProfileResult]`, one per profile, in profile order |
| `recognize(sequence, profile, automaton=None)` | Sorted word, profile | `bool` (ACCEPTED / REJECTED) |
| `build_enfa(profile)` / `build_automaton(profile)` | Profile | `EpsilonNFA` with states q0…qn, p0…p(n-1), start q0, F = {qn} |
| `build_dfa(profile)` / `build_minimal_dfa(profile)` | Profile | Equivalent `DeterministicFiniteAutomaton` (subset construction / minimized) |
| `automaton_kind(automaton)` | Any pyformlang automaton | `"DFA"`, `"NFA"` or `"ε-NFA"`, decided from the transition relation |
| `automaton_tuple(automaton, profile)` | Automaton, profile | `{kind, Q, Sigma, delta, q0, F}` with readable state names (source of the tables in `docs/formalization.md`) |

### 3.6 `diagrams.py` and `scripts/export_diagrams.py` (Stage 3 documentation)
- **Owner:** Juan Diego Balanta Molina (Diego)
- **Responsibility:** Draws the transition diagrams of the four automata from `automaton_tuple`, so the diagrams always match the code.

| Function | Input | Output |
|---|---|---|
| `to_mermaid(spec, title="")` | 5-tuple | Mermaid `flowchart` source (rendered by GitHub) |
| `to_dot(spec, title="")` | 5-tuple | Graphviz DOT source |
| `tuple_markdown(spec)` | 5-tuple | Markdown with Q, Σ, q0, F and the δ table |
| `export_all(out_dir, profiles=None)` | Output folder | `.mmd` / `.dot` files per profile and automaton, plus `automata.md`; the script also renders SVGs with `--svg` |

### 3.7 `dsl.py` and `candidate.tx` (Stage 4)
- **Owner:** Edwar Estacio
- **Formal Model:** Context-Free Grammar (CFG in EBNF via `textX`).
- **Responsibility:** Serializes candidate information, normalized skills, and profile verdicts into a structured DSL and validates incoming DSL text.
- **Functions:**
  - `get_metamodel()`: Compiles and caches the textX metamodel from `candidate.tx`.
  - `to_dsl(candidate: Candidate, tokens: list[str], results: list[ProfileResult]) -> str`: Serializes structured data into DSL source text.
  - `validate(dsl_text: str) -> Any`: Parses DSL text against the grammar. Returns the parsed model on success; raises `DSLValidationError` on lexical or syntactic violation.
- **Input:** `Candidate`, `list[str]`, `list[ProfileResult]` (for `to_dsl`); `dsl_text: str` (for `validate`).
- **Output:** `str` (from `to_dsl`); textX model instance (from `validate`).

### 3.8 `render.py` (Stage 4b)
- **Owner:** Edwar Estacio
- **Responsibility:** Generates human-readable visualizations (HTML and Markdown) directly from the validated textX candidate model.
- **Functions:**
  - `to_html(model: Any) -> str`: Produces a self-contained HTML document with escaped text.
  - `to_markdown(model: Any) -> str`: Produces a structured Markdown report.
- **Input:** Validated textX candidate model.
- **Output:** `str` (HTML or Markdown).

---

## 4. Integration and Execution Modules

### 4.1 `pipeline.py`
- **Owner:** Edwar Estacio
- **Responsibility:** Orchestrates stages 1 through 4b into a cohesive pipeline via `run(resume_text: str) -> PipelineResult`.
- **Input:** `resume_text: str`.
- **Output:** `PipelineResult`.

### 4.2 `app.py`
- **Owner:** Edwar Estacio
- **Responsibility:** Command-line user interface (CLI) to process résumé files, display terminal summaries, and save generated DSL, HTML, and Markdown artifacts to disk.
