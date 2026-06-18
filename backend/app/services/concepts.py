"""Concept prerequisite graph: the spine of the dynamic curriculum.

The JEE syllabus (subjects/chapters) is fixed, but *progression* is adaptive.
When a student repeatedly fails a concept, we recursively decompose it into the
smaller prerequisite concepts that underpin it, point them at the foundation
that teaches each, and only then climb back up.

Each node maps a concept to the chapter that teaches it and the concepts it
depends on. Concepts not in the graph fall back to chapter-level prerequisites.
"""
from __future__ import annotations

from typing import Callable

# concept -> {"chapter": <chapter-slug>, "prereqs": [concept, ...]}
CONCEPT_GRAPH: dict[str, dict] = {
    # ---- Electrostatics chain (the canonical example) ----
    "Gauss's Law": {"chapter": "electrostatics", "prereqs": ["Electric Field", "Vector Area", "Dot Product"]},
    "Electric Field": {"chapter": "electrostatics", "prereqs": ["Coulomb's Law"]},
    "Electric Potential": {"chapter": "electrostatics", "prereqs": ["Electric Field"]},
    "Capacitor Energy": {"chapter": "electrostatics", "prereqs": ["Electric Potential"]},
    "Coulomb's Law": {"chapter": "electrostatics", "prereqs": ["Vector Algebra"]},
    # ---- Vectors (fundamentals the electrostatics chain decomposes into) ----
    "Vector Area": {"chapter": "vectors", "prereqs": ["Cross Product", "Magnitude"]},
    "Dot Product": {"chapter": "vectors", "prereqs": ["Vector Algebra"]},
    "Cross Product": {"chapter": "vectors", "prereqs": ["Vector Algebra"]},
    "Cross Product Properties": {"chapter": "vectors", "prereqs": ["Cross Product"]},
    "Magnitude": {"chapter": "vectors", "prereqs": ["Vector Algebra"]},
    "Vector Algebra": {"chapter": "vectors", "prereqs": []},
    # ---- Downstream of electrostatics ----
    "Ohm's Law": {"chapter": "current-electricity", "prereqs": ["Electric Field", "Electric Potential"]},
    "Resistor Combinations": {"chapter": "current-electricity", "prereqs": ["Ohm's Law"]},
    "Electrical Power": {"chapter": "current-electricity", "prereqs": ["Ohm's Law"]},
    "Kirchhoff's Laws": {"chapter": "current-electricity", "prereqs": ["Ohm's Law"]},
    "Lorentz Force": {"chapter": "magnetism", "prereqs": ["Electric Field", "Cross Product"]},
    "Faraday's Law": {"chapter": "emi", "prereqs": ["Gauss's Law", "Lorentz Force"]},
    "Lenz's Law": {"chapter": "emi", "prereqs": ["Faraday's Law"]},
    # ---- Mechanics chain ----
    "Kinematics": {"chapter": "mechanics", "prereqs": []},
    "Newton's Laws": {"chapter": "mechanics", "prereqs": ["Kinematics"]},
    "Work-Energy Theorem": {"chapter": "mechanics", "prereqs": ["Newton's Laws"]},
    "Circular Motion": {"chapter": "mechanics", "prereqs": ["Newton's Laws", "Kinematics"]},
    "Projectile Motion": {"chapter": "mechanics", "prereqs": ["Kinematics", "Vector Algebra"]},
    # ---- Calculus chain ----
    "Limits": {"chapter": "calculus", "prereqs": []},
    "Differentiation": {"chapter": "calculus", "prereqs": ["Limits"]},
    "Integration": {"chapter": "calculus", "prereqs": ["Differentiation"]},
    "Definite Integrals": {"chapter": "calculus", "prereqs": ["Integration"]},
    # ---- Algebra chain ----
    "Quadratic Equations": {"chapter": "algebra", "prereqs": []},
    "Nature of Roots": {"chapter": "algebra", "prereqs": ["Quadratic Equations", "Complex Numbers"]},
    "Complex Numbers": {"chapter": "algebra", "prereqs": []},
    "Binomial Theorem": {"chapter": "algebra", "prereqs": ["Sequences and Series"]},
    # ---- Inorganic chain ----
    "VSEPR Geometry": {"chapter": "chemical-bonding", "prereqs": []},
    "Hybridisation": {"chapter": "chemical-bonding", "prereqs": ["VSEPR Geometry"]},
    "Molecular Orbital Theory": {"chapter": "chemical-bonding", "prereqs": ["Hybridisation"]},
    "Oxidation State": {"chapter": "coordination-compounds", "prereqs": []},
    "Crystal Field Theory": {"chapter": "coordination-compounds", "prereqs": ["Oxidation State", "Hybridisation"]},
    "Low-Spin Complexes": {"chapter": "coordination-compounds", "prereqs": ["Crystal Field Theory"]},
    # ---- Organic chain ----
    "Carbocation Stability": {"chapter": "goc", "prereqs": []},
    "SN2 Mechanism": {"chapter": "haloalkanes", "prereqs": ["Carbocation Stability"]},
    "SN1 Kinetics": {"chapter": "haloalkanes", "prereqs": ["Carbocation Stability"]},
    "SN1 vs SN2 Factors": {"chapter": "haloalkanes", "prereqs": ["SN2 Mechanism", "SN1 Kinetics"]},
    "Nucleophilic Addition": {"chapter": "aldehydes-ketones", "prereqs": ["Carbocation Stability"]},
    "Aldol Reaction": {"chapter": "aldehydes-ketones", "prereqs": ["Nucleophilic Addition"]},
    "Iodoform Test": {"chapter": "aldehydes-ketones", "prereqs": ["Nucleophilic Addition"]},
}


