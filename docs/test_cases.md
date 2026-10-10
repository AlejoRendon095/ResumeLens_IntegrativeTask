# Test Cases and Verification Scenarios

This document formalizes the validation test suite and evaluation scenarios for ResumeLens, covering each stage of the pipeline and the end-to-end qualification screening system.

---

## 1. Test Suite Structure

The ResumeLens verification framework is divided into five test modules:

| Test Module | Coverage | Associated Stage |
|---|---|---|
| `test_extraction.py` | Regular expression pattern matching for contact, education, experience, and raw skills. | Stage 1 (Regex) |
| `test_vocabulary.py` | Canonical vocabulary integrity, alphabet compliance ($\Sigma$ and $\Gamma$), rules of Section 3.2. | Core Shared |
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
