"""Tests for the diagram generator of the Stage 3 automata."""

import pytest

from resumelens.diagrams import export_all, to_dot, to_mermaid, tuple_markdown
from resumelens.profiles import load_profiles
from resumelens.recognition import automaton_tuple, build_enfa, build_minimal_dfa

PROFILES = load_profiles()


@pytest.mark.parametrize("builder", [build_enfa, build_minimal_dfa])
@pytest.mark.parametrize("profile", PROFILES, ids=[p["id"] for p in PROFILES])
def test_every_transition_is_drawn(profile, builder):
    spec = automaton_tuple(builder(profile), profile)
    mermaid, dot = to_mermaid(spec), to_dot(spec)
    for source, symbol, target in spec["delta"]:
        assert symbol in mermaid and symbol in dot
        assert f"{source} --" in mermaid
        assert f'"{source}" -> "{target}"' in dot


def test_initial_and_accepting_states_are_marked():
    profile = PROFILES[0]
    spec = automaton_tuple(build_enfa(profile), profile)
    mermaid, dot = to_mermaid(spec), to_dot(spec)
    final = spec["F"][0]
    assert "start(( )) --> q0" in mermaid
    assert f"{final}((({final})))" in mermaid
    assert f'"{final}" [shape=doublecircle]' in dot
    assert 'start -> "q0"' in dot


def test_parallel_transitions_are_merged():
    profile = PROFILES[0]
    spec = automaton_tuple(build_minimal_dfa(profile), profile)
    assert '"JAVASCRIPT | TYPESCRIPT"' in to_mermaid(spec)


def test_tuple_markdown_lists_the_five_components():
    profile = PROFILES[1]
    text = tuple_markdown(automaton_tuple(build_enfa(profile), profile))
    for part in ("**Q**", "**Σ**", "**q0**", "**F**", "| State | Symbol | Next state |"):
        assert part in text


def test_export_all_writes_every_file(tmp_path):
    written = export_all(tmp_path)
    names = {path.name for path in written}
    for profile in PROFILES:
        stem = profile["id"].lower()
        for kind in ("enfa", "dfa"):
            assert f"{stem}_{kind}.mmd" in names
            assert f"{stem}_{kind}.dot" in names
    assert "automata.md" in names
    index = (tmp_path / "automata.md").read_text(encoding="utf-8")
    assert index.count("```mermaid") == 2 * len(PROFILES)
