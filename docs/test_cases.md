# Test Cases and Verification Scenarios

This document formalizes the validation test suite and evaluation scenarios for ResumeLens, covering each stage of the pipeline and the end-to-end qualification screening system.

---

## 1. Test Suite Structure

The ResumeLens verification framework is divided into the following test modules:

| Test Module | Coverage | Associated Stage |
|---|---|---|
| `test_extraction.py` | Regular expression pattern matching for contact, education, experience, and raw skills. | Stage 1 (Regex) |
| `test_normalization.py` | Preprocessing, one transducer per canonical token, whole-string matching, deduplication and unrecognized strings. | Stage 2 (FST) |
| `test_vocabulary.py` | Canonical vocabulary integrity, alphabet compliance ($\Sigma$ and $\Gamma$), rules of Section 3.2. | Core Shared |
| `test_profiles.py` | Profile files: the four project profiles load in order; validation rules of contract Section 7.3. | Profiles (configuration) |
| `test_sorting.py` | Filtering and canonical ordering by profile; permutation independence; no mutation. | Stage 2b (Sorting) |
| `test_recognition.py` | ε-NFA built from the slots; classification of the contract and assignment examples. | Stage 3 (FSA) |
| `test_automata.py` | ε-NFA ≡ DFA ≡ minimal DFA for the four profiles; 5-tuple export; invariants 3, 4, 5, 7. | Stage 3 (FSA) |
| `test_diagrams.py` | Mermaid / Graphviz diagrams contain every transition, initial and accepting states. | Stage 3 (docs) |
| `test_recognition_scenarios.py` | Scenarios S2B-1…4 and S3-1…7 below, run through the complete pipeline. | Stages 2b + 3 |
| `test_dsl.py` | Context-free grammar syntax, textX parsing, round-trip serialization, and syntax rejection. | Stage 4 (CFG) |
| `test_render.py` | HTML / Markdown generation, structural completeness, CSS styling, and XSS escaping. | Stage 4b (Render) |
| `test_pipeline.py` | Orchestration, stage resolution, error propagation, and contract invariants. | Pipeline Core |
| `test_app.py` | Command-line interface (CLI), exit codes, flag options, and disk artifact exports. | Application |
| `test_integration.py` | End-to-end evaluation using realistic sample CV files from `samples/`. | System E2E |

---

## 2. End-to-End Evaluation Scenarios

### Scenario 1: Full Stack Developer (`samples/wednesday_addams.txt`)

- **Candidate:** Wednesday Addams
- **Input Text:**
  ```text
  Wednesday Addams
  wednesday@nevermore.edu | https://github.com/wednesday
  3 years of experience developing web applications.
  Technical Skills:
  JS, React.js, NodeJS, Postgres, Git.
  ```
- **Expected Extracted Skills:** `["JS", "React.js", "NodeJS", "Postgres", "Git"]`
- **Expected Normalized Tokens:** `["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]`
- **Expected Profile Verdicts:**
  - `FULL_STACK_DEVELOPER`: **ACCEPTED** (All mandatory slots satisfied; optional `REST_API` skipped).
  - `MACHINE_LEARNING_ENGINEER`: **REJECTED** (Missing Python, Data libs, ML libs).
  - `DEVOPS_ENGINEER`: **REJECTED** (Missing Linux, Docker, CI/CD, AWS).
  - `DATA_ENGINEER`: **REJECTED** (Missing Python, Spark).

---

### Scenario 2: Machine Learning Engineer (`samples/mary_jane_watson.txt`)

- **Candidate:** Mary Jane Watson
- **Input Text:**
  ```text
  Mary Jane Watson
  mj.watson@dailybugle.com | https://linkedin.com/in/mjwatson
  5 years of experience developing predictive models.
  Technical Skills:
  Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git.
  ```
- **Expected Extracted Skills:** `["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"]`
- **Expected Normalized Tokens:** `["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]`
- **Expected Profile Verdicts:**
  - `FULL_STACK_DEVELOPER`: **REJECTED** (Missing frontend and backend frameworks).
  - `MACHINE_LEARNING_ENGINEER`: **ACCEPTED** (Multiple tokens satisfying DATA_LIB and ML_LIB slots).
  - `DEVOPS_ENGINEER`: **REJECTED** (Missing DevOps stack).
  - `DATA_ENGINEER`: **REJECTED** (Missing Spark).

---

### Scenario 3: DevOps Engineer (`samples/linus_torvalds.txt`)

