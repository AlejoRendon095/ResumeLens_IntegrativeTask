# ResumeLens — Formal Language-Based Resume Screening

Integrative Task 1 · Computación y Estructuras Discretas III · Universidad Icesi · 2026-2

ResumeLens processes plain-text résumés and determines, for each of four professional profiles, whether the qualifications explicitly stated in the résumé satisfy a formally defined qualification pattern. It does **not** rank candidates, evaluate personal merit, or make automated hiring decisions.

---

## 1. Formal Models and Architecture

ResumeLens integrates four distinct formal computational models into a sequential pipeline:

| Stage | Formal Model | Computational Tool / Library | Module | Owner |
|---|---|---|---|---|
| **1. Extraction** | Regular Expressions | Python standard library `re` | [`extraction.py`](src/resumelens/extraction.py) | Alejandro Rendón |
| **2. Normalization** | Finite-State Transducers (7-tuple FST) | `pyformlang` | [`normalization.py`](src/resumelens/normalization.py) | Alejandro Rendón |
| **2b. Sorting / Filtering** | Canonical Slot Ordering | Standard Python | [`sorting.py`](src/resumelens/sorting.py) | Juan Diego Balanta |
| **3. Recognition** | Finite-State Automata (5-tuple FSA) | `pyformlang` | [`recognition.py`](src/resumelens/recognition.py) | Juan Diego Balanta |
| **4. Candidate Language** | Context-Free Grammar (EBNF) | `textX` | [`dsl.py`](src/resumelens/dsl.py), [`candidate.tx`](src/resumelens/candidate.tx) | Edwar Estacio |
| **4b. Visualization** | Semantic HTML / Markdown Rendering | Standard Python | [`render.py`](src/resumelens/render.py) | Edwar Estacio |
| **Pipeline & CLI** | Orchestration & Console Application | Standard Python (`argparse`) | [`pipeline.py`](src/resumelens/pipeline.py), [`app.py`](src/resumelens/app.py) | Edwar Estacio |

Detailed system diagrams are available in [`docs/diagrams/diagram.md`](docs/diagrams/diagram.md).

---

## 2. Professional Profiles

The screening engine evaluates candidates against four configured profiles:

1. **Full Stack Developer** (`profiles/full_stack.json`): Requires Language (JS/TS), Frontend (React/Angular/Vue), Backend (Node/Django/Spring), Database (SQL/Postgres/MySQL/MongoDB), Version Control (Git), and optional API (REST).
2. **Machine Learning Engineer** (`profiles/ml_engineer.json`): Requires Python, Data libraries (Pandas/NumPy), ML libraries (Scikit-learn/TensorFlow/PyTorch), Database, Version Control (Git), and optional ML practice.
3. **DevOps Engineer** (`profiles/devops_engineer.json`): Software engineering profile requiring Linux, Git, CI/CD, Docker, Cloud (AWS), and optional Kubernetes.
4. **Data Engineer** (`profiles/data_engineer.json`): AI/data profile requiring Python, Database, Spark, Git, and optional Airflow/Kafka.

All four profiles are processed through the same shared engine without profile-specific branching.

---

## 3. Team Responsibilities

| Member | Primary Responsibility |
|---|---|
| **Alejandro Rendón Garzón** | Stage 1 (Regex extraction) and Stage 2 (FST normalization). |
| **Juan Diego Balanta Molina** | Profile configurations, Stage 2b (sorting) and Stage 3 (FSA pattern recognition). |
| **Edwar Estacio** | Stage 4 (CFG grammar, textX DSL), Stage 4b (HTML/Markdown renderers), pipeline orchestrator and CLI application. |

The interfaces, data structures, and shared decisions governing module interactions are specified in [`docs/contracts.md`](docs/contracts.md).

---

## 4. Setup and Installation

### Requirements
* Python 3.10 or newer (tested on Python 3.10, 3.11, 3.12, 3.13)
* Virtual environment tool (`venv`)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/AlejoRendon095/ResumeLens_IntegrativeTask.git
cd ResumeLens_IntegrativeTask

# 2. Create and activate a virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 5. Usage and CLI Application

