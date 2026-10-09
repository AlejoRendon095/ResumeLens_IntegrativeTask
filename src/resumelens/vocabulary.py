"""Canonical vocabulary loader (contract, Sections 3 and 4).

The canonical vocabulary is the single source of truth shared by:

* Stage 2 (transducers): the aliases are the input strings and the canonical
  token is the output, so the set of tokens is the output alphabet Γ;
* Stage 3 (automata): every canonical token is ONE symbol of the input
  alphabet Σ (decision D3).

Neither stage may hard-code token names: they read them through this module.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from resumelens.errors import VocabularyError

VOCABULARY_PATH = Path(__file__).with_name("vocabulary.json")

# Output alphabet of the transducers: Γ = {A-Z, _} (decision D2).
TOKEN_PATTERN = re.compile(r"[A-Z][A-Z_]*")
# Categories follow the same UPPER_SNAKE_CASE convention.
CATEGORY_PATTERN = re.compile(r"[A-Z][A-Z_]*")
# Input alphabet of the transducers after preprocessing:
# Σ = {a-z, 0-9, space, '.', '-', '/'} (decision D2). Aliases are stored
# already preprocessed: no leading/trailing spaces and no double spaces.
ALIAS_PATTERN = re.compile(r"[a-z0-9./\-]+(?: [a-z0-9./\-]+)*")


@dataclass(frozen=True)
class VocabularyEntry:
    """One canonical token with its category and accepted aliases."""

    token: str
    category: str
    aliases: tuple[str, ...]


def load_vocabulary(path: str | Path | None = None) -> dict[str, VocabularyEntry]:
    """Load and validate the vocabulary file.

    Returns an insertion-ordered ``{token: VocabularyEntry}`` dictionary that
    follows the order of the JSON file. Raises ``VocabularyError`` when the
    file is missing, is not valid JSON, or violates contract Section 3.2.
    """
    file_path = Path(path) if path is not None else VOCABULARY_PATH
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VocabularyError(f"Vocabulary file not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise VocabularyError(f"Vocabulary file is not valid JSON: {file_path}: {exc}") from exc
    return parse_vocabulary(raw)


def parse_vocabulary(raw: object) -> dict[str, VocabularyEntry]:
    """Validate an already-decoded vocabulary document (see ``vocabulary.json``)."""
    if not isinstance(raw, dict) or not isinstance(raw.get("tokens"), dict):
        raise VocabularyError("Vocabulary must be an object with a 'tokens' object.")
    tokens = raw["tokens"]
    if not tokens:
        raise VocabularyError("Vocabulary must define at least one token.")

    entries: dict[str, VocabularyEntry] = {}
    alias_owner: dict[str, str] = {}
    for token, spec in tokens.items():
        if not isinstance(token, str) or not TOKEN_PATTERN.fullmatch(token):
            raise VocabularyError(f"Invalid canonical token {token!r}: must match [A-Z][A-Z_]*.")
        if not isinstance(spec, dict):
            raise VocabularyError(f"Token {token}: specification must be an object.")
        category = spec.get("category")
        if not isinstance(category, str) or not CATEGORY_PATTERN.fullmatch(category):
            raise VocabularyError(f"Token {token}: invalid category {category!r}.")
        aliases = spec.get("aliases")
        if not isinstance(aliases, list) or not aliases:
            raise VocabularyError(f"Token {token}: 'aliases' must be a non-empty list.")
        for alias in aliases:
            if not isinstance(alias, str) or not ALIAS_PATTERN.fullmatch(alias):
                raise VocabularyError(
                    f"Token {token}: alias {alias!r} is not a preprocessed string over "
                    "{a-z, 0-9, space, '.', '-', '/'}."
                )
            # Rule 2: an alias maps to exactly one token.
            if alias in alias_owner:
                raise VocabularyError(
                    f"Alias {alias!r} is declared for both {alias_owner[alias]} and {token}."
                )
            alias_owner[alias] = token
        entries[token] = VocabularyEntry(token, category, tuple(aliases))
    return entries


@lru_cache(maxsize=1)
def default_vocabulary() -> dict[str, VocabularyEntry]:
    """The project vocabulary (``vocabulary.json``), loaded once and cached."""
    return load_vocabulary()


def canonical_tokens(vocabulary: dict[str, VocabularyEntry] | None = None) -> list[str]:
    """Canonical tokens in file order: Γ of the transducers = Σ of the automata."""
    vocab = default_vocabulary() if vocabulary is None else vocabulary
    return list(vocab)


def is_canonical(token: str, vocabulary: dict[str, VocabularyEntry] | None = None) -> bool:
    """True if ``token`` belongs to the canonical vocabulary."""
    vocab = default_vocabulary() if vocabulary is None else vocabulary
    return token in vocab


def token_category(token: str, vocabulary: dict[str, VocabularyEntry] | None = None) -> str:
    """Category of a canonical token. Raises ``VocabularyError`` if unknown."""
    vocab = default_vocabulary() if vocabulary is None else vocabulary
    try:
        return vocab[token].category
    except KeyError as exc:
        raise VocabularyError(f"Unknown canonical token {token!r}.") from exc


def alias_index(vocabulary: dict[str, VocabularyEntry] | None = None) -> dict[str, str]:
    """``{alias: token}`` lookup table (useful for tests and documentation)."""
    vocab = default_vocabulary() if vocabulary is None else vocabulary
    return {alias: entry.token for entry in vocab.values() for alias in entry.aliases}


__all__ = [
    "ALIAS_PATTERN",
    "TOKEN_PATTERN",
    "VOCABULARY_PATH",
    "VocabularyEntry",
    "alias_index",
    "canonical_tokens",
    "default_vocabulary",
    "is_canonical",
    "load_vocabulary",
    "parse_vocabulary",
    "token_category",
]
