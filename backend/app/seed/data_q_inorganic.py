"""Inorganic Chemistry question bank (JEE Advanced level)."""

QUESTIONS = [
    # ---------------- Chemical Bonding ----------------
    {
        "chapter": "chemical-bonding", "difficulty": "Easy", "concept": "VSEPR Geometry", "type": "single_correct",
        "prompt": "According to VSEPR theory, the shape of the methane (CH₄) molecule is:",
        "options": ["Tetrahedral", "Square planar", "Trigonal planar", "Octahedral"], "correct": 0,
        "solution": "Four bond pairs and no lone pairs around carbon give a tetrahedral geometry (bond angle 109.5°).",
    },
    {
        "chapter": "chemical-bonding", "difficulty": "Medium", "concept": "Hybridisation", "type": "single_correct",
        "prompt": "The hybridisation of the carbon atom in carbon dioxide (CO₂) is:",
        "options": ["sp", "sp²", "sp³", "sp³d"], "correct": 0,
        "solution": "CO₂ is linear (O=C=O) with two σ regions on carbon, so the carbon is sp hybridised.",
    },
    {
        "chapter": "chemical-bonding", "difficulty": "Medium", "concept": "Effect of Lone Pairs", "type": "single_correct",
        "prompt": "The shape of the water (H₂O) molecule is:",
        "options": ["Bent (angular)", "Linear", "Trigonal planar", "Tetrahedral"], "correct": 0,
        "solution": "Oxygen has two bond pairs and two lone pairs; lone-pair repulsion bends the molecule to ~104.5°, giving an angular shape.",
    },
    {
        "chapter": "chemical-bonding", "difficulty": "Medium", "concept": "Molecular Orbital Theory", "type": "integer",
        "prompt": "Using molecular orbital theory, the bond order of the O₂ molecule is:",
        "correct": 2,
        "solution": "Bond order = (bonding − antibonding)/2 = (10 − 6)/2 = 2 for O₂.",
    },
    {
        "chapter": "chemical-bonding", "difficulty": "Advanced", "concept": "Magnetic Behaviour (MOT)", "type": "multiple_correct",
        "prompt": "Which of the following molecules are paramagnetic according to MOT?",
        "options": ["O₂", "N₂", "B₂", "F₂"], "correct": [0, 2],
        "solution": "O₂ and B₂ each have two unpaired electrons in degenerate π* / π orbitals (paramagnetic). N₂ and F₂ have all electrons paired (diamagnetic).",
    },
    # ---------------- Coordination Compounds ----------------
    {
        "chapter": "coordination-compounds", "difficulty": "Medium", "concept": "Oxidation State", "type": "single_correct",
        "prompt": "The oxidation state of iron in the complex [Fe(CN)₆]³⁻ is:",
        "options": ["+3", "+2", "+6", "0"], "correct": 0,
        "solution": "Each CN⁻ is −1; x + 6(−1) = −3 ⇒ x = +3.",
    },
    {
        "chapter": "coordination-compounds", "difficulty": "Easy", "concept": "Coordination Number", "type": "single_correct",
        "prompt": "The coordination number of platinum in [PtCl₄]²⁻ is:",
        "options": ["4", "2", "6", "1"], "correct": 0,
        "solution": "Four chloride ligands are directly bonded to Pt, so the coordination number is 4.",
    },
    {
        "chapter": "coordination-compounds", "difficulty": "Medium", "concept": "Crystal Field Theory", "type": "single_correct",
        "prompt": "In an octahedral crystal field, the five d-orbitals split into:",
        "options": ["t₂g (lower) and eg (higher)", "eg (lower) and t₂g (higher)", "No splitting occurs", "Three equal sets"], "correct": 0,
        "solution": "In an octahedral field the t₂g set is stabilised (lower) and the eg set is raised (higher).",
    },
    {
        "chapter": "coordination-compounds", "difficulty": "Advanced", "concept": "Low-Spin Complexes", "type": "integer",
        "prompt": "The number of unpaired electrons in the strong-field, low-spin complex [Fe(CN)₆]³⁻ is:",
        "correct": 1,
        "solution": "Fe³⁺ is d⁵; with strong-field CN⁻ the configuration is t₂g⁵eg⁰, leaving exactly one unpaired electron.",
    },
    {
        "chapter": "coordination-compounds", "difficulty": "Advanced", "concept": "Isomerism", "type": "multiple_correct",
        "prompt": "Which of the following types of isomerism are exhibited by coordination compounds?",
        "options": ["Geometrical", "Optical", "Linkage", "Metallic"], "correct": [0, 1, 2],
        "solution": "Coordination compounds show geometrical, optical and linkage isomerism. 'Metallic isomerism' is not a recognised type.",
    },
    # ---------------- p-block ----------------
    {
        "chapter": "p-block", "difficulty": "Medium", "concept": "Inert Pair Effect", "type": "single_correct",
        "prompt": "Down group 13, the +1 oxidation state becomes increasingly stable relative to +3 because of the:",
        "options": ["Inert pair effect", "Increasing electronegativity", "Decreasing atomic size", "Aromatic stabilisation"], "correct": 0,
        "solution": "The reluctance of the ns² electrons to participate in bonding (inert pair effect) grows down the group, stabilising the +1 state.",
    },
    {
        "chapter": "p-block", "difficulty": "Easy", "concept": "Periodic Trends", "type": "single_correct",
        "prompt": "Which of the following is the most electronegative element?",
        "options": ["Fluorine", "Oxygen", "Chlorine", "Nitrogen"], "correct": 0,
        "solution": "Fluorine is the most electronegative element on the Pauling scale (3.98).",
    },
    {
        "chapter": "p-block", "difficulty": "Medium", "concept": "Oxidation States of Group 15", "type": "single_correct",
        "prompt": "On moving down group 15, the stability of the +5 oxidation state:",
        "options": ["Decreases", "Increases", "Remains constant", "Becomes zero"], "correct": 0,
        "solution": "Because of the inert pair effect, the +5 state becomes less stable down the group (e.g. Bi⁵⁺ is strongly oxidising).",
    },
    {
        "chapter": "p-block", "difficulty": "Easy", "concept": "Electronic Configuration", "type": "integer",
        "prompt": "The number of valence electrons in a nitrogen atom is:",
        "correct": 5,
        "solution": "Nitrogen ([He]2s²2p³) has 5 electrons in its valence shell.",
    },
    # ---------------- d-block ----------------
    {
        "chapter": "d-block", "difficulty": "Medium", "concept": "Colour of Complexes", "type": "single_correct",
        "prompt": "Transition-metal ions are usually coloured because of:",
        "options": ["d–d electronic transitions", "s–s transitions", "Nuclear transitions", "Molecular vibrations"], "correct": 0,
        "solution": "Partially filled d-orbitals allow d–d transitions that absorb visible light, giving the complementary colour.",
    },
    {
        "chapter": "d-block", "difficulty": "Easy", "concept": "Characteristic Properties", "type": "single_correct",
        "prompt": "A characteristic property of transition elements is that they commonly show:",
        "options": ["Variable oxidation states", "Only the +1 state", "No catalytic activity", "A single fixed oxidation state"], "correct": 0,
        "solution": "Closeness in energy of (n−1)d and ns electrons lets transition metals display several oxidation states.",
    },
    {
        "chapter": "d-block", "difficulty": "Medium", "concept": "Magnetic Moment", "type": "single_correct",
        "prompt": "The spin-only magnetic moment √(n(n+2)) of a transition-metal ion is expressed in units of:",
        "options": ["Bohr magneton (BM)", "Debye", "Coulomb", "Tesla"], "correct": 0,
        "solution": "Magnetic moment is measured in Bohr magnetons (BM).",
    },
    {
        "chapter": "d-block", "difficulty": "Advanced", "concept": "Unpaired Electrons", "type": "integer",
        "prompt": "The number of unpaired electrons in the Mn²⁺ ion (Z = 25) is:",
        "correct": 5,
        "solution": "Mn is [Ar]3d⁵4s²; removing the two 4s electrons gives Mn²⁺ = 3d⁵, which has 5 unpaired electrons.",
    },
    # ---------------- f-block ----------------
    {
        "chapter": "f-block", "difficulty": "Easy", "concept": "Lanthanide Contraction", "type": "single_correct",
        "prompt": "The steady decrease in atomic and ionic radii across the lanthanide series is known as:",
        "options": ["Lanthanide contraction", "The inert pair effect", "The diagonal relationship", "Screening"], "correct": 0,
        "solution": "Poor shielding by 4f electrons causes a gradual size decrease called the lanthanide contraction.",
    },
    {
        "chapter": "f-block", "difficulty": "Easy", "concept": "Oxidation States", "type": "single_correct",
        "prompt": "The most common and stable oxidation state of the lanthanides is:",
        "options": ["+3", "+1", "+5", "+7"], "correct": 0,
        "solution": "Lanthanides characteristically exhibit the +3 oxidation state.",
    },
    {
        "chapter": "f-block", "difficulty": "Medium", "concept": "Actinides vs Lanthanides", "type": "single_correct",
        "prompt": "Compared with the lanthanides, a distinctive feature of the actinides is that they:",
        "options": ["Are all radioactive", "Are non-metallic", "Contain no f electrons", "Exist as gases"], "correct": 0,
        "solution": "All actinides are radioactive and (unlike the lanthanides) show a wide range of oxidation states.",
    },
    # ---------------- Metallurgy ----------------
    {
        "chapter": "metallurgy", "difficulty": "Medium", "concept": "Reduction in the Blast Furnace", "type": "single_correct",
        "prompt": "In the extraction of iron in a blast furnace, the principal reducing agent is:",
        "options": ["Carbon monoxide (CO)", "Oxygen", "Silica", "Limestone"], "correct": 0,
        "solution": "Carbon monoxide produced from coke reduces iron oxides to iron in the upper regions of the furnace.",
    },
    {
        "chapter": "metallurgy", "difficulty": "Easy", "concept": "Ore Concentration", "type": "single_correct",
        "prompt": "Froth flotation is most suitable for concentrating which type of ore?",
        "options": ["Sulphide ores", "Oxide ores", "Carbonate ores", "Halide ores"], "correct": 0,
        "solution": "Froth flotation exploits the preferential wetting of sulphide ores by oil, separating them from gangue.",
    },
    {
        "chapter": "metallurgy", "difficulty": "Medium", "concept": "Calcination", "type": "single_correct",
        "prompt": "Calcination involves heating an ore:",
        "options": ["In the limited supply or absence of air", "In an excess of air", "With coke as reductant", "With water"], "correct": 0,
        "solution": "Calcination heats an ore below its melting point in limited/absent air to expel volatile matter (e.g. converting carbonates to oxides). Heating in excess air is roasting.",
    },
    # ---------------- Qualitative Analysis ----------------
    {
        "chapter": "qualitative-analysis", "difficulty": "Easy", "concept": "Flame Tests", "type": "single_correct",
        "prompt": "A persistent golden-yellow colour in the flame test indicates the presence of:",
        "options": ["Sodium (Na⁺)", "Potassium (K⁺)", "Calcium (Ca²⁺)", "Copper (Cu²⁺)"], "correct": 0,
        "solution": "Sodium imparts a characteristic intense golden-yellow flame.",
    },
    {
        "chapter": "qualitative-analysis", "difficulty": "Medium", "concept": "Confirmatory Tests", "type": "single_correct",
        "prompt": "The brown-ring test is used to confirm the presence of which ion?",
        "options": ["Nitrate (NO₃⁻)", "Sulphate (SO₄²⁻)", "Chloride (Cl⁻)", "Carbonate (CO₃²⁻)"], "correct": 0,
        "solution": "The brown ring of [Fe(H₂O)₅NO]²⁺ at the interface confirms nitrate ions.",
    },
    {
        "chapter": "qualitative-analysis", "difficulty": "Medium", "concept": "Group Separation", "type": "single_correct",
        "prompt": "Passing H₂S through a solution acidified with dilute HCl precipitates the cations of analytical:",
        "options": ["Group II (e.g. Cu²⁺, Pb²⁺)", "Group I", "Group IV", "Group VI"], "correct": 0,
        "solution": "In acidic medium the low sulphide-ion concentration precipitates only the least-soluble Group II sulphides.",
    },
]
