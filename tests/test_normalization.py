"""Tests for Stage 2 normalization helpers."""
from __future__ import annotations
import pytest

from resumelens.normalization import (
    _apply_transducer,
    build_transducer,
    normalize,
    preprocess,
)
from resumelens.vocabulary import load_vocabulary

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  JS ", "js"),
        ("React.js,", "react.js"),
        ("Node  JS", "node js"),
        ("Scikit-learn.", "scikit-learn"),
        ("node.js", "node.js"),
        ("", ""),
    ],
)

def test_preprocess(raw: str, expected: str) -> None:
    assert preprocess(raw) == expected

def test_javascript_aliases() -> None:
    transducer = build_transducer(
        "JAVASCRIPT", ["js", "javascript", "java script"]
    )
    for alias in ("js", "javascript", "java script"):
        assert _apply_transducer(transducer, alias) == "JAVASCRIPT"

def test_whole_string_matching() -> None:
    java = build_transducer("JAVA", ["java"])
    javascript = build_transducer("JAVASCRIPT", ["javascript"])

    assert _apply_transducer(java, "java") == "JAVA"
    assert _apply_transducer(javascript, "java") is None

@pytest.mark.parametrize(
    ("canonical", "aliases"),
    [
        ("REACT", ["react", "react.js", "reactjs", "react js"]),
        ("SCIKIT_LEARN", ["sklearn", "scikit learn", "scikit-learn"]),
        ("CI_CD", ["ci/cd"]),
    ],
)

def test_required_aliases(canonical: str, aliases: list[str]) -> None:
    transducer = build_transducer(canonical, aliases)
    for alias in aliases:
        assert _apply_transducer(transducer, alias) == canonical

def test_unknown_and_unsupported_inputs_are_unrecognized() -> None:
    transducer = build_transducer("NODE_JS", ["node.js"])

    assert _apply_transducer(transducer, "figma") is None
    assert _apply_transducer(transducer, "") is None
    assert _apply_transducer(transducer, "c#") is None
    assert _apply_transducer(transducer, "node@js") is None

def test_every_vocabulary_alias_maps_to_its_token() -> None:
    vocabulary = load_vocabulary()

    for entry in vocabulary.values():
        transducer = build_transducer(entry.token, list(entry.aliases))
        for alias in entry.aliases:
            assert _apply_transducer(transducer, preprocess(alias)) == entry.token

def test_calls_are_repeatable_and_do_not_mutate_inputs() -> None:
    aliases = ["react", "react.js"]
    original_aliases = aliases.copy()
    transducer = build_transducer("REACT", aliases)

    assert _apply_transducer(transducer, "react.js") == "REACT"
    assert _apply_transducer(transducer, "react.js") == "REACT"
    assert aliases == original_aliases


def test_normalize_required_skills() -> None:
    result = normalize(["JS", "React.js", "NodeJS", "Postgres", "Git"])

    assert result.tokens == [
        "JAVASCRIPT",
        "REACT",
        "NODE_JS",
        "POSTGRESQL",
        "GIT",
    ]
    assert result.mapping == {
        "JS": "JAVASCRIPT",
        "React.js": "REACT",
        "NodeJS": "NODE_JS",
        "Postgres": "POSTGRESQL",
        "Git": "GIT",
    }
    assert result.unrecognized == []


def test_normalize_preserves_first_appearance_order() -> None:
    result = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"])

    assert result.tokens == ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]


def test_normalize_deduplicates_tokens_but_keeps_mapping_keys() -> None:
    result = normalize(["JS", "Javascript", "js"])

    assert result.tokens == ["JAVASCRIPT"]
    assert result.mapping == {
        "JS": "JAVASCRIPT",
        "Javascript": "JAVASCRIPT",
        "js": "JAVASCRIPT",
    }
    assert result.unrecognized == []


def test_normalize_tracks_unique_unknown_surface_strings() -> None:
    result = normalize(["JS", "Figma", "Git", "Figma", "c#"])

    assert result.tokens == ["JAVASCRIPT", "GIT"]
    assert result.unrecognized == ["Figma", "c#"]


def test_normalize_unknown_characters_and_empty_strings() -> None:
    result = normalize(["c#", "", "node@js"])

    assert result.tokens == []
    assert result.mapping == {}
    assert result.unrecognized == ["c#", "", "node@js"]


def test_normalize_preserves_surface_keys() -> None:
    result = normalize(["  React.js, ", "SCIKIT LEARN", "ci/cd"])

    assert result.tokens == ["REACT", "SCIKIT_LEARN", "CI_CD"]
    assert result.mapping == {
        "  React.js, ": "REACT",
        "SCIKIT LEARN": "SCIKIT_LEARN",
        "ci/cd": "CI_CD",
    }


def test_normalize_empty_and_vocabulary_aliases() -> None:
    assert normalize([]).tokens == []

    for entry in load_vocabulary().values():
        for alias in entry.aliases:
            assert normalize([alias]).tokens == [entry.token]


@pytest.mark.parametrize("raw_skills", [None, "JS", [1, 2]])
def test_normalize_rejects_invalid_argument_types(raw_skills: object) -> None:
    with pytest.raises(TypeError, match="list or tuple of strings"):
        normalize(raw_skills)  # type: ignore[arg-type]


def test_normalize_invariants_and_input_immutability() -> None:
    raw_skills = ["JS", "Figma", "Figma", "React.js", "c#"]
    original = raw_skills.copy()

    first = normalize(raw_skills)
    second = normalize(raw_skills)

    assert raw_skills == original
    assert first == second
    assert set(first.mapping) | set(first.unrecognized) == set(raw_skills)
    assert set(first.mapping).isdisjoint(first.unrecognized)
