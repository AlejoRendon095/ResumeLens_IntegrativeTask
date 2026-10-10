"""Stage 2 normalization helpers based on finite-state transducers."""

from __future__ import annotations

from functools import lru_cache
import re

from pyformlang.fst import FST

from resumelens.models import NormalizationResult
from resumelens.vocabulary import default_vocabulary

INPUT_ALPHABET = frozenset("abcdefghijklmnopqrstuvwxyz0123456789 .-/")

def preprocess(raw: str) -> str:
    """Convert a raw skill spelling to the vocabulary's input format."""
    clean = raw.strip().casefold()
    clean = re.sub(r"\s+", " ", clean)
    clean = clean.rstrip(",;:")
    if clean.endswith("."):
        clean = clean[:-1]
    return clean

def build_transducer(canonical: str, aliases: list[str]) -> FST:
    """Build one transducer mapping every alias to ``canonical``."""
    transducer = FST()
    transducer.add_start_state(0)
    next_state = 1

    for alias in aliases:
        state = 0
        for index, character in enumerate(alias):
            destination = next_state
            next_state += 1
            # Each alias becomes a path; only its final edge emits the token.
            output = list(canonical) if index == len(alias) - 1 else []
            transducer.add_transition(state, character, destination, output)
            state = destination
        transducer.add_final_state(state)

    return transducer

def _apply_transducer(transducer: FST, preprocessed: str) -> str | None:
    """Return the transducer output for a complete input path, if one exists."""
    if any(character not in INPUT_ALPHABET for character in preprocessed):
        return None

    outputs = list(transducer.translate(preprocessed))
    if len(outputs) != 1:
        return None
    return "".join(str(symbol) for symbol in outputs[0])


@lru_cache(maxsize=1)
def _transducers() -> tuple[tuple[str, FST], ...]:
    """Build and retain one transducer for each vocabulary token."""
    return tuple(
        (entry.token, build_transducer(entry.token, list(entry.aliases)))
        for entry in default_vocabulary().values()
    )


def normalize(raw_skills: list[str] | tuple[str, ...]) -> NormalizationResult:
    """Map extracted skill spellings to canonical vocabulary tokens."""
    if not isinstance(raw_skills, (list, tuple)) or not all(
        isinstance(raw, str) for raw in raw_skills
    ):
        raise TypeError("raw_skills must be a list or tuple of strings")

    tokens: list[str] = []
    mapping: dict[str, str] = {}
    unrecognized: list[str] = []

    for raw in raw_skills:
        preprocessed = preprocess(raw)
        matches = [
            token
            for token, transducer in _transducers()
            if _apply_transducer(transducer, preprocessed) == token
        ]
        if len(matches) != 1:
            if raw not in unrecognized:
                unrecognized.append(raw)
            continue

        canonical = matches[0]
        mapping[raw] = canonical
        if canonical not in tokens:
            tokens.append(canonical)

    return NormalizationResult(
        tokens=tokens,
        mapping=mapping,
        unrecognized=unrecognized,
    )
