# Literature Review: Formal Language-Based Resume Screening

Integrative Task 1 · Computación y Estructuras Discretas III · Universidad Icesi · 2026-2

---
## 1. Context: automated résumé screening

Recruiters receive far more applications than they can read, so most companies use applicant tracking systems that parse résumés and filter candidates before a person looks at them. Two problems appear in every study of these systems. First, résumés have no fixed format: the same information appears in different sections, orders and spellings. Second, automated filters influence who gets hired, so their decisions must be explainable and auditable. Raghavan et al. (2020) reviewed the public claims of commercial pre-employment assessment vendors and found that most of them say little about how their models work or how bias is checked, which makes independent validation difficult.

ResumeLens addresses a narrower question than those products. It does not rank candidates or predict job performance; it only checks whether the qualifications *written* in a résumé match a formally defined profile pattern. This scope lets every decision be traced back to a regular expression, a transducer, an automaton or a grammar rule.

## 3. Information extraction from résumés

Early work treated résumé parsing as information extraction over semi-structured text. Yu, Guan and Zhou (2005) proposed a *cascaded hybrid model*: a first pass splits the résumé into general blocks (personal information, education, work experience) and a second pass extracts detailed fields inside each block, combining HMMs for some fields and SVMs for others. Chen, Zhang and Niu (2018) follow the same two-step idea: they classify the lines of a résumé into blocks using writing-style features and then extract fields inside each block, reporting better results than a single-pass extractor. Both papers show that résumé structure (sections and their typical vocabulary) is the main signal for extraction.

Statistical extractors need labelled data, which is scarce for résumés written in many styles and languages. Chiticariu, Li and Reiss (2013) surveyed commercial information-extraction products and found that rule-based systems dominate industry, while academic research focuses on machine learning. They attribute this to the fact that rules are easy to explain, debug and maintain, which matters more to companies than a small gain in accuracy.

**Relevance to ResumeLens.** Stage 1 follows the rule-based approach: one regular expression per information type (contact data, languages, frameworks, databases, education, experience). Rules are transparent and their recognized language can be stated exactly, as the assignment requires.

## 4. Theoretical Foundations

### 4.1 Regular Expressions in Information Extraction
Regular expressions represent languages recognizable by finite automata (Chomsky Type-3). In information extraction, regular expressions serve as efficient pattern matchers for structured and semi-structured text components characterized by regular boundaries, such as email addresses, telephone numbers, URLs, and section delimiters (Hopcroft, Motwani, & Ullman, 2006; Friedl, 2006).

In ResumeLens, compiled regular expressions operate in Stage 1 to isolate surface qualification tokens and candidate metadata from noisy unstructured résumé text without altering capitalization or original surface spellings.

### 4.2 Finite-State Transducers for Canonical Normalization
Finite-State Transducers (FSTs) extend standard finite automata by associating each transition with both an input symbol and an output string, formally computing a rational relation between an input alphabet $\Sigma$ and an output alphabet $\Gamma$ (Mohri, 1997; Roche & Schabes, 1997).

In technical résumés, identical technologies appear under numerous lexical variants and surface aliases (e.g., `js`, `react.js`, `postgres`, `sklearn`). The formal mapping from variant spellings to canonical symbols ($\Gamma$) requires whole-string matching to prevent prefix ambiguities (e.g., ensuring `java` is never recognized as a prefix of `javascript`). A transducer-based approach ensures:
1. **Mathematical determinism:** A given alias always produces the exact same canonical token.
2. **Explicit alphabet boundaries:** Inputs containing symbols outside the recognized alphabet $\Sigma$ are rejected deterministically rather than guessed.
3. **Traceability:** Unrecognized terms are captured explicitly for inspection without silent data corruption.

### 4.3 Finite Automata in Qualification Pattern Recognition
A Finite-State Automaton (FSA) is a 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$ that accepts or rejects sequences of input symbols based on state transitions (Sipser, 2013).

In Stage 3 of ResumeLens, each professional profile corresponds to a formal language over the canonical vocabulary $\Sigma = \Gamma$. Because candidate skills are pre-sorted into a canonical slot order (e.g., Language $\to$ Frontend $\to$ Backend $\to$ Database $\to$ Version Control), pattern satisfaction reduces to regular language membership. Non-optional slots require at least one representative token, while optional slots permit $\varepsilon$-transitions or bypass paths. The binary decision ($w \in L(M)$) provides provable formal verification of qualification satisfaction.

