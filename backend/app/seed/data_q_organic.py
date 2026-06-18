"""Organic Chemistry question bank (JEE Advanced level)."""

QUESTIONS = [
    # ---------------- General Organic Chemistry ----------------
    {
        "chapter": "goc", "difficulty": "Easy", "concept": "Carbocation Stability", "type": "single_correct",
        "prompt": "Which of the following carbocations is the most stable?",
        "options": ["Tertiary (3°)", "Secondary (2°)", "Primary (1°)", "Methyl"], "correct": 0,
        "solution": "Stability increases with the number of alkyl groups due to +I effect and hyperconjugation: 3° > 2° > 1° > methyl.",
    },
    {
        "chapter": "goc", "difficulty": "Medium", "concept": "Inductive Effect & Acidity", "type": "single_correct",
        "prompt": "Which of the following is the strongest acid?",
        "options": ["Trichloroacetic acid", "Acetic acid", "Formic acid", "Ethanol"], "correct": 0,
        "solution": "Three electron-withdrawing chlorines stabilise the carboxylate by −I effect, making trichloroacetic acid the strongest of these.",
    },
    {
        "chapter": "goc", "difficulty": "Medium", "concept": "Degree of Unsaturation", "type": "integer",
        "prompt": "The degree of unsaturation (index of hydrogen deficiency) of benzene, C₆H₆, is:",
        "correct": 4,
        "solution": "DoU = (2×6 + 2 − 6)/2 = (14 − 6)/2 = 4 (three π bonds + one ring).",
    },
    {
        "chapter": "goc", "difficulty": "Easy", "concept": "Structural Isomerism", "type": "single_correct",
        "prompt": "The number of structural (chain) isomers of C₄H₁₀ is:",
        "options": ["2", "3", "4", "1"], "correct": 0,
        "solution": "n-butane and isobutane (2-methylpropane): exactly 2 isomers.",
    },
    {
        "chapter": "goc", "difficulty": "Advanced", "concept": "Resonance", "type": "multiple_correct",
        "prompt": "Which of the following species are stabilised by resonance (delocalisation)?",
        "options": ["Carboxylate ion", "Benzene", "Phenoxide ion", "Methane"], "correct": [0, 1, 2],
        "solution": "Carboxylate, benzene and phenoxide all have delocalised π systems. Methane has only σ bonds and no resonance.",
    },
    # ---------------- Hydrocarbons ----------------
    {
        "chapter": "hydrocarbons", "difficulty": "Easy", "concept": "Markovnikov Addition", "type": "single_correct",
        "prompt": "Addition of HBr to propene (in the absence of peroxide) gives predominantly:",
        "options": ["2-bromopropane", "1-bromopropane", "propane", "propyne"], "correct": 0,
        "solution": "Markovnikov's rule: H adds to the carbon with more hydrogens, Br to the more substituted carbon, giving 2-bromopropane.",
    },
    {
        "chapter": "hydrocarbons", "difficulty": "Easy", "concept": "Aromaticity", "type": "single_correct",
        "prompt": "Benzene most readily undergoes which type of reaction?",
        "options": ["Electrophilic substitution", "Nucleophilic substitution", "Electrophilic addition", "Elimination"], "correct": 0,
        "solution": "To preserve its stable aromatic sextet, benzene undergoes electrophilic substitution rather than addition.",
    },
    {
        "chapter": "hydrocarbons", "difficulty": "Medium", "concept": "Terminal Alkyne Acidity", "type": "single_correct",
        "prompt": "Which of the following is the most acidic?",
        "options": ["Ethyne (HC≡CH)", "Ethene", "Ethane", "Methane"], "correct": 0,
        "solution": "The terminal alkyne C–H is on an sp carbon (50% s-character), holding the lone pair tightly, so ethyne is the most acidic.",
    },
    {
        "chapter": "hydrocarbons", "difficulty": "Medium", "concept": "Bonding", "type": "integer",
        "prompt": "The total number of sigma (σ) bonds in a molecule of ethyne, C₂H₂, is:",
        "correct": 3,
        "solution": "H–C≡C–H has two C–H σ bonds and one C–C σ bond (the triple bond is 1 σ + 2 π), giving 3 σ bonds.",
    },
    # ---------------- Haloalkanes ----------------
    {
        "chapter": "haloalkanes", "difficulty": "Easy", "concept": "SN2 Mechanism", "type": "single_correct",
        "prompt": "The SN2 reaction proceeds fastest with which type of substrate?",
        "options": ["Primary (methyl) halide", "Tertiary halide", "Neopentyl halide", "It is independent of substrate"], "correct": 0,
        "solution": "SN2 needs back-side attack; less steric hindrance means primary/methyl halides react fastest.",
    },
    {
        "chapter": "haloalkanes", "difficulty": "Medium", "concept": "SN1 Kinetics", "type": "single_correct",
        "prompt": "The rate of an SN1 reaction depends on the concentration of:",
        "options": ["The substrate only", "The nucleophile only", "Both substrate and nucleophile", "Neither"], "correct": 0,
        "solution": "The slow step of SN1 is carbocation formation from the substrate, so rate = k[substrate]: first order.",
    },
    {
        "chapter": "haloalkanes", "difficulty": "Medium", "concept": "Stereochemistry", "type": "single_correct",
        "prompt": "An SN2 reaction at a chiral carbon proceeds with:",
        "options": ["Inversion of configuration", "Retention of configuration", "Complete racemisation", "No effect on configuration"], "correct": 0,
        "solution": "Back-side attack flips the configuration: the Walden inversion.",
    },
    {
        "chapter": "haloalkanes", "difficulty": "Advanced", "concept": "SN1 vs SN2 Factors", "type": "multiple_correct",
        "prompt": "Which factors favour the SN1 pathway over SN2?",
        "options": ["A tertiary substrate", "A polar protic solvent", "A strong nucleophile", "A primary substrate"], "correct": [0, 1],
        "solution": "SN1 is favoured by stable carbocations (tertiary substrates) and polar protic solvents that stabilise ions. Strong nucleophiles and primary substrates favour SN2.",
    },
    # ---------------- Alcohols ----------------
    {
        "chapter": "alcohols", "difficulty": "Medium", "concept": "Acidity of Alcohols & Phenols", "type": "single_correct",
        "prompt": "Which of the following is the most acidic?",
        "options": ["Phenol", "Ethanol", "Methanol", "Cyclohexanol"], "correct": 0,
        "solution": "The phenoxide ion is resonance-stabilised, so phenol (pKa ≈ 10) is far more acidic than the aliphatic alcohols.",
    },
    {
        "chapter": "alcohols", "difficulty": "Easy", "concept": "Oxidation", "type": "single_correct",
        "prompt": "Oxidation of a primary alcohol with a strong oxidising agent (e.g. acidified KMnO₄) ultimately gives a:",
        "options": ["Carboxylic acid", "Ketone", "Ester", "Alkane"], "correct": 0,
        "solution": "Primary alcohol → aldehyde → carboxylic acid under strong oxidation.",
    },
    {
        "chapter": "alcohols", "difficulty": "Medium", "concept": "Lucas Test", "type": "single_correct",
        "prompt": "The Lucas test distinguishes 1°, 2° and 3° alcohols based on the:",
        "options": ["Rate of appearance of turbidity (3° > 2° > 1°)", "Colour change to green", "Evolution of a gas", "Change in pH"], "correct": 0,
        "solution": "Lucas reagent (conc. HCl + ZnCl₂) reacts fastest with 3° alcohols (immediate turbidity) and slowest with 1°.",
    },
    {
        "chapter": "alcohols", "difficulty": "Easy", "concept": "Isomerism", "type": "integer",
        "prompt": "The number of isomeric alcohols having the molecular formula C₃H₈O is:",
        "correct": 2,
        "solution": "Propan-1-ol and propan-2-ol (methoxyethane is an ether, not an alcohol).",
    },
    # ---------------- Aldehydes and Ketones ----------------
    {
        "chapter": "aldehydes-ketones", "difficulty": "Easy", "concept": "Nucleophilic Addition", "type": "single_correct",
        "prompt": "Towards nucleophilic addition, the reactivity of the carbonyl group is:",
        "options": ["Aldehydes more reactive than ketones", "Ketones more reactive than aldehydes", "Both equally reactive", "Neither is reactive"], "correct": 0,
        "solution": "Ketones have two electron-donating alkyl groups creating more steric and electronic hindrance, so aldehydes are more reactive.",
    },
    {
        "chapter": "aldehydes-ketones", "difficulty": "Medium", "concept": "Aldol Reaction", "type": "single_correct",
        "prompt": "For a carbonyl compound to undergo the aldol condensation, it must possess at least one:",
        "options": ["α-hydrogen", "β-hydrogen", "aromatic ring", "halogen atom"], "correct": 0,
        "solution": "The aldol reaction proceeds via an enolate, which requires an acidic α-hydrogen.",
    },
    {
        "chapter": "aldehydes-ketones", "difficulty": "Easy", "concept": "Tollens' Test", "type": "single_correct",
        "prompt": "Tollens' reagent (ammoniacal silver nitrate) gives a silver mirror with:",
        "options": ["Aldehydes", "Ketones", "Both equally", "Neither"], "correct": 0,
        "solution": "Aldehydes are oxidised to carboxylates, reducing Ag⁺ to metallic silver. Ketones do not respond.",
    },
    {
        "chapter": "aldehydes-ketones", "difficulty": "Advanced", "concept": "Iodoform Test", "type": "multiple_correct",
        "prompt": "Which of the following give a positive iodoform test?",
        "options": ["Acetaldehyde", "Acetone", "Ethanol", "Benzaldehyde"], "correct": [0, 1, 2],
        "solution": "The iodoform test is positive for methyl ketones, acetaldehyde and compounds oxidisable to them (ethanol). Benzaldehyde has no CH₃CO/CH₃CH(OH) group, so it is negative.",
    },
    {
        "chapter": "aldehydes-ketones", "difficulty": "Medium", "concept": "Aldol Product", "type": "integer",
        "prompt": "The self-aldol addition of two molecules of acetaldehyde gives 3-hydroxybutanal. The number of carbon atoms in this product is:",
        "correct": 4,
        "solution": "Two C₂ units combine to give CH₃CH(OH)CH₂CHO, which has 4 carbon atoms.",
    },
    # ---------------- Carboxylic Acids ----------------
    {
        "chapter": "carboxylic-acids", "difficulty": "Medium", "concept": "Acid Strength", "type": "single_correct",
        "prompt": "Which of the following is the strongest acid?",
        "options": ["Chloroacetic acid", "Acetic acid", "Propanoic acid", "Ethanol"], "correct": 0,
        "solution": "The −I effect of chlorine stabilises the carboxylate, so chloroacetic acid is stronger than the unsubstituted acids (and far stronger than ethanol).",
    },
    {
        "chapter": "carboxylic-acids", "difficulty": "Medium", "concept": "Derivative Reactivity", "type": "single_correct",
        "prompt": "The most reactive carboxylic-acid derivative towards nucleophilic acyl substitution is the:",
        "options": ["Acid chloride", "Ester", "Amide", "Carboxylate ion"], "correct": 0,
        "solution": "Reactivity order: acid chloride > anhydride > ester > amide. Chloride is the best leaving group, so acid chlorides are most reactive.",
    },
    {
        "chapter": "carboxylic-acids", "difficulty": "Medium", "concept": "Decarboxylation", "type": "single_correct",
        "prompt": "Heating the sodium salt of a carboxylic acid with soda lime (NaOH/CaO) yields a:",
        "options": ["Alkane with one fewer carbon", "Alkene", "Alcohol", "Ketone"], "correct": 0,
        "solution": "This decarboxylation replaces –COONa with –H, giving an alkane with one carbon fewer (e.g. CH₃COONa → CH₄).",
    },
    {
        "chapter": "carboxylic-acids", "difficulty": "Easy", "concept": "Functional Groups", "type": "integer",
        "prompt": "The number of carboxylic-acid (–COOH) groups present in oxalic acid is:",
        "correct": 2,
        "solution": "Oxalic acid is HOOC–COOH, a dicarboxylic acid with 2 –COOH groups.",
    },
    # ---------------- Amines ----------------
    {
        "chapter": "amines", "difficulty": "Easy", "concept": "Basicity Origin", "type": "single_correct",
        "prompt": "Amines act as bases primarily because the nitrogen atom possesses:",
        "options": ["A lone pair of electrons", "No lone pair", "A positive charge", "A C=N double bond"], "correct": 0,
        "solution": "The nitrogen lone pair can accept a proton (or donate to an electrophile), making amines basic/nucleophilic.",
    },
    {
        "chapter": "amines", "difficulty": "Medium", "concept": "Aliphatic vs Aromatic Basicity", "type": "single_correct",
        "prompt": "Which is the stronger base?",
        "options": ["Ethylamine", "Aniline", "They are equal", "Neither is basic"], "correct": 0,
        "solution": "In aniline the nitrogen lone pair is delocalised into the ring, reducing availability. Ethylamine's lone pair is fully available, so it is the stronger base.",
    },
    {
        "chapter": "amines", "difficulty": "Medium", "concept": "Diazotisation", "type": "single_correct",
        "prompt": "Benzenediazonium chloride is prepared by treating aniline with:",
        "options": ["NaNO₂ and HCl at 0–5 °C", "NaOH", "concentrated H₂SO₄", "bromine water"], "correct": 0,
        "solution": "Diazotisation uses nitrous acid (NaNO₂ + HCl) kept at 0–5 °C, since the diazonium salt is unstable at higher temperature.",
    },
    {
        "chapter": "amines", "difficulty": "Advanced", "concept": "Carbylamine Test", "type": "multiple_correct",
        "prompt": "Which statements about the carbylamine (isocyanide) test are correct?",
        "options": ["Primary amines give the test", "The reagents are CHCl₃ and alcoholic KOH", "Tertiary amines give the test", "Aniline gives the test"], "correct": [0, 1, 3],
        "solution": "Only primary amines (aliphatic or aromatic, including aniline) form foul-smelling isocyanides with CHCl₃ and alcoholic KOH. Secondary and tertiary amines do not respond.",
    },
    # ---------------- Biomolecules ----------------
    {
        "chapter": "biomolecules", "difficulty": "Easy", "concept": "Carbohydrates", "type": "single_correct",
        "prompt": "Glucose is classified as a/an:",
        "options": ["Aldohexose", "Ketohexose", "Aldopentose", "Ketopentose"], "correct": 0,
        "solution": "Glucose has six carbons (hexose) and an aldehyde group (aldo-), making it an aldohexose.",
    },
    {
        "chapter": "biomolecules", "difficulty": "Easy", "concept": "Proteins", "type": "single_correct",
        "prompt": "Amino-acid residues in a protein are joined by which type of covalent bond?",
        "options": ["Peptide bond", "Glycosidic bond", "Ester bond", "Hydrogen bond"], "correct": 0,
        "solution": "A peptide (amide) bond forms between the –COOH of one amino acid and the –NH₂ of the next.",
    },
    {
        "chapter": "biomolecules", "difficulty": "Medium", "concept": "Nucleic Acids", "type": "single_correct",
        "prompt": "The sugar present in DNA is:",
        "options": ["2-deoxyribose", "Ribose", "Glucose", "Fructose"], "correct": 0,
        "solution": "DNA (deoxyribonucleic acid) contains 2-deoxyribose; ribose is found in RNA.",
    },
    # ---------------- Polymers ----------------
    {
        "chapter": "polymers", "difficulty": "Easy", "concept": "Classification", "type": "single_correct",
        "prompt": "Nylon-6,6 is an example of a/an:",
        "options": ["Condensation polymer", "Addition polymer", "Natural polymer", "Elastomer"], "correct": 0,
        "solution": "Nylon-6,6 forms by condensation of a diamine and a diacid, eliminating water.",
    },
    {
        "chapter": "polymers", "difficulty": "Easy", "concept": "Monomers", "type": "single_correct",
        "prompt": "The monomer used to make polythene (polyethylene) is:",
        "options": ["Ethene", "Propene", "Styrene", "Vinyl chloride"], "correct": 0,
        "solution": "Polythene is the addition polymer of ethene (ethylene).",
    },
    {
        "chapter": "polymers", "difficulty": "Medium", "concept": "Natural Polymers", "type": "single_correct",
        "prompt": "Natural rubber is a polymer of:",
        "options": ["Isoprene (2-methylbuta-1,3-diene)", "Ethene", "Vinyl chloride", "Glucose"], "correct": 0,
        "solution": "Natural rubber is cis-1,4-polyisoprene, built from isoprene units.",
    },
]
