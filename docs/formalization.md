# Formalization of Computational Models

This document presents the formal definitions and theoretical models used across the ResumeLens pipeline. Each section is written by the owner of the stage (see `docs/contracts.md`, Section 1).

---

## 1. Regular Expressions (Stage 1 — Alejo)

*TODO: Document regular expressions for candidate contact, education, experience, and skill surface strings.*

---

## 2. Finite-State Transducers — 7-Tuple (Stage 2 — Alejo)

*TODO: Document the 7-tuple $M = (Q, \Sigma, \Gamma, \delta, \omega, q_0, F)$ for canonical skill normalization.*

---

## 3. Finite Automata — 5-Tuple (Stage 3 — Diego)

*Stage 3: qualification pattern recognition. Owner: Diego (Juan Diego Balanta Molina). Code: `src/resumelens/recognition.py`, `src/resumelens/sorting.py`, `profiles/*.json`.*

### 3.1 What the automata decide

Each of the four professional profiles has its own automaton. The automaton reads the canonical tokens of a résumé (output of Stage 2, already filtered and sorted for that profile by Stage 2b) and answers ACCEPTED or REJECTED. A résumé is evaluated against the four profiles independently, so it can be accepted by several of them or by none. The result is binary per profile; it is not a ranking of candidates.

### 3.2 Alphabet

The input alphabet of every automaton is a subset of the canonical vocabulary (`src/resumelens/vocabulary.json`), which is exactly the output alphabet Γ of the Stage 2 transducers. Each canonical token is **one symbol**: `NODE_JS` is a single letter of Σ, not a sequence of characters. For a profile with slots S1, …, Sn,

Σ = S1 ∪ S2 ∪ … ∪ Sn

where Si is the set of tokens of slot i (`any_of`). The sets Si are pairwise disjoint (rule 4 of the profile format), so every symbol belongs to exactly one slot.

Tokens of the résumé that belong to no slot of the profile are removed by Stage 2b before the automaton runs (design decision D5). Without that filter, a Full Stack candidate who also lists Docker would be rejected for knowing *more*, and the alphabet would have to include the whole vocabulary.

### 3.3 Construction and type of the automata

All four automata are produced by the same function, `build_enfa(profile)`, from the ordered list of slots. This keeps the four profiles in one general solution (assignment requirement) and makes the diagrams and tables in this document reproducible: they are generated from the same objects that classify résumés (`scripts/export_diagrams.py`).

**Pattern.** A profile pattern is satisfied when the slots appear in order and every mandatory slot contributes at least one of its tokens; an optional slot may be absent; a slot may contribute several tokens (Mary Jane Watson lists both Pandas and NumPy). Over Σ this is the regular language

L = S1^k1 · S2^k2 · … · Sn^kn,  with ki = `+` if slot i is mandatory and ki = `*` if it is optional.

**States.** For n slots, Q = {q0, …, qn} ∪ {p0, …, p(n-1)}, so |Q| = 2n + 1:

* qi means "the automaton is about to read slot i" (qn means "all slots are done");
* pi means "at least one token of slot i has been read".

**Transitions.** For every slot i and every token t ∈ Si:

* δ(qi, t) ∋ pi: the first token of the slot;
* δ(pi, t) ∋ pi: more tokens of the same slot (loop);
* δ(pi, ε) ∋ q(i+1): the slot is satisfied, move to the next one;
* δ(qi, ε) ∋ q(i+1): only when slot i is optional, skip it.

**Initial and accepting states.** q0 is the initial state and F = {qn}.

**Type: ε-NFA.** The transition relation is δ : Q × (Σ ∪ {ε}) → P(Q) and it contains ε-moves (pi →ε q(i+1) for every slot, and qi →ε q(i+1) for optional slots). A DFA requires δ : Q × Σ → Q, with no ε and exactly one next state, and a plain NFA allows several next states but no ε. Because ε appears in the domain of δ, these automata are ε-NFAs. `automaton_kind()` in the code checks exactly this property on the transition relation.

We use the ε-NFA as the model because it is a direct, slot-by-slot translation of the profile: each slot is a small "one-or-more" gadget joined to the next by ε, and an optional slot is just one extra ε-edge. Adding or editing a profile does not require redrawing anything by hand.

**Equivalent DFA.** By subset construction with ε-closures (`build_dfa`) and minimization (`build_minimal_dfa`) every ε-NFA becomes a minimal DFA; for the four profiles of this project it has n + 1 = 7 states, D0, …, D6 (one state per slot already satisfied). The tests (`tests/test_automata.py`) check with pyformlang that the three automata (ε-NFA, DFA, minimal DFA) accept the same language for the four profiles, and compare them on random and exhaustively enumerated words. Both versions are shown for each profile below.

