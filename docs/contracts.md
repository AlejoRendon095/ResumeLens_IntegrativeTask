# ResumeLens — Interface Contract and Canonical Vocabulary

| Field | Value |
|---|---|
| Document | `docs/contracts.md` |
| Version | 1.3 |
| Date | 2026-10-09 |
| Authors | Alejo, Diego, Edwar |
| Status | Agreed by all members (Sync 1) |

## 0. Purpose and scope

This document is the single source of truth for **how the modules of ResumeLens talk to each other**. It defines:

1. The pipeline and who owns each stage.
2. The data structures exchanged between stages.
3. The **canonical vocabulary**: the output alphabet Γ of the transducers (Stage 2) and, at the same time, the input alphabet Σ of the automata (Stage 3).
4. The configuration format of the professional profiles.
5. The design decisions that affect more than one module.
6. Error handling, invariants, worked examples, and the change policy.

Each member can implement their stage independently as long as they respect this contract. If a stage needs something that is not written here, the contract must be changed first (see Section 12), not worked around in code.

> **Out of scope.** This document does *not* contain the formal definitions (regular expressions, 7-tuples of the transducers, 5-tuples of the automata, or the EBNF grammar). Those live in `docs/formalization.md`. ResumeLens does **not** rank candidates or make hiring decisions: it only reports whether the qualifications explicitly identified in a résumé satisfy formally defined patterns.

## 1. Pipeline overview and ownership

```
 résumé text (str)
        │
        ▼
┌───────────────────┐   ExtractionResult
│ Stage 1           │ ───────────────────┐
│ Extraction (regex)│                    │
│ owner: Alejo      │                    │
└───────────────────┘                    │
        │ raw_skills: list[str]          │
        ▼                                │
┌───────────────────┐   NormalizationResult
│ Stage 2           │ ───────────────────┤
│ Normalization(FST)│                    │
│ owner: Alejo      │                    │
└───────────────────┘                    │
        │ tokens: list[str]              │
        ▼                                │
┌───────────────────┐                    │
│ Stage 2b          │  (per profile)     │
│ Sorting + filter  │                    │
│ owner: Diego      │                    │
└───────────────────┘                    │
        │ sequence: list[str]            │
        ▼                                │
┌───────────────────┐   list[ProfileResult]
│ Stage 3           │ ───────────────────┤
│ Recognition (FSA) │                    │
│ owner: Diego      │                    │
└───────────────────┘                    │
                                         ▼
                              ┌───────────────────┐
                              │ Stage 4           │
                              │ DSL (CFG, textX)  │
                              │ + HTML/Markdown   │
                              │ owner: Edwar      │
                              └───────────────────┘
```

| Stage | Formal model | Tool | Module | Owner |
|---|---|---|---|---|
| 1. Extraction | Regular expressions | `re` | `extraction.py` | Alejo |
| 2. Normalization | Finite-state transducers (7-tuple) | `pyformlang` | `normalization.py` | Alejo |
| 2b. Sorting | Profile-defined canonical order | plain Python | `sorting.py` | Diego |
| 3. Recognition | Finite automata (5-tuple) | `pyformlang` | `recognition.py` | Diego |
| Profile loading | JSON configuration (Section 7) | `json` | `profiles.py` | Diego |
| 4. Candidate language | Context-free grammar (EBNF) | `textX` | `dsl.py`, `src/resumelens/candidate.tx` | Edwar |
| 4b. Visualization | — | plain Python | `render.py` | Edwar |
| Orchestration and UI | — | — | `pipeline.py`, `app.py` | Edwar |

Shared code (data models, errors, vocabulary loader) lives in `models.py`, `errors.py`, `vocabulary.py`, and `vocabulary.json` (all under `src/resumelens/`). Any change to those files requires approval from all three members.

## 2. Global conventions

| Topic | Rule |
|---|---|
| Language | Python 3.10 or newer. Type hints on every public function. |
| Encoding | UTF-8 everywhere (source, JSON files, DSL files, HTML output). |
| Naming | `snake_case` for functions, variables, and files. `UPPER_SNAKE_CASE` for canonical tokens and profile ids. |
| Missing data | Never `None` for collections or strings: use `[]` and `""`. The only nullable field is `Experience.years` (`float \| None`). |
| Ordering | Lists preserve the order defined in each stage's contract. Never rely on `set` ordering. |
| Purity | Stage functions are pure: no global state, no I/O except the explicit loaders (`vocabulary.py`, profile loader). |
| Language of artifacts | Code, docs, poster, and presentation are written in English. |
| Immutability | A stage must not mutate the object it receives; it returns a new one. |
| Layout | Package in `src/resumelens/`; tests in `tests/` (run `pytest` from the repository root, configured in `pyproject.toml`); dependencies in `requirements.txt`. |
| Line endings | LF everywhere, enforced by `.gitattributes`. Do not commit files whose only change is CRLF ↔ LF. |

