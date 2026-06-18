"""Premium lesson content: Inorganic Chemistry."""

LESSONS = [
    {
        "chapter": "chemical-bonding",
        "theory": "Chemical bonding explains how atoms combine. VSEPR predicts molecular shapes from electron-pair repulsion; valence-bond theory introduces hybridisation; molecular-orbital theory explains magnetism and bond order that VSEPR cannot.",
        "key_concepts": [
            "Shape follows the steric number (bond pairs + lone pairs) around the central atom.",
            "Lone pairs repel more strongly than bond pairs, compressing bond angles.",
            "Hybridisation: sp (linear), sp² (trigonal planar), sp³ (tetrahedral).",
            "MOT gives bond order = (bonding − antibonding)/2 and predicts magnetism.",
        ],
        "formulas": [
            {"name": "Bond order (MOT)", "expr": "BO = (N_b − N_a)/2"},
            {"name": "Steric number", "expr": "SN = (bond pairs) + (lone pairs)"},
        ],
        "examples": [
            {"problem": "Shape of CH₄?", "solution": "Four bond pairs, no lone pairs ⇒ tetrahedral (109.5°)."},
            {"problem": "Bond order of O₂?", "solution": "(10 − 6)/2 = 2; O₂ is also paramagnetic."},
        ],
        "common_mistakes": [
            "Ignoring lone pairs when predicting shape (e.g. calling H₂O linear).",
            "Forgetting that O₂ is paramagnetic, a classic MOT result.",
        ],
        "pyq_highlights": [
            "Predict shape, hybridisation and polarity of given molecules.",
            "MOT bond order and magnetic behaviour of diatomics.",
        ],
        "practice": {"easy": "Assign hybridisation and shape.", "medium": "Compare bond angles using lone-pair repulsion.", "advanced": "MOT diagrams, bond order and magnetism."},
    },
    {
        "chapter": "coordination-compounds",
        "theory": "Coordination compounds feature a central metal bonded to ligands. Werner's theory, IUPAC nomenclature, isomerism and crystal-field theory (CFT) together explain their colour, magnetism and geometry.",
        "key_concepts": [
            "Oxidation state of the metal = complex charge − sum of ligand charges.",
            "CFT splits d-orbitals: octahedral → t₂g (lower) + eg (higher).",
            "Strong-field ligands cause pairing (low spin); weak-field give high spin.",
            "Complexes show geometrical, optical, ionisation and linkage isomerism.",
        ],
        "formulas": [
            {"name": "CFSE (octahedral)", "expr": "CFSE = (−0.4 t₂g + 0.6 eg)Δ₀"},
            {"name": "Spin-only moment", "expr": "μ = √(n(n+2)) BM"},
        ],
        "examples": [
            {"problem": "Oxidation state of Fe in [Fe(CN)₆]³⁻?", "solution": "x + 6(−1) = −3 ⇒ x = +3."},
            {"problem": "Unpaired electrons in low-spin [Fe(CN)₆]³⁻?", "solution": "Fe³⁺ d⁵, t₂g⁵ ⇒ 1 unpaired electron."},
        ],
        "common_mistakes": [
            "Forgetting to account for ligand charge when finding oxidation state.",
            "Applying high-spin counts to strong-field (low-spin) complexes.",
        ],
        "pyq_highlights": [
            "Magnetic moment and spin state from ligand field strength.",
            "Counting geometrical/optical isomers of octahedral complexes.",
        ],
        "practice": {"easy": "Name complexes and find oxidation states.", "medium": "Predict spin state and magnetic moment.", "advanced": "Isomer counting and CFSE comparisons."},
    },
    {
        "chapter": "p-block",
        "theory": "The p-block (groups 13–18) shows the richest variety of properties in the periodic table. Periodic trends, the inert-pair effect, and the anomalous behaviour of the first member of each group are recurring themes.",
        "key_concepts": [
            "Down a group, the lower oxidation state becomes more stable (inert-pair effect).",
            "Fluorine is the most electronegative element; non-metallic character decreases down a group.",
            "Group 15: stability of +5 falls down the group (Bi⁵⁺ strongly oxidising).",
            "The first element of each group often behaves anomalously (small size, no d-orbitals).",
        ],
        "formulas": [
            {"name": "Inert pair effect", "expr": "ns² electrons increasingly reluctant to bond down a group"},
        ],
        "examples": [
            {"problem": "Why is Tl⁺ more stable than Tl³⁺?", "solution": "The inert-pair effect stabilises the +1 state low in group 13."},
            {"problem": "Most electronegative element?", "solution": "Fluorine."},
        ],
        "common_mistakes": [
            "Forgetting the inert-pair effect when predicting stable oxidation states.",
            "Overlooking the anomalous first-member behaviour (e.g. N vs P).",
        ],
        "pyq_highlights": [
            "Trends in acidic/basic nature of oxides and hydrides.",
            "Structure and bonding of interhalogens and oxoacids.",
        ],
        "practice": {"easy": "Recall group trends.", "medium": "Compare oxidation-state stabilities.", "advanced": "Structure/bonding of p-block oxoacids and hydrides."},
    },
    {
        "chapter": "d-block",
        "theory": "The d-block (transition) elements have partially filled d-orbitals, giving them variable oxidation states, coloured ions, magnetic behaviour and catalytic activity.",
        "key_concepts": [
            "Variable oxidation states arise from close (n−1)d and ns energies.",
            "Colour comes from d–d electronic transitions.",
            "Magnetic moment μ = √(n(n+2)) BM measures unpaired electrons.",
            "Many transition metals and their compounds are good catalysts.",
        ],
        "formulas": [
            {"name": "Spin-only moment", "expr": "μ = √(n(n+2)) BM"},
        ],
        "examples": [
            {"problem": "Unpaired electrons in Mn²⁺ (Z = 25)?", "solution": "Mn²⁺ = 3d⁵ ⇒ 5 unpaired electrons."},
            {"problem": "Why are transition-metal complexes coloured?", "solution": "d–d transitions absorb visible light; the complementary colour is seen."},
        ],
        "common_mistakes": [
            "Removing 3d before 4s electrons when forming ions (4s goes first).",
            "Confusing colour cause (d–d transitions) with charge transfer in special cases.",
        ],
        "pyq_highlights": [
            "Calculate spin-only magnetic moments.",
            "Explain trends in oxidation states and stability.",
        ],
        "practice": {"easy": "Write d-electron configurations of ions.", "medium": "Compute magnetic moments.", "advanced": "Rationalise oxidation-state and colour trends."},
    },
    {
        "chapter": "f-block",
        "theory": "The f-block comprises the lanthanides and actinides, characterised by filling 4f and 5f orbitals. The lanthanide contraction and the radioactivity of actinides are the headline features.",
        "key_concepts": [
            "Lanthanide contraction: steady size decrease due to poor 4f shielding.",
            "Lanthanides predominantly show the +3 oxidation state.",
            "Actinides are all radioactive and show more variable oxidation states.",
            "The contraction affects the properties of the elements that follow (e.g. Zr ≈ Hf).",
        ],
        "formulas": [
            {"name": "Characteristic state", "expr": "Ln → +3 (most stable)"},
        ],
        "examples": [
            {"problem": "Name the steady size decrease across the lanthanides.", "solution": "The lanthanide contraction."},
            {"problem": "Most stable lanthanide oxidation state?", "solution": "+3."},
        ],
        "common_mistakes": [
            "Attributing the contraction to relativistic effects alone (it is mainly poor f-shielding).",
            "Assuming actinides behave exactly like lanthanides.",
        ],
        "pyq_highlights": [
            "Consequences of lanthanide contraction.",
            "Comparison of lanthanide and actinide chemistry.",
        ],
        "practice": {"easy": "Recall key f-block facts.", "medium": "Explain contraction consequences.", "advanced": "Compare Ln/An oxidation-state behaviour."},
    },
    {
        "chapter": "metallurgy",
        "theory": "Metallurgy covers the principles of extracting metals from their ores: concentration, conversion to oxide, reduction and refining. Thermodynamics (Ellingham diagrams) guides the choice of reducing agent.",
        "key_concepts": [
            "Froth flotation concentrates sulphide ores.",
            "Roasting (in air) and calcination (limited air) convert ores to oxides.",
            "Reduction of oxides uses C/CO, a more reactive metal, or electrolysis.",
            "Ellingham diagrams show which reductant works at a given temperature.",
        ],
        "formulas": [
            {"name": "Blast-furnace reduction", "expr": "Fe₂O₃ + 3CO → 2Fe + 3CO₂"},
        ],
        "examples": [
            {"problem": "Reducing agent for iron in the blast furnace?", "solution": "Carbon monoxide (CO)."},
            {"problem": "Process to concentrate a sulphide ore?", "solution": "Froth flotation."},
        ],
        "common_mistakes": [
            "Confusing roasting (in air) with calcination (limited/absent air).",
            "Choosing a reductant without checking the Ellingham diagram.",
        ],
        "pyq_highlights": [
            "Match ore-treatment step to purpose.",
            "Ellingham-diagram reasoning for reductant choice.",
        ],
        "practice": {"easy": "Match ore to concentration method.", "medium": "Sequence the extraction steps.", "advanced": "Use Ellingham diagrams to justify reductants."},
    },
    {
        "chapter": "qualitative-analysis",
        "theory": "Qualitative analysis identifies the ions in a salt. Systematic group separation precipitates cations in order, while specific confirmatory tests (flame colours, brown ring, gas evolution) pin down the exact ion.",
        "key_concepts": [
            "Cations are separated into analytical groups by selective precipitation.",
            "Group II sulphides precipitate from acidic H₂S; Group IV from basic H₂S.",
            "Flame colours: Na⁺ golden-yellow, K⁺ lilac, Ca²⁺ brick-red, Cu²⁺ green.",
            "Confirmatory tests clinch identity (brown ring for nitrate, etc.).",
        ],
        "formulas": [
            {"name": "Brown ring", "expr": "[Fe(H₂O)₅NO]²⁺ confirms NO₃⁻"},
        ],
        "examples": [
            {"problem": "Golden-yellow flame indicates?", "solution": "Sodium (Na⁺)."},
            {"problem": "H₂S in dilute HCl precipitates which group?", "solution": "Group II (e.g. Cu²⁺, Pb²⁺)."},
        ],
        "common_mistakes": [
            "Adding the group reagent in the wrong medium (acidic vs basic).",
            "Confusing flame-test colours of the alkali/alkaline-earth metals.",
        ],
        "pyq_highlights": [
            "Identify the ion from a described test result.",
            "Reasoning through interfering-ion separations.",
        ],
        "practice": {"easy": "Match flame colour to cation.", "medium": "Assign cations to analytical groups.", "advanced": "Deduce a salt from a sequence of test observations."},
    },
]
