"""Shared data models exchanged between stages (contract, Section 5).

These dataclasses ARE the contract. Changing a field requires the agreement
of all three members (contract, Section 12).

Conventions (contract, Section 2):
* collections and strings are never ``None`` (use ``[]`` and ``""``);
* the only nullable field is ``Experience.years``;
* a stage never mutates the object it receives, it returns a new one.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Education:
    degree: str = ""        # e.g. "B.Sc. Computer Engineering"
    institution: str = ""   # e.g. "Universidad Icesi"
    year: str = ""          # kept as text: "2024", "2020-2024", "" if absent


@dataclass
class Experience:
    years: float | None = None  # "3 years of experience" -> 3.0; None if not stated
    description: str = ""       # e.g. "developing web applications"


@dataclass
class Candidate:
    name: str = ""                                          # "" if not detected
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)          # GitHub, LinkedIn, portfolio
    education: list[Education] = field(default_factory=list)
    experience: list[Experience] = field(default_factory=list)


@dataclass
class ExtractionResult:
    """Output of Stage 1 (regular expressions)."""

    candidate: Candidate
    raw_skills: list[str]   # surface strings, original case, in order, NOT deduplicated


@dataclass
class NormalizationResult:
    """Output of Stage 2 (finite-state transducers)."""

    tokens: list[str]           # canonical tokens, deduplicated, order of first appearance
    mapping: dict[str, str]     # raw string (as extracted) -> canonical token
    unrecognized: list[str]     # raw strings rejected by the transducers, in order


@dataclass
class ProfileResult:
    """Output of Stage 3 (finite automata), one per profile."""

    profile_id: str             # e.g. "FULL_STACK_DEVELOPER"
    sequence: list[str]         # sorted and filtered sequence the automaton consumed
    accepted: bool              # True -> "ACCEPTED", False -> "REJECTED"

    @property
    def verdict(self) -> str:
        """``"ACCEPTED"`` or ``"REJECTED"``, as written in the DSL."""
        return "ACCEPTED" if self.accepted else "REJECTED"


@dataclass
class PipelineResult:
    """Output of the orchestrator (``pipeline.run``)."""

    extraction: ExtractionResult
    normalization: NormalizationResult
    classifications: list[ProfileResult]
    dsl_text: str               # validated DSL source
    html: str                   # visualization (HTML)
    markdown: str               # visualization (Markdown)


__all__ = [
    "Candidate",
    "Education",
    "Experience",
    "ExtractionResult",
    "NormalizationResult",
    "PipelineResult",
    "ProfileResult",
]