def prereqs_of(concept: str) -> list[str]:
    node = CONCEPT_GRAPH.get(concept)
    return list(node["prereqs"]) if node else []


def chapter_of(concept: str) -> str | None:
    node = CONCEPT_GRAPH.get(concept)
    return node["chapter"] if node else None


def is_known_concept(concept: str) -> bool:
    return concept in CONCEPT_GRAPH


def decompose(concept: str) -> list[str]:
    """Full prerequisite chain below a concept, deepest fundamentals first."""
    out: list[str] = []
    seen: set[str] = set()

    def walk(c: str):
        for p in prereqs_of(c):
            if p in seen:
                continue
            seen.add(p)
            walk(p)
            out.append(p)

    walk(concept)
    return out


def remediation_steps(concept: str, is_weak: Callable[[str], bool], max_steps: int = 4) -> list[str]:
    """Concepts to shore up before retrying `concept`.

    Walks the prerequisite tree depth-first (fundamentals first) and collects the
    prerequisites the student is weak in. If a direct prerequisite has no data and
    no deeper weak node surfaces, it is still suggested as a foundation to revisit.
    """
    steps: list[str] = []
    seen: set[str] = set()

    def walk(c: str) -> bool:
        """Returns True if any weak prerequisite was found under c."""
        found = False
        for p in prereqs_of(c):
            if p in seen:
                continue
            seen.add(p)
            deeper = walk(p)
            if deeper or is_weak(p):
                steps.append(p)
                found = True
        return found

    found_any = walk(concept)
    if not found_any:
        # No weak prerequisite identified: suggest the immediate foundations.
        for p in prereqs_of(concept):
            if p not in steps:
                steps.append(p)
    # Deepest-first already (DFS appends children before parents); trim.
    deduped: list[str] = []
    for s in steps:
        if s not in deduped:
            deduped.append(s)
    return deduped[:max_steps]


def downstream_count(chapter_prereq_chain: dict[str, str | None], chapter_id: str) -> int:
    """How many chapters list `chapter_id` somewhere up their prerequisite chain.

    `chapter_prereq_chain` maps chapter_id -> its immediate prerequisite chapter_id.
    Used to rank weak areas by how much they block.
    """
    count = 0
    for cid in chapter_prereq_chain:
        if cid == chapter_id:
            continue
        cur = chapter_prereq_chain.get(cid)
        guard = 0
        while cur and guard < 50:
            if cur == chapter_id:
                count += 1
                break
            cur = chapter_prereq_chain.get(cur)
            guard += 1
    return count
