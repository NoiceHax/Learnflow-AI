"""Subjects and chapters: the JEE Advanced syllabus, with prerequisites.

Each chapter references its prerequisite by slug; the seed runner resolves
slugs to ids in a second pass.
"""

CATALOG = [
    {
        "name": "Advanced Physics",
        "slug": "physics",
        "icon": "atom",
        "chapters": [
            ("Mechanics", "mechanics", None, 5, "Kinematics, Newton's laws, work–energy, momentum, rotation and gravitation."),
            ("Waves", "waves", "mechanics", 4, "SHM, wave motion, sound, superposition, beats and resonance."),
            ("Thermodynamics", "thermodynamics", "mechanics", 4, "Heat, the laws of thermodynamics, kinetic theory and thermal processes."),
            ("Electrostatics", "electrostatics", "mechanics", 5, "Coulomb's law, electric field, potential, Gauss's law and capacitors."),
            ("Current Electricity", "current-electricity", "electrostatics", 4, "Ohm's law, DC circuits, Kirchhoff's laws and measuring instruments."),
            ("Magnetism", "magnetism", "current-electricity", 4, "Magnetic force on charges and currents, fields of currents and magnetic materials."),
            ("EMI", "emi", "magnetism", 4, "Electromagnetic induction, Faraday & Lenz, inductance and alternating current."),
            ("Optics", "optics", "waves", 4, "Ray optics, lenses and mirrors, plus wave optics: interference and diffraction."),
            ("Modern Physics", "modern-physics", "electrostatics", 5, "Dual nature, photoelectric effect, atomic models and nuclear physics."),
        ],
    },
    {
        "name": "Advanced Mathematics",
        "slug": "mathematics",
        "icon": "sigma",
        "chapters": [
            ("Algebra", "algebra", None, 5, "Quadratics, complex numbers, sequences & series, binomial theorem and matrices."),
            ("Trigonometry", "trigonometry", None, 4, "Trigonometric ratios, identities, equations and inverse functions."),
            ("Coordinate Geometry", "coordinate-geometry", "algebra", 4, "Straight lines, circles and conic sections."),
            ("Calculus", "calculus", "trigonometry", 5, "Limits, continuity, differentiation, integration, areas and differential equations."),
            ("Vectors", "vectors", "coordinate-geometry", 4, "Vector algebra, dot and cross products, and three-dimensional geometry."),
            ("Probability", "probability", "algebra", 4, "Permutations & combinations, conditional probability, Bayes' theorem and distributions."),
        ],
    },
    {
        "name": "Organic Chemistry",
        "slug": "organic-chemistry",
        "icon": "flask-conical",
        "chapters": [
            ("General Organic Chemistry", "goc", None, 5, "Inductive & resonance effects, hybridisation, acidity/basicity, isomerism and intermediates."),
            ("Hydrocarbons", "hydrocarbons", "goc", 4, "Alkanes, alkenes, alkynes and aromatic hydrocarbons."),
            ("Haloalkanes", "haloalkanes", "hydrocarbons", 4, "Nucleophilic substitution (SN1/SN2), elimination and haloarenes."),
            ("Alcohols", "alcohols", "haloalkanes", 4, "Alcohols, phenols and ethers: preparation and reactions."),
            ("Aldehydes and Ketones", "aldehydes-ketones", "alcohols", 5, "Carbonyl chemistry: nucleophilic addition, aldol and related reactions."),
            ("Carboxylic Acids", "carboxylic-acids", "aldehydes-ketones", 4, "Carboxylic acids and their derivatives."),
            ("Amines", "amines", "carboxylic-acids", 4, "Amines, basicity and diazonium chemistry."),
            ("Biomolecules", "biomolecules", "goc", 3, "Carbohydrates, proteins, amino acids and nucleic acids."),
            ("Polymers", "polymers", "goc", 3, "Addition and condensation polymers."),
        ],
    },
    {
        "name": "Inorganic Chemistry",
        "slug": "inorganic-chemistry",
        "icon": "hexagon",
        "chapters": [
            ("Chemical Bonding", "chemical-bonding", None, 5, "VSEPR, hybridisation, molecular orbital theory and bond parameters."),
            ("Coordination Compounds", "coordination-compounds", "chemical-bonding", 5, "Nomenclature, isomerism, crystal field theory and bonding."),
            ("p-block", "p-block", "chemical-bonding", 4, "Groups 13–18: periodic trends and key compounds."),
            ("d-block", "d-block", "chemical-bonding", 4, "Transition elements and their characteristic properties."),
            ("f-block", "f-block", "d-block", 3, "Lanthanides and actinides."),
            ("Metallurgy", "metallurgy", "p-block", 3, "Principles and processes of metal extraction."),
            ("Qualitative Analysis", "qualitative-analysis", "coordination-compounds", 3, "Salt analysis: cation and anion identification."),
        ],
    },
]