**Order inside a slot.** The slot loop accepts the tokens of a slot in any order. Stage 2b always delivers them in the order of `any_of`, so the language is slightly larger than the set of sequences that can actually reach the automaton; this keeps the automaton small and does not change any result.

### 3.4 Full Stack Developer (`FULL_STACK_DEVELOPER`)

**Profile pattern.** A Full Stack Developer must show a client-side language, a frontend framework, a backend technology, a database and version control. REST APIs are listed in the assignment as a possible qualification, but the reference résumé (Wednesday Addams) does not mention them and is expected to be accepted, so the API slot is optional.

| Slot | Category | Tokens (`any_of`) | Repetition |
|---|---|---|---|
| 1 | LANGUAGE | `JAVASCRIPT`, `TYPESCRIPT` | mandatory (`+`) |
| 2 | FRONTEND | `REACT`, `ANGULAR`, `VUE` | mandatory (`+`) |
| 3 | BACKEND | `NODE_JS`, `DJANGO`, `SPRING_BOOT` | mandatory (`+`) |
| 4 | DATABASE | `SQL`, `POSTGRESQL`, `MYSQL`, `MONGODB` | mandatory (`+`) |
| 5 | API | `REST_API` | optional (`*`) |
| 6 | VERSION_CONTROL | `GIT` | mandatory (`+`) |

**Language recognized** (regular expression over Σ, `|` = union, `+` = one or more, `*` = zero or more):

```
(JAVASCRIPT | TYPESCRIPT)+ (REACT | ANGULAR | VUE)+ (NODE_JS | DJANGO | SPRING_BOOT)+
(SQL | POSTGRESQL | MYSQL | MONGODB)+ (REST_API)* (GIT)+
```

**Formal definition (ε-NFA).** M = (Q, Σ, δ, q0, F) where

* Q = {q0, q1, q2, q3, q4, q5, q6, p0, p1, p2, p3, p4, p5} (13 states)
* Σ = {JAVASCRIPT, TYPESCRIPT, REACT, ANGULAR, VUE, NODE_JS, DJANGO, SPRING_BOOT, SQL, POSTGRESQL, MYSQL, MONGODB, REST_API, GIT}
* Initial state: q0
* F = {q6}
* δ : Q × (Σ ∪ {ε}) → P(Q) is given by the table below (every pair not listed maps to ∅):

| From | Reads | To |
|---|---|---|
| q0 | `JAVASCRIPT`, `TYPESCRIPT` | p0 |
| p0 | `JAVASCRIPT`, `TYPESCRIPT` | p0 |
| p0 | `ε` | q1 |
| q1 | `REACT`, `ANGULAR`, `VUE` | p1 |
| p1 | `REACT`, `ANGULAR`, `VUE` | p1 |
| p1 | `ε` | q2 |
| q2 | `NODE_JS`, `DJANGO`, `SPRING_BOOT` | p2 |
| p2 | `NODE_JS`, `DJANGO`, `SPRING_BOOT` | p2 |
| p2 | `ε` | q3 |
| q3 | `SQL`, `POSTGRESQL`, `MYSQL`, `MONGODB` | p3 |
| p3 | `SQL`, `POSTGRESQL`, `MYSQL`, `MONGODB` | p3 |
| p3 | `ε` | q4 |
| q4 | `REST_API` | p4 |
| q4 | `ε` | q5 |
| p4 | `REST_API` | p4 |
| p4 | `ε` | q5 |
| q5 | `GIT` | p5 |
| p5 | `GIT` | p5 |
| p5 | `ε` | q6 |

**Transition diagram.**

![FULL_STACK_DEVELOPER ε-NFA](diagrams/full_stack_developer_enfa.svg)

(Mermaid source: [`diagrams/full_stack_developer_enfa.mmd`](diagrams/full_stack_developer_enfa.mmd); all diagrams are also rendered in [`diagrams/automata.md`](diagrams/automata.md).)

**Equivalent minimal DFA.** Subset construction plus minimization gives 7 states, Q = {D0, D1, D2, D3, D4, D5, D6}, q0 = D0, F = {D6}, δ a partial function Q × Σ → Q (missing pairs go to an implicit dead state):

