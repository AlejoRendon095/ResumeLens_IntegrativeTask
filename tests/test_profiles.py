"""Tests for the profile configuration loader (contract, Section 7)."""

import copy
import json

import pytest

from resumelens.errors import ProfileConfigError
from resumelens.profiles import (
    load_profile,
    load_profiles,
    profile_alphabet,
    validate_profile,
)
from resumelens.vocabulary import is_canonical

VALID = {
    "id": "TEST_PROFILE",
    "display_name": "Test profile",
    "slots": [
        {"category": "LANGUAGE", "any_of": ["PYTHON"], "optional": False},
        {"category": "VERSION_CONTROL", "any_of": ["GIT"], "optional": True},
    ],
}


def _with(**changes):
    profile = copy.deepcopy(VALID)
    profile.update(changes)
    return profile


def _write(folder, name, data):
    (folder / name).write_text(json.dumps(data), encoding="utf-8")


# --- the four project profiles -----------------------------------------------

def test_project_profiles_load_in_contract_order():
    ids = [p["id"] for p in load_profiles()]
    assert ids == [
        "FULL_STACK_DEVELOPER",
        "MACHINE_LEARNING_ENGINEER",
        "DEVOPS_ENGINEER",
        "DATA_ENGINEER",
    ]


def test_project_profiles_only_use_canonical_tokens():
    for profile in load_profiles():
        assert all(is_canonical(token) for token in profile_alphabet(profile))


def test_full_stack_slot_order():
    full_stack = load_profiles()[0]
    assert [s["category"] for s in full_stack["slots"]] == [
        "LANGUAGE", "FRONTEND", "BACKEND", "DATABASE", "API", "VERSION_CONTROL",
    ]
    assert [s["optional"] for s in full_stack["slots"]] == [False, False, False, False, True, False]


def test_profile_alphabet_follows_slot_order():
    ml = load_profiles()[1]
    assert profile_alphabet(ml)[:3] == ["PYTHON", "PANDAS", "NUMPY"]


# --- validation rules (Section 7.3) ------------------------------------------

def test_valid_profile_is_normalized_and_not_mutated():
    original = copy.deepcopy(VALID)
    result = validate_profile(VALID)
    assert VALID == original
    assert result["order"] is None
    assert result["slots"][1]["optional"] is True


@pytest.mark.parametrize(
    "profile",
    [
        _with(id=""),                                    # rule 1: empty id
        _with(id="full stack"),                          # id not UPPER_SNAKE_CASE
        _with(slots=[]),                                 # rule 2: no slots
        _with(slots=[{"category": "X", "any_of": ["FIGMA"], "optional": False}]),   # rule 3
        _with(slots=[                                    # rule 4: overlapping slots
            {"category": "A", "any_of": ["SQL"], "optional": False},
            {"category": "B", "any_of": ["SQL", "MYSQL"], "optional": False},
        ]),
        _with(slots=[{"category": "A", "any_of": ["SQL", "SQL"], "optional": False}]),
        _with(slots=[{"category": "A", "any_of": ["GIT"], "optional": True}]),       # rule 5
        _with(slots=[{"category": "A", "any_of": [], "optional": False}]),
        _with(slots=[{"category": "A", "any_of": ["GIT"], "optional": "no"}]),
        _with(order="first"),
        ["not", "an", "object"],
    ],
)
def test_invalid_profiles_are_rejected(profile):
    with pytest.raises(ProfileConfigError):
        validate_profile(profile)


def test_duplicate_ids_across_files_are_rejected(tmp_path):
    _write(tmp_path, "a.json", VALID)
    _write(tmp_path, "b.json", VALID)
    with pytest.raises(ProfileConfigError):
        load_profiles(tmp_path)


def test_order_key_then_file_name(tmp_path):
    _write(tmp_path, "a.json", _with(id="NO_ORDER"))
    _write(tmp_path, "b.json", _with(id="SECOND", order=2))
    _write(tmp_path, "c.json", _with(id="FIRST", order=1))
    assert [p["id"] for p in load_profiles(tmp_path)] == ["FIRST", "SECOND", "NO_ORDER"]


def test_missing_directory_and_empty_directory(tmp_path):
    with pytest.raises(ProfileConfigError):
        load_profiles(tmp_path / "missing")
    with pytest.raises(ProfileConfigError):
        load_profiles(tmp_path)


def test_invalid_json_file(tmp_path):
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")
    with pytest.raises(ProfileConfigError):
        load_profile(tmp_path / "broken.json")