## 3. Canonical vocabulary

The canonical vocabulary is the set of **canonical tokens**. Each token is a single indivisible symbol:

* At the **output of the transducers** a token is a string over Γ = {A–Z, `_`}.
* At the **input of the automata** a token is one symbol of the alphabet Σ. Therefore **Γ (as a set of strings) = Σ (as a set of symbols)**: the transducer produces exactly the symbols the automaton consumes.

### 3.1 Tokens, categories, and aliases

Aliases are the *input* spellings (after preprocessing, see Section 4) that the transducers map to the canonical token. They are the team's proposal and may grow as new résumé variants are found; the list below is the **minimum** that must be supported.

| Category | Canonical token | Accepted aliases (lowercase, after preprocessing) |
|---|---|---|
| LANGUAGE | `JAVASCRIPT` | `js`, `javascript`, `java script`, `ecmascript` |
| LANGUAGE | `TYPESCRIPT` | `ts`, `typescript`, `type script` |
| LANGUAGE | `PYTHON` | `python`, `python3`, `py` |
| LANGUAGE | `JAVA` | `java` |
| LANGUAGE | `SQL` | `sql` |
| FRONTEND | `REACT` | `react`, `react.js`, `reactjs`, `react js` |
| FRONTEND | `ANGULAR` | `angular`, `angular.js`, `angularjs` |
| FRONTEND | `VUE` | `vue`, `vue.js`, `vuejs`, `vue js` |
| BACKEND | `NODE_JS` | `node`, `node.js`, `nodejs`, `node js` |
| BACKEND | `DJANGO` | `django` |
| BACKEND | `SPRING_BOOT` | `spring boot`, `springboot`, `spring-boot` |
| API | `REST_API` | `rest`, `rest api`, `rest apis`, `restful`, `restful api` |
| DATABASE | `POSTGRESQL` | `postgres`, `postgresql`, `postgre sql` |
| DATABASE | `MYSQL` | `mysql`, `my sql` |
| DATABASE | `MONGODB` | `mongo`, `mongodb`, `mongo db` |
| VERSION_CONTROL | `GIT` | `git` |
| DATA_LIB | `PANDAS` | `pandas` |
| DATA_LIB | `NUMPY` | `numpy`, `num py` |
| ML_LIB | `SCIKIT_LEARN` | `sklearn`, `scikit learn`, `scikit-learn`, `scikitlearn` |
| ML_LIB | `TENSORFLOW` | `tensorflow`, `tensor flow`, `tf` |
| ML_LIB | `PYTORCH` | `pytorch`, `py torch`, `torch` |
| ML_PRACTICE | `ML_MODEL_DEVELOPMENT` | `machine learning`, `ml`, `ml models`, `predictive models` |
| OPERATING_SYSTEM | `LINUX` | `linux`, `ubuntu`, `gnu/linux` |
| CI_CD | `CI_CD` | `ci/cd`, `ci cd`, `cicd` |
| CONTAINER | `DOCKER` | `docker` |
| ORCHESTRATION | `KUBERNETES` | `kubernetes`, `k8s` |
| CLOUD | `AWS` | `aws`, `amazon web services` |
| PROCESSING | `SPARK` | `spark`, `apache spark`, `pyspark` |
| WORKFLOW | `AIRFLOW` | `airflow`, `apache airflow` |
| STREAMING | `KAFKA` | `kafka`, `apache kafka` |

> The last block (`LINUX` … `KAFKA`) supports the two **team-defined profiles** (Section 6.3). It is provisional until the professor confirms the requirements for those profiles; changing it only affects this table and the profile files, never the engine.

### 3.2 Rules for the vocabulary