| From | Reads | To |
|---|---|---|
| D0 | `JAVASCRIPT`, `TYPESCRIPT` | D1 |
| D1 | `JAVASCRIPT`, `TYPESCRIPT` | D1 |
| D1 | `REACT`, `ANGULAR`, `VUE` | D2 |
| D2 | `REACT`, `ANGULAR`, `VUE` | D2 |
| D2 | `NODE_JS`, `DJANGO`, `SPRING_BOOT` | D3 |
| D3 | `NODE_JS`, `DJANGO`, `SPRING_BOOT` | D3 |
| D3 | `SQL`, `POSTGRESQL`, `MYSQL`, `MONGODB` | D4 |
| D4 | `SQL`, `POSTGRESQL`, `MYSQL`, `MONGODB` | D4 |
| D4 | `REST_API` | D5 |
| D4 | `GIT` | D6 |
| D5 | `REST_API` | D5 |
| D5 | `GIT` | D6 |
| D6 | `GIT` | D6 |

![FULL_STACK_DEVELOPER minimal DFA](diagrams/full_stack_developer_dfa.svg)

**Examples.**

| Sorted sequence (Stage 2b output) | Run of the ε-NFA | Result |
|---|---|---|
| JAVASCRIPT REACT NODE_JS POSTGRESQL GIT (Wednesday Addams) | q0 →JAVASCRIPT p0 →ε q1 →REACT p1 →ε q2 →NODE_JS p2 →ε q3 →POSTGRESQL p3 →ε q4 →ε q5 →GIT p5 →ε q6 | ACCEPTED (q6 ∈ F; the API slot is skipped with q4 →ε q5) |
| TYPESCRIPT REACT VUE DJANGO MYSQL REST_API GIT | two tokens of the frontend slot use the loop p1 →VUE p1 | ACCEPTED |
| JAVASCRIPT REACT GIT (résumé with JS, React.js, Docker, Figma, Git) | after q2 the next symbol is GIT, but q2 only reads backend tokens | REJECTED (no backend, no database) |
| REACT JAVASCRIPT … (unsorted) | q0 has no transition on REACT | REJECTED by the automaton alone; in the pipeline Stage 2b always sorts first, so the candidate's writing order never matters |

### 3.5 Machine Learning Engineer (`MACHINE_LEARNING_ENGINEER`)

**Profile pattern.** A Machine Learning Engineer must show Python, at least one data-processing library, at least one machine-learning library, a SQL database and version control. "Machine-learning model development" is a listed qualification, but neither the reference résumé (Mary Jane Watson) nor the example automaton of the assignment requires it as a separate token, so that slot is optional. MongoDB is not part of this profile (the assignment asks for SQL).

| Slot | Category | Tokens (`any_of`) | Repetition |
|---|---|---|---|
| 1 | LANGUAGE | `PYTHON` | mandatory (`+`) |
| 2 | DATA_LIB | `PANDAS`, `NUMPY` | mandatory (`+`) |
| 3 | ML_LIB | `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH` | mandatory (`+`) |
| 4 | ML_PRACTICE | `ML_MODEL_DEVELOPMENT` | optional (`*`) |
| 5 | DATABASE | `SQL`, `POSTGRESQL`, `MYSQL` | mandatory (`+`) |
| 6 | VERSION_CONTROL | `GIT` | mandatory (`+`) |

**Language recognized** (regular expression over Σ, `|` = union, `+` = one or more, `*` = zero or more):

```
(PYTHON)+ (PANDAS | NUMPY)+ (SCIKIT_LEARN | TENSORFLOW | PYTORCH)+ (ML_MODEL_DEVELOPMENT)*
(SQL | POSTGRESQL | MYSQL)+ (GIT)+
```

**Formal definition (ε-NFA).** M = (Q, Σ, δ, q0, F) where

* Q = {q0, q1, q2, q3, q4, q5, q6, p0, p1, p2, p3, p4, p5} (13 states)
* Σ = {PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, PYTORCH, ML_MODEL_DEVELOPMENT, SQL, POSTGRESQL, MYSQL, GIT}
* Initial state: q0
* F = {q6}
* δ : Q × (Σ ∪ {ε}) → P(Q) is given by the table below (every pair not listed maps to ∅):

| From | Reads | To |
|---|---|---|
| q0 | `PYTHON` | p0 |
| p0 | `PYTHON` | p0 |
| p0 | `ε` | q1 |
| q1 | `PANDAS`, `NUMPY` | p1 |
| p1 | `PANDAS`, `NUMPY` | p1 |
| p1 | `ε` | q2 |
| q2 | `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH` | p2 |
| p2 | `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH` | p2 |
| p2 | `ε` | q3 |
| q3 | `ML_MODEL_DEVELOPMENT` | p3 |
| q3 | `ε` | q4 |
| p3 | `ML_MODEL_DEVELOPMENT` | p3 |
| p3 | `ε` | q4 |
| q4 | `SQL`, `POSTGRESQL`, `MYSQL` | p4 |
| p4 | `SQL`, `POSTGRESQL`, `MYSQL` | p4 |
| p4 | `ε` | q5 |
| q5 | `GIT` | p5 |
| p5 | `GIT` | p5 |
| p5 | `ε` | q6 |

