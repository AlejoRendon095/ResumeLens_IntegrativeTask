from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import textx
from textx import metamodel_from_file

from resumelens.errors import DSLValidationError
from resumelens.models import Candidate, ProfileResult

GRAMMAR_PATH = Path(__file__).with_name("candidate.tx")


@lru_cache(maxsize=1)
def get_metamodel():
    if not GRAMMAR_PATH.is_file():
        raise DSLValidationError(f"Grammar file not found: {GRAMMAR_PATH}")
    return metamodel_from_file(str(GRAMMAR_PATH))


def _escape_str(value: str) -> str:
    escaped = value.replace('"', r'\"').replace("\n", " ").replace("\r", "")
    return f'"{escaped}"'


def to_dsl(
    candidate: Candidate,
    tokens: list[str],
    results: list[ProfileResult],
) -> str:
    if not isinstance(candidate, Candidate):
        raise TypeError(f"candidate must be an instance of Candidate, got {type(candidate).__name__}")
    if not isinstance(tokens, list):
        raise TypeError(f"tokens must be a list, got {type(tokens).__name__}")
    if not isinstance(results, list):
        raise TypeError(f"results must be a list, got {type(results).__name__}")

    lines: list[str] = []
    lines.append(f"candidate {_escape_str(candidate.name)} {{")

    has_contact = bool(candidate.emails or candidate.phones or candidate.links)
    if has_contact:
        lines.append("  contact {")
        for email in candidate.emails:
            lines.append(f"    email {_escape_str(email)}")
        for phone in candidate.phones:
            lines.append(f"    phone {_escape_str(phone)}")
        for link in candidate.links:
            lines.append(f"    link {_escape_str(link)}")
        lines.append("  }")
    else:
        lines.append("  contact { }")

    for edu in candidate.education:
        parts: list[str] = []
        if edu.degree:
            parts.append(f"degree {_escape_str(edu.degree)}")
        if edu.institution:
            parts.append(f"institution {_escape_str(edu.institution)}")
        if edu.year:
            parts.append(f"year {_escape_str(edu.year)}")
        if parts:
            lines.append("  education { " + " ".join(parts) + " }")
        else:
            lines.append("  education { }")

    for exp in candidate.experience:
        parts = []
        if exp.years is not None:
            years_val = int(exp.years) if exp.years.is_integer() else exp.years
            parts.append(f"years {years_val}")
        if exp.description:
            parts.append(f"description {_escape_str(exp.description)}")
        if parts:
            lines.append("  experience { " + " ".join(parts) + " }")
        else:
            lines.append("  experience { }")

    if tokens:
        lines.append("  skills {")
        lines.append("    " + " ".join(tokens))
        lines.append("  }")
    else:
        lines.append("  skills { }")

    lines.append("  classification {")
    for res in results:
        lines.append(f"    {res.profile_id}: {res.verdict}")
    lines.append("  }")

    lines.append("}")
    return "\n".join(lines)


def validate(dsl_text: str) -> Any:
    if not isinstance(dsl_text, str):
        raise DSLValidationError("DSL input must be a string.")
    if not dsl_text.strip():
        raise DSLValidationError("DSL input cannot be empty.")

    mm = get_metamodel()
    try:
        model = mm.model_from_str(dsl_text)
        return model
    except textx.exceptions.TextXError as exc:
        raise DSLValidationError(
            str(exc),
            line=getattr(exc, "line", None),
            column=getattr(exc, "col", None),
        ) from exc


__all__ = [
    "GRAMMAR_PATH",
    "get_metamodel",
    "to_dsl",
    "validate",
]
