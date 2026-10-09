"""Tests for the shared data models (contract, Section 5.1)."""

from resumelens import (
    Candidate,
    DSLValidationError,
    Experience,
    ProfileResult,
    ResumeLensError,
    VocabularyError,
)


def test_candidate_defaults_are_never_none():
    candidate = Candidate()
    assert candidate.name == ""
    for field_name in ("emails", "phones", "links", "education", "experience"):
        assert getattr(candidate, field_name) == []


def test_default_lists_are_not_shared():
    a, b = Candidate(), Candidate()
    a.emails.append("a@example.com")
    assert b.emails == []


def test_experience_years_is_the_only_nullable_field():
    assert Experience().years is None
    assert Experience().description == ""


def test_profile_result_verdict():
    assert ProfileResult("FULL_STACK_DEVELOPER", [], True).verdict == "ACCEPTED"
    assert ProfileResult("FULL_STACK_DEVELOPER", [], False).verdict == "REJECTED"


def test_error_hierarchy():
    assert issubclass(VocabularyError, ResumeLensError)
    error = DSLValidationError("Unexpected token", line=3, column=7)
    assert error.line == 3 and error.column == 7
    assert "line 3, column 7" in str(error)