**Transition diagram.**

![MACHINE_LEARNING_ENGINEER ε-NFA](diagrams/machine_learning_engineer_enfa.svg)

(Mermaid source: [`diagrams/machine_learning_engineer_enfa.mmd`](diagrams/machine_learning_engineer_enfa.mmd); all diagrams are also rendered in [`diagrams/automata.md`](diagrams/automata.md).)

**Equivalent minimal DFA.** Subset construction plus minimization gives 7 states, Q = {D0, D1, D2, D3, D4, D5, D6}, q0 = D0, F = {D6}, δ a partial function Q × Σ → Q (missing pairs go to an implicit dead state):

| From | Reads | To |
|---|---|---|
| D0 | `PYTHON` | D1 |
| D1 | `PYTHON` | D1 |
| D1 | `PANDAS`, `NUMPY` | D2 |
| D2 | `PANDAS`, `NUMPY` | D2 |
| D2 | `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH` | D3 |
| D3 | `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH` | D3 |
| D3 | `ML_MODEL_DEVELOPMENT` | D4 |
| D3 | `SQL`, `POSTGRESQL`, `MYSQL` | D5 |
| D4 | `ML_MODEL_DEVELOPMENT` | D4 |
| D4 | `SQL`, `POSTGRESQL`, `MYSQL` | D5 |
| D5 | `SQL`, `POSTGRESQL`, `MYSQL` | D5 |
| D5 | `GIT` | D6 |
| D6 | `GIT` | D6 |

![MACHINE_LEARNING_ENGINEER minimal DFA](diagrams/machine_learning_engineer_dfa.svg)

**Examples.**

| Sorted sequence (Stage 2b output) | Run of the ε-NFA | Result |
|---|---|---|
| PYTHON PANDAS NUMPY SCIKIT_LEARN TENSORFLOW SQL GIT (Mary Jane Watson) | q0 →PYTHON p0 →ε q1 →PANDAS p1 →NUMPY p1 →ε q2 →SCIKIT_LEARN p2 →TENSORFLOW p2 →ε q3 →ε q4 →SQL p4 →ε q5 →GIT p5 →ε q6 | ACCEPTED (two data libraries and two ML libraries are read by the slot loops) |
| PYTHON PANDAS TENSORFLOW POSTGRESQL GIT (assignment, Stage 3 example) | same path with one token per slot | ACCEPTED |
| PYTHON PANDAS SQL GIT | in q2 the next symbol is SQL, but q2 only reads ML libraries | REJECTED (no ML library) |

### 3.6 DevOps Engineer (`DEVOPS_ENGINEER`, team-defined, software engineering)

**Profile pattern.** A DevOps Engineer builds, ships and operates software, so the pattern follows the delivery chain: an operating system to work on (Linux), version control, a CI/CD practice, containers and a cloud provider. Container orchestration (Kubernetes) is common but not universal in junior profiles, so it is optional. The profile reuses `GIT` from the reference profiles and adds five tokens to the vocabulary (`LINUX`, `CI_CD`, `DOCKER`, `KUBERNETES`, `AWS`). This profile is provisional until the professor publishes the requirements of the team-defined profiles; changing it only means editing `profiles/devops_engineer.json`.

| Slot | Category | Tokens (`any_of`) | Repetition |
|---|---|---|---|
| 1 | OPERATING_SYSTEM | `LINUX` | mandatory (`+`) |
| 2 | VERSION_CONTROL | `GIT` | mandatory (`+`) |
| 3 | CI_CD | `CI_CD` | mandatory (`+`) |
| 4 | CONTAINER | `DOCKER` | mandatory (`+`) |
| 5 | ORCHESTRATION | `KUBERNETES` | optional (`*`) |
| 6 | CLOUD | `AWS` | mandatory (`+`) |

**Language recognized** (regular expression over Σ, `|` = union, `+` = one or more, `*` = zero or more):

```
(LINUX)+ (GIT)+ (CI_CD)+ (DOCKER)+ (KUBERNETES)* (AWS)+
```

**Formal definition (ε-NFA).** M = (Q, Σ, δ, q0, F) where

* Q = {q0, q1, q2, q3, q4, q5, q6, p0, p1, p2, p3, p4, p5} (13 states)
* Σ = {LINUX, GIT, CI_CD, DOCKER, KUBERNETES, AWS}
* Initial state: q0
* F = {q6}
* δ : Q × (Σ ∪ {ε}) → P(Q) is given by the table below (every pair not listed maps to ∅):