1. **A token has exactly one canonical spelling.** Two different aliases that mean the same technology must map to the same token (`JS` and `Javascript` → `JAVASCRIPT`).
2. **An alias maps to exactly one token.** No alias may appear in two rows.
3. **Whole-string matching.** The transducer maps the *entire* input string. `java` must never match as a prefix of `javascript`.
4. **Single source of truth.** The vocabulary is stored in `src/resumelens/vocabulary.json` (token → category → aliases) and loaded by `vocabulary.py`. The transducers (Alejo) and the automata (Diego) both read it. Neither may hard-code token names.
5. **Adding a token** requires: a row in Section 3.1, an entry in `vocabulary.json`, and a one-line note in the change log (Section 13).

## 4. Preprocessing rules (applied before the transducers)

Preprocessing is **not** part of the transducers. It is a plain function `preprocess(raw: str) -> str` in `normalization.py` that applies, in this order:

1. `str.strip()` — remove leading and trailing whitespace.
2. `str.casefold()` — lowercase.
3. Collapse runs of internal whitespace into a single space.
4. Remove trailing punctuation characters (`,`, `;`, `:`, and a final `.` that is not part of an alias such as `node.js`).

Consequences for the formal models:

* **Σ of the transducers** = `a`–`z`, `0`–`9`, space, `.`, `-`, `/` (explicit, finite, listed in the 7-tuple).
* **Γ of the transducers** = `A`–`Z` and `_`.
* Any input character outside Σ means the string is **not recognized** (Decision D4).

## 5. Shared data models (`models.py`)

All stages exchange instances of the following dataclasses. They are the contract; the JSON examples elsewhere in this document are serializations of them.

```python
from dataclasses import dataclass, field


@dataclass
class Education:
    degree: str = ""          # e.g. "B.Sc. Computer Engineering"
    institution: str = ""     # e.g. "Universidad Icesi"
    year: str = ""            # kept as text: "2024", "2020-2024", "" if absent


@dataclass
class Experience:
    years: float | None = None   # "3 years of experience" -> 3.0; None if not stated
    description: str = ""        # e.g. "developing web applications"


@dataclass
class Candidate:
    name: str = ""                                   # "" if not detected
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)   # GitHub, LinkedIn, portfolio
    education: list[Education] = field(default_factory=list)
    experience: list[Experience] = field(default_factory=list)


@dataclass
class ExtractionResult:             # output of Stage 1
    candidate: Candidate
    raw_skills: list[str]           # surface strings, original case, in order, NOT deduplicated


@dataclass
class NormalizationResult:          # output of Stage 2
    tokens: list[str]               # canonical tokens, deduplicated, order of first appearance
    mapping: dict[str, str]         # raw string (as extracted) -> canonical token
    unrecognized: list[str]         # raw strings rejected by the transducers, in order


@dataclass
class ProfileResult:                # output of Stage 3, one per profile
    profile_id: str                 # e.g. "FULL_STACK_DEVELOPER"
    sequence: list[str]             # the sorted and filtered sequence the automaton consumed
    accepted: bool                  # True -> "ACCEPTED", False -> "REJECTED"


@dataclass
class PipelineResult:               # output of the orchestrator
    extraction: ExtractionResult
    normalization: NormalizationResult
    classifications: list[ProfileResult]
    dsl_text: str                   # validated DSL source
    html: str                       # visualization (HTML)
    markdown: str                   # visualization (Markdown)
```

### 5.1 Field-level guarantees

| Field | Guarantee |
|---|---|
| `Candidate.name` | Never `None`. `""` when not detected. |
| `Candidate.emails/phones/links/education/experience` | Never `None`. Empty list when absent. |
| `ExtractionResult.raw_skills` | Original spelling and case; duplicates preserved; order of appearance in the résumé. |
| `NormalizationResult.tokens` | Every element belongs to the canonical vocabulary. No duplicates. |
| `NormalizationResult.mapping` | Keys are the extracted strings; values are canonical tokens. `mapping.keys() ∪ unrecognized = set(raw_skills)`. |
| `ProfileResult.sequence` | Contains only tokens defined in that profile's slots, already sorted. |
| `PipelineResult.classifications` | Exactly one entry per configured profile (four), in the order of `profiles/` loading (Section 6.2). |

## 6. Stage contracts

### 6.1 Stage 1 — Extraction (regular expressions) · Alejo

```python
def extract(text: str) -> ExtractionResult: ...
```

