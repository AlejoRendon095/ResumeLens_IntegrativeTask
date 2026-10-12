"""Tests for Stage 3: qualification pattern recognition (contract, Section 6.4)."""

import pytest

from resumelens.models import ProfileResult
from resumelens.profiles import load_profiles
from resumelens.recognition import build_enfa, classify, recognize

PROFILES = load_profiles()
BY_ID = {p["id"]: p for p in PROFILES}
FULL_STACK = BY_ID["FULL_STACK_DEVELOPER"]
ML = BY_ID["MACHINE_LEARNING_ENGINEER"]
DEVOPS = BY_ID["DEVOPS_ENGINEER"]
DATA = BY_ID["DATA_ENGINEER"]


def accepted_ids(tokens):
    return [r.profile_id for r in classify(tokens, PROFILES) if r.accepted]


# --- worked examples of the contract and the assignment ----------------------

def test_contract_classify_example():
    tokens = ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "POSTGRESQL", "GIT"]
    assert classify(tokens, PROFILES) == [
        # POSTGRESQL and GIT belong to Full Stack slots, so they stay in its sequence.
        ProfileResult("FULL_STACK_DEVELOPER", ["POSTGRESQL", "GIT"], False),
        ProfileResult(
            "MACHINE_LEARNING_ENGINEER",
            ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "POSTGRESQL", "GIT"],
            True,
        ),
        ProfileResult("DEVOPS_ENGINEER", ["GIT"], False),
        ProfileResult("DATA_ENGINEER", ["PYTHON", "POSTGRESQL", "GIT"], False),
    ]


def test_wednesday_addams_is_full_stack():
    # JS, React.js, NodeJS, Postgres, Git -> REST_API slot is skipped (optional)
    tokens = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert accepted_ids(tokens) == ["FULL_STACK_DEVELOPER"]


def test_out_of_order_resume_is_still_full_stack():
    tokens = ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]
    result = classify(tokens, PROFILES)[0]
    assert result.sequence == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert result.accepted


def test_mary_jane_watson_is_ml_engineer():
    tokens = ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]
    assert accepted_ids(tokens) == ["MACHINE_LEARNING_ENGINEER"]


def test_assignment_stage3_example():
    # PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT -> MACHINE_LEARNING_ENGINEER: ACCEPTED
    assert recognize(["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"], ML)


def test_rejection_and_noise_example():
    # JS, React.js, Docker, Figma, Git: no backend and no database
    result = classify(["JAVASCRIPT", "REACT", "DOCKER", "GIT"], PROFILES)[0]
    assert result.sequence == ["JAVASCRIPT", "REACT", "GIT"]
    assert not result.accepted


# --- slot semantics (decision D7) --------------------------------------------

def test_several_tokens_of_the_same_slot():
    assert recognize(["TYPESCRIPT", "REACT", "VUE", "NODE_JS", "DJANGO", "MYSQL", "GIT"], FULL_STACK)


def test_optional_slot_may_be_present_or_absent():
    base = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL"]
    assert recognize(base + ["GIT"], FULL_STACK)
    assert recognize(base + ["REST_API", "GIT"], FULL_STACK)


@pytest.mark.parametrize(
    "missing",
    ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
)
def test_missing_mandatory_slot_is_rejected(missing):
    sequence = [t for t in ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"] if t != missing]
    assert not recognize(sequence, FULL_STACK)


def test_automaton_alone_requires_slot_order():
    # The automaton reads the order fixed by Stage 2b; an unsorted word is not in L.
    assert not recognize(["REACT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL", "GIT"], FULL_STACK)


def test_empty_sequence_is_rejected_by_every_profile():
    assert all(not r.accepted for r in classify([], PROFILES))


def test_two_optional_slots_in_a_row():
    base = ["PYTHON", "SQL", "SPARK"]
    assert recognize(base + ["GIT"], DATA)
    assert recognize(base + ["AIRFLOW", "GIT"], DATA)
    assert recognize(base + ["KAFKA", "GIT"], DATA)
    assert recognize(base + ["AIRFLOW", "KAFKA", "GIT"], DATA)


def test_devops_profile():
    tokens = ["AWS", "DOCKER", "GIT", "LINUX", "CI_CD"]
    assert "DEVOPS_ENGINEER" in accepted_ids(tokens)
    assert "DEVOPS_ENGINEER" not in accepted_ids(["LINUX", "GIT", "DOCKER", "AWS"])  # no CI/CD


# --- multi-profile behaviour (decision D8) -----------------------------------

def test_one_resume_can_satisfy_several_profiles():
    tokens = [
        "PYTHON", "PANDAS", "SCIKIT_LEARN", "POSTGRESQL", "GIT",
        "SPARK", "AIRFLOW",
    ]
    assert accepted_ids(tokens) == ["MACHINE_LEARNING_ENGINEER", "DATA_ENGINEER"]


def test_one_result_per_profile_in_order():
    results = classify(["GIT"], PROFILES)
    assert [r.profile_id for r in results] == [p["id"] for p in PROFILES]


def test_classify_uses_project_profiles_by_default():
    assert len(classify(["GIT"])) == 4


# --- structure of the automaton ----------------------------------------------

def test_enfa_structure():
    enfa = build_enfa(FULL_STACK)
    n = len(FULL_STACK["slots"])
    assert len(enfa.states) == 2 * n + 1          # q0..qn and p0..p(n-1)
    assert {s.value for s in enfa.start_states} == {"q0"}
    assert {s.value for s in enfa.final_states} == {f"q{n}"}
    assert not enfa.is_deterministic()            # it has ε-transitions
