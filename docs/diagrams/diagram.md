# System Diagrams

This document contains visual diagrams representing the architecture and execution pipeline of ResumeLens.

---

## 1. End-to-End Pipeline Architecture

```mermaid
flowchart TD
    Input["Raw Résumé Text (plain text)"] --> Stage1["Stage 1: Extraction (re)<br/>Extracts raw skills, contact & experience"]
    Stage1 --> ExtRes["ExtractionResult"]

    ExtRes -->|raw_skills| Stage2["Stage 2: Normalization (pyformlang FST)<br/>Maps aliases to canonical tokens Γ"]
    Stage2 --> NormRes["NormalizationResult<br/>tokens ⊆ Γ, unrecognized"]

    NormRes -->|tokens| Stage2b["Stage 2b: Sorting & Filtering<br/>Orders tokens according to profile slots"]
    Stage2b --> Seq["Profile Sequences (per profile)"]

    Seq --> Stage3["Stage 3: Recognition (pyformlang FSA)<br/>Evaluates qualification patterns"]
    ProfilesConfig[("profiles/*.json<br/>Full Stack, ML, DevOps, Data")] --> Stage3
    Stage3 --> ClassRes["list[ProfileResult]<br/>ACCEPTED / REJECTED"]

    ExtRes -->|candidate| Stage4["Stage 4: Candidate DSL (textX / CFG)<br/>Serializes and validates candidate AST"]
    NormRes -->|tokens| Stage4
    ClassRes --> Stage4
    Stage4 --> ValidatedModel["Validated CandidateModel"]

    ValidatedModel --> Stage4b_HTML["to_html()<br/>Self-contained HTML Report"]
    ValidatedModel --> Stage4b_MD["to_markdown()<br/>Formatted Markdown Report"]
    Stage4 --> DSLText["DSL Source Text (.dsl)"]
```

---

## 2. Sequence Diagram of Pipeline Execution

```mermaid
sequenceDiagram
    autonumber
    actor User as User / CLI
    participant Pipeline as pipeline.run()
    participant Extractor as Stage 1 (extraction.py)
    participant Normalizer as Stage 2 (normalization.py)
    participant Classifier as Stage 3 (recognition.py)
    participant DSL as Stage 4 (dsl.py / candidate.tx)
    participant Renderer as Stage 4b (render.py)

    User->>Pipeline: run(resume_text)
    Pipeline->>Extractor: extract(resume_text)
    Extractor-->>Pipeline: ExtractionResult
    Pipeline->>Normalizer: normalize(raw_skills)
    Normalizer-->>Pipeline: NormalizationResult
    Pipeline->>Classifier: classify(tokens, profiles)
    Classifier-->>Pipeline: list[ProfileResult]
    Pipeline->>DSL: to_dsl(candidate, tokens, results)
    DSL-->>Pipeline: dsl_text
    Pipeline->>DSL: validate(dsl_text)
    DSL-->>Pipeline: validated textX model
    Pipeline->>Renderer: to_html(model)
    Renderer-->>Pipeline: html_output
    Pipeline->>Renderer: to_markdown(model)
    Renderer-->>Pipeline: markdown_output
    Pipeline-->>User: PipelineResult(extraction, normalization, classifications, dsl_text, html, markdown)
```