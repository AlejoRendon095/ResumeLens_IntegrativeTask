from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from resumelens.dsl import to_dsl, validate
from resumelens.errors import ExtractionError
from resumelens.models import (
    Candidate,
    Education,
    Experience,
    ExtractionResult,
    NormalizationResult,
    PipelineResult,
    ProfileResult,
)
from resumelens.render import to_html, to_markdown
from resumelens.vocabulary import alias_index

DEFAULT_PROFILES: list[dict[str, Any]] = [
    {
        "id": "FULL_STACK_DEVELOPER",
        "display_name": "Full Stack Developer",
        "slots": [
            {"category": "LANGUAGE", "any_of": ["JAVASCRIPT", "TYPESCRIPT"], "optional": False},
            {"category": "FRONTEND", "any_of": ["REACT", "ANGULAR", "VUE"], "optional": False},
            {"category": "BACKEND", "any_of": ["NODE_JS", "DJANGO", "SPRING_BOOT"], "optional": False},
            {"category": "DATABASE", "any_of": ["SQL", "POSTGRESQL", "MYSQL", "MONGODB"], "optional": False},
            {"category": "API", "any_of": ["REST_API"], "optional": True},
            {"category": "VERSION_CONTROL", "any_of": ["GIT"], "optional": False},
        ],
    },
    {
        "id": "MACHINE_LEARNING_ENGINEER",
        "display_name": "Machine Learning Engineer",
        "slots": [
            {"category": "LANGUAGE", "any_of": ["PYTHON"], "optional": False},
            {"category": "DATA_LIB", "any_of": ["PANDAS", "NUMPY"], "optional": False},
            {"category": "ML_LIB", "any_of": ["SCIKIT_LEARN", "TENSORFLOW", "PYTORCH"], "optional": False},
            {"category": "ML_PRACTICE", "any_of": ["ML_MODEL_DEVELOPMENT"], "optional": True},
            {"category": "DATABASE", "any_of": ["SQL", "POSTGRESQL", "MYSQL"], "optional": False},
            {"category": "VERSION_CONTROL", "any_of": ["GIT"], "optional": False},
        ],
    },
    {
        "id": "DEVOPS_ENGINEER",
        "display_name": "DevOps Engineer",
        "slots": [
            {"category": "OPERATING_SYSTEM", "any_of": ["LINUX"], "optional": False},
            {"category": "VERSION_CONTROL", "any_of": ["GIT"], "optional": False},
            {"category": "CI_CD", "any_of": ["CI_CD"], "optional": False},
            {"category": "CONTAINER", "any_of": ["DOCKER"], "optional": False},
            {"category": "ORCHESTRATION", "any_of": ["KUBERNETES"], "optional": True},
            {"category": "CLOUD", "any_of": ["AWS"], "optional": False},
        ],
    },
    {
        "id": "DATA_ENGINEER",
        "display_name": "Data Engineer",
        "slots": [
            {"category": "LANGUAGE", "any_of": ["PYTHON"], "optional": False},
            {"category": "DATABASE", "any_of": ["SQL", "POSTGRESQL", "MYSQL"], "optional": False},
            {"category": "PROCESSING", "any_of": ["SPARK"], "optional": False},
            {"category": "WORKFLOW", "any_of": ["AIRFLOW"], "optional": True},
            {"category": "STREAMING", "any_of": ["KAFKA"], "optional": True},
            {"category": "VERSION_CONTROL", "any_of": ["GIT"], "optional": False},
        ],
    },
]


def _mock_extract(text: str) -> ExtractionResult:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    name = lines[0] if lines else ""

    experience: list[Experience] = []
    exp_pattern = re.compile(r"(\d+(?:\.\d+)?)\s+years?\s+of\s+experience\s*(.*)", re.IGNORECASE)
    for line in lines[1:]:
        match = exp_pattern.search(line)
        if match:
            years = float(match.group(1))
            desc = match.group(2).strip(" .")
            experience.append(Experience(years=years, description=desc))

    raw_skills: list[str] = []
    skill_header = False
    for line in lines[1:]:
        if re.search(r"technical skills|skills:", line, re.IGNORECASE):
            skill_header = True
            content = re.sub(r"^(technical skills|skills):\s*", "", line, flags=re.IGNORECASE)
            items = [item.strip(" .,;") for item in content.split(",") if item.strip(" .,;")]
            raw_skills.extend(items)
        elif skill_header:
            items = [item.strip(" .,;") for item in line.split(",") if item.strip(" .,;")]
            raw_skills.extend(items)

    candidate = Candidate(
        name=name,
        emails=[],
        phones=[],
        links=[],
        education=[],
        experience=experience,
    )
    return ExtractionResult(candidate=candidate, raw_skills=raw_skills)


