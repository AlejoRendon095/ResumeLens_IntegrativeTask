"""Scenario tests for Stages 2b and 3 through the complete pipeline.

The sample résumés of ``samples/`` are covered by ``test_integration.py``.
These scenarios target the behaviour of the profile automata themselves:
several tokens per slot, optional slots, aliases, duplicates, noise,
multi-profile acceptance and missing mandatory slots. Each résumé is a small
text that goes through extraction, normalization, sorting and recognition.

Scenario IDs (S2B-x / S3-x) match docs/test_cases.md, Section 4.
"""

import pytest

from resumelens.pipeline import run


def resume(skills: str, name: str = "Test Candidate") -> str:
    return (
        f"{name}\n"
        "test.candidate@example.com\n"
        "2 years of experience.\n"
        "Technical Skills:\n"
        f"{skills}\n"
    )


def accepted(skills: str) -> list[str]:
    return [c.profile_id for c in run(resume(skills)).classifications if c.accepted]


def sequence(skills: str, profile_id: str) -> list[str]:
    result = run(resume(skills))
    return next(c.sequence for c in result.classifications if c.profile_id == profile_id)


# --- Stage 2b: what each automaton reads -------------------------------------

def test_s2b_1_canonical_order_from_unsorted_resume():
    assert sequence("Git, MySQL, Django, Vue, TypeScript.", "FULL_STACK_DEVELOPER") == [
        "TYPESCRIPT", "VUE", "DJANGO", "MYSQL", "GIT",
    ]


def test_s2b_2_foreign_and_unknown_skills_are_not_read():
    # Docker belongs to DevOps, Figma is not in the vocabulary.
    skills = "TypeScript, Vue, Django, MySQL, Git, Docker, Figma."
    assert "DOCKER" not in sequence(skills, "FULL_STACK_DEVELOPER")
    assert run(resume(skills)).normalization.unrecognized == ["Figma"]
    assert "FULL_STACK_DEVELOPER" in accepted(skills)


def test_s2b_3_duplicated_aliases_become_one_symbol():
    # JS + Javascript -> one JAVASCRIPT, ReactJS + React.js -> one REACT
    skills = "JS, Javascript, ReactJS, React.js, Node.js, MongoDB, REST APIs, Git."
    assert sequence(skills, "FULL_STACK_DEVELOPER") == [
        "JAVASCRIPT", "REACT", "NODE_JS", "MONGODB", "REST_API", "GIT",
    ]


def test_s2b_4_same_resume_different_sequence_per_profile():
    skills = "Python, PostgreSQL, Spark, Git, Linux."
    assert sequence(skills, "DATA_ENGINEER") == ["PYTHON", "POSTGRESQL", "SPARK", "GIT"]
    assert sequence(skills, "DEVOPS_ENGINEER") == ["LINUX", "GIT"]


# --- Stage 3: acceptance ------------------------------------------------------

def test_s3_1_optional_slot_present_full_stack_with_rest():
    assert accepted("JS, React.js, Node.js, MongoDB, REST APIs, Git.") == ["FULL_STACK_DEVELOPER"]


def test_s3_2_lowercase_and_spaced_aliases_ml():
    assert accepted("tensor flow, py torch, sklearn, num py, python3, sql, git") == [
        "MACHINE_LEARNING_ENGINEER"
    ]


def test_s3_3_devops_with_alias_tokens():
    # Ubuntu -> LINUX, K8s -> KUBERNETES (optional slot used)
    assert accepted("Ubuntu, Git, CI/CD, Docker, K8s, AWS.") == ["DEVOPS_ENGINEER"]


def test_s3_4_data_engineer_with_both_optional_slots_skipped():
    assert accepted("Python, SQL, PySpark, Git.") == ["DATA_ENGINEER"]


def test_s3_5_one_resume_two_profiles():
    skills = "Python, Pandas, Scikit-learn, PostgreSQL, Spark, Airflow, Git."
    assert accepted(skills) == ["MACHINE_LEARNING_ENGINEER", "DATA_ENGINEER"]


# --- Stage 3: rejection -------------------------------------------------------

@pytest.mark.parametrize(
    "skills, missing",
    [
        ("JavaScript, React, Git.", "backend and database (Full Stack)"),
        ("Linux, Git, Docker, AWS.", "CI/CD (DevOps)"),
        ("Python, Pandas, SQL, Git.", "ML library (ML Engineer)"),
        ("Python, PostgreSQL, Airflow, Kafka, Git.", "processing engine (Data Engineer)"),
    ],
)
def test_s3_6_missing_mandatory_slot_is_rejected_everywhere(skills, missing):
    assert accepted(skills) == [], missing


def test_s3_7_resume_without_skills_section():
    text = "Nobody Special\nnobody@example.com\n1 year of experience.\n"
    result = run(text)
    assert all(not c.accepted for c in result.classifications)
    assert all(c.sequence == [] for c in result.classifications)
