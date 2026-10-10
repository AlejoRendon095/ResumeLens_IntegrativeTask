"""Regular-expression extraction for Stage 1 of ResumeLens."""

from __future__ import annotations

import re

from resumelens.errors import ExtractionError
from resumelens.models import Candidate, Education, Experience, ExtractionResult
from resumelens.vocabulary import alias_index

# Email addresses with a conventional local part and domain.
EMAIL_RE = re.compile(r"(?i)\b[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+\b")
# Common international and Colombian-style phone number layouts.
PHONE_RE = re.compile(r"(?<!\w)(?:\+\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}(?!\w)")
# HTTP(S) URLs and bare GitHub or LinkedIn profile URLs.
LINK_RE = re.compile(r"(?i)(?<![\w@])(?:https?://)?(?:www\.)?(?:github\.com/[^\s,;|]+|linkedin\.com/in/[^\s,;|]+|https?://[^\s,;|]+)")
# A person's name is two to four Unicode-letter words, allowing hyphens and apostrophes.
NAME_RE = re.compile(r"^[^\W\d_]+(?:[-'][^\W\d_]+)?(?:\s+[^\W\d_]+(?:[-'][^\W\d_]+)?){1,3}$", re.UNICODE)
# Numeric experience statements in English or Spanish, capturing the trailing description.
EXPERIENCE_RE = re.compile(
    r"(?im)^\s*(?P<years>\d+(?:\.\d+)?)\s*\+?\s*(?:years?|años?)"
    r"\s+(?:of\s+|de\s+)?(?:experience|experiencia)\s*(?:en\s+)?(?P<description>[^.\r\n]+)"
    r"\.?\s*$"
)
# Education lines containing a degree keyword, with optional institution and year.
EDUCATION_RE = re.compile(
    r"(?im)^\s*(?P<degree>.*?\b(?:B\.?\s*Sc\.?|M\.?\s*Sc\.?|Ph\.?D\.?|"
    r"bachelor(?:'s)?|master(?:'s)?|engineer(?:ing)?|ingenier[ií]a|"
    r"licenciatura|doctorate|degree)\b.*?)"
    r"(?:\s*[-,|]\s*|\s+)(?P<institution>(?:Universidad|University(?:\s+of)?)[^,|;\r\n]*?)?"
    r"(?:\s*[-,|]?\s*(?P<year>\d{4}(?:\s*-\s*\d{4})?))?\s*$"
)
# A skills heading followed by content up to a blank line, next colon heading, or end of text.
SKILLS_SECTION_RE = re.compile(
    r"(?ims)^[ \t]*(?:technical skills|skills|tech stack)[ \t]*:?[ \t]*(?:\r?\n)?"
    r"(?P<body>.*?)(?=\r?\n[ \t]*\r?\n"
    r"|\r?\n[ \t]*[^:\r\n]{1,60}[ \t]*:[ \t]*(?:\r?\n|$)"
    r"|\r?\n[ \t]*(?:education|experience|projects|languages|certifications|contact|summary)"
    r"[ \t]*(?:\r?$)|\Z)"
)

_SKILL_SPLIT_RE = re.compile(r"[,;|\u2022\r\n]+")
_HEADER_NAMES = {"skills", "technical skills", "tech stack", "experience", "education"}
_FALLBACK_STOPWORDS = frozenset({"rest", "node", "torch"})
_DEGREE_ONLY_ENGINEER_RE = re.compile(r"(?i)^(?:engineer|engineering)$")


def _extract_emails(text: str) -> list[str]:
    """Return email addresses in textual order."""
    return [match.group(0) for match in EMAIL_RE.finditer(text)]


def _extract_phones(text: str) -> list[str]:
    """Return phone numbers in textual order."""
    return [match.group(0).strip() for match in PHONE_RE.finditer(text)]


def _extract_links(text: str) -> list[str]:
    """Return supported links without sentence punctuation."""
    links: list[str] = []
    for match in LINK_RE.finditer(text):
        links.append(match.group(0).rstrip(".,;:!?)]}"))
    return links


def _extract_name(text: str) -> str:
    """Return the first non-empty line that looks like a person's name."""
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        if (
            not EMAIL_RE.search(candidate)
            and not LINK_RE.search(candidate)
            and candidate.lower().rstrip(":") not in _HEADER_NAMES
            and NAME_RE.fullmatch(candidate)
        ):
            return candidate
        return ""
    return ""


def _extract_experience(text: str) -> list[Experience]:
    """Return experience statements with numeric durations."""
    return [
        Experience(float(match.group("years")), match.group("description").strip())
        for match in EXPERIENCE_RE.finditer(text)
    ]


def _extract_education(text: str) -> list[Education]:
    """Return degree lines with best-effort institution and year fields."""
    education: list[Education] = []
    for match in EDUCATION_RE.finditer(text):
        degree = match.group("degree").strip(" ,-|")
        institution = (match.group("institution") or "").strip(" ,-|")
        year = (match.group("year") or "").replace(" ", "")
        if _DEGREE_ONLY_ENGINEER_RE.fullmatch(degree) and not institution and not year:
            continue
        education.append(
            Education(
                degree=degree,
                institution=institution,
                year=year,
            )
        )
    return education


def _clean_skill(value: str) -> str:
    """Trim whitespace and one sentence-final period from a skill."""
    return value.strip().rstrip(".").strip()


def _extract_skills(text: str) -> list[str]:
    """Extract section skills or vocabulary aliases when no section exists."""
    section = SKILLS_SECTION_RE.search(text)
    if section:
        return [
            skill
            for piece in _SKILL_SPLIT_RE.split(section.group("body"))
            if (skill := _clean_skill(piece))
        ]

    aliases = sorted(
        (
            alias
            for alias in alias_index()
            if len(alias) >= 3 and alias.casefold() not in _FALLBACK_STOPWORDS
        ),
        key=len,
        reverse=True,
    )
    if not aliases:
        return []
    alias_pattern = re.compile(
        r"(?i)(?<![\w])(?:" + "|".join(re.escape(alias) for alias in aliases) + r")(?![\w])"
    )
    return [match.group(0) for match in alias_pattern.finditer(text)]


def extract(text: str) -> ExtractionResult:
    """Extract candidate contact, education, experience, and skill fields."""
    if not isinstance(text, str):
        raise ExtractionError("Extraction input must be a str.")

    candidate = Candidate(
        name=_extract_name(text),
        emails=_extract_emails(text),
        phones=_extract_phones(text),
        links=_extract_links(text),
        education=_extract_education(text),
        experience=_extract_experience(text),
    )
    return ExtractionResult(candidate=candidate, raw_skills=_extract_skills(text))