| | |
|---|---|
| **Input** | `text: str`, the raw résumé text. May be empty. |
| **Output** | `ExtractionResult` |
| **Formal model** | One regular expression per information type (contact, programming languages, frameworks/libraries, databases, academic qualifications, professional experience, tools/technologies, other profile-relevant qualifications). |
| **Responsibility** | Detect *candidate strings*. It does **not** decide whether two strings are equivalent and does **not** decide whether the candidate satisfies a profile. |
| **Preserves** | The surface form of every skill (`"React.js"`, `"NodeJS"`), including case. |
| **Errors** | Raises `ExtractionError` only if `text` is not a `str`. Empty or unparsable text returns an `ExtractionResult` with empty fields. |

**Example (résumé fragment from the assignment):**

```
Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git.
```

```json
{
  "candidate": {
    "name": "Wednesday Addams",
    "emails": [],
    "phones": [],
    "links": [],
    "education": [],
    "experience": [{"years": 3.0, "description": "developing web applications"}]
  },
  "raw_skills": ["JS", "React.js", "NodeJS", "Postgres", "Git"]
}
```

### 6.2 Stage 2 — Normalization (finite-state transducers) · Alejo

```python
def preprocess(raw: str) -> str: ...                                  # Section 4
def build_transducer(canonical: str, aliases: list[str]): ...         # one pyformlang FST per token
def normalize(raw_skills: list[str]) -> NormalizationResult: ...
```

| | |
|---|---|
| **Input** | `raw_skills: list[str]` taken from `ExtractionResult`. |
| **Output** | `NormalizationResult` |
| **Formal model** | Finite-state transducers `M = (Q, Σ, Γ, δ, ω, q0, F)`. One transducer per canonical token, all generated by the same function from `vocabulary.json`; their union is used by `normalize`. |
| **Algorithm** | For each raw string: `preprocess` → run the transducers → if exactly one accepts, record `raw → TOKEN`; if none accepts, append to `unrecognized`. Then deduplicate tokens preserving first appearance. |
| **Does NOT** | Sort tokens by profile (that is Stage 2b) or filter them. |
| **Determinism** | For a given vocabulary, the same input always yields the same output. |
| **Errors** | Never raises for unknown strings (they go to `unrecognized`). Raises `ProfileConfigError`/`VocabularyError` only if `vocabulary.json` is malformed. |

**Example:**

```python
normalize(["JS", "React.js", "NodeJS", "Postgres", "Git", "Figma"])
# NormalizationResult(
#   tokens=["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
#   mapping={"JS": "JAVASCRIPT", "React.js": "REACT", "NodeJS": "NODE_JS",
#            "Postgres": "POSTGRESQL", "Git": "GIT"},
#   unrecognized=["Figma"],
# )
```

### 6.3 Stage 2b — Sorting and filtering by profile · Diego

```python
def sort_for_profile(tokens: list[str], profile: dict) -> list[str]: ...
```

| | |
|---|---|
| **Input** | `tokens` from `NormalizationResult`; `profile`, a loaded profile configuration (Section 7). |
| **Output** | The sequence the automaton will read. |
| **Filtering** | Tokens that do not appear in any slot of the profile are **dropped from the sequence** (Decision D5). They remain in `NormalizationResult.tokens` and are still shown in the DSL and the visualization. |
| **Ordering** | Primary key: the index of the slot that contains the token. Secondary key: the position of the token in that slot's `any_of` list. |
| **Result independence** | The output does not depend on the order in which the candidate wrote the skills (`sort_for_profile` is a function of the *set* of tokens). |

**Example (Full Stack profile):**

```python
sort_for_profile(["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT", "DOCKER"], full_stack)
# ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
```

### 6.4 Stage 3 — Qualification pattern recognition (finite automata) · Diego

```python
def build_automaton(profile: dict): ...                                        # pyformlang automaton
def classify(tokens: list[str], profiles: list[dict]) -> list[ProfileResult]: ...
```

| | |
|---|---|
| **Input** | `tokens` from `NormalizationResult` and the list of the four loaded profiles. |
| **Output** | One `ProfileResult` per profile, in the same order as `profiles`. |
| **Algorithm** | For each profile: `sequence = sort_for_profile(tokens, profile)` → build/reuse the automaton → `accepted = automaton.accepts(sequence)`. |
| **Formal model** | `M = (Q, Σ, δ, q0, F)`. Σ is the canonical vocabulary (Section 3). The type of each automaton (DFA, NFA, or ε-NFA) is chosen by Diego and justified in `docs/formalization.md` from the definition of its transition function. |
| **Semantics** | A profile accepts when, **for every non-optional slot, at least one of its `any_of` tokens appears**, and tokens appear in slot order. Several tokens of the same slot are allowed (Section 7.2). |
| **Multi-profile** | A résumé may be accepted by several profiles at the same time, or by none. |
| **Not a ranking** | The result is binary per profile. No scores, no ordering between candidates. |

