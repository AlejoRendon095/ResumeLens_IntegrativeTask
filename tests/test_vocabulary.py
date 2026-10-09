"""Tests for the shared canonical vocabulary (contract, Sections 3 and 4)."""

import json

import pytest

from resumelens.errors import VocabularyError
from resumelens.vocabulary import (
    ALIAS_PATTERN,
    TOKEN_PATTERN,
    alias_index,
    canonical_tokens,
    default_vocabulary,
    is_canonical,
    load_vocabulary,
    parse_vocabulary,
    token_category,
)


def _write(tmp_path, data):
    path = tmp_path / "vocabulary.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# --- project vocabulary -------------------------------------------------------

def test_project_vocabulary_loads():
    vocab = default_vocabulary()
    assert "JAVASCRIPT" in vocab
    assert vocab["SCIKIT_LEARN"].category == "ML_LIB"


def test_tokens_belong_to_output_alphabet_gamma():
    for token in canonical_tokens():
        assert TOKEN_PATTERN.fullmatch(token), token


def test_aliases_belong_to_input_alphabet_sigma():
    for alias in alias_index():
        assert ALIAS_PATTERN.fullmatch(alias), alias


@pytest.mark.parametrize(
    "alias, token",
    [
        ("js", "JAVASCRIPT"),
        ("react.js", "REACT"),
        ("nodejs", "NODE_JS"),
        ("postgres", "POSTGRESQL"),
        ("scikit learn", "SCIKIT_LEARN"),
        ("sklearn", "SCIKIT_LEARN"),
        ("tensor flow", "TENSORFLOW"),
        ("py torch", "PYTORCH"),
        ("git", "GIT"),
    ],
)
def test_assignment_examples_are_covered(alias, token):
    assert alias_index()[alias] == token


def test_java_is_not_a_prefix_alias_of_javascript():
    index = alias_index()
    assert index["java"] == "JAVA"
    assert index["javascript"] == "JAVASCRIPT"


def test_helpers():
    assert is_canonical("GIT")
    assert not is_canonical("FIGMA")
    assert token_category("DOCKER") == "CONTAINER"
    with pytest.raises(VocabularyError):
        token_category("FIGMA")


# --- validation rules (Section 3.2) ------------------------------------------

def test_missing_file_raises(tmp_path):
    with pytest.raises(VocabularyError):
        load_vocabulary(tmp_path / "nope.json")


def test_malformed_json_raises(tmp_path):
    path = tmp_path / "vocabulary.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(VocabularyError):
        load_vocabulary(path)


def test_valid_custom_file(tmp_path):
    path = _write(tmp_path, {"tokens": {"GIT": {"category": "VERSION_CONTROL", "aliases": ["git"]}}})
    assert canonical_tokens(load_vocabulary(path)) == ["GIT"]


@pytest.mark.parametrize(
    "tokens",
    [
        {},                                                                 # empty vocabulary
        {"git": {"category": "VERSION_CONTROL", "aliases": ["git"]}},       # token not in Γ
        {"NODE.JS": {"category": "BACKEND", "aliases": ["node"]}},          # token not in Γ
        {"GIT": {"category": "VERSION_CONTROL", "aliases": []}},            # no aliases
        {"GIT": {"category": "", "aliases": ["git"]}},                      # bad category
        {"GIT": {"category": "VERSION_CONTROL", "aliases": ["Git"]}},       # not preprocessed
        {"GIT": {"category": "VERSION_CONTROL", "aliases": [" git"]}},      # not stripped
        {"CPP": {"category": "LANGUAGE", "aliases": ["c++"]}},              # char outside Σ
        {                                                                   # alias in two rows
            "JAVA": {"category": "LANGUAGE", "aliases": ["java"]},
            "JAVASCRIPT": {"category": "LANGUAGE", "aliases": ["java"]},
        },
    ],
)
def test_invalid_vocabularies_are_rejected(tokens):
    with pytest.raises(VocabularyError):
        parse_vocabulary({"tokens": tokens})


def test_document_without_tokens_object_is_rejected():
    with pytest.raises(VocabularyError):
        parse_vocabulary(["GIT"])