| From | Reads | To |
|---|---|---|
| q0 | `LINUX` | p0 |
| p0 | `LINUX` | p0 |
| p0 | `ε` | q1 |
| q1 | `GIT` | p1 |
| p1 | `GIT` | p1 |
| p1 | `ε` | q2 |
| q2 | `CI_CD` | p2 |
| p2 | `CI_CD` | p2 |
| p2 | `ε` | q3 |
| q3 | `DOCKER` | p3 |
| p3 | `DOCKER` | p3 |
| p3 | `ε` | q4 |
| q4 | `KUBERNETES` | p4 |
| q4 | `ε` | q5 |
| p4 | `KUBERNETES` | p4 |
| p4 | `ε` | q5 |
| q5 | `AWS` | p5 |
| p5 | `AWS` | p5 |
| p5 | `ε` | q6 |

**Transition diagram.**

![DEVOPS_ENGINEER ε-NFA](diagrams/devops_engineer_enfa.svg)

(Mermaid source: [`diagrams/devops_engineer_enfa.mmd`](diagrams/devops_engineer_enfa.mmd); all diagrams are also rendered in [`diagrams/automata.md`](diagrams/automata.md).)

**Equivalent minimal DFA.** Subset construction plus minimization gives 7 states, Q = {D0, D1, D2, D3, D4, D5, D6}, q0 = D0, F = {D6}, δ a partial function Q × Σ → Q (missing pairs go to an implicit dead state):

| From | Reads | To |
|---|---|---|
| D0 | `LINUX` | D1 |
| D1 | `LINUX` | D1 |
| D1 | `GIT` | D2 |
| D2 | `GIT` | D2 |
| D2 | `CI_CD` | D3 |
| D3 | `CI_CD` | D3 |
| D3 | `DOCKER` | D4 |
| D4 | `DOCKER` | D4 |
| D4 | `KUBERNETES` | D5 |
| D4 | `AWS` | D6 |
| D5 | `KUBERNETES` | D5 |
| D5 | `AWS` | D6 |
| D6 | `AWS` | D6 |

![DEVOPS_ENGINEER minimal DFA](diagrams/devops_engineer_dfa.svg)

**Examples.**

| Sorted sequence (Stage 2b output) | Run of the ε-NFA | Result |
|---|---|---|
| LINUX GIT CI_CD DOCKER AWS | q0 →LINUX p0 →ε q1 →GIT p1 →ε q2 →CI_CD p2 →ε q3 →DOCKER p3 →ε q4 →ε q5 →AWS p5 →ε q6 | ACCEPTED (Kubernetes skipped) |
| LINUX GIT CI_CD DOCKER KUBERNETES AWS | the orchestration slot is used: q4 →KUBERNETES p4 →ε q5 | ACCEPTED |
| LINUX GIT DOCKER AWS | in q2 the next symbol is DOCKER, but q2 only reads `CI_CD` | REJECTED (no CI/CD) |
| GIT (the Mary Jane Watson résumé, filtered for this profile) | q0 has no transition on GIT | REJECTED |

### 3.7 Data Engineer (`DATA_ENGINEER`, team-defined, AI/data)

**Profile pattern.** A Data Engineer builds the pipelines that feed analytics and machine learning. The pattern asks for Python, a SQL database, a distributed processing engine (Spark) and version control. Workflow orchestration (Airflow) and streaming (Kafka) are frequent but depend on the company, so both slots are optional; this is the only profile with two consecutive optional slots, which the ε-NFA handles with two chained ε-edges (q3 →ε q4 →ε q5). New tokens: `SPARK`, `AIRFLOW`, `KAFKA`. Provisional, like the DevOps profile.

| Slot | Category | Tokens (`any_of`) | Repetition |
|---|---|---|---|
| 1 | LANGUAGE | `PYTHON` | mandatory (`+`) |
| 2 | DATABASE | `SQL`, `POSTGRESQL`, `MYSQL` | mandatory (`+`) |
| 3 | PROCESSING | `SPARK` | mandatory (`+`) |
| 4 | WORKFLOW | `AIRFLOW` | optional (`*`) |
| 5 | STREAMING | `KAFKA` | optional (`*`) |
| 6 | VERSION_CONTROL | `GIT` | mandatory (`+`) |

**Language recognized** (regular expression over Σ, `|` = union, `+` = one or more, `*` = zero or more):

```
(PYTHON)+ (SQL | POSTGRESQL | MYSQL)+ (SPARK)+ (AIRFLOW)* (KAFKA)* (GIT)+
```

**Formal definition (ε-NFA).** M = (Q, Σ, δ, q0, F) where

