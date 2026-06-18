"""Tests for the concept prerequisite graph (services/concepts.py).

This graph drives recursive remediation — when a student keeps failing a
concept it is decomposed into the fundamentals beneath it. The walks are
recursive, so the cycle/dedup guarantees matter.
"""
from __future__ import annotations

from app.services import concepts


def test_prereqs_and_chapter_lookup():
    assert concepts.prereqs_of("Gauss's Law") == ["Electric Field", "Vector Area", "Dot Product"]
    assert concepts.chapter_of("Gauss's Law") == "electrostatics"
    assert concepts.is_known_concept("Gauss's Law") is True


def test_unknown_concept_returns_empty():
    assert concepts.prereqs_of("Quantum Gravity") == []
    assert concepts.chapter_of("Quantum Gravity") is None
    assert concepts.is_known_concept("Quantum Gravity") is False


def test_decompose_is_fundamentals_first_and_deduped():
    chain = concepts.decompose("Gauss's Law")
    # The deepest fundamental must appear, and exactly once.
    assert "Vector Algebra" in chain
    assert chain.count("Vector Algebra") == 1
    # A fundamental must be listed before a concept that depends on it.
    assert chain.index("Vector Algebra") < chain.index("Dot Product")


def test_decompose_leaf_concept_has_no_prereqs():
    assert concepts.decompose("Vector Algebra") == []


def test_remediation_collects_weak_prerequisites():
    weak = {"Dot Product", "Vector Algebra"}
    steps = concepts.remediation_steps("Gauss's Law", lambda c: c in weak, max_steps=4)
    assert "Dot Product" in steps
    assert "Vector Algebra" in steps
    assert len(steps) <= 4
    # fundamentals-first ordering preserved
    assert steps.index("Vector Algebra") < steps.index("Dot Product")


def test_remediation_falls_back_to_immediate_prereqs_when_no_weakness():
    # Student is weak in nothing -> suggest the immediate foundations anyway.
    steps = concepts.remediation_steps("Gauss's Law", lambda c: False)
    assert steps == ["Electric Field", "Vector Area", "Dot Product"][: len(steps)]
    assert len(steps) >= 1


def test_remediation_respects_max_steps():
    steps = concepts.remediation_steps("Gauss's Law", lambda c: True, max_steps=2)
    assert len(steps) == 2


def test_downstream_count_ranks_blocking_chapters():
    # vectors <- electrostatics <- current ; magnetism depends on electrostatics
    chain = {
        "vectors": None,
        "electrostatics": "vectors",
        "current": "electrostatics",
        "magnetism": "electrostatics",
    }
    # vectors blocks everything below it (3 chapters)
    assert concepts.downstream_count(chain, "vectors") == 3
    # electrostatics blocks current + magnetism
    assert concepts.downstream_count(chain, "electrostatics") == 2
    # a leaf blocks nothing
    assert concepts.downstream_count(chain, "current") == 0


def test_downstream_count_survives_cycle():
    # Defensive: a malformed cyclic chain must not hang (guard caps the walk).
    chain = {"a": "b", "b": "a"}
    assert concepts.downstream_count(chain, "a") == 1