- **Candidate:** Linus Torvalds
- **Input Text:**
  ```text
  Linus Torvalds
  linus@kernel.org | https://github.com/torvalds
  10 years of experience building scalable systems and infrastructure.
  Technical Skills:
  Linux, Git, CI/CD, Docker, Kubernetes, AWS.
  ```
- **Expected Normalized Tokens:** `["LINUX", "GIT", "CI_CD", "DOCKER", "KUBERNETES", "AWS"]`
- **Expected Profile Verdicts:**
  - `FULL_STACK_DEVELOPER`: **REJECTED**
  - `MACHINE_LEARNING_ENGINEER`: **REJECTED**
  - `DEVOPS_ENGINEER`: **ACCEPTED** (Operating system, containerization, orchestration, CI/CD, and cloud verified).
  - `DATA_ENGINEER`: **REJECTED**

---

### Scenario 4: Data Engineer (`samples/grace_hopper.txt`)

- **Candidate:** Grace Hopper
- **Input Text:**
  ```text
  Grace Hopper
  grace.hopper@navy.mil | https://github.com/ghopper
  8 years of experience designing high-throughput data processing pipelines.
  Technical Skills:
  Python, SQL, Spark, Airflow, Kafka, Git.
  ```
- **Expected Normalized Tokens:** `["PYTHON", "SQL", "SPARK", "AIRFLOW", "KAFKA", "GIT"]`
- **Expected Profile Verdicts:**
  - `FULL_STACK_DEVELOPER`: **REJECTED**
  - `MACHINE_LEARNING_ENGINEER`: **REJECTED**
  - `DEVOPS_ENGINEER`: **REJECTED**
  - `DATA_ENGINEER`: **ACCEPTED** (Python, SQL, processing, streaming, workflow orchestration, version control).

---

### Scenario 5: Rejection and Noise Handling (`samples/rejected_candidate.txt`)

- **Candidate:** John Doe
- **Input Text:**
  ```text
  John Doe
  john.doe@example.com | +1-555-9999
  1 year of experience in IT support.
  Technical Skills:
  Figma, Photoshop, Microsoft Word, Jira, Git.
  ```
- **Expected Normalized Tokens:** `["GIT"]`
- **Expected Unrecognized Skills:** `["Figma", "Photoshop", "Microsoft Word", "Jira"]`
- **Expected Profile Verdicts:** All profiles evaluated as **REJECTED**.

---

## 3. Formal Invariants Verification

The test suite systematically enforces the following contract invariants (Section 10 of `docs/contracts.md`):

1. **Alphabet Invariance ($\text{tokens} \subseteq \Gamma$):** Every token emitted by normalization belongs to the canonical vocabulary.
2. **Partition Invariance:** $\text{mapping.keys()} \cup \text{unrecognized} = \text{raw\_skills}$ and $\text{mapping.keys()} \cap \text{unrecognized} = \emptyset$.
3. **Permutation Invariance:** Permuting the order of skill declarations in the résumé yields identical qualification verdicts across all profiles.
4. **Noise Invariance:** Adding unmapped or extraneous tools does not affect existing profile decisions.
5. **Cardinality Invariance:** Exactly four `ProfileResult` objects are returned, corresponding to the configured profiles.
6. **DSL Round-Trip Invariance:** For every pipeline execution, $\text{validate}(\text{to\_dsl}(\dots))$ succeeds without error.
7. **Immutability Invariance:** Intermediate dataclasses are not mutated during stage execution.

---

## 4. Stages 2b and 3 — Sorting and Qualification Pattern Recognition

*Owner: Diego. Automated in `tests/test_recognition_scenarios.py` (complete pipeline) and, at unit level, in `tests/test_sorting.py`, `tests/test_recognition.py` and `tests/test_automata.py`.*

Each scenario is a short résumé whose `Technical Skills` line is given below. "Sequence" is what the automaton of that profile reads after Stage 2b (filtered and sorted).

### 4.1 Stage 2b — what each automaton reads

| ID | Skills line | Profile | Expected sequence | What it checks |
|---|---|---|---|---|
| S2B-1 | Git, MySQL, Django, Vue, TypeScript | Full Stack | TYPESCRIPT VUE DJANGO MYSQL GIT | Canonical order does not depend on the writing order. |
| S2B-2 | TypeScript, Vue, Django, MySQL, Git, Docker, Figma | Full Stack | TYPESCRIPT VUE DJANGO MYSQL GIT | `DOCKER` (other profile) is filtered out; `Figma` is reported as unrecognized; the profile is still accepted. |
| S2B-3 | JS, Javascript, ReactJS, React.js, Node.js, MongoDB, REST APIs, Git | Full Stack | JAVASCRIPT REACT NODE_JS MONGODB REST_API GIT | Two aliases of the same technology become one symbol. |
| S2B-4 | Python, PostgreSQL, Spark, Git, Linux | Data Engineer / DevOps | PYTHON POSTGRESQL SPARK GIT / LINUX GIT | One résumé produces a different word for each automaton. |