ResumeLens can be executed via its command-line interface:

### 5.1 Basic Execution (Terminal Summary)

```bash
python -m resumelens samples/wednesday_addams.txt
```

Example terminal output:
```text
============================================================
 ResumeLens — Candidate Analysis: Wednesday Addams
============================================================

Normalized Skills:
  JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT

Qualification Pattern Recognition:
  [ACCEPTED] FULL_STACK_DEVELOPER
  [REJECTED] MACHINE_LEARNING_ENGINEER
  [REJECTED] DEVOPS_ENGINEER
  [REJECTED] DATA_ENGINEER
============================================================
```

### 5.2 Exporting Artifacts to Disk

To generate and export the candidate DSL specification (`.dsl`), self-contained HTML report (`.html`), and formatted Markdown document (`.md`):

```bash
python -m resumelens samples/wednesday_addams.txt -o output/
```

This creates:
- `output/wednesday_addams.dsl`: The validated context-free domain-specific language representation.
- `output/wednesday_addams.html`: Self-contained, responsive HTML visualization with security-escaped entities.
- `output/wednesday_addams.md`: Structured Markdown documentation.

### 5.3 CLI Options and Flags

```bash
python -m resumelens --help
```

| Option | Flag | Description |
|---|---|---|
| `resume_path` | Positional | Path to the candidate plain-text résumé file. |
| `--output-dir` | `-o` | Directory path where generated artifacts (`.dsl`, `.html`, `.md`) are saved. |
| `--format` | — | Display format printed to stdout (`summary`, `dsl`, `markdown`, `html`). Default: `summary`. |
| `--quiet` | `-q` | Suppress console output (useful for automated batch scripts). |

### 5.4 Evaluating Different Candidate Profiles

```bash
# Machine Learning Engineer profile
python -m resumelens samples/mary_jane_watson.txt

# DevOps Engineer profile
python -m resumelens samples/linus_torvalds.txt

# Data Engineer profile
python -m resumelens samples/grace_hopper.txt

# Rejected / Noise candidate
python -m resumelens samples/rejected_candidate.txt
```

---

## 6. Running the Test Suite

The automated test suite covers all pipeline stages, model contracts, security escaping, and end-to-end integration:

```bash
pytest
```

To run with verbose output:
```bash
pytest -v
```

The test suite includes 101 tests across eight test modules:
- `tests/test_extraction.py`: Regular expression matching for contact, education, experience, and skills.
- `tests/test_vocabulary.py`: Canonical vocabulary integrity, alphabet validation, and alias constraints.
- `tests/test_normalization.py`: Preprocessing and finite-state transducer mappings.
- `tests/test_models.py`: Dataclass immutability and default field guarantees.
- `tests/test_dsl.py`: Context-free grammar validation, round-trip serialization, and syntax rejection.
- `tests/test_render.py`: Markdown and HTML rendering, XSS prevention, and empty-state handling.
- `tests/test_pipeline.py`: Stage orchestration, dependency injection, and contract invariants.
- `tests/test_app.py`: CLI flags, exit codes, and artifact file generation.
- `tests/test_integration.py`: End-to-end evaluation using sample résumés in `samples/`.

---

## 7. Documentation Index

Comprehensive academic and technical documentation is available under `docs/`:

- [`docs/contracts.md`](docs/contracts.md): Interface contracts, canonical vocabulary (30 tokens), profile formats, and cross-module decisions (D1–D10).
- [`docs/formalization.md`](docs/formalization.md): Mathematical formalization of the computational models (Regex, FST 7-tuple, FSA 5-tuple, and CFG EBNF 4-tuple).
- [`docs/design_modules.md`](docs/design_modules.md): Architectural design, module responsibilities, inputs, outputs, and exception hierarchy.
- [`docs/test_cases.md`](docs/test_cases.md): Test scenarios, canonical evaluation cases, and contract invariants verification.
- [`docs/diagrams/diagram.md`](docs/diagrams/diagram.md): Mermaid sequence and flowchart architectural diagrams.
- [`docs/iag_log.md`](docs/iag_log.md): Formal log of generative AI interactions, prompts, student contributions, and adaptations.
