"""Premium lesson content: Organic Chemistry."""

LESSONS = [
    {
        "chapter": "goc",
        "theory": "General Organic Chemistry (GOC) is the grammar of organic reactions. Electronic effects (inductive, resonance, hyperconjugation) explain stability, acidity, basicity and reactivity. Master GOC and the rest of organic chemistry becomes reasoning rather than rote.",
        "key_concepts": [
            "Carbocation stability: 3° > 2° > 1° > methyl (hyperconjugation + inductive).",
            "Resonance delocalises charge and adds stability (carboxylate, phenoxide, benzene).",
            "Electron-withdrawing groups (−I) increase acidity; electron-donating groups decrease it.",
            "Degree of unsaturation = (2C + 2 + N − H − X)/2.",
        ],
        "formulas": [
            {"name": "Degree of unsaturation", "expr": "DoU = (2C + 2 + N − H − X)/2"},
            {"name": "Acidity trend", "expr": "More stable conjugate base ⇒ stronger acid"},
        ],
        "examples": [
            {"problem": "Why is trichloroacetic acid stronger than acetic acid?", "solution": "Three −I chlorines stabilise the carboxylate anion, favouring ionisation."},
            {"problem": "DoU of benzene C₆H₆?", "solution": "(12 + 2 − 6)/2 = 4 (3 π + 1 ring)."},
        ],
        "common_mistakes": [
            "Confusing the +I (donating) and −I (withdrawing) directions.",
            "Forgetting that resonance requires proper p-orbital overlap (planarity).",
        ],
        "pyq_highlights": [
            "Ranking acidity/basicity of a set of compounds.",
            "Identifying the most stable resonance contributor.",
        ],
        "practice": {"easy": "Identify hybridisation and count DoU.", "medium": "Order acidity/basicity with reasons.", "advanced": "Predict the dominant intermediate and product from electronic effects."},
    },
    {
        "chapter": "hydrocarbons",
        "theory": "Hydrocarbons contain only carbon and hydrogen: alkanes (saturated), alkenes and alkynes (unsaturated), and aromatics. Their reactions illustrate addition, substitution and the special stability of the aromatic ring.",
        "key_concepts": [
            "Markovnikov addition: the electrophile's H goes to the carbon with more hydrogens.",
            "Peroxides reverse the selectivity (anti-Markovnikov, radical mechanism) for HBr.",
            "Benzene prefers electrophilic substitution to preserve aromaticity.",
            "Terminal alkynes are weakly acidic (sp C–H).",
        ],
        "formulas": [
            {"name": "Markovnikov's rule", "expr": "H adds to the carbon already richer in H"},
            {"name": "Aromaticity (Hückel)", "expr": "planar, cyclic, conjugated, (4n+2) π electrons"},
        ],
        "examples": [
            {"problem": "HBr + propene (no peroxide) gives?", "solution": "2-bromopropane (Markovnikov)."},
            {"problem": "Most acidic: ethyne, ethene or ethane?", "solution": "Ethyne: its sp carbon holds the lone pair most tightly."},
        ],
        "common_mistakes": [
            "Forgetting the peroxide (anti-Markovnikov) exception applies only to HBr.",
            "Expecting benzene to undergo addition like alkenes.",
        ],
        "pyq_highlights": [
            "Ozonolysis to deduce alkene structure.",
            "Directing effects in aromatic electrophilic substitution.",
        ],
        "practice": {"easy": "Predict simple addition products.", "medium": "Markovnikov vs peroxide selectivity.", "advanced": "Multi-step aromatic substitution with directing groups."},
    },
    {
        "chapter": "haloalkanes",
        "theory": "Haloalkanes are the workhorses of substitution and elimination chemistry. The competition between SN1, SN2, E1 and E2 is governed by substrate, nucleophile/base strength, and solvent.",
        "key_concepts": [
            "SN2: one step, back-side attack, inversion, favoured by 1° substrate + strong nucleophile.",
            "SN1: two steps via a carbocation, favoured by 3° substrate + polar protic solvent.",
            "Elimination competes with substitution, especially with strong bulky bases.",
            "Haloarenes are unreactive to ordinary nucleophilic substitution.",
        ],
        "formulas": [
            {"name": "SN2 kinetics", "expr": "rate = k[substrate][nucleophile] (2nd order)"},
            {"name": "SN1 kinetics", "expr": "rate = k[substrate] (1st order)"},
        ],
        "examples": [
            {"problem": "Which substrate reacts fastest by SN2?", "solution": "A primary (methyl) halide: least steric hindrance to back-side attack."},
            {"problem": "Stereochemical outcome of SN2 at a chiral centre?", "solution": "Inversion of configuration (Walden inversion)."},
        ],
        "common_mistakes": [
            "Assuming SN1 rate depends on nucleophile concentration.",
            "Overlooking elimination when a strong base is used.",
        ],
        "pyq_highlights": [
            "Predicting SN1/SN2/E1/E2 from given conditions.",
            "Stereochemistry of substitution reactions.",
        ],
        "practice": {"easy": "Classify substrate as 1°/2°/3°.", "medium": "Choose mechanism from conditions.", "advanced": "Predict stereochemistry and major elimination product."},
    },
    {
        "chapter": "alcohols",
        "theory": "Alcohols, phenols and ethers all contain C–O bonds but differ sharply in acidity and reactivity. Phenols are far more acidic than alcohols because the phenoxide ion is resonance-stabilised.",
        "key_concepts": [
            "Acidity: carboxylic acid > phenol > water > alcohol.",
            "Primary alcohols oxidise to aldehydes then carboxylic acids; secondary to ketones; tertiary resist.",
            "The Lucas test distinguishes 1°/2°/3° alcohols by reaction rate.",
            "Ethers are relatively inert but cleave with hot HI.",
        ],
        "formulas": [
            {"name": "Oxidation ladder", "expr": "1° alcohol → aldehyde → carboxylic acid"},
        ],
        "examples": [
            {"problem": "Why is phenol more acidic than ethanol?", "solution": "Phenoxide spreads the negative charge over the ring by resonance; ethoxide cannot."},
            {"problem": "Isomeric alcohols of C₃H₈O?", "solution": "Propan-1-ol and propan-2-ol (two)."},
        ],
        "common_mistakes": [
            "Forgetting tertiary alcohols are not easily oxidised.",
            "Treating phenol as a typical (weak) alcohol.",
        ],
        "pyq_highlights": [
            "Distinguishing alcohols (Lucas, Victor Meyer).",
            "Reactions of phenol (electrophilic substitution, Reimer–Tiemann).",
        ],
        "practice": {"easy": "Classify and name alcohols.", "medium": "Predict oxidation products.", "advanced": "Multi-step synthesis involving phenols and ethers."},
    },
    {
        "chapter": "aldehydes-ketones",
        "theory": "The carbonyl group (C=O) is electrophilic at carbon and is the heart of this chapter. Nucleophilic addition, the aldol reaction, and characteristic tests (Tollens, Fehling, iodoform) recur constantly in JEE.",
        "key_concepts": [
            "Aldehydes are more reactive than ketones to nucleophilic addition (less steric/electronic hindrance).",
            "Aldol reactions need an α-hydrogen; those without one undergo Cannizzaro.",
            "Tollens'/Fehling's distinguish aldehydes from ketones (aldehydes reduce them).",
            "The iodoform test is positive for methyl ketones and CH₃CH(OH)– compounds.",
        ],
        "formulas": [
            {"name": "Nucleophilic addition", "expr": "Nu⁻ adds to C, O picks up H⁺"},
        ],
        "examples": [
            {"problem": "Which give a positive iodoform test: acetaldehyde, acetone, ethanol, benzaldehyde?", "solution": "Acetaldehyde, acetone and ethanol (benzaldehyde lacks the CH₃CO/CH₃CH(OH) group)."},
            {"problem": "Carbons in the acetaldehyde self-aldol product?", "solution": "CH₃CH(OH)CH₂CHO: four carbons."},
        ],
        "common_mistakes": [
            "Attempting an aldol on a carbonyl with no α-hydrogen.",
            "Expecting ketones to respond to Tollens' reagent.",
        ],
        "pyq_highlights": [
            "Distinguishing carbonyl compounds by chemical tests.",
            "Aldol vs Cannizzaro product prediction.",
        ],
        "practice": {"easy": "Identify aldehyde vs ketone reactivity.", "medium": "Predict aldol/Cannizzaro products.", "advanced": "Multi-step carbonyl synthesis and test-based identification."},
    },
    {
        "chapter": "carboxylic-acids",
        "theory": "Carboxylic acids and their derivatives (acid chlorides, anhydrides, esters, amides) are linked by nucleophilic acyl substitution. Acidity is enhanced by electron-withdrawing groups; derivative reactivity follows leaving-group ability.",
        "key_concepts": [
            "Acidity rises with −I substituents near the carboxyl group.",
            "Derivative reactivity: acid chloride > anhydride > ester > amide.",
            "Decarboxylation (soda lime) removes –COOH to give an alkane with one fewer carbon.",
            "Resonance in the carboxylate is what makes acids stronger than alcohols.",
        ],
        "formulas": [
            {"name": "Reactivity order", "expr": "RCOCl > (RCO)₂O > RCOOR' > RCONH₂"},
        ],
        "examples": [
            {"problem": "Strongest acid: chloroacetic, acetic, propanoic, ethanol?", "solution": "Chloroacetic acid (−I of Cl stabilises the anion)."},
            {"problem": "–COOH groups in oxalic acid?", "solution": "Two (HOOC–COOH)."},
        ],
        "common_mistakes": [
            "Reversing the derivative-reactivity order.",
            "Ignoring the distance of the −I group from the carboxyl (effect weakens with distance).",
        ],
        "pyq_highlights": [
            "Acidity ordering of substituted acids.",
            "Interconversion of acid derivatives.",
        ],
        "practice": {"easy": "Name acids and rank simple acidities.", "medium": "Predict derivative interconversions.", "advanced": "Multi-step synthesis through acid derivatives."},
    },
    {
        "chapter": "amines",
        "theory": "Amines are organic derivatives of ammonia and are basic/nucleophilic because of the nitrogen lone pair. Their basicity depends on substituents and solvent, and diazonium chemistry makes aromatic amines synthetically powerful.",
        "key_concepts": [
            "Basicity arises from the nitrogen lone pair accepting a proton.",
            "Aliphatic amines are more basic than aniline (whose lone pair is delocalised into the ring).",
            "Diazotisation (NaNO₂/HCl, 0–5 °C) converts aryl amines to diazonium salts.",
            "The carbylamine test is specific to primary amines.",
        ],
        "formulas": [
            {"name": "Diazotisation", "expr": "ArNH₂ + NaNO₂ + 2HCl → ArN₂⁺Cl⁻ + NaCl + 2H₂O"},
        ],
        "examples": [
            {"problem": "Stronger base: ethylamine or aniline?", "solution": "Ethylamine: aniline's lone pair is tied up in ring resonance."},
            {"problem": "Which amines give the carbylamine test?", "solution": "Only primary amines (including aniline)."},
        ],
        "common_mistakes": [
            "Assuming aromatic amines are stronger bases than aliphatic ones.",
            "Forgetting the low-temperature requirement for diazonium stability.",
        ],
        "pyq_highlights": [
            "Basicity ordering of amines (gas phase vs aqueous).",
            "Diazonium coupling and substitution reactions.",
        ],
        "practice": {"easy": "Classify amines and recall basicity origin.", "medium": "Order basicity with reasons.", "advanced": "Diazonium-based aromatic synthesis."},
    },
    {
        "chapter": "biomolecules",
        "theory": "Biomolecules are the chemistry of life: carbohydrates, proteins, nucleic acids, lipids and vitamins. JEE focuses on their classification, key functional groups and the bonds that build their polymers.",
        "key_concepts": [
            "Glucose is an aldohexose; fructose is a ketohexose.",
            "Amino acids link through peptide (amide) bonds to form proteins.",
            "DNA contains 2-deoxyribose; RNA contains ribose.",
            "Monosaccharides join by glycosidic bonds.",
        ],
        "formulas": [
            {"name": "Peptide bond", "expr": "–CO–NH– between amino acids"},
        ],
        "examples": [
            {"problem": "Classify glucose.", "solution": "An aldohexose (six carbons, aldehyde group)."},
            {"problem": "Sugar in DNA?", "solution": "2-deoxyribose."},
        ],
        "common_mistakes": [
            "Confusing the sugars of DNA and RNA.",
            "Mixing up glycosidic and peptide bonds.",
        ],
        "pyq_highlights": [
            "Structure-based classification of carbohydrates.",
            "Identifying linkages in biopolymers.",
        ],
        "practice": {"easy": "Classify common biomolecules.", "medium": "Identify functional groups and linkages.", "advanced": "Reactions distinguishing reducing/non-reducing sugars."},
    },
    {
        "chapter": "polymers",
        "theory": "Polymers are macromolecules built from repeating monomer units. They are classified by source, structure and mode of polymerisation (addition vs condensation), which determines their properties and uses.",
        "key_concepts": [
            "Addition polymers form from unsaturated monomers without losing atoms (e.g. polythene).",
            "Condensation polymers form with elimination of a small molecule (e.g. nylon, water).",
            "Natural rubber is cis-1,4-polyisoprene.",
            "Cross-linking (vulcanisation) hardens and strengthens rubber.",
        ],
        "formulas": [
            {"name": "Addition polymerisation", "expr": "n(CH₂=CH₂) → –(CH₂–CH₂)ₙ–"},
        ],
        "examples": [
            {"problem": "Classify nylon-6,6.", "solution": "A condensation polymer (diamine + diacid, losing water)."},
            {"problem": "Monomer of polythene?", "solution": "Ethene."},
        ],
        "common_mistakes": [
            "Confusing addition and condensation classifications.",
            "Misremembering monomers of common polymers.",
        ],
        "pyq_highlights": [
            "Match polymer to monomer and type.",
            "Properties from structure (thermoplastic vs thermosetting).",
        ],
        "practice": {"easy": "Identify monomer and polymer type.", "medium": "Classify by structure and source.", "advanced": "Mechanistic distinction of polymerisation modes."},
    },
]