**Example:**

```python
classify(["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "POSTGRESQL", "GIT"], profiles)
# [ProfileResult("FULL_STACK_DEVELOPER",       ["POSTGRESQL","GIT"],                 False),
#  ProfileResult("MACHINE_LEARNING_ENGINEER",  ["PYTHON","PANDAS","NUMPY","SCIKIT_LEARN",
#                                               "TENSORFLOW","POSTGRESQL","GIT"],      True),
#  ProfileResult("DEVOPS_ENGINEER",            ["GIT"],                              False),
#  ProfileResult("DATA_ENGINEER",              ["PYTHON","POSTGRESQL","GIT"],        False)]
```

### 6.5 Stage 4 — Candidate Profile Language (context-free grammar, textX) · Edwar

```python
def to_dsl(candidate: Candidate, tokens: list[str], results: list[ProfileResult]) -> str: ...
def validate(dsl_text: str): ...      # returns the textX model, or raises DSLValidationError
```

| | |
|---|---|
| **Input** | The `Candidate`, the normalized `tokens`, and the four `ProfileResult`s. |
| **Output of `to_dsl`** | DSL source text following the grammar in `candidate.tx`. |
| **Output of `validate`** | The parsed textX model on success. |
| **Must be representable** | Personal information, contact information, education records (repeated), professional experiences (repeated), skills (repeated), and the classification result for **each** profile. |
| **Rejection** | `validate` raises `DSLValidationError` for any text that violates the lexical or syntactic rules (unknown keyword, unclosed string, missing mandatory block, invalid token name, invalid classification value, etc.). The error message includes line and column when textX provides them. |
| **Round trip** | `validate(to_dsl(...))` must succeed for every `Candidate` the previous stages can produce. |

**Reference example (the grammar is the source of truth; this only shows the intended shape):**

```
candidate "Wednesday Addams" {
  contact { }
  experience { years 3 description "developing web applications" }
  skills { JAVASCRIPT REACT NODE_JS POSTGRESQL GIT }
  classification {
    FULL_STACK_DEVELOPER: ACCEPTED
    MACHINE_LEARNING_ENGINEER: REJECTED
    DEVOPS_ENGINEER: REJECTED
    DATA_ENGINEER: REJECTED
  }
}
```

### 6.6 Stage 4b — Visualization · Edwar

```python
def to_html(model) -> str: ...
def to_markdown(model) -> str: ...
```

| | |
|---|---|
| **Input** | The validated textX model (never raw dictionaries or unvalidated text). |
| **Output** | A short, self-contained HTML document, and a Markdown equivalent. |
| **Content** | Name, contact data, experience, education, normalized skills, and the result for each of the four profiles. |
| **Safety** | All text inserted into HTML must be escaped (`html.escape`). |

### 6.7 Orchestrator · Edwar

```python
def run(resume_text: str) -> PipelineResult: ...
```

```python
def run(resume_text):
    extraction = extract(resume_text)                                  # Stage 1
    normalization = normalize(extraction.raw_skills)                   # Stage 2
    profiles = load_profiles("profiles/")                              # Section 7
    classifications = classify(normalization.tokens, profiles)         # Stages 2b + 3
    dsl_text = to_dsl(extraction.candidate, normalization.tokens, classifications)
    model = validate(dsl_text)                                         # Stage 4
    return PipelineResult(extraction, normalization, classifications,
                          dsl_text, to_html(model), to_markdown(model))
```

The same function handles **all four profiles**; there is no per-profile code path (assignment requirement).

## 7. Professional profile configuration

Profiles are **data, not code**. Each profile is a JSON file in `profiles/`, loaded by a single `load_profiles()` function in `src/resumelens/profiles.py` (owner: Diego).

### 7.1 Format

```json
{
  "id": "PROFILE_ID",
  "display_name": "Human readable name",
  "slots": [
    {
      "category": "CATEGORY_NAME",
      "any_of": ["TOKEN_A", "TOKEN_B"],
      "optional": false
    }
  ]
}
```

