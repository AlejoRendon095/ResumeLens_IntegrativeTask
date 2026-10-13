# Research Poster: ResumeLens

**Title:** ResumeLens: Formal Language-Based Resume Screening  
**Authors:** Alejandro Rendón Garzón, Juan Diego Balanta Molina, Edwar Estacio  
**Affiliation:** Departamento de TIC, Universidad Icesi · Computación y Estructuras Discretas III (2026-2)  
**Language:** English (Academic Deliverable)

---

## Poster Content Layout (A0 Vertical Format)

```
┌────────────────────────────────────────────────────────────────────────┐
│                                HEADER                                  │
│         ResumeLens: Formal Language-Based Resume Screening             │
│        Alejandro Rendón · Juan Diego Balanta · Edwar Estacio           │
│                         Universidad Icesi                              │
├──────────────────────────────────┬─────────────────────────────────────┤
│ 1. MOTIVATION & PROBLEM          │ 3. PIPELINE ARCHITECTURE            │
│  - Black-box ML screening risks  │  - Sequential 4-stage pipeline      │
│  - Algorithmic bias & hallucination  - Data contracts & models       │
│  - Deterministic qualification   │  - System flowchart                 │
│    pattern recognition           │                                     │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 2. COMPUTATIONAL MODELS          │ 4. FORMAL MODELS IN ACTION          │
│  - Stage 1: Regular Expressions  │  - Regex Entity Isolation           │
│  - Stage 2: Transducers (FST)    │  - FST Canonical Mapping            │
│  - Stage 3: Automata (FSA / DFA) │  - FSA Slot Pattern Recognition     │
│  - Stage 4: CFG & textX DSL      │  - CFG Structural AST & Visualizer  │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 5. EXPERIMENTAL RESULTS          │ 6. DISCUSSION & FUTURE WORK         │
│  - 4 Professional Profiles       │  - Deterministic explainability     │
│  - 249 Automated tests (100%)    │  - Scalability & vocabulary bounds  │
│  - Invariance under permutation  │  - Attribute grammars extension     │
└──────────────────────────────────┴─────────────────────────────────────┘
```

---

### Section 1: Motivation & Problem Statement

- **The Challenge:** Modern applicant tracking systems (ATS) increasingly rely on opaque deep learning models and LLMs to rank job applicants. These systems suffer from non-deterministic outputs, prompt injection vulnerability, and the reinforcement of historical demographic biases.
- **Our Approach:** **ResumeLens** rejects subjective merit ranking and automated hiring. Instead, it solves a strictly bounded formal decision problem: determining whether explicitly stated candidate qualifications satisfy mathematically defined qualification patterns.
- **Core Principle:** A candidate either satisfies a formal pattern or does not ($w \in L(M)$). The evaluation is 100% deterministic, auditable, and mathematically explainable.

---

### Section 2: Four-Stage Integrated Formal Framework

| Pipeline Stage | Formal Computational Model | Formalism & Alphabet | Implementation | Responsibility |
|---|---|---|---|---|
| **1. Extraction** | Regular Expressions | $\Sigma_{\text{text}} \to \text{Surface Strings}$ | Python `re` | Alejandro Rendón |
| **2. Normalization** | Finite-State Transducers (FST) | $M = (Q, \Sigma, \Gamma, \delta, \omega, q_0, F)$ | `pyformlang` | Alejandro Rendón |
| **3. Recognition** | Finite-State Automata (FSA / $\varepsilon$-NFA / DFA) | $M = (Q, \Sigma, \delta, q_0, F)$ over $\Sigma = \Gamma$ | `pyformlang` | Juan Diego Balanta |
| **4. Representation** | Context-Free Grammar (CFG in EBNF) | $G = (V, \Sigma, R, S)$ | `textX` | Edwar Estacio |
| **4b. Visualization** | Model-Driven Transformation | AST $\to$ Semantic HTML & Markdown | Python | Edwar Estacio |

---

### Section 3: Architecture & Data Transformation

