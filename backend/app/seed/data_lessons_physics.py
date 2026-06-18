"""Premium lesson content: Advanced Physics."""

LESSONS = [
    {
        "chapter": "mechanics",
        "theory": "Mechanics is the study of motion and the forces that cause it. Kinematics describes motion using displacement, velocity and acceleration, while dynamics links motion to force through Newton's three laws. Energy and momentum give powerful conservation principles that often sidestep messy force analysis. For rigid bodies, the same ideas extend to torque, moment of inertia and angular momentum.",
        "key_concepts": [
            "Always start a force problem with a clearly labelled free-body diagram.",
            "Newton's second law applies along each axis independently: ΣF = ma.",
            "Use energy conservation when forces are conservative; use momentum conservation in collisions.",
            "Rotational analogues: torque τ = Iα, angular momentum L = Iω.",
        ],
        "formulas": [
            {"name": "Equation of motion", "expr": "v = u + at,  s = ut + ½at²,  v² = u² + 2as"},
            {"name": "Newton's second law", "expr": "F = ma"},
            {"name": "Work–energy theorem", "expr": "W_net = ΔKE = ½mv² − ½mu²"},
            {"name": "Projectile range", "expr": "R = u²·sin(2θ)/g"},
            {"name": "Angular momentum", "expr": "L = Iω,  τ = dL/dt"},
        ],
        "examples": [
            {"problem": "A 2 kg block on a frictionless incline of 30° is released. Find its acceleration (g = 10 m/s²).", "solution": "Along the incline: ma = mg·sin30° ⇒ a = g·sin30° = 10 × 0.5 = 5 m/s²."},
            {"problem": "A ball is projected at 45° with 20 m/s. Find the range (g = 10).", "solution": "R = u²·sin(2θ)/g = 400 × sin90°/10 = 40 m."},
        ],
        "common_mistakes": [
            "Forgetting that the normal force is not always equal to mg (e.g. on an incline or in a lift).",
            "Mixing up mass and weight; weight = mg is a force.",
            "Applying energy conservation when friction is present without including heat lost.",
        ],
        "pyq_highlights": [
            "Blocks-and-pulleys with constraint relations are a recurring favourite.",
            "Conservation of angular momentum in a contracting system (skater/turntable) appears often.",
        ],
        "practice": {"easy": "Single-block Newton's-law and uniform acceleration problems.", "medium": "Connected bodies, friction, and work–energy combinations.", "advanced": "Rotational dynamics with rolling and angular-momentum conservation."},
    },
    {
        "chapter": "waves",
        "theory": "A wave transports energy without transporting matter. Simple harmonic motion (SHM) is the building block: a restoring force proportional to displacement produces sinusoidal oscillation. Travelling waves superpose to give interference, standing waves and beats. Sound is a longitudinal pressure wave whose speed depends on the medium.",
        "key_concepts": [
            "SHM: acceleration is proportional and opposite to displacement (a = −ω²x).",
            "Superposition lets two waves add algebraically at every point.",
            "Standing waves form between fixed/free boundaries with quantised frequencies.",
            "Beats arise from two nearby frequencies; beat frequency = |f₁ − f₂|.",
        ],
        "formulas": [
            {"name": "SHM period", "expr": "T = 2π√(m/k)"},
            {"name": "Wave speed", "expr": "v = fλ = ω/k"},
            {"name": "Closed pipe frequencies", "expr": "f_n = (2n−1)v/4L"},
            {"name": "Beat frequency", "expr": "f_beat = |f₁ − f₂|"},
        ],
        "examples": [
            {"problem": "A 1 kg mass on a 100 N/m spring. Find the period.", "solution": "T = 2π√(m/k) = 2π√(1/100) = 2π/10 ≈ 0.63 s."},
            {"problem": "Two forks of 256 Hz and 260 Hz sound together. Beats per second?", "solution": "|260 − 256| = 4 beats/s."},
        ],
        "common_mistakes": [
            "Confusing the closed-pipe (odd harmonics) and open-pipe (all harmonics) series.",
            "Using v = fλ with frequency from the wrong medium when a wave crosses a boundary (f is unchanged, λ changes).",
        ],
        "pyq_highlights": [
            "Resonance-column / organ-pipe end-correction problems.",
            "Phase difference and path difference in superposition questions.",
        ],
        "practice": {"easy": "Period, frequency and wave-speed substitutions.", "medium": "Standing waves in strings and pipes.", "advanced": "Doppler effect with moving source and observer."},
    },
    {
        "chapter": "thermodynamics",
        "theory": "Thermodynamics relates heat, work and internal energy. The first law is energy conservation for a gas: ΔU = Q − W. The second law introduces entropy and limits efficiency. The kinetic theory connects macroscopic pressure and temperature to the microscopic motion of molecules.",
        "key_concepts": [
            "Internal energy of an ideal gas depends only on temperature.",
            "Sign convention: Q positive when heat is added, W positive when the gas does work.",
            "Isothermal (ΔU = 0), adiabatic (Q = 0), isochoric (W = 0) and isobaric processes.",
            "No engine can beat the Carnot efficiency between two temperatures.",
        ],
        "formulas": [
            {"name": "First law", "expr": "ΔU = Q − W"},
            {"name": "Work done by gas", "expr": "W = ∫P dV"},
            {"name": "Adiabatic relation", "expr": "PVᵞ = constant"},
            {"name": "Carnot efficiency", "expr": "η = 1 − T_c/T_h"},
        ],
        "examples": [
            {"problem": "A gas absorbs 100 J and does 40 J of work. Find ΔU.", "solution": "ΔU = Q − W = 100 − 40 = 60 J."},
            {"problem": "Carnot engine between 400 K and 300 K. Efficiency?", "solution": "η = 1 − 300/400 = 0.25 = 25%."},
        ],
        "common_mistakes": [
            "Getting the work sign wrong (work done ON vs BY the gas).",
            "Assuming ΔU ≠ 0 in an isothermal ideal-gas process.",
            "Using temperatures in Celsius instead of Kelvin in efficiency formulas.",
        ],
        "pyq_highlights": [
            "P–V cycle problems asking for net work as the enclosed area.",
            "Comparing isothermal and adiabatic curves on the same diagram.",
        ],
        "practice": {"easy": "Single-process first-law calculations.", "medium": "Multi-step cycles and net work.", "advanced": "Entropy change and Carnot-cycle reasoning."},
    },
    {
        "chapter": "electrostatics",
        "theory": "Electrostatics studies charges at rest and the fields they create. Coulomb's law gives the force; the electric field and potential package this information geometrically. Gauss's law exploits symmetry to find fields quickly, and capacitors store energy in the field between conductors.",
        "key_concepts": [
            "Field lines start on positive and end on negative charge; density indicates strength.",
            "Use Gauss's law when the charge distribution has spherical, cylindrical or planar symmetry.",
            "Potential is a scalar: superpose it by simple addition, which is easier than vectors.",
            "A conductor in equilibrium has zero internal field and is an equipotential.",
        ],
        "formulas": [
            {"name": "Coulomb's law", "expr": "F = kq₁q₂/r²"},
            {"name": "Field of a point charge", "expr": "E = kq/r²"},
            {"name": "Gauss's law", "expr": "Φ = ∮E·dA = q_enc/ε₀"},
            {"name": "Capacitor energy", "expr": "U = ½CV² = ½QV"},
        ],
        "examples": [
            {"problem": "Find E at 1 m from a 1 nC charge (k = 9×10⁹).", "solution": "E = kq/r² = 9×10⁹ × 1×10⁻⁹ / 1 = 9 N/C."},
            {"problem": "Energy stored in a 2 μF capacitor at 10 V?", "solution": "U = ½CV² = ½ × 2 × 10² = 100 μJ."},
        ],
        "common_mistakes": [
            "Adding fields as scalars instead of vectors.",
            "Forgetting that only enclosed charge contributes to Gauss's-law flux.",
            "Confusing the formulas U = ½CV² and Q = CV.",
        ],
        "pyq_highlights": [
            "Gauss's-law fields for spheres, shells and infinite sheets.",
            "Capacitor networks with dielectrics partly inserted.",
        ],
        "practice": {"easy": "Coulomb force and point-charge fields.", "medium": "Gauss's-law symmetry problems.", "advanced": "Capacitor networks and energy with dielectrics."},
    },
    {
        "chapter": "current-electricity",
        "theory": "Current electricity deals with moving charge in circuits. Ohm's law links voltage, current and resistance; Kirchhoff's laws (junction and loop) solve any network. Power dissipation and the behaviour of meters and cells round out the chapter.",
        "key_concepts": [
            "Kirchhoff's current law expresses charge conservation at a node.",
            "Kirchhoff's voltage law expresses energy conservation around a loop.",
            "Resistors add in series; reciprocals add in parallel.",
            "Real cells have internal resistance, reducing terminal voltage under load.",
        ],
        "formulas": [
            {"name": "Ohm's law", "expr": "V = IR"},
            {"name": "Series / parallel", "expr": "R_s = ΣR,  1/R_p = Σ(1/R)"},
            {"name": "Power", "expr": "P = VI = I²R = V²/R"},
            {"name": "Terminal voltage", "expr": "V = ε − Ir"},
        ],
        "examples": [
            {"problem": "Two 6 Ω resistors in parallel: equivalent resistance?", "solution": "1/R = 1/6 + 1/6 = 1/3 ⇒ R = 3 Ω."},
            {"problem": "A 60 W bulb at 120 V: find its resistance.", "solution": "R = V²/P = 14400/60 = 240 Ω."},
        ],
        "common_mistakes": [
            "Adding parallel resistances directly instead of using reciprocals.",
            "Ignoring internal resistance when comparing EMF and terminal voltage.",
            "Sign errors when applying the loop rule.",
        ],
        "pyq_highlights": [
            "Wheatstone-bridge balance and meter-bridge problems.",
            "Maximum-power-transfer and potentiometer questions.",
        ],
        "practice": {"easy": "Single-loop Ohm's-law circuits.", "medium": "Series–parallel reduction and power.", "advanced": "Multi-loop Kirchhoff and bridge circuits."},
    },
    {
        "chapter": "magnetism",
        "theory": "Magnetism describes forces between currents and moving charges. A charge moving in a magnetic field feels a velocity-dependent force; currents create fields described by the Biot–Savart and Ampère laws. Materials respond as dia-, para- or ferromagnets.",
        "key_concepts": [
            "The magnetic force qv×B is always perpendicular to velocity, so it does no work.",
            "A charge moving perpendicular to B travels in a circle of radius r = mv/qB.",
            "Use Ampère's law for symmetric current distributions (wires, solenoids).",
            "Diamagnetic μ_r < 1, paramagnetic μ_r slightly > 1, ferromagnetic μ_r ≫ 1.",
        ],
        "formulas": [
            {"name": "Lorentz force", "expr": "F = q(E + v×B)"},
            {"name": "Force on a wire", "expr": "F = BIL·sinθ"},
            {"name": "Circular-path radius", "expr": "r = mv/qB"},
            {"name": "Field of a long wire", "expr": "B = μ₀I/2πr"},
        ],
        "examples": [
            {"problem": "A charge moves parallel to B. Find the magnetic force.", "solution": "F = qvB·sinθ with θ = 0 ⇒ F = 0."},
            {"problem": "If a charged particle's speed doubles in a field, how does its circular radius change?", "solution": "r = mv/qB ∝ v, so the radius doubles."},
        ],
        "common_mistakes": [
            "Thinking the magnetic force can change a particle's speed (it cannot; it only turns it).",
            "Forgetting the sinθ factor in F = BIL·sinθ.",
        ],
        "pyq_highlights": [
            "Combined E and B fields (velocity selector, cyclotron).",
            "Force and torque on current loops (magnetic moment).",
        ],
        "practice": {"easy": "Force on charges and wires.", "medium": "Circular motion and fields of wires/solenoids.", "advanced": "Velocity selectors and current-loop torque."},
    },
    {
        "chapter": "emi",
        "theory": "Electromagnetic induction (EMI) is the production of EMF by a changing magnetic flux. Faraday's law gives the magnitude, Lenz's law the direction. Inductance quantifies the back-EMF of coils, and these ideas power AC circuits and transformers.",
        "key_concepts": [
            "Only a CHANGING flux induces an EMF (change B, area, or orientation).",
            "Lenz's law: the induced current opposes the change, a statement of energy conservation.",
            "An inductor stores energy ½LI² in its magnetic field.",
            "Transformers trade voltage for current via the turns ratio.",
        ],
        "formulas": [
            {"name": "Faraday's law", "expr": "ε = −dΦ/dt"},
            {"name": "Motional EMF", "expr": "ε = BLv"},
            {"name": "Inductor energy", "expr": "U = ½LI²"},
            {"name": "Transformer", "expr": "V_s/V_p = N_s/N_p"},
        ],
        "examples": [
            {"problem": "Energy stored in a 2 H inductor carrying 3 A.", "solution": "U = ½LI² = ½ × 2 × 9 = 9 J."},
            {"problem": "A step-up transformer has how many secondary turns relative to primary?", "solution": "More turns in the secondary, since V_s/V_p = N_s/N_p > 1."},
        ],
        "common_mistakes": [
            "Stating an EMF when the flux is large but constant (no change ⇒ no EMF).",
            "Reversing the induced-current direction (mis-applying Lenz's law).",
        ],
        "pyq_highlights": [
            "Rod-on-rails motional-EMF problems with circuit current.",
            "LR and LC transient analysis and AC resonance.",
        ],
        "practice": {"easy": "Faraday/Lenz qualitative direction questions.", "medium": "Motional EMF and inductor energy.", "advanced": "AC circuits, impedance and resonance."},
    },
    {
        "chapter": "optics",
        "theory": "Optics has two parts. Ray (geometric) optics treats light as straight-line rays and explains mirrors and lenses. Wave optics treats light as a wave and explains interference, diffraction and polarisation. The lens/mirror formulas and the double-slit experiment are central.",
        "key_concepts": [
            "Use a consistent sign convention (Cartesian) for all mirror/lens problems.",
            "Power of a lens P = 1/f (in metres), measured in dioptres.",
            "Interference needs coherent sources; bright fringes occur at path difference = nλ.",
            "Refraction bends light towards the normal entering a denser medium.",
        ],
        "formulas": [
            {"name": "Lens formula", "expr": "1/v − 1/u = 1/f"},
            {"name": "Lens power", "expr": "P = 1/f (f in metres)"},
            {"name": "Snell's law", "expr": "n₁·sinθ₁ = n₂·sinθ₂"},
            {"name": "Fringe width", "expr": "β = λD/d"},
        ],
        "examples": [
            {"problem": "Object at 2f from a convex lens of focal length f. Where is the image?", "solution": "1/v − 1/(−2f) = 1/f ⇒ v = 2f: a real, inverted, same-size image."},
            {"problem": "Power of a lens with f = 50 cm?", "solution": "P = 1/0.5 = 2 D."},
        ],
        "common_mistakes": [
            "Sign-convention errors in the lens/mirror formula.",
            "Forgetting that frequency (not wavelength) is unchanged across a refracting boundary.",
        ],
        "pyq_highlights": [
            "Lens-maker and combination-of-lenses problems.",
            "Young's double slit with a thin film or shifted fringes.",
        ],
        "practice": {"easy": "Single-lens/mirror imaging.", "medium": "Lens combinations and refraction.", "advanced": "Interference, thin films and diffraction gratings."},
    },
    {
        "chapter": "modern-physics",
        "theory": "Modern physics covers the quantum and nuclear world. Light shows particle behaviour in the photoelectric effect; matter shows wave behaviour (de Broglie). The Bohr model quantises atomic energy levels, and nuclear physics handles radioactivity, fission and fusion.",
        "key_concepts": [
            "Photon energy E = hf; the photoelectric maximum KE depends on frequency, not intensity.",
            "Bohr energy levels: E_n = −13.6/n² eV for hydrogen.",
            "Radioactive decay is exponential; each half-life halves the population.",
            "Mass number A = Z (protons) + N (neutrons).",
        ],
        "formulas": [
            {"name": "Photon energy", "expr": "E = hf = 1240/λ(nm) eV"},
            {"name": "Photoelectric equation", "expr": "KE_max = hf − φ"},
            {"name": "Bohr energy", "expr": "E_n = −13.6/n² eV"},
            {"name": "Decay law", "expr": "N = N₀e^(−λt),  t_½ = ln2/λ"},
        ],
        "examples": [
            {"problem": "Energy of a 620 nm photon?", "solution": "E = 1240/620 = 2.0 eV."},
            {"problem": "Fraction of nuclei left after two half-lives?", "solution": "(½)² = ¼."},
        ],
        "common_mistakes": [
            "Believing higher intensity raises the maximum KE of photoelectrons (it raises only their number).",
            "Dropping the negative sign or the 1/n² in Bohr energy levels.",
        ],
        "pyq_highlights": [
            "Photoelectric stopping-potential vs frequency graphs.",
            "Hydrogen spectral series (Lyman, Balmer) transitions.",
        ],
        "practice": {"easy": "Photon energy and basic decay fractions.", "medium": "Photoelectric and Bohr-model calculations.", "advanced": "Nuclear binding energy, Q-values and de Broglie wavelengths."},
    },
]
