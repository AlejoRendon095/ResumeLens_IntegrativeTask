"""Stage 2b - canonical ordering and filtering by profile (contract, Section 6.3).

Before a profile's automaton reads the normalized tokens, they are:

1. filtered: tokens that do not belong to any slot of the profile are
   dropped (decision D5), so extra skills such as Docker or Figma never make
   a Full Stack résumé fail;
2. sorted: primary key = index of the slot that contains the token,
   secondary key = position of the token inside that slot's ``any_of`` list.

The result is a function of the SET of tokens, so it does not depend on the
order in which the candidate wrote the skills (invariant 3). Duplicated
tokens are emitted once.

Example (Full Stack Developer)::

    sort_for_profile(["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT", "DOCKER"], full_stack)
    -> ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
"""

from __future__ import annotations

from collections.abc import Iterable


def canonical_order(profile: dict) -> dict[str, tuple[int, int]]:
    """``{token: (slot_index, position_in_any_of)}`` for every token of the profile."""
    return {
        token: (slot_index, position)
        for slot_index, slot in enumerate(profile["slots"])
        for position, token in enumerate(slot["any_of"])
    }


def filter_for_profile(tokens: Iterable[str], profile: dict) -> list[str]:
    """Tokens that belong to some slot of the profile, in their original order."""
    order = canonical_order(profile)
    return [token for token in tokens if token in order]


def sort_for_profile(tokens: Iterable[str], profile: dict) -> list[str]:
    """Filter and sort ``tokens`` into the sequence the profile automaton reads.

    The input is not modified; a new list is returned.
    """
    order = canonical_order(profile)
    kept = {token for token in tokens if token in order}
    return sorted(kept, key=order.__getitem__)


def discarded_for_profile(tokens: Iterable[str], profile: dict) -> list[str]:
    """Tokens removed by the filter (useful to explain a result), in original order."""
    order = canonical_order(profile)
    seen: set[str] = set()
    discarded: list[str] = []
    for token in tokens:
        if token not in order and token not in seen:
            seen.add(token)
            discarded.append(token)
    return discarded


__all__ = [
    "canonical_order",
    "discarded_for_profile",
    "filter_for_profile",
    "sort_for_profile",
]
