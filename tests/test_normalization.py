"""Tests for Stage 2 normalization helpers."""
from __future__ import annotations
import pytest

from resumelens.normalization import (
    _apply_transducer,
    build_transducer,
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