| Key | Meaning |
|---|---|
| `id` | `UPPER_SNAKE_CASE`, unique across profiles. Used in the DSL and in `ProfileResult.profile_id`. |
| `slots` | **Ordered** list of pattern positions. The order defines the canonical order of the profile (Stage 2b) and the structure of the automaton (Stage 3). |
| `category` | Informational label (matches a category of Section 3.1). |
| `any_of` | Tokens that satisfy the slot. Every element must exist in the vocabulary. |
| `optional` | `true` means the slot may be skipped by the automaton. |
| `order` | *(optional)* Integer position of the profile in `PipelineResult.classifications`. Profiles without it go last, then by file name. |

### 7.2 Slot semantics (what the automaton recognizes)

* A slot is satisfied by **one or more** tokens from its `any_of` list (a résumé that lists both `PANDAS` and `NUMPY` satisfies the `DATA_LIB` slot).
* Within a slot, tokens appear in the order of `any_of` (guaranteed by Stage 2b).
* An `optional` slot may be absent.
* Slots appear in the order of the `slots` list.

### 7.3 Validation rules (enforced by `load_profiles`, raises `ProfileConfigError`)

1. `id` is non-empty and unique.
2. `slots` is non-empty.
3. Every token in every `any_of` exists in the canonical vocabulary.
4. **The `any_of` sets of different slots in the same profile are pairwise disjoint.** (Otherwise the same token could satisfy two slots and the automaton would become ambiguous.)
5. At least one slot is non-optional.

### 7.4 Profiles

**Reference profile 1 — `profiles/full_stack.json`**

```json
{
  "id": "FULL_STACK_DEVELOPER",
  "display_name": "Full Stack Developer",
  "slots": [
    {"category": "LANGUAGE",        "any_of": ["JAVASCRIPT", "TYPESCRIPT"],                       "optional": false},
    {"category": "FRONTEND",        "any_of": ["REACT", "ANGULAR", "VUE"],                        "optional": false},
    {"category": "BACKEND",         "any_of": ["NODE_JS", "DJANGO", "SPRING_BOOT"],               "optional": false},
    {"category": "DATABASE",        "any_of": ["SQL", "POSTGRESQL", "MYSQL", "MONGODB"],          "optional": false},
    {"category": "API",             "any_of": ["REST_API"],                                       "optional": true},
    {"category": "VERSION_CONTROL", "any_of": ["GIT"],                                            "optional": false}
  ]
}
```

Order: Language → Frontend → Backend → Database → API → Version control. `REST_API` is optional because the assignment's own example résumé (JS, React.js, NodeJS, Postgres, Git) does not mention it and must be accepted.

**Reference profile 2 — `profiles/ml_engineer.json`**

```json
{
  "id": "MACHINE_LEARNING_ENGINEER",
  "display_name": "Machine Learning Engineer",
  "slots": [
    {"category": "LANGUAGE",        "any_of": ["PYTHON"],                                         "optional": false},
    {"category": "DATA_LIB",        "any_of": ["PANDAS", "NUMPY"],                                "optional": false},
    {"category": "ML_LIB",          "any_of": ["SCIKIT_LEARN", "TENSORFLOW", "PYTORCH"],          "optional": false},
    {"category": "ML_PRACTICE",     "any_of": ["ML_MODEL_DEVELOPMENT"],                           "optional": true},
    {"category": "DATABASE",        "any_of": ["SQL", "POSTGRESQL", "MYSQL"],                     "optional": false},
    {"category": "VERSION_CONTROL", "any_of": ["GIT"],                                            "optional": false}
  ]
}
```

`ML_MODEL_DEVELOPMENT` is optional because the assignment's example automaton and example résumé do not require it as a separate token.

**Team-defined profile 3 (software engineering) — `profiles/devops_engineer.json`** *(provisional)*

```json
{
  "id": "DEVOPS_ENGINEER",
  "display_name": "DevOps Engineer",
  "slots": [
    {"category": "OPERATING_SYSTEM", "any_of": ["LINUX"],                                        "optional": false},
    {"category": "VERSION_CONTROL",  "any_of": ["GIT"],                                          "optional": false},
    {"category": "CI_CD",            "any_of": ["CI_CD"],                                        "optional": false},
    {"category": "CONTAINER",        "any_of": ["DOCKER"],                                       "optional": false},
    {"category": "ORCHESTRATION",    "any_of": ["KUBERNETES"],                                   "optional": true},
    {"category": "CLOUD",            "any_of": ["AWS"],                                          "optional": false}
  ]
}
```