* Q = {q0, q1, q2, q3, q4, q5, q6, p0, p1, p2, p3, p4, p5} (13 states)
* Σ = {PYTHON, SQL, POSTGRESQL, MYSQL, SPARK, AIRFLOW, KAFKA, GIT}
* Initial state: q0
* F = {q6}
* δ : Q × (Σ ∪ {ε}) → P(Q) is given by the table below (every pair not listed maps to ∅):

| From | Reads | To |
|---|---|---|
| q0 | `PYTHON` | p0 |
| p0 | `PYTHON` | p0 |
| p0 | `ε` | q1 |
| q1 | `SQL`, `POSTGRESQL`, `MYSQL` | p1 |
| p1 | `SQL`, `POSTGRESQL`, `MYSQL` | p1 |
| p1 | `ε` | q2 |
| q2 | `SPARK` | p2 |
| p2 | `SPARK` | p2 |
| p2 | `ε` | q3 |
| q3 | `AIRFLOW` | p3 |
| q3 | `ε` | q4 |
| p3 | `AIRFLOW` | p3 |
| p3 | `ε` | q4 |
| q4 | `KAFKA` | p4 |
| q4 | `ε` | q5 |
| p4 | `KAFKA` | p4 |
| p4 | `ε` | q5 |
| q5 | `GIT` | p5 |
| p5 | `GIT` | p5 |
| p5 | `ε` | q6 |

**Transition diagram.**

![DATA_ENGINEER ε-NFA](diagrams/data_engineer_enfa.svg)

(Mermaid source: [`diagrams/data_engineer_enfa.mmd`](diagrams/data_engineer_enfa.mmd); all diagrams are also rendered in [`diagrams/automata.md`](diagrams/automata.md).)

**Equivalent minimal DFA.** Subset construction plus minimization gives 7 states, Q = {D0, D1, D2, D3, D4, D5, D6}, q0 = D0, F = {D6}, δ a partial function Q × Σ → Q (missing pairs go to an implicit dead state):

| From | Reads | To |
|---|---|---|
| D0 | `PYTHON` | D1 |
| D1 | `PYTHON` | D1 |
| D1 | `SQL`, `POSTGRESQL`, `MYSQL` | D2 |
| D2 | `SQL`, `POSTGRESQL`, `MYSQL` | D2 |
| D2 | `SPARK` | D3 |
| D3 | `SPARK` | D3 |
| D3 | `AIRFLOW` | D4 |
| D3 | `KAFKA` | D5 |
| D3 | `GIT` | D6 |
| D4 | `AIRFLOW` | D4 |
| D4 | `KAFKA` | D5 |
| D4 | `GIT` | D6 |
| D5 | `KAFKA` | D5 |
| D5 | `GIT` | D6 |
| D6 | `GIT` | D6 |

![DATA_ENGINEER minimal DFA](diagrams/data_engineer_dfa.svg)

**Examples.**

| Sorted sequence (Stage 2b output) | Run of the ε-NFA | Result |
|---|---|---|
| PYTHON SQL SPARK GIT | q0 →PYTHON p0 →ε q1 →SQL p1 →ε q2 →SPARK p2 →ε q3 →ε q4 →ε q5 →GIT p5 →ε q6 | ACCEPTED (both optional slots skipped) |
| PYTHON POSTGRESQL SPARK AIRFLOW KAFKA GIT | every slot used once | ACCEPTED |
| PYTHON SQL GIT (the Mary Jane Watson résumé, filtered for this profile) | in q2 the next symbol is GIT, but q2 only reads `SPARK` | REJECTED (no processing engine) |

### 3.8 Summary, design decisions and limitations

**The four automata at a glance** (counts generated from the code):

| Profile | Slots | Optional slots | \|Σ\| | ε-NFA states | ε-NFA transitions | Minimal DFA states | Minimal DFA transitions |
|---|---|---|---|---|---|---|---|
| Full Stack Developer | 6 | 1 | 14 | 13 | 35 (7 ε) | 7 | 29 |
| Machine Learning Engineer | 6 | 1 | 11 | 13 | 29 (7 ε) | 7 | 25 |
| DevOps Engineer | 6 | 1 | 6 | 13 | 19 (7 ε) | 7 | 13 |
| Data Engineer | 6 | 2 | 8 | 13 | 24 (8 ε) | 7 | 19 |

**Design decisions.**

