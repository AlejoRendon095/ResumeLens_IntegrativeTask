"""Tests for Stage 2b: canonical ordering and filtering by profile (contract, Section 6.3)."""

import itertools

import pytest

from resumelens.profiles import load_profiles
from resumelens.sorting import (
    canonical_order,
    discarded_for_profile,
    filter_for_profile,
    sort_for_profile,
)

PROFILES = {p["id"]: p for p in load_profiles()}
FULL_STACK = PROFILES["FULL_STACK_DEVELOPER"]
ML = PROFILES["MACHINE_LEARNING_ENGINEER"]
DEVOPS = PROFILES["DEVOPS_ENGINEER"]
DATA = PROFILES["DATA_ENGINEER"]


def test_contract_example_full_stack():
    tokens = ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT", "DOCKER"]
    assert sort_for_profile(tokens, FULL_STACK) == [
        "JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT",
    ]


def test_assignment_sorting_example():
    # Résumé order: Git, NodeJS, JS, Postgres, React.js (assignment, Stage 2)
    tokens = ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]
    assert sort_for_profile(tokens, FULL_STACK) == [
        "JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT",
    ]


def test_secondary_key_is_position_inside_the_slot():
    tokens = ["TENSORFLOW", "NUMPY", "GIT", "SCIKIT_LEARN", "SQL", "PANDAS", "PYTHON"]
    assert sort_for_profile(tokens, ML) == [
        "PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT",
    ]


@pytest.mark.parametrize("profile", [FULL_STACK, ML, DEVOPS, DATA], ids=lambda p: p["id"])
def test_result_does_not_depend_on_input_order(profile):
    tokens = ["PYTHON", "GIT", "SQL", "REACT", "DOCKER", "SPARK"]
    expected = sort_for_profile(tokens, profile)
    for permutation in itertools.permutations(tokens):
        assert sort_for_profile(list(permutation), profile) == expected


def test_tokens_outside_the_profile_are_filtered():
    tokens = ["JAVASCRIPT", "REACT", "DOCKER", "GIT", "PYTORCH"]
    assert sort_for_profile(tokens, FULL_STACK) == ["JAVASCRIPT", "REACT", "GIT"]
    assert discarded_for_profile(tokens, FULL_STACK) == ["DOCKER", "PYTORCH"]


def test_filter_keeps_original_order():
    assert filter_for_profile(["GIT", "DOCKER", "REACT"], FULL_STACK) == ["GIT", "REACT"]


def test_duplicates_are_emitted_once():
    assert sort_for_profile(["GIT", "GIT", "JAVASCRIPT"], FULL_STACK) == ["JAVASCRIPT", "GIT"]


def test_empty_and_unrelated_inputs():
    assert sort_for_profile([], FULL_STACK) == []
    assert sort_for_profile(["PANDAS", "SPARK"], FULL_STACK) == []


def test_input_is_not_mutated():
    tokens = ["GIT", "JAVASCRIPT"]
    sort_for_profile(tokens, FULL_STACK)
    assert tokens == ["GIT", "JAVASCRIPT"]


def test_same_token_sorts_differently_per_profile():
    # GIT is the 2nd slot for DevOps but the last slot for Data Engineer.
    tokens = ["GIT", "PYTHON", "LINUX", "SQL", "SPARK", "AWS"]
    assert sort_for_profile(tokens, DEVOPS) == ["LINUX", "GIT", "AWS"]
    assert sort_for_profile(tokens, DATA) == ["PYTHON", "SQL", "SPARK", "GIT"]


def test_canonical_order_keys():
    order = canonical_order(FULL_STACK)
    assert order["JAVASCRIPT"] == (0, 0)
    assert order["TYPESCRIPT"] == (0, 1)
    assert order["GIT"] == (5, 0)