**Team-defined profile 4 (AI / data) — `profiles/data_engineer.json`** *(provisional)*

```json
{
  "id": "DATA_ENGINEER",
  "display_name": "Data Engineer",
  "slots": [
    {"category": "LANGUAGE",         "any_of": ["PYTHON"],                                       "optional": false},
    {"category": "DATABASE",         "any_of": ["SQL", "POSTGRESQL", "MYSQL"],                   "optional": false},
    {"category": "PROCESSING",       "any_of": ["SPARK"],                                        "optional": false},
    {"category": "WORKFLOW",         "any_of": ["AIRFLOW"],                                      "optional": true},
    {"category": "STREAMING",        "any_of": ["KAFKA"],                                        "optional": true},
    {"category": "VERSION_CONTROL",  "any_of": ["GIT"],                                          "optional": false}
  ]
}
```

> Profiles 3 and 4 are **placeholders** until the professor provides the detailed requirements. Replacing them only requires editing the two JSON files and, if new technologies appear, the vocabulary (Section 3.2, rule 5). No Python module changes.

## 8. Design decisions that affect several modules

| ID | Decision | Rationale | Affects |
|---|---|---|---|
| D1 | Case-insensitive matching through `casefold()` in `preprocess`, **before** the transducers. | Avoids duplicating every transition for upper- and lowercase letters. Keeps the alphabet small enough to list explicitly in the 7-tuple. | Alejo |
| D2 | Transducer alphabets: Σ = `a–z`, `0–9`, space, `.`, `-`, `/`; Γ = `A–Z`, `_`. | Finite, explicit, and sufficient for the whole vocabulary. | Alejo |
| D3 | Automaton alphabet = set of canonical tokens; each token is **one symbol** (not a sequence of characters). | Equals Γ of the transducers (as strings), so Stage 2 output feeds Stage 3 directly. | Alejo, Diego |
| D4 | Strings not accepted by any transducer go to `NormalizationResult.unrecognized` and are not passed on. | A transducer without an accepting path produces no output; nothing is silently guessed. Keeps traceability for the poster and the tests. | Alejo, Diego, Edwar |
| D5 | Tokens that do not belong to a profile are filtered out before that profile's automaton. | A résumé that also lists Docker or Figma must not be rejected as Full Stack because of that. | Diego |
| D6 | Duplicate tokens are removed after normalization (`JS` + `Javascript` → one `JAVASCRIPT`). | Prevents repeated symbols in the automaton input. | Alejo |
| D7 | Slot semantics: one or more tokens from `any_of`; `optional` slots may be skipped. | The assignment's example résumés list several tokens of the same category (Pandas **and** NumPy). A single-token-per-slot automaton would reject them. | Diego |
| D8 | Every résumé is evaluated against **all four** profiles; zero, one, or several may be accepted. | The system classifies, it does not choose a single "best" profile or rank candidates. | Diego, Edwar |
| D9 | One transducer per canonical token, generated by the same function from `vocabulary.json`; their union is used at runtime. | Readable diagrams, and one code path for all tokens. The 7-tuple is documented per token family. | Alejo |
| D10 | Profiles are JSON configuration processed by a single engine. | The four profiles must go through the same general solution; new profiles require no code. | Diego, Edwar |

## 9. Errors

Defined in `errors.py`. Every error inherits from `ResumeLensError`.

| Exception | Raised by | When |
|---|---|---|
| `ExtractionError` | `extract` | Input is not a `str`. |
| `VocabularyError` | `vocabulary.py`, `normalize` | `vocabulary.json` is missing, malformed, or violates Section 3.2. |
| `ProfileConfigError` | `load_profiles` | A profile file violates Section 7.3. |
| `DSLValidationError` | `validate` | DSL text violates the lexical or syntactic rules of the grammar. |

Unknown or unsupported skills are **not** errors: they are reported in `NormalizationResult.unrecognized`.

## 10. Invariants (what must always be true)

1. `NormalizationResult.tokens` ⊆ canonical vocabulary.
2. `set(mapping.keys()) ∪ set(unrecognized) = set(raw_skills)` and the two sets are disjoint.
3. Reordering the skills in the résumé does not change any `ProfileResult.accepted`.
4. Adding a skill that belongs to no slot of a profile does not change that profile's result.
5. `len(classifications)` equals the number of loaded profiles (four).
6. `validate(to_dsl(candidate, tokens, results))` succeeds for every output of Stages 1–3.
7. No stage mutates its input.

