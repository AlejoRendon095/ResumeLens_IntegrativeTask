"""Professional profile configuration loader (contract, Section 7).

Profiles are data, not code: each one is a JSON file in ``profiles/`` and
every profile is processed by the same engine (sorting.py + recognition.py).
Adding or replacing a profile only requires a new JSON file.

Profile format::

    {
      "id": "FULL_STACK_DEVELOPER",          # UPPER_SNAKE_CASE, unique
      "display_name": "Full Stack Developer",
      "order": 1,                             # optional, position in the results
      "slots": [                              # ordered pattern positions
        {"category": "LANGUAGE", "any_of": ["JAVASCRIPT", "TYPESCRIPT"], "optional": false},
        ...
      ]
    }
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from resumelens.errors import ProfileConfigError
from resumelens.vocabulary import VocabularyEntry, default_vocabulary

# <repository root>/profiles
PROFILES_DIR = Path(__file__).resolve().parents[2] / "profiles"

ID_PATTERN = re.compile(r"[A-Z][A-Z_]*")


def validate_profile(
    raw: Any,
    source: str = "<profile>",
    vocabulary: dict[str, VocabularyEntry] | None = None,
) -> dict:
    """Check the rules of contract Section 7.3 and return a normalized copy.

    The returned dictionary always has the keys ``id``, ``display_name``,
    ``order`` and ``slots``; every slot has ``category``, ``any_of`` and
    ``optional``. The input is never mutated.
    """
    vocab = default_vocabulary() if vocabulary is None else vocabulary

    def fail(message: str) -> ProfileConfigError:
        return ProfileConfigError(f"{source}: {message}")

    if not isinstance(raw, dict):
        raise fail("a profile must be a JSON object.")

    # Rule 1: id is non-empty (uniqueness is checked across files in load_profiles).
    profile_id = raw.get("id")
    if not isinstance(profile_id, str) or not ID_PATTERN.fullmatch(profile_id):
        raise fail(f"'id' must be a non-empty UPPER_SNAKE_CASE string, got {profile_id!r}.")

    display_name = raw.get("display_name", profile_id)
    if not isinstance(display_name, str) or not display_name.strip():
        raise fail("'display_name' must be a non-empty string.")

    order = raw.get("order")
    if order is not None and (not isinstance(order, int) or isinstance(order, bool)):
        raise fail("'order' must be an integer when present.")

    # Rule 2: slots is non-empty.
    slots = raw.get("slots")
    if not isinstance(slots, list) or not slots:
        raise fail("'slots' must be a non-empty list.")

    normalized_slots: list[dict] = []
    owner: dict[str, int] = {}
    for index, slot in enumerate(slots):
        where = f"slot {index}"
        if not isinstance(slot, dict):
            raise fail(f"{where} must be an object.")
        category = slot.get("category")
        if not isinstance(category, str) or not category:
            raise fail(f"{where}: 'category' must be a non-empty string.")
        any_of = slot.get("any_of")
        if not isinstance(any_of, list) or not any_of:
            raise fail(f"{where}: 'any_of' must be a non-empty list of tokens.")
        optional = slot.get("optional", False)
        if not isinstance(optional, bool):
            raise fail(f"{where}: 'optional' must be true or false.")
        for token in any_of:
            # Rule 3: every token exists in the canonical vocabulary.
            if not isinstance(token, str) or token not in vocab:
                raise fail(f"{where}: {token!r} is not a canonical token.")
            # Rule 4: the any_of sets of different slots are pairwise disjoint.
            if token in owner:
                if owner[token] == index:
                    raise fail(f"{where}: token {token} is repeated.")
                raise fail(
                    f"token {token} appears in slots {owner[token]} and {index}; "
                    "the any_of sets must be disjoint."
                )
            owner[token] = index
        normalized_slots.append(
            {"category": category, "any_of": list(any_of), "optional": optional}
        )

    # Rule 5: at least one slot is non-optional.
    if all(slot["optional"] for slot in normalized_slots):
        raise fail("at least one slot must be non-optional.")

    return {
        "id": profile_id,
        "display_name": display_name,
        "order": order,
        "slots": normalized_slots,
    }


def load_profile(
    path: str | Path, vocabulary: dict[str, VocabularyEntry] | None = None
) -> dict:
    """Load and validate one profile file."""
    file_path = Path(path)
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProfileConfigError(f"Profile file not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise ProfileConfigError(f"{file_path.name}: invalid JSON: {exc}") from exc
    return validate_profile(raw, source=file_path.name, vocabulary=vocabulary)


def load_profiles(
    directory: str | Path | None = None,
    vocabulary: dict[str, VocabularyEntry] | None = None,
) -> list[dict]:
    """Load every ``*.json`` profile of ``directory`` (default: ``profiles/``).

    Profiles are returned sorted by their ``order`` key (profiles without it go
    last) and then by file name, so the result order is deterministic. This is
    the order of ``PipelineResult.classifications``.
    """
    folder = Path(directory) if directory is not None else PROFILES_DIR
    if not folder.is_dir():
        raise ProfileConfigError(f"Profiles directory not found: {folder}")

    profiles = [load_profile(path, vocabulary) for path in sorted(folder.glob("*.json"))]
    if not profiles:
        raise ProfileConfigError(f"No profile files (*.json) found in {folder}")

    # Rule 1: ids are unique across profiles.
    seen: set[str] = set()
    for profile in profiles:
        if profile["id"] in seen:
            raise ProfileConfigError(f"Duplicated profile id {profile['id']}.")
        seen.add(profile["id"])

    # sorted() is stable, so ties keep the file-name order.
    return sorted(
        profiles,
        key=lambda p: (p["order"] is None, p["order"] if p["order"] is not None else 0),
    )


def profile_alphabet(profile: dict) -> list[str]:
    """Tokens used by a profile, in slot order (the alphabet Σ of its automaton)."""
    return [token for slot in profile["slots"] for token in slot["any_of"]]


__all__ = [
    "PROFILES_DIR",
    "load_profile",
    "load_profiles",
    "profile_alphabet",
    "validate_profile",
]