def _mock_normalize(raw_skills: list[str]) -> NormalizationResult:
    aliases = alias_index()
    tokens: list[str] = []
    mapping: dict[str, str] = {}
    unrecognized: list[str] = []

    for raw in raw_skills:
        clean = raw.strip().casefold()
        clean = re.sub(r"\s+", " ", clean)
        clean = clean.rstrip(".,;:")
        token = aliases.get(clean)
        if token:
            mapping[raw] = token
            if token not in tokens:
                tokens.append(token)
        else:
            unrecognized.append(raw)

    return NormalizationResult(tokens=tokens, mapping=mapping, unrecognized=unrecognized)


def _mock_classify(tokens: list[str], profiles: list[dict[str, Any]]) -> list[ProfileResult]:
    token_set = set(tokens)
    results: list[ProfileResult] = []

    for profile in profiles:
        slots = profile.get("slots", [])
        matched_sequence: list[str] = []
        is_accepted = True

        for slot in slots:
            slot_tokens = slot.get("any_of", [])
            is_optional = slot.get("optional", False)
            found_in_slot = [t for t in slot_tokens if t in token_set]

            if found_in_slot:
                matched_sequence.extend(found_in_slot)
            elif not is_optional:
                is_accepted = False

        results.append(
            ProfileResult(
                profile_id=profile["id"],
                sequence=matched_sequence,
                accepted=is_accepted,
            )
        )

    return results


def _resolve_extractor(custom: Callable[[str], ExtractionResult] | None) -> Callable[[str], ExtractionResult]:
    if custom is not None:
        return custom
    try:
        from resumelens.extraction import extract
        if callable(extract):
            return extract
    except (ImportError, AttributeError):
        pass
    return _mock_extract


def _resolve_normalizer(custom: Callable[[list[str]], NormalizationResult] | None) -> Callable[[list[str]], NormalizationResult]:
    if custom is not None:
        return custom
    try:
        from resumelens.normalization import normalize
        if callable(normalize):
            return normalize
    except (ImportError, AttributeError):
        pass
    return _mock_normalize


def _resolve_classifier(
    custom: Callable[[list[str], list[dict[str, Any]]], list[ProfileResult]] | None
) -> Callable[[list[str], list[dict[str, Any]]], list[ProfileResult]]:
    if custom is not None:
        return custom
    try:
        from resumelens.recognition import classify
        if callable(classify):
            return classify
    except (ImportError, AttributeError):
        pass
    return _mock_classify


def _resolve_profiles(custom: list[dict[str, Any]] | None, profiles_dir: str | Path | None) -> list[dict[str, Any]]:
    if custom is not None:
        return custom
    try:
        from resumelens.profiles import load_profiles
        if callable(load_profiles):
            path = profiles_dir if profiles_dir is not None else "profiles/"
            return load_profiles(path)
    except (ImportError, AttributeError):
        pass
    return DEFAULT_PROFILES


def run(
    resume_text: str,
    *,
    extractor: Callable[[str], ExtractionResult] | None = None,
    normalizer: Callable[[list[str]], NormalizationResult] | None = None,
    classifier: Callable[[list[str], list[dict[str, Any]]], list[ProfileResult]] | None = None,
    profiles: list[dict[str, Any]] | None = None,
    profiles_dir: str | Path | None = None,
) -> PipelineResult:
    if not isinstance(resume_text, str):
        raise ExtractionError(f"resume_text must be a string, got {type(resume_text).__name__}")

    extract_fn = _resolve_extractor(extractor)
    normalize_fn = _resolve_normalizer(normalizer)
    classify_fn = _resolve_classifier(classifier)
    active_profiles = _resolve_profiles(profiles, profiles_dir)

    extraction = extract_fn(resume_text)
    normalization = normalize_fn(extraction.raw_skills)
    classifications = classify_fn(normalization.tokens, active_profiles)

    dsl_text = to_dsl(extraction.candidate, normalization.tokens, classifications)
    model = validate(dsl_text)

    html_report = to_html(model)
    markdown_report = to_markdown(model)

    return PipelineResult(
        extraction=extraction,
        normalization=normalization,
        classifications=classifications,
        dsl_text=dsl_text,
        html=html_report,
        markdown=markdown_report,
    )


__all__ = [
    "DEFAULT_PROFILES",
    "run",
]
