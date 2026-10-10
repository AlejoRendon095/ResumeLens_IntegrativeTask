"""Tests for ResumeLens Stage 1 extraction."""

import pytest

from resumelens.errors import ExtractionError
from resumelens.extraction import extract


def test_extracts_name_experience_and_section_skills() -> None:
    result = extract(
        "Wednesday Addams\n3 years of experience developing web applications.\n"
        "Technical Skills:\nJS, React.js, NodeJS, Postgres, Git."
    )
    assert result.candidate.name == "Wednesday Addams"
    assert result.candidate.experience[0].years == 3.0
    assert result.candidate.experience[0].description == "developing web applications"
    assert result.raw_skills == ["JS", "React.js", "NodeJS", "Postgres", "Git"]


def test_extracts_data_science_skills() -> None:
    result = extract(
        "Mary Jane Watson\n2 years of experience developing predictive models and "
        "data-processing pipelines.\nTechnical Skills:\nPython, Pandas, NumPy, "
        "Scikit-learn, TensorFlow, SQL, Git."
    )
    assert result.raw_skills == [
        "Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"
    ]


def test_empty_input_returns_empty_fields() -> None:
    result = extract("")
    assert result.candidate.name == ""
    assert result.candidate.emails == []
    assert result.candidate.phones == []
    assert result.candidate.links == []
    assert result.candidate.education == []
    assert result.candidate.experience == []
    assert result.raw_skills == []


@pytest.mark.parametrize("value", [None, 123])
def test_non_string_input_raises_extraction_error(value: object) -> None:
    with pytest.raises(ExtractionError):
        extract(value)  # type: ignore[arg-type]


def test_preserves_skill_duplicates_case_and_slashes() -> None:
    assert extract("Skills: js, JS, Javascript").raw_skills == ["js", "JS", "Javascript"]
    assert extract("Technical Skills:\nCI/CD, Docker").raw_skills == ["CI/CD", "Docker"]


def test_extracts_contacts_in_appearance_order() -> None:
    result = extract(
        "José Peña\njose@example.com; second@example.org\n"
        "+57 300 123 4567, (300) 123-4567, 300-123-4567\n"
        "https://example.com, github.com/jose, linkedin.com/in/jose."
    )
    assert result.candidate.name == "José Peña"
    assert result.candidate.emails == ["jose@example.com", "second@example.org"]
    assert result.candidate.phones == ["+57 300 123 4567", "(300) 123-4567", "300-123-4567"]
    assert result.candidate.links == [
        "https://example.com", "github.com/jose", "linkedin.com/in/jose"
    ]


def test_extracts_english_and_spanish_experience_variants() -> None:
    result = extract("5+ years of experience leading teams.\n3 años de experiencia en análisis de datos.")
    assert result.candidate.experience[0].years == 5.0
    assert result.candidate.experience[0].description == "leading teams"
    assert result.candidate.experience[1].years == 3.0
    assert result.candidate.experience[1].description == "análisis de datos"


def test_extracts_education_fields() -> None:
    result = extract("B.Sc. Computer Science - Universidad de los Andes - 2020-2024")
    assert len(result.candidate.education) == 1
    assert result.candidate.education[0].degree == "B.Sc. Computer Science"
    assert result.candidate.education[0].institution == "Universidad de los Andes"
    assert result.candidate.education[0].year == "2020-2024"


def test_fallback_finds_known_aliases_in_appearance_order() -> None:
    result = extract("I work with React.js and Git.")
    assert result.raw_skills == ["React.js", "Git"]


def test_fallback_ignores_short_and_ambiguous_aliases() -> None:
    result = extract("I use JS, ML, TF, REST, Node, Torch, Git, and React.")
    assert result.raw_skills == ["Git", "React"]


def test_skills_section_stops_at_header_without_colon() -> None:
    result = extract(
        "Technical Skills:\nPython, Git\n"
        "Education\nB.Sc. Computer Science - Universidad X - 2024"
    )
    assert result.raw_skills == ["Python", "Git"]


def test_engineer_alone_is_not_education() -> None:
    result = extract("Engineer\nEngineering\nB.Sc. Computer Science - 2024")
    assert len(result.candidate.education) == 1
    assert result.candidate.education[0].degree == "B.Sc. Computer Science"


def test_name_only_uses_first_non_empty_line() -> None:
    result = extract("Resume\nAda Lovelace\nSkills:\nPython")
    assert result.candidate.name == ""


def test_handles_missing_sections_and_windows_line_endings() -> None:
    result = extract("José Peña\r\nEmail: jose@example.com\r\n")
    assert result.candidate.name == "José Peña"
    assert result.candidate.education == []
    assert result.candidate.experience == []
    assert result.raw_skills == []


def test_extract_is_deterministic_and_does_not_modify_input() -> None:
    text = "Ada Lovelace\nSkills:\nPython, Git."
    original = text
    first = extract(text)
    second = extract(text)
    assert text == original
    assert first == second
