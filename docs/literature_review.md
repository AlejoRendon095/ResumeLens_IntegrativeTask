# Literature Review: Formal Language-Based Resume Screening

Integrative Task 1 · Computación y Estructuras Discretas III · Universidad Icesi · 2026-2

---

## 1. Introduction and Context

Automated résumé screening has become widespread across human resource workflows. Traditional statistical machine learning and modern large language model (LLM) approaches often suffer from well-documented flaws: opaque decision criteria ("black-box" models), non-deterministic outputs, vulnerability to adversarial prompt injection, and the reinforcement of historical demographic biases (O'Neil, 2016; Dastin, 2018).

In contrast, **ResumeLens** investigates a formal language and automata-theoretic foundation for resume screening. Rather than attempting to rank candidates by perceived subjective merit or predict job performance, ResumeLens solves a well-defined decision problem: determining whether the explicitly declared qualifications in a candidate's résumé satisfy formally specified qualification patterns for target professional profiles.

This document reviews the theoretical foundations of the computational models employed across the ResumeLens pipeline and contrasts formal methods against probabilistic techniques.

---

## 2. Theoretical Foundations

### 2.1 Regular Expressions in Information Extraction
Regular expressions represent languages recognizable by finite automata (Chomsky Type-3). In information extraction, regular expressions serve as efficient pattern matchers for structured and semi-structured text components characterized by regular boundaries, such as email addresses, telephone numbers, URLs, and section delimiters (Hopcroft, Motwani, & Ullman, 2006; Friedl, 2006).

In ResumeLens, compiled regular expressions operate in Stage 1 to isolate surface qualification tokens and candidate metadata from noisy unstructured résumé text without altering capitalization or original surface spellings.

### 2.2 Finite-State Transducers for Canonical Normalization
Finite-State Transducers (FSTs) extend standard finite automata by associating each transition with both an input symbol and an output string, formally computing a rational relation between an input alphabet $\Sigma$ and an output alphabet $\Gamma$ (Mohri, 1997; Roche & Schabes, 1997).

In technical résumés, identical technologies appear under numerous lexical variants and surface aliases (e.g., `js`, `react.js`, `postgres`, `sklearn`). The formal mapping from variant spellings to canonical symbols ($\Gamma$) requires whole-string matching to prevent prefix ambiguities (e.g., ensuring `java` is never recognized as a prefix of `javascript`). A transducer-based approach ensures:
1. **Mathematical determinism:** A given alias always produces the exact same canonical token.
2. **Explicit alphabet boundaries:** Inputs containing symbols outside the recognized alphabet $\Sigma$ are rejected deterministically rather than guessed.
3. **Traceability:** Unrecognized terms are captured explicitly for inspection without silent data corruption.

### 2.3 Finite Automata in Qualification Pattern Recognition
A Finite-State Automaton (FSA) is a 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$ that accepts or rejects sequences of input symbols based on state transitions (Sipser, 2013).

In Stage 3 of ResumeLens, each professional profile corresponds to a formal language over the canonical vocabulary $\Sigma = \Gamma$. Because candidate skills are pre-sorted into a canonical slot order (e.g., Language $\to$ Frontend $\to$ Backend $\to$ Database $\to$ Version Control), pattern satisfaction reduces to regular language membership. Non-optional slots require at least one representative token, while optional slots permit $\varepsilon$-transitions or bypass paths. The binary decision ($w \in L(M)$) provides provable formal verification of qualification satisfaction.

### 2.4 Context-Free Grammars and Domain-Specific Languages
Context-Free Grammars (CFGs, Chomsky Type-2) introduce production rules capable of generating hierarchical and nested structures with balanced delimiters (Chomsky, 1956). While regular languages suffice for linear token sequences, hierarchical candidate profiles (containing repeated, variable-cardinality blocks of education, work experience, normalized skills, and multi-profile evaluation results) require context-free expressiveness.

Parsing Expression Grammars (PEGs) and tools such as **textX** (Dejanović et al., 2017; Ford, 2004) allow unambiguous, top-down deterministic parsing of domain-specific languages (DSLs). By defining the candidate profile language in ISO/IEC 14977 EBNF and compiling it into an Abstract Syntax Tree (AST), the system validates structural integrity before generating human-readable visualizations (HTML/Markdown).

---

## 3. Comparison: Formal Language Screening vs. Probabilistic / LLM Systems

| Evaluation Criterion | Formal Methods (ResumeLens) | Probabilistic ML / LLM Screening |
|---|---|---|
| **Determinism** | **100% Deterministic:** Identical input guaranteed to produce identical output. | **Stochastic:** Outputs vary across runs depending on sampling temperature and prompt phrasing. |
| **Explainability** | **Fully Transparent:** Rejection or acceptance maps directly to specific automaton states and missing slots. | **Opaque ("Black Box"):** Difficult to audit why a candidate was ranked higher or lower. |
| **Auditability & Verification** | **Provable:** Invariants and grammar rules mathematically verifiable. | **Empirical:** Requires statistical evaluation; cannot guarantee zero hallucinations. |
| **Computational Footprint** | **Minimal:** Linear-time parsing ($O(n)$) requiring negligible CPU and memory resources. | **High:** Requires substantial GPU infrastructure and high energy consumption. |
| **Ethical Risk Profile** | **Eliminates Algorithmic Bias:** Does not rank candidates or infer subjective merit. | **High Risk:** Prone to learning and amplifying historical gender, racial, and institutional biases. |

---

## 4. Academic References

1. **Chomsky, N.** (1956). *Three models for the description of language*. IRE Transactions on Information Theory, 2(3), 113–124.
2. **Dastin, J.** (2018). *Amazon scraps secret AI recruiting tool that showed bias against women*. Reuters Technology News.
3. **Dejanović, I., Vaderna, R., Milosavljević, G., & Vuković, Ž.** (2017). *TextX: A Python tool for Domain-Specific Language implementation*. Knowledge-Based Systems, 115, 1–4.
4. **Ford, B.** (2004). *Parsing expression grammars: a recognition-based syntactic foundation*. ACM SIGPLAN Notices, 39(1), 111–122.
5. **Friedl, J. E.** (2006). *Mastering Regular Expressions* (3rd ed.). O'Reilly Media.
6. **Hopcroft, J. E., Motwani, R., & Ullman, J. D.** (2006). *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Addison-Wesley.
7. **Mohri, M.** (1997). *Finite-state transducers in language and speech processing*. Computational Linguistics, 23(2), 269–311.
8. **O'Neil, C.** (2016). *Weapons of Math Destruction: How Big Data Increases Inequality and Threatens Democracy*. Crown Publishing Group.
9. **Roche, E., & Schabes, Y.** (1997). *Finite-State Language Processing*. MIT Press.
10. **Sipser, M.** (2013). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning.