```
Raw Plain-Text Résumé
        │
        ▼ (Stage 1: Regular Expressions)
Candidate Metadata & Raw Skill Strings
        │
        ▼ (Stage 2: Finite-State Transducers)
Normalized Canonical Tokens Γ (30 discrete tokens)
        │
        ▼ (Stage 2b: Profile Slot Ordering & Filtering)
Canonical Token Sequences (per profile)
        │
        ▼ (Stage 3: Finite Automata Evaluation)
Binary Qualification Verdicts (ACCEPTED / REJECTED)
        │
        ▼ (Stage 4: Context-Free Grammar & textX AST)
Domain-Specific Language (DSL) Specification (.dsl)
        │
        ▼ (Stage 4b: Model-Driven Rendering)
Self-Contained HTML Report (.html) & Structured Markdown (.md)
```

---

### Section 4: Mathematical Modeling Highlights

1. **Finite-State Transducers ($7$-Tuple):**
   - Maps noisy aliases (`"js"`, `"react.js"`, `"postgres"`, `"sklearn"`) to canonical tokens (`JAVASCRIPT`, `REACT`, `POSTGRESQL`, `SCIKIT_LEARN`).
   - Whole-string matching guarantees prefix independence: `"java"` never matches as a prefix of `"javascript"`.
   - Characters outside $\Sigma$ deterministically yield no transition, routing unmapped tools directly to `unrecognized` for full auditability.

2. **Qualification Pattern Automata ($5$-Tuple):**
   - Each profile $P$ defines an ordered sequence of category slots $S_1, S_2, \dots, S_n$.
   - Expressed over canonical alphabet $\Sigma$:
     $$L(P) = S_1^{k_1} S_2^{k_2} \cdots S_n^{k_n}, \quad k_i \in \{+, *\}$$
   - Constructed as $\varepsilon$-NFAs and determinized into minimal DFAs via subset construction.

3. **Context-Free Candidate Profile DSL:**
   - Formal $4$-tuple $G = (V, \Sigma, R, S)$ specified in ISO/IEC 14977 EBNF.
   - Balanced hierarchical block delimiters (`{ ... }`) and repeated variable-cardinality records (education, experience, skills, classifications) require Chomsky Type-2 power.
   - $LL(1)$ and PEG compatibility ensures deterministic, linear-time AST generation.

---

### Section 5: Experimental Verification & Results

- **Evaluation Profiles:**
  1. *Full Stack Developer:* Languages $\to$ Frontend $\to$ Backend $\to$ Database $\to$ API (opt) $\to$ Version Control.
  2. *Machine Learning Engineer:* Python $\to$ Data Libs $\to$ ML Libs $\to$ ML Practice (opt) $\to$ Database $\to$ Version Control.
  3. *DevOps Engineer:* Linux $\to$ Git $\to$ CI/CD $\to$ Docker $\to$ Kubernetes (opt) $\to$ Cloud (AWS).
  4. *Data Engineer:* Python $\to$ Database $\to$ Spark $\to$ Airflow (opt) $\to$ Kafka (opt) $\to$ Git.
- **Empirical Results:**
  - **249 / 249 Automated Tests Passing (100% test suite success).**
  - **Permutation Invariance Verified:** Reordering skill declarations within résumés yields identical classification verdicts across all profiles.
  - **Robustness against Noise:** Unrecognized skills (e.g., Figma, Photoshop, Jira) do not corrupt or alter valid profile evaluations.
  - **Zero Security Vulnerabilities:** 100% of candidate inputs sanitized through entity escaping (`html.escape`), preventing layout disruption or cross-site scripting (XSS).

---

### Section 6: Key Findings & Future Directions

- **Strengths:** Eliminates subjectivity and algorithmic discrimination. Provides instant, human-interpretable explanations showing exactly which automaton state failed or which slot was missing.
- **Limitations:** Bounded to the discrete canonical vocabulary ($\Gamma = 30$ tokens); novel technology synonyms require vocabulary registration.
- **Future Work:** Extension to attribute grammars for context-sensitive constraints (e.g., verifying minimum years of experience conditional on specific technology stacks).