### 4.2 Stage 3 — accepted patterns

| ID | Skills line | Expected accepted profiles | What it checks |
|---|---|---|---|
| S3-1 | JS, React.js, Node.js, MongoDB, REST APIs, Git | Full Stack | Optional slot (REST) used: path q4 →REST_API p4 →ε q5. |
| S3-2 | tensor flow, py torch, sklearn, num py, python3, sql, git | ML Engineer | Lower-case and spaced aliases; two ML libraries read by the slot loop. |
| S3-3 | Ubuntu, Git, CI/CD, Docker, K8s, AWS | DevOps | Alias tokens (Ubuntu → LINUX, K8s → KUBERNETES); optional orchestration slot used. |
| S3-4 | Python, SQL, PySpark, Git | Data Engineer | Two consecutive optional slots skipped: q3 →ε q4 →ε q5. |
| S3-5 | Python, Pandas, Scikit-learn, PostgreSQL, Spark, Airflow, Git | ML Engineer **and** Data Engineer | A résumé can satisfy several profiles; the result is not a ranking. |

### 4.3 Stage 3 — rejected patterns

| ID | Skills line | Missing mandatory slot | Expected result |
|---|---|---|---|
| S3-6a | JavaScript, React, Git | Backend and database | Rejected by every profile |
| S3-6b | Linux, Git, Docker, AWS | CI/CD | Rejected by every profile |
| S3-6c | Python, Pandas, SQL, Git | ML library | Rejected by every profile |
| S3-6d | Python, PostgreSQL, Airflow, Kafka, Git | Processing engine (Spark) | Rejected by every profile |
| S3-7 | *(no skills section)* | All | Every sequence is empty and every profile rejects |

### 4.4 Properties checked on the automata

| Property | How it is tested |
|---|---|
| The ε-NFA, the subset-construction DFA and the minimal DFA accept the same language | `is_equivalent_to` from pyformlang, 300 random words per profile and every word of length ≤ 6 for DevOps (`test_automata.py`). |
| The automaton alone requires slot order | An unsorted word (`REACT JAVASCRIPT …`) is rejected by `recognize` (`test_recognition.py`); in the pipeline Stage 2b always sorts first. |
| Adding a token outside the profile never changes its verdict | Every token of the vocabulary that is not in the profile is added to five résumés (`test_automata.py`, invariant 4). |
| Profile files are valid | Overlapping slots, unknown tokens, empty or all-optional profiles and duplicated ids raise `ProfileConfigError` (`test_profiles.py`). |

---

## 5. Stages 1 and 2 — Extraction and Normalization

*Documents the tests written by Alejo in `tests/test_extraction.py` and `tests/test_normalization.py`.*

### 5.1 Stage 1 — regular-expression extraction

| ID | Input (fragment) | Expected output | What it checks |
|---|---|---|---|
| S1-1 | Wednesday Addams résumé (name, experience line, `Technical Skills:` line) | name `Wednesday Addams`; experience 3.0 years, "developing web applications"; `raw_skills` = JS, React.js, NodeJS, Postgres, Git | Name, experience and skills-section patterns on the assignment example. |
| S1-2 | `Skills: js, JS, Javascript` / `CI/CD, Docker` | `["js", "JS", "Javascript"]` / `["CI/CD", "Docker"]` | Surface form, case and duplicates are preserved; `/` is kept inside a skill. |
| S1-3 | Two e-mails, three phone formats, three links on separate lines | All of them, in order of appearance | Contact patterns (e-mail, phone with country code/parentheses/dashes, URLs). |
| S1-4 | `5+ years of experience leading teams.` / `3 años de experiencia en análisis de datos.` | 5.0 "leading teams"; 3.0 "análisis de datos" | Experience pattern in English and Spanish, including `N+`. |
| S1-5 | `B.Sc. Computer Science - Universidad de los Andes - 2020-2024` | degree, institution and year range | Education pattern. |
| S1-6 | `Engineer` / `Engineering` alone | No education record | The degree pattern does not fire on job titles. |
| S1-7 | Text without a skills section: `I work with React.js and Git.` | `["React.js", "Git"]` | Fallback search of known aliases in free text. |
| S1-8 | `I use JS, ML, TF, REST, Node, Torch, Git, and React.` | `["Git", "React"]` | The fallback ignores short or ambiguous aliases (JS, ML, TF, REST, Node, Torch) to avoid false positives. |
| S1-9 | `Technical Skills:` followed by an `Education` header without colon | Skills stop at the header | The skills section ends at the next section header. |
| S1-10 | Empty string; Windows line endings; first line `Resume` | Empty fields, no crash; name `""` when the first line is not a name | Robustness and the "never `None`" rule of the contract. |
| S1-11 | `None` or `123` | `ExtractionError` | Contract Section 9. |