| Decision | Alternative considered | Why we chose it |
|---|---|---|
| One symbol per canonical token (Σ = tokens of the profile) | Automata over characters | The transducers of Stage 2 already turn character strings into tokens; reading characters again would mix two stages and blow up the number of states. |
| Filter and sort the tokens before the automaton (Stage 2b) | Self-loops on every foreign token in every state | With filtering, Σ stays small and each automaton describes only its profile. A résumé that also lists Docker or Figma is not rejected for that, and the result does not depend on the order in which the candidate wrote the skills. |
| One or more tokens per slot | Exactly one token per slot (the example diagram of the assignment) | The reference résumé of Mary Jane Watson lists Pandas *and* NumPy, Scikit-learn *and* TensorFlow; a one-token-per-slot automaton would reject the assignment's own example. |
| Optional slots (`REST_API`, `ML_MODEL_DEVELOPMENT`, `KUBERNETES`, `AIRFLOW`, `KAFKA`) | Make every listed qualification mandatory | The reference résumés are expected to be accepted without REST or an explicit "ML model development" token. An ε-edge expresses "may be absent" without duplicating states. |
| ε-NFA as the formal model, minimal DFA as its proof of determinism | Write the DFA by hand | The ε-NFA is a mechanical translation of the profile file, so the four automata come from one function. The DFA is derived automatically and checked to be equivalent by the tests. |
| Profiles as JSON data | One Python class per profile | The assignment requires one general solution for all profiles. Replacing the two provisional profiles needs no code change. |

**Limitations.**

* **Presence, not proficiency.** The automata only check that a qualification is *written* in the résumé. They do not measure level, years per technology or the quality of the experience.
* **Closed vocabulary.** A technology that is not in `vocabulary.json` (for example "Svelte" or "GCP") never reaches the automata, so a valid candidate can be rejected until the vocabulary and the profile are extended.
* **Slots are a conjunction of disjunctions.** Every profile is "at least one of these AND at least one of those". Rules such as "Kubernetes only counts if Docker is present", or "two of these three", need a different construction (product automata or counters).
* **The language is slightly larger than the reachable inputs.** Inside a slot, the loop accepts tokens in any order, while Stage 2b always sends them in `any_of` order. This never changes a result, but the automaton alone would accept sequences that the pipeline cannot produce.
* **Provisional team profiles.** DevOps Engineer and Data Engineer were defined by the team while the professor's requirements were pending; they may change.

---

## 4. Context-Free Grammar (EBNF) — Stage 4 (Edwar)

### 4.1 Purpose and Formal Definition

Stage 4 represents the structured profile of a candidate using a Domain-Specific Language (DSL). The language is formally defined as a Context-Free Grammar (CFG) denoted by the 4-tuple:

$$G = (V, \Sigma, R, S)$$

Where:
- **$V$** is the finite set of non-terminal symbols (variables).
- **$\Sigma$** is the finite set of terminal symbols (alphabet).
- **$R$** is the finite set of production rules ($V \to (V \cup \Sigma)^*$).
- **$S \in V$** is the start symbol ($S = \text{CandidateModel}$).

### 4.2 Non-Terminal Symbols ($V$)

$$V = \{ \text{CandidateModel}, \text{ContactBlock}, \text{EducationBlock}, \text{ExperienceBlock}, \text{SkillsBlock}, \text{ClassificationBlock}, \text{ProfileClassification} \}$$

| Non-Terminal | Semantic Role |
|---|---|
| `CandidateModel` | Root symbol representing the entire candidate profile document. |
| `ContactBlock` | Block enclosing optional communication channels (email, phone, link). |
| `EducationBlock` | Single academic qualification record (degree, institution, graduation year). |
| `ExperienceBlock` | Single professional experience record (duration in years, description). |
| `SkillsBlock` | Block enclosing the sequence of normalized canonical skill tokens. |
| `ClassificationBlock` | Block mapping each configured profile to its binary verdict. |
| `ProfileClassification` | Association between a profile identifier and its qualification verdict. |

### 4.3 Terminal Symbols ($\Sigma$)

The terminal alphabet consists of reserved keywords, structural delimiters, and lexical token categories:

1. **Keywords and structural delimiters:**
   $$\Sigma_{\text{lit}} = \{ \texttt{candidate}, \texttt{contact}, \texttt{education}, \texttt{experience}, \texttt{skills}, \texttt{classification}, \texttt{email}, \texttt{phone}, \texttt{link}, \texttt{degree}, \texttt{institution}, \texttt{year}, \texttt{years}, \texttt{description}, \texttt{\{}, \texttt{\}}, \texttt{:} \}$$

