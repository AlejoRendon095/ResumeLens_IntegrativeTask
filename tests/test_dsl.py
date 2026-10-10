import pytest

from resumelens import (
    Candidate,
    DSLValidationError,
    Education,
    Experience,
    ProfileResult,
    to_dsl,
    validate,
)
from resumelens.dsl import get_metamodel


def test_metamodel_loads():
    metamodel = get_metamodel()
    assert metamodel is not None


def test_reference_example_from_contract():
    dsl_source = """
    candidate "Wednesday Addams" {
      contact { }
      experience { years 3 description "developing web applications" }
      skills { JAVASCRIPT REACT NODE_JS POSTGRESQL GIT }
      classification {
        FULL_STACK_DEVELOPER: ACCEPTED
        MACHINE_LEARNING_ENGINEER: REJECTED
        DEVOPS_ENGINEER: REJECTED
        DATA_ENGINEER: REJECTED
      }
    }
    """
    model = validate(dsl_source)
    assert model.name == "Wednesday Addams"
    assert len(model.experience) == 1
    assert model.experience[0].years == 3
    assert model.experience[0].description == "developing web applications"
    assert model.skills.skills == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert len(model.classification.entries) == 4
    assert model.classification.entries[0].profile_id == "FULL_STACK_DEVELOPER"
    assert model.classification.entries[0].verdict == "ACCEPTED"
    assert model.classification.entries[1].verdict == "REJECTED"


def test_to_dsl_round_trip_full():
    candidate = Candidate(
        name="Ada Lovelace",
        emails=["ada@example.com"],
        phones=["+44 123456789"],
        links=["https://github.com/adalovelace"],
        education=[
            Education(
                degree="M.Sc. Mathematics",
                institution="University of London",
                year="1840",
            ),
            Education(
                degree="B.Sc. Natural Philosophy",
                institution="Cambridge",
                year="1836",
            ),
        ],
        experience=[
            Experience(years=5.0, description="Analytical engine programming"),
            Experience(years=2.5, description="Algorithm design"),
        ],
    )
    tokens = ["PYTHON", "PANDAS", "NUMPY", "GIT"]
    results = [
        ProfileResult("MACHINE_LEARNING_ENGINEER", tokens, True),
        ProfileResult("FULL_STACK_DEVELOPER", [], False),
        ProfileResult("DATA_ENGINEER", ["PYTHON", "GIT"], True),
        ProfileResult("DEVOPS_ENGINEER", ["GIT"], False),
    ]

    dsl_text = to_dsl(candidate, tokens, results)
    model = validate(dsl_text)

    assert model.name == "Ada Lovelace"
    assert model.contact.emails == ["ada@example.com"]
    assert model.contact.phones == ["+44 123456789"]
    assert model.contact.links == ["https://github.com/adalovelace"]
    assert len(model.education) == 2
    assert model.education[0].degree == "M.Sc. Mathematics"
    assert model.education[0].institution == "University of London"
    assert model.education[0].year == "1840"
    assert len(model.experience) == 2
    assert model.experience[0].years == 5
    assert model.experience[0].description == "Analytical engine programming"
    assert model.experience[1].years == 2.5
    assert model.skills.skills == ["PYTHON", "PANDAS", "NUMPY", "GIT"]
    assert len(model.classification.entries) == 4
    assert model.classification.entries[0].profile_id == "MACHINE_LEARNING_ENGINEER"
    assert model.classification.entries[0].verdict == "ACCEPTED"
    assert model.classification.entries[1].verdict == "REJECTED"


def test_to_dsl_round_trip_minimal():
    candidate = Candidate(name="")
    tokens: list[str] = []
    results = [ProfileResult("FULL_STACK_DEVELOPER", [], False)]

    dsl_text = to_dsl(candidate, tokens, results)
    model = validate(dsl_text)

    assert model.name == ""
    assert model.education == []
    assert model.experience == []
    assert model.skills.skills == []
    assert len(model.classification.entries) == 1
    assert model.classification.entries[0].profile_id == "FULL_STACK_DEVELOPER"
    assert model.classification.entries[0].verdict == "REJECTED"


def test_validate_rejects_non_string():
    with pytest.raises(DSLValidationError, match="must be a string"):
        validate(123)  # type: ignore[arg-type]


@pytest.mark.parametrize("empty_input", ["", "   ", "\n\t  \n"])
def test_validate_rejects_empty_input(empty_input):
    with pytest.raises(DSLValidationError, match="cannot be empty"):
        validate(empty_input)


def test_validate_rejects_missing_candidate_keyword():
    with pytest.raises(DSLValidationError):
        validate('"Wednesday Addams" { classification { FULL_STACK_DEVELOPER: ACCEPTED } }')


def test_validate_rejects_missing_classification_block():
    with pytest.raises(DSLValidationError) as exc_info:
        validate('candidate "Wednesday Addams" { skills { GIT } }')
    assert exc_info.value.line is not None


def test_validate_rejects_invalid_verdict():
    dsl = """
    candidate "Wednesday Addams" {
      classification {
        FULL_STACK_DEVELOPER: MAYBE
      }
    }
    """
    with pytest.raises(DSLValidationError) as exc_info:
        validate(dsl)
    assert exc_info.value.line is not None


def test_validate_rejects_lowercase_skill_token():
    dsl = """
    candidate "Wednesday Addams" {
      skills { javascript }
      classification {
        FULL_STACK_DEVELOPER: ACCEPTED
      }
    }
    """
    with pytest.raises(DSLValidationError):
        validate(dsl)


def test_validate_rejects_unclosed_string():
    dsl = 'candidate "Wednesday Addams { classification { FULL_STACK_DEVELOPER: ACCEPTED } }'
    with pytest.raises(DSLValidationError):
        validate(dsl)


def test_validate_rejects_unknown_block():
    dsl = """
    candidate "Wednesday Addams" {
      unknown_block { value "test" }
      classification {
        FULL_STACK_DEVELOPER: ACCEPTED
      }
    }
    """
    with pytest.raises(DSLValidationError):
        validate(dsl)


def test_to_dsl_argument_type_validation():
    candidate = Candidate(name="Test")
    with pytest.raises(TypeError):
        to_dsl("not_a_candidate", [], [])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        to_dsl(candidate, "not_a_list", [])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        to_dsl(candidate, [], "not_a_list")  # type: ignore[arg-type]
