"""Stage 2 normalization helpers based on finite-state transducers."""

from __future__ import annotations
import re
from pyformlang.fst import FST

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
