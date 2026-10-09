"""Tests for the equivalent automata and the contract invariants of Stage 3.

* the ε-NFA, its subset-construction DFA and the minimal DFA accept the
  same language for every profile;
* the 5-tuple exported for the documentation is consistent;
* invariants 3, 4, 5 and 7 of docs/contracts.md (Section 10).
"""

import copy
import itertools
import random

import pytest

from resumelens.profiles import load_profiles, profile_alphabet
from resumelens.recognition import (
    EPSILON,
    automaton_kind,
    automaton_tuple,
    build_dfa,
    build_enfa,
    build_minimal_dfa,
    classify,
    recognize,
)
from resumelens.sorting import sort_for_profile
from resumelens.vocabulary import canonical_tokens

PROFILES = load_profiles()
IDS = [p["id"] for p in PROFILES]


def _words(alphabet, max_length):
    for length in range(max_length + 1):
        yield from itertools.product(alphabet, repeat=length)


# --- equivalence of the three automata ---------------------------------------

@pytest.mark.parametrize("profile", PROFILES, ids=IDS)
def test_enfa_dfa_and_minimal_dfa_are_equivalent(profile):
    enfa, dfa, minimal = build_enfa(profile), build_dfa(profile), build_minimal_dfa(profile)
    assert enfa.is_equivalent_to(dfa)
    assert enfa.is_equivalent_to(minimal)


@pytest.mark.parametrize("profile", PROFILES, ids=IDS)
def test_same_answer_on_random_words(profile):
    # Brute-force check with random words over the profile alphabet (fixed seed).
    rng = random.Random(2026)
    alphabet = profile_alphabet(profile)
    enfa, minimal = build_enfa(profile), build_minimal_dfa(profile)
    for _ in range(300):
        word = [rng.choice(alphabet) for _ in range(rng.randint(0, 9))]
        assert enfa.accepts(word) == minimal.accepts(word)


def test_exhaustive_short_words_devops():
    profile = next(p for p in PROFILES if p["id"] == "DEVOPS_ENGINEER")
    enfa, minimal = build_enfa(profile), build_minimal_dfa(profile)
    for word in _words(profile_alphabet(profile), 6):
        assert enfa.accepts(word) == minimal.accepts(word)


# --- kinds and 5-tuples ------------------------------------------------------

@pytest.mark.parametrize("profile", PROFILES, ids=IDS)
def test_kinds(profile):
    assert automaton_kind(build_enfa(profile)) == "ε-NFA"
    assert automaton_kind(build_dfa(profile)) == "DFA"
    assert automaton_kind(build_minimal_dfa(profile)) == "DFA"


@pytest.mark.parametrize("profile", PROFILES, ids=IDS)
def test_enfa_tuple(profile):
    n = len(profile["slots"])
    t = automaton_tuple(build_enfa(profile), profile)
    assert t["kind"] == "ε-NFA"
    assert t["q0"] == "q0"
    assert t["F"] == [f"q{n}"]
    assert len(t["Q"]) == 2 * n + 1
    assert t["Sigma"] == profile_alphabet(profile)
    # one ε-transition per slot (leave it) plus one per optional slot (skip it)
    optional = sum(slot["optional"] for slot in profile["slots"])
    assert sum(1 for (_, a, _) in t["delta"] if a == EPSILON) == n + optional


@pytest.mark.parametrize("profile", PROFILES, ids=IDS)
def test_minimal_dfa_tuple_is_a_partial_function(profile):
    t = automaton_tuple(build_minimal_dfa(profile), profile)
    assert t["kind"] == "DFA"
    assert t["q0"] == "D0"
    pairs = [(p, a) for (p, a, _) in t["delta"]]
    assert len(pairs) == len(set(pairs))          # at most one target per (state, symbol)
    assert all(a != EPSILON for (_, a, _) in t["delta"])
    assert set(t["F"]) <= set(t["Q"])


def test_full_stack_minimal_dfa_size():
    # 6 slots -> D0 (start) + one state per slot = 7 states
    full_stack = PROFILES[0]
    assert len(automaton_tuple(build_minimal_dfa(full_stack), full_stack)["Q"]) == 7


# --- contract invariants (Section 10) ----------------------------------------

RESUMES = [
    ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
    ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"],
    ["LINUX", "GIT", "CI_CD", "DOCKER", "KUBERNETES", "AWS"],
    ["PYTHON", "SQL", "SPARK", "AIRFLOW", "KAFKA", "GIT"],
    ["JAVASCRIPT", "REACT", "DOCKER", "GIT"],
]


@pytest.mark.parametrize("tokens", RESUMES)
def test_invariant_3_order_of_skills_does_not_matter(tokens):
    expected = [r.accepted for r in classify(tokens, PROFILES)]
    rng = random.Random(7)
    for _ in range(25):
        shuffled = tokens[:]
        rng.shuffle(shuffled)
        assert [r.accepted for r in classify(shuffled, PROFILES)] == expected


@pytest.mark.parametrize("profile", PROFILES, ids=IDS)
def test_invariant_4_unrelated_skill_does_not_change_result(profile):
    outside = [t for t in canonical_tokens() if t not in profile_alphabet(profile)]
    for tokens in RESUMES:
        before = recognize(sort_for_profile(tokens, profile), profile)
        for extra in outside:
            after = recognize(sort_for_profile(tokens + [extra], profile), profile)
            assert after == before


def test_invariant_5_one_result_per_loaded_profile():
    for tokens in RESUMES:
        assert len(classify(tokens, PROFILES)) == len(PROFILES) == 4


def test_invariant_7_inputs_are_not_mutated():
    tokens = ["GIT", "JAVASCRIPT", "REACT"]
    profiles = copy.deepcopy(PROFILES)
    classify(tokens, profiles)
    assert tokens == ["GIT", "JAVASCRIPT", "REACT"]
    assert profiles == PROFILES
