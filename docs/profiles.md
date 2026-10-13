# Professional Profiles

*Owner: Diego (Juan Diego Balanta Molina). Configuration: `profiles/*.json`. Loader: `src/resumelens/profiles.py`. Formal automata: `docs/formalization.md`, Section 3.*

ResumeLens evaluates every résumé against four professional profiles. Two are fixed by the assignment (Full Stack Developer and Machine Learning Engineer) and two were defined by the team: one in software engineering (DevOps Engineer) and one in AI/data (Data Engineer). All four go through the same code; a profile is only a JSON file.

## 1. How a profile is described

A profile is an **ordered list of slots**. Each slot groups interchangeable qualifications (canonical tokens of `src/resumelens/vocabulary.json`) and says whether the slot is mandatory.

```json
{
  "id": "FULL_STACK_DEVELOPER",
  "display_name": "Full Stack Developer",
  "order": 1,
  "slots": [
    {"category": "LANGUAGE", "any_of": ["JAVASCRIPT", "TYPESCRIPT"], "optional": false},
    {"category": "API",      "any_of": ["REST_API"],                 "optional": true}
  ]
}
```

| Key | Meaning |
|---|---|
| `id` | Unique `UPPER_SNAKE_CASE` name; it is the profile name used in the DSL and the results. |
| `display_name` | Human-readable name for the visualization. |
| `order` | Position of the profile in the results (Full Stack 1, ML 2, DevOps 3, Data 4). |
| `slots` | Ordered pattern positions. The order is the canonical order used by Stage 2b and the structure of the automaton. |
| `any_of` | Tokens that satisfy the slot. One or more of them may appear. |
| `optional` | `true` if the slot may be missing. |

**Pattern rule.** A résumé satisfies a profile when, after removing the tokens that do not belong to the profile and sorting the rest by slot, every mandatory slot has at least one token and the slots appear in order. As a regular expression over tokens, each mandatory slot is `(t1 | t2 | …)+` and each optional slot is `(…)*`.

**Validation.** `load_profiles()` rejects a profile file (`ProfileConfigError`) when the id is missing or duplicated, there are no slots, a token is not in the vocabulary, two slots share a token, or every slot is optional. Shared tokens are forbidden because one token would then satisfy two slots and the automaton would be ambiguous.

## 2. Full Stack Developer (reference profile)

**Who it describes.** A developer who builds both the user interface and the server side of web applications: client language, frontend framework, backend technology, database, version control.

| # | Slot | Accepted qualifications | Required |
|---|---|---|---|
| 1 | Language | JavaScript, TypeScript | yes |
| 2 | Frontend | React, Angular, Vue | yes |
| 3 | Backend | Node.js, Django, Spring Boot | yes |
| 4 | Database | SQL, PostgreSQL, MySQL, MongoDB | yes |
| 5 | API | REST APIs | no |
| 6 | Version control | Git | yes |

**Why REST is optional.** The assignment lists REST APIs as a possible qualification, but its own example résumé (Wednesday Addams: JS, React.js, NodeJS, Postgres, Git) has no REST and is meant to be a Full Stack candidate. Making the slot mandatory would reject the reference example.

**Canonical order** (assignment, Stage 2): Language → Frontend → Backend → Database → API → Version control. Example: `Git, NodeJS, JS, Postgres, React.js` → `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT`.

## 3. Machine Learning Engineer (reference profile)

**Who it describes.** An engineer who builds software that trains and serves predictive models: Python, data libraries, machine-learning frameworks, a SQL database and version control.

| # | Slot | Accepted qualifications | Required |
|---|---|---|---|
| 1 | Language | Python | yes |
| 2 | Data libraries | Pandas, NumPy | yes |
| 3 | ML libraries | Scikit-learn, TensorFlow, PyTorch | yes |
| 4 | ML practice | Machine-learning model development | no |
| 5 | Database | SQL, PostgreSQL, MySQL | yes |
| 6 | Version control | Git | yes |