2. **Lexical tokens:**
   - **`STRING`**: A double-quoted literal string matching `"[^"\\]*(?:\\.[^"\\]*)*"`. Used for candidate names, contact values, academic degrees, institutions, years, and job descriptions.
   - **`NUMBER`**: A non-negative numeric literal matching `[0-9]+(?:\.[0-9]+)?`. Used for years of experience.
   - **`SkillToken`**: An uppercase token matching regular expression `[A-Z][A-Z_]*`. Represents a canonical token from output alphabet $\Gamma$ of Stage 2.
   - **`ProfileId`**: An identifier matching regular expression `[A-Z][A-Z_]*`. Represents a configured professional profile.
   - **`Verdict`**: Binary evaluation result, matching exactly $\texttt{ACCEPTED} \mid \texttt{REJECTED}$.

$$\Sigma = \Sigma_{\text{lit}} \cup \{ \texttt{STRING}, \texttt{NUMBER}, \texttt{SkillToken}, \texttt{ProfileId}, \texttt{Verdict} \}$$

### 4.4 Production Rules ($R$) in ISO/IEC 14977 EBNF

In the standard notation, `,` denotes concatenation, `|` denotes alternation, `[ ... ]` denotes optionality (0 or 1), and `{ ... }` denotes repetition (0 or more times):

```ebnf
CandidateModel = "candidate" , STRING , "{" ,
                 [ ContactBlock ] ,
                 { EducationBlock } ,
                 { ExperienceBlock } ,
                 [ SkillsBlock ] ,
                 ClassificationBlock ,
                 "}" ;

ContactBlock   = "contact" , "{" ,
                 { ( "email" , STRING )
                 | ( "phone" , STRING )
                 | ( "link"  , STRING ) } ,
                 "}" ;

EducationBlock = "education" , "{" ,
                 [ "degree" , STRING ] ,
                 [ "institution" , STRING ] ,
                 [ "year" , STRING ] ,
                 "}" ;

ExperienceBlock = "experience" , "{" ,
                  [ "years" , NUMBER ] ,
                  [ "description" , STRING ] ,
                  "}" ;

SkillsBlock    = "skills" , "{" ,
                 { SkillToken } ,
                 "}" ;

ClassificationBlock = "classification" , "{" ,
                      ProfileClassification ,
                      { ProfileClassification } ,
                      "}" ;

ProfileClassification = ProfileId , ":" , Verdict ;

Verdict        = "ACCEPTED" | "REJECTED" ;
```

### 4.5 Mapping to the textX Metamodel (`candidate.tx`)

The formal EBNF productions map directly to the textX grammar implementation in `src/resumelens/candidate.tx`:

| EBNF Production | textX Syntax in `candidate.tx` | Python Object Attribute |
|---|---|---|
| `CandidateModel` | `'candidate' name=STRING '{' ... '}'` | `model.name`, `model.contact`, etc. |
| `ContactBlock` | `('email' emails+=STRING \| 'phone' phones+=STRING \| 'link' links+=STRING)*` | `model.contact.emails`, `phones`, `links` (`list[str]`) |
| `EducationBlock` | `education*=EducationBlock` | `model.education` (`list[EducationBlock]`) |
| `ExperienceBlock` | `experience*=ExperienceBlock` | `model.experience` (`list[ExperienceBlock]`) |
| `SkillsBlock` | `skills*=SkillToken` | `model.skills.skills` (`list[str]`) |
| `ClassificationBlock` | `entries+=ProfileClassification` | `model.classification.entries` (`list`) |
| `ProfileClassification` | `profile_id=ProfileId ':' verdict=Verdict` | `entry.profile_id`, `entry.verdict` |

### 4.6 Theoretical Justification

1. **Need for a Context-Free Language (Chomsky Type-2):**
   A candidate profile contains hierarchical recursive structures: balanced block delimiters (`{ ... }`), arbitrarily repeated entries (multiple educations, multiple jobs), and optional nested elements. The language of balanced nested delimiters and structured nested records cannot be modeled by regular languages (Chomsky Type-3) due to the pumping lemma for regular languages. A CFG provides the exact expressiveness required while remaining efficient to parse.

2. **Unambiguity and Determinism:**
   Each block begins with an unambiguous keyword (`candidate`, `contact`, `education`, `experience`, `skills`, `classification`). No two non-terminals share initial terminal prefixes, eliminating shift-reduce or reduce-reduce ambiguities. The grammar is $LL(1)$ and Parsing Expression Grammar (PEG) compatible, enabling linear-time deterministic parsing without backtracking.

3. **Separation of Syntax and Semantics:**
   The grammar enforces lexical correctness (valid token casing, quote escaping, valid verdict literals) and syntactic structure (required blocks and balanced braces). Semantic constraints—such as ensuring that tokens in `skills` belong to `vocabulary.json` and profiles in `classification` match the active profile registry—are decoupled from parser execution and validated in the application layer.
