import pytest

from resumelens import (
    Candidate,
    Education,
    Experience,
    ExtractionError,
    ExtractionResult,
    NormalizationResult,
    ProfileResult,
    run,
    validate,
)
from resumelens.vocabulary import canonical_tokens


def test_pipeline_run_wednesday_addams():
    cv_text = """
    Wednesday Addams
    3 years of experience developing web applications.
    Technical Skills:
    JS, React.js, NodeJS, Postgres, Git.
    """
    result = run(cv_text)

    assert result.extraction.candidate.name == "Wednesday Addams"
    assert len(result.extraction.candidate.experience) == 1
    assert result.extraction.candidate.experience[0].years == 3.0
    assert result.extraction.candidate.experience[0].description == "developing web applications"

    expected_tokens = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert result.normalization.tokens == expected_tokens
    assert result.normalization.mapping["JS"] == "JAVASCRIPT"
    assert result.normalization.unrecognized == []

    classifications_map = {res.profile_id: res.accepted for res in result.classifications}
    assert classifications_map["FULL_STACK_DEVELOPER"] is True
    assert classifications_map["MACHINE_LEARNING_ENGINEER"] is False
    assert classifications_map["DEVOPS_ENGINEER"] is False
    assert classifications_map["DATA_ENGINEER"] is False

    assert 'candidate "Wednesday Addams"' in result.dsl_text
    assert "<!DOCTYPE html>" in result.html
    assert "# Candidate Profile: Wednesday Addams" in result.markdown

    # Contract Invariant 6: validate(dsl_text) must succeed
    model = validate(result.dsl_text)
    assert model.name == "Wednesday Addams"


def test_pipeline_run_mary_jane_watson_ml():
    cv_text = """
    Mary Jane Watson
    5 years of experience developing machine learning models.
    Technical Skills:
    Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git.
    """
    result = run(cv_text)

    assert result.extraction.candidate.name == "Mary Jane Watson"
    assert "PYTHON" in result.normalization.tokens
    assert "SCIKIT_LEARN" in result.normalization.tokens

    classifications_map = {res.profile_id: res.accepted for res in result.classifications}
    assert classifications_map["MACHINE_LEARNING_ENGINEER"] is True
    assert classifications_map["FULL_STACK_DEVELOPER"] is False


def test_pipeline_run_with_unrecognized_skills():
    cv_text = """
    Jane Doe
    1 year of experience software development.
    Technical Skills:
    Git, Figma, Photoshop, Jira.
    """
    result = run(cv_text)

    assert result.normalization.tokens == ["GIT"]
    assert set(result.normalization.unrecognized) == {"Figma", "Photoshop", "Jira"}

    # Contract Invariant 2: set(mapping) | set(unrecognized) == set(raw_skills)
    assert set(result.normalization.mapping.keys()) | set(result.normalization.unrecognized) == set(
        result.extraction.raw_skills
    )


def test_pipeline_run_custom_stage_injection():
    def custom_extractor(text: str) -> ExtractionResult:
        candidate = Candidate(
            name="Custom Engineer",
            emails=["custom@example.com"],
            phones=[],
            links=[],
            education=[Education(degree="B.Sc.", institution="Icesi", year="2025")],
            experience=[Experience(years=4.0, description="Cloud infrastructure")],
        )
        return ExtractionResult(candidate=candidate, raw_skills=["Linux", "Docker", "Git"])

    def custom_normalizer(raw_skills: list[str]) -> NormalizationResult:
        return NormalizationResult(
            tokens=["LINUX", "DOCKER", "GIT"],
            mapping={"Linux": "LINUX", "Docker": "DOCKER", "Git": "GIT"},
            unrecognized=[],
        )

    def custom_classifier(tokens: list[str], profiles: list[dict]) -> list[ProfileResult]:
        return [
            ProfileResult("DEVOPS_ENGINEER", tokens, True),
            ProfileResult("FULL_STACK_DEVELOPER", [], False),
            ProfileResult("MACHINE_LEARNING_ENGINEER", [], False),
            ProfileResult("DATA_ENGINEER", [], False),
        ]

    result = run(
        "dummy text",
        extractor=custom_extractor,
        normalizer=custom_normalizer,
        classifier=custom_classifier,
    )

    assert result.extraction.candidate.name == "Custom Engineer"
    assert result.normalization.tokens == ["LINUX", "DOCKER", "GIT"]
    assert result.classifications[0].profile_id == "DEVOPS_ENGINEER"
    assert result.classifications[0].accepted is True
    assert "DEVOPS_ENGINEER: ACCEPTED" in result.dsl_text


def test_pipeline_run_rejects_non_string():
    with pytest.raises(ExtractionError, match="must be a string"):
        run(12345)  # type: ignore[arg-type]


def test_pipeline_invariants_and_immutability():
    cv_text = """
    Alex Rivera
    Technical Skills:
    Python, SQL, Git, Linux.
    """
    vocab = set(canonical_tokens())
    result = run(cv_text)

    # Invariant 1: NormalizationResult.tokens is subset of canonical vocabulary
    assert set(result.normalization.tokens).issubset(vocab)

    # Invariant 5: len(classifications) equals the number of loaded profiles (4)
    assert len(result.classifications) == 4

    # Invariant 6: validate(dsl_text) succeeds
    assert validate(result.dsl_text) is not None