### 4.4 Context-Free Grammars and Domain-Specific Languages
Context-Free Grammars (CFGs, Chomsky Type-2) introduce production rules capable of generating hierarchical and nested structures with balanced delimiters (Chomsky, 1956). While regular languages suffice for linear token sequences, hierarchical candidate profiles (containing repeated, variable-cardinality blocks of education, work experience, normalized skills, and multi-profile evaluation results) require context-free expressiveness.

Parsing Expression Grammars (PEGs) and tools such as **textX** (Dejanović et al., 2017; Ford, 2004) allow unambiguous, top-down deterministic parsing of domain-specific languages (DSLs). By defining the candidate profile language in ISO/IEC 14977 EBNF and compiling it into an Abstract Syntax Tree (AST), the system validates structural integrity before generating human-readable visualizations (HTML/Markdown).

---

## 5. Comparison: Formal Language Screening vs. Probabilistic / LLM Systems

| Evaluation Criterion | Formal Methods (ResumeLens) | Probabilistic ML / LLM Screening |
|---|---|---|
| **Determinism** | **100% Deterministic:** Identical input guaranteed to produce identical output. | **Stochastic:** Outputs vary across runs depending on sampling temperature and prompt phrasing. |
| **Explainability** | **Fully Transparent:** Rejection or acceptance maps directly to specific automaton states and missing slots. | **Opaque ("Black Box"):** Difficult to audit why a candidate was ranked higher or lower. |
| **Auditability & Verification** | **Provable:** Invariants and grammar rules mathematically verifiable. | **Empirical:** Requires statistical evaluation; cannot guarantee zero hallucinations. |
| **Computational Footprint** | **Minimal:** Linear-time parsing ($O(n)$) requiring negligible CPU and memory resources. | **High:** Requires substantial GPU infrastructure and high energy consumption. |
| **Ethical Risk Profile** | **Eliminates Algorithmic Bias:** Does not rank candidates or infer subjective merit. | **High Risk:** Prone to learning and amplifying historical gender, racial, and institutional biases. |

---

## 6. Skill extraction and normalization

Recent NLP work studies skills in job postings and résumés. Zhang et al. (2022) released SkillSpan, a dataset of English job postings annotated with hard and soft skills, and showed that skills are often long, fuzzy spans that are hard to delimit. Senger et al. (2024) surveyed deep-learning approaches to skill extraction and classification and identified *normalization* as a separate step: after a skill mention is found, it must be mapped to an entry of a taxonomy such as ESCO, because the same skill appears with many surface forms.

**Relevance to ResumeLens.** The normalization problem in the assignment (JS, Javascript and JavaScript are the same qualification) is exactly this step. ResumeLens uses a small closed vocabulary of canonical tokens (`src/resumelens/vocabulary.json`) instead of a large taxonomy, and performs the mapping with finite-state transducers rather than a learned model.

## 7. Finite-state methods for text processing and normalization

Regular expressions and finite automata have been linked since Thompson (1968), who compiled regular expressions into nondeterministic automata to search text. Finite-state transducers extend automata with output and are a standard tool in language processing: Mohri (1997) describes their use in morphology, phonology and speech, and shows that they can be composed, determinized and minimized efficiently. Roche and Schabes (1997) collect applications of finite-state devices to dictionaries, tagging and parsing. In production systems, text normalization (for example, converting "Dr." or "12kg" into their spoken form before speech synthesis) is still written as weighted finite-state grammars; Gorman (2016) presents Pynini, the Python library used for that purpose at Google.

**Relevance to ResumeLens.** Stage 2 uses one transducer per canonical token to rewrite surface variants into the canonical form. This is the same kind of rewrite performed by text normalization grammars, at a much smaller scale.

## 8. Finite automata for pattern recognition

Classic automata theory (Hopcroft, Motwani and Ullman, 2006; Sipser, 2012) gives the tools used in Stage 3: every regular language is accepted by an NFA with ε-transitions, every ε-NFA can be converted to an equivalent DFA by subset construction, and every DFA has a unique minimal equivalent. Regular languages are closed under union and concatenation, which is what allows a profile pattern such as "one or more languages, then one or more frameworks, then …" to be written as a regular expression over a token alphabet and turned into an automaton mechanically.

**Relevance to ResumeLens.** Each profile is a sequence of slots; the corresponding language is a concatenation of `+` and `*` blocks over canonical tokens. We build the ε-NFA directly from the profile and derive the minimal DFA to show the equivalence (see `docs/formalization.md`, FSA section). Because recognition depends only on finite-state machinery, the decision for each profile is a path through a diagram that a reviewer can follow by hand.