**Why "model development" is optional.** It appears in the assignment's list, but neither the reference résumé (Mary Jane Watson) nor the example automaton of the assignment contains it as a separate token. It still counts when a résumé mentions it (e.g. "machine learning", "predictive models").

**Several tokens per slot.** Mary Jane Watson lists Pandas *and* NumPy, Scikit-learn *and* TensorFlow. Each slot accepts one or more of its tokens, so the résumé is accepted.

## 4. DevOps Engineer (team-defined, software engineering)

**Who it describes.** An engineer who automates how software is built, tested, shipped and run. The slots follow that delivery chain: the operating system the tooling runs on, version control, continuous integration/delivery, containers, orchestration and a cloud platform.

| # | Slot | Accepted qualifications | Required |
|---|---|---|---|
| 1 | Operating system | Linux (also Ubuntu, GNU/Linux) | yes |
| 2 | Version control | Git | yes |
| 3 | CI/CD | CI/CD | yes |
| 4 | Containers | Docker | yes |
| 5 | Orchestration | Kubernetes (K8s) | no |
| 6 | Cloud | AWS | yes |

**Why Kubernetes is optional.** Many junior DevOps roles work with Docker and a managed cloud service without operating a Kubernetes cluster themselves; requiring it would reject reasonable candidates.

**Reuse.** The profile shares `GIT` with the reference profiles and adds five tokens to the vocabulary: `LINUX`, `CI_CD`, `DOCKER`, `KUBERNETES`, `AWS`.

## 5. Data Engineer (team-defined, AI/data)

**Who it describes.** An engineer who builds and maintains the data pipelines that feed analytics and machine learning: Python, SQL, a distributed processing engine and version control, often with workflow orchestration and streaming.

| # | Slot | Accepted qualifications | Required |
|---|---|---|---|
| 1 | Language | Python | yes |
| 2 | Database | SQL, PostgreSQL, MySQL | yes |
| 3 | Processing | Spark (also Apache Spark, PySpark) | yes |
| 4 | Workflow | Airflow | no |
| 5 | Streaming | Kafka | no |
| 6 | Version control | Git | yes |

**Why two optional slots.** Airflow and Kafka are common in data teams but depend on the company's stack (batch-only teams do not use streaming). It is also the only profile with two optional slots in a row, which tests that the automaton can skip consecutive slots.

**Difference with ML Engineer.** Both use Python and SQL. The Data Engineer needs a processing engine (Spark) instead of data/ML libraries, so the two profiles accept different résumés and one résumé can be accepted by both.

> The two team-defined profiles are final (contract decision D11). They were chosen because they are common roles next to the two reference profiles, reuse most of the vocabulary and exercise optional slots, including two consecutive ones in Data Engineer. Replacing them would only mean editing `profiles/devops_engineer.json` and `profiles/data_engineer.json` (and, if new technologies appear, `vocabulary.json`); no Python code changes.

## 6. Results on the sample résumés

Output of the complete pipeline (`pipeline.run`) on the files in `samples/`:

| Résumé | Skills written | Accepted profiles |
|---|---|---|
| `wednesday_addams.txt` | JS, React.js, NodeJS, Postgres, Git | Full Stack Developer |
| `mary_jane_watson.txt` | Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git | Machine Learning Engineer |
| `linus_torvalds.txt` | Linux, Git, CI/CD, Docker, Kubernetes, AWS | DevOps Engineer |
| `grace_hopper.txt` | Python, SQL, Spark, Airflow, Kafka, Git | Data Engineer |
| `rejected_candidate.txt` | Figma, Photoshop, Microsoft Word, Jira, Git | none (only `GIT` is recognized; Figma, Photoshop, Microsoft Word and Jira are not in the vocabulary) |

The result is binary for each profile and is not a ranking: a résumé can match zero, one or several profiles.