### 5.2 Stage 2 — finite-state transducer normalization

| ID | Input | Expected output | What it checks |
|---|---|---|---|
| S2-1 | `"  JS "`, `"React.js,"`, `"Node  JS"`, `"Scikit-learn."` | `js`, `react.js`, `node js`, `scikit-learn` | `preprocess`: strip, casefold, collapse spaces, remove trailing punctuation but keep `.js`. |
| S2-2 | `js`, `javascript`, `java script` | `JAVASCRIPT` | One transducer per token accepts every alias of its row. |
| S2-3 | `java` on the JAVASCRIPT transducer | no output | Whole-string matching: `java` is not a prefix match of `javascript`. |
| S2-4 | Every alias of `vocabulary.json` | Its own canonical token | The 30 generated transducers cover the full vocabulary. |
| S2-5 | `JS, React.js, NodeJS, Postgres, Git` | `JAVASCRIPT REACT NODE_JS POSTGRESQL GIT`, full `mapping`, `unrecognized = []` | Assignment example. |
| S2-6 | `Git, NodeJS, JS, Postgres, React.js` | Tokens in first-appearance order | Stage 2 does not sort (sorting is Stage 2b). |
| S2-7 | `JS, Javascript, js` | `tokens = [JAVASCRIPT]`, three mapping keys | Deduplication (decision D6) without losing traceability. |
| S2-8 | `JS, Figma, Git, Figma, c#` | `tokens = [JAVASCRIPT, GIT]`, `unrecognized = [Figma, c#]` | Unknown skills are reported once and never guessed (decision D4); `#` is outside Σ. |
| S2-9 | `None`, `"JS"`, `[1, 2]` | `TypeError` | Argument types (a list or tuple of strings is required). |

## 6. Stage 4 — Candidate Profile Language and Visualization

*Documents the tests written by Edwar in `tests/test_dsl.py` and `tests/test_render.py`.*

### 6.1 Accepted DSL

| ID | Input | Expected result | What it checks |
|---|---|---|---|
| S4-1 | Reference example of contract Section 6.5 | Parsed model with name, experience, skills and four classifications | The grammar accepts the agreed shape. |
| S4-2 | `to_dsl` of a complete candidate (contacts, education, experience, skills) | `validate(to_dsl(...))` succeeds and returns the same data | Round trip (invariant 6). |
| S4-3 | `to_dsl` of a candidate with only a name and classifications | Valid DSL | Optional blocks may be absent. |

### 6.2 Rejected DSL (lexical or syntactic errors)

| ID | Input | Expected result | Error type |
|---|---|---|---|
| S4-4 | Empty or whitespace-only text | `DSLValidationError` | Missing start symbol |
| S4-5 | Missing `candidate` keyword | `DSLValidationError` | Syntactic |
| S4-6 | Missing `classification` block | `DSLValidationError` with line number | Syntactic (mandatory block) |
| S4-7 | Verdict `MAYBE` | `DSLValidationError` with line number | Lexical (only `ACCEPTED` / `REJECTED`) |
| S4-8 | Skill token `javascript` (lower case) | `DSLValidationError` | Lexical (tokens are `[A-Z][A-Z_]*`) |
| S4-9 | Unclosed string `"Wednesday Addams {` | `DSLValidationError` | Lexical |
| S4-10 | Unknown block `unknown_block { … }` | `DSLValidationError` | Syntactic |

### 6.3 Visualization

| ID | Input | Expected result | What it checks |
|---|---|---|---|
| S4-11 | Complete validated model | Markdown and HTML with name, contacts, education, experience, skills and the four verdicts | Completeness of both outputs. |
| S4-12 | Name and description with `<script>`, `&`, quotes | Escaped entities in the HTML, no raw `<script>` | XSS protection (`html.escape`). |
| S4-13 | Model without contacts, education, experience or skills | "No … provided" messages and REJECTED badges | Empty states. |
| S4-14 | 1 year and 2.5 years of experience | "1 year", "2.5 years" | Singular and fractional years. |
| S4-15 | `None` or a plain dictionary | `TypeError` | Rendering only accepts a validated model (contract Section 6.6). |