## 9. Grammars and domain-specific languages for structured output

Once the information is extracted and classified, it must be represented in a form that can be validated. Domain-specific languages defined by context-free grammars are a common way to do this, because the parser rejects any representation that breaks the lexical or syntactic rules. Dejanović et al. (2017) present textX, a Python meta-language inspired by Xtext: a grammar written in an EBNF-like notation produces both a parser and a metamodel, and parsed files become Python objects.

**Relevance to ResumeLens.** Stage 4 defines the candidate-profile language as a textX grammar, validates every generated profile against it, and renders the validated model as HTML or Markdown.

## 10. Tools for formal languages in Python

pyformlang (Romero, 2021) is an educational Python library that implements regular expressions, finite automata, finite-state transducers, context-free grammars and pushdown automata, together with the classic algorithms (ε-removal, determinization, minimization, equivalence). ResumeLens uses it for the transducers of Stage 2 and the automata of Stage 3, and relies on its equivalence check to test that the ε-NFA and the minimal DFA of each profile accept the same language.

## 11. Gap and position of ResumeLens

Most recent work on résumés and job postings uses neural models that are accurate on benchmark data but hard to explain (Senger et al., 2024), while industry still prefers transparent rules for extraction (Chiticariu et al., 2013). Concerns about fairness and transparency in hiring tools (Raghavan et al., 2020) make explainability more than a technical preference.

ResumeLens takes the transparent end of this spectrum on purpose: every stage is a formal model with an exact definition (regular expressions, 7-tuple transducers, 5-tuple automata, an EBNF grammar), so each result can be justified step by step. The price is coverage: the vocabulary is closed, the patterns only check presence of qualifications, and the system cannot judge experience level or context. These limitations are discussed for Stage 3 in `docs/formalization.md` (Section 3.8).

## References

* Chen, J., Zhang, C., & Niu, Z. (2018). A two-step resume information extraction algorithm. *Mathematical Problems in Engineering*, 2018, 5761287. https://doi.org/10.1155/2018/5761287
* Chiticariu, L., Li, Y., & Reiss, F. R. (2013). Rule-based information extraction is dead! Long live rule-based information extraction systems! In *Proceedings of EMNLP 2013* (pp. 827–832). https://aclanthology.org/D13-1079/
* Dejanović, I., Vaderna, R., Milosavljević, G., & Vuković, Ž. (2017). TextX: A Python tool for Domain-Specific Languages implementation. *Knowledge-Based Systems*. https://github.com/textX/textX
* Gorman, K. (2016). Pynini: A Python library for weighted finite-state grammar compilation. In *Proceedings of the SIGFSM Workshop on Statistical NLP and Weighted Automata* (pp. 75–80). https://aclanthology.org/W16-2409/
* Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Pearson.
* Mohri, M. (1997). Finite-state transducers in language and speech processing. *Computational Linguistics*, 23(2), 269–311. https://aclanthology.org/J97-2003/
* Raghavan, M., Barocas, S., Kleinberg, J., & Levy, K. (2020). Mitigating bias in algorithmic hiring: Evaluating claims and practices. In *Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency (FAT\* 2020)*. https://arxiv.org/abs/1906.09208
* Roche, E., & Schabes, Y. (Eds.). (1997). *Finite-State Language Processing*. MIT Press.
* Romero, J. (2021). Pyformlang: An educational library for formal language manipulation. In *Proceedings of SIGCSE 2021*. https://pyformlang.readthedocs.io/
* Senger, E., Zhang, M., van der Goot, R., & Plank, B. (2024). Deep learning-based computational job market analysis: A survey on skill extraction and classification from job postings. In *Proceedings of the First Workshop on NLP for Human Resources (NLP4HR 2024)*. https://aclanthology.org/2024.nlp4hr-1.1/
* Sipser, M. (2012). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning.
* Thompson, K. (1968). Programming techniques: Regular expression search algorithm. *Communications of the ACM*, 11(6), 419–422.
* Yu, K., Guan, G., & Zhou, M. (2005). Resume information extraction with cascaded hybrid model. In *Proceedings of the 43rd Annual Meeting of the Association for Computational Linguistics (ACL 2005)*. Microsoft Research: https://www.microsoft.com/en-us/research/?p=151936
* Zhang, M., Jensen, K. N., Sonniks, S. D., & Plank, B. (2022). SkillSpan: Hard and soft skill extraction from English job postings. In *Proceedings of NAACL 2022* (pp. 4962–4984). https://aclanthology.org/2022.naacl-main.366/
