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

### 3.3 `sorting.py` (Stage 2b)
- **Owner:** Juan Diego Balanta Molina (Diego)
- **Formal Model:** Profile-defined canonical ordering.
- **Responsibility:** Filters tokens that do not belong to the target profile and orders the remaining tokens according to the profile's slots.
- **Input:** `tokens: list[str]`, `profile: dict`.
- **Output:** `list[str]` (sequence for automaton consumption).

### 3.4 `recognition.py` (Stage 3)
- **Owner:** Juan Diego Balanta Molina (Diego)
- **Formal Model:** Finite-State Automata (FSAs via `pyformlang`).
- **Responsibility:** Builds automata from profile specifications and evaluates whether candidate token sequences satisfy qualification patterns.
- **Input:** `tokens: list[str]`, `profiles: list[dict]`.
- **Output:** `list[ProfileResult]`.

### 3.5 `dsl.py` and `candidate.tx` (Stage 4)
- **Owner:** Edwar Estacio
- **Formal Model:** Context-Free Grammar (CFG in EBNF via `textX`).
- **Responsibility:** Serializes candidate information, normalized skills, and profile verdicts into a structured DSL and validates incoming DSL text.
- **Functions:**
  - `get_metamodel()`: Compiles and caches the textX metamodel from `candidate.tx`.
  - `to_dsl(candidate: Candidate, tokens: list[str], results: list[ProfileResult]) -> str`: Serializes structured data into DSL source text.
  - `validate(dsl_text: str) -> Any`: Parses DSL text against the grammar. Returns the parsed model on success; raises `DSLValidationError` on lexical or syntactic violation.
- **Input:** `Candidate`, `list[str]`, `list[ProfileResult]` (for `to_dsl`); `dsl_text: str` (for `validate`).
- **Output:** `str` (from `to_dsl`); textX model instance (from `validate`).

### 3.6 `render.py` (Stage 4b)
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