Each invariant should have at least one automated test (`tests/`).

## 11. Worked examples (end to end)

### 11.1 Wednesday Addams (Full Stack Developer)

| Step | Value |
|---|---|
| Résumé skills line | `JS, React.js, NodeJS, Postgres, Git.` |
| Stage 1 `raw_skills` | `["JS", "React.js", "NodeJS", "Postgres", "Git"]` |
| Stage 2 `tokens` | `["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]` |
| Stage 2b (Full Stack) | `["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]` |
| Stage 3 | `FULL_STACK_DEVELOPER: ACCEPTED` (`REST_API` slot skipped) |
| Other profiles | `MACHINE_LEARNING_ENGINEER`, `DEVOPS_ENGINEER`, `DATA_ENGINEER`: `REJECTED` |

### 11.2 Out-of-order input (matches the assignment's sorting example)

| Step | Value |
|---|---|
| `raw_skills` | `["Git", "NodeJS", "JS", "Postgres", "React.js"]` |
| `tokens` (first appearance) | `["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]` |
| Sorted for Full Stack | `["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]` |
| Result | `FULL_STACK_DEVELOPER: ACCEPTED` |

### 11.3 Mary Jane Watson (Machine Learning Engineer)

| Step | Value |
|---|---|
| Résumé skills line | `Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git.` |
| `raw_skills` | `["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"]` |
| `tokens` | `["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]` |
| Sorted for ML | `["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]` |
| Result | `MACHINE_LEARNING_ENGINEER: ACCEPTED` (both `PANDAS` and `NUMPY`, both `SCIKIT_LEARN` and `TENSORFLOW`, accepted by D7) |

### 11.4 Rejection and noise

| Step | Value |
|---|---|
| `raw_skills` | `["JS", "React.js", "Docker", "Figma", "Git"]` |
| `tokens` | `["JAVASCRIPT", "REACT", "DOCKER", "GIT"]`; `unrecognized = ["Figma"]` |
| Sorted for Full Stack | `["JAVASCRIPT", "REACT", "GIT"]` (`DOCKER` filtered by D5) |
| Result | `FULL_STACK_DEVELOPER: REJECTED` (no backend, no database) |

## 12. Change policy

1. Any change to Sections 3, 5, 6, or 7 requires agreement of **all three** members.
2. The proposer opens the change as a normal commit that modifies this file and `models.py`/`vocabulary.json` together, so the repository is never inconsistent.
3. Update the version number and add a line to the change log below.
4. Each member must adapt their module (and its tests) before the next integration sync.
5. Do not change the contract by "just making the code work": if a module needs a different interface, change the document first.

## 13. Change log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-10-05 | Alejo, Diego, Edwar | Initial contract: pipeline, data models, vocabulary, profile format, decisions D1–D10. |
| 1.1 | 2026-10-09 | Diego | Repository fixes: package `__init__.py`, `requirements.txt`, `pyproject.toml`, `.gitattributes` (LF), `candidate.tx` extension, profile files renamed to `devops_engineer.json` / `data_engineer.json`. Shared code created as specified in Sections 3, 5 and 9 (`models.py`, `errors.py`, `vocabulary.py`, `vocabulary.json`). `load_profiles()` placed in `profiles.py`. No interface was changed. |
| 1.2 | 2026-10-09 | Diego | Optional `order` key in the profile format (Section 7.1) so the four results always come out as Full Stack, ML, DevOps, Data. The four profile files filled in as listed in Section 7.4. |
| 1.3 | 2026-10-09 | Diego | Fix the `classify` example of Section 6.4: the Full Stack sequence is `["POSTGRESQL", "GIT"]` (both tokens belong to Full Stack slots), not `[]`. Stage 3 automata documented as ε-NFAs built from the slots. |

## 14. Open items

| Item | Owner | Notes |
|---|---|---|
| Final requirements of the two team-defined profiles | Professor / all | Profiles 3 and 4 in Section 7.4 are provisional. |
| Final alias list | Alejo | Extend with real résumé variants found while testing the regex stage. |
| Automaton type per profile (DFA / NFA / ε-NFA) | Diego | Justify in `docs/formalization.md`. |
| EBNF of the candidate language | Edwar | Lives in `docs/formalization.md` and `candidate.tx`. |
| Short or ambiguous aliases (`ts`, `tf`, `ml`, `py`, `torch`, `node`) | Alejo, Diego | Keep only if tests show no false positives. |