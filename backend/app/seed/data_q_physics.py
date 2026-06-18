"""Advanced Physics question bank (JEE Advanced level)."""

QUESTIONS = [
    # ---------------- Mechanics ----------------
    {
        "chapter": "mechanics", "difficulty": "Easy", "concept": "Kinematics", "type": "single_correct",
        "prompt": "A ball is thrown vertically upward with a speed of 20 m/s (take g = 10 m/s²). How long after release does it return to the thrower's hand?",
        "options": ["2 s", "4 s", "1 s", "5 s"], "correct": 1,
        "solution": "Time to rise = v/g = 20/10 = 2 s. By symmetry the total time of flight is twice this, i.e. 4 s.",
    },
    {
        "chapter": "mechanics", "difficulty": "Easy", "concept": "Newton's Laws", "type": "single_correct",
        "prompt": "A 2 kg block rests on a frictionless surface and is pushed by a constant horizontal force of 10 N. Its acceleration is:",
        "options": ["5 m/s²", "2 m/s²", "10 m/s²", "20 m/s²"], "correct": 0,
        "solution": "a = F/m = 10/2 = 5 m/s².",
    },
    {
        "chapter": "mechanics", "difficulty": "Medium", "concept": "Work-Energy Theorem", "type": "integer",
        "prompt": "A 1 kg body is released from rest and falls freely through 5 m (g = 10 m/s²). Its kinetic energy on reaching the ground, in joules, is:",
        "correct": 50,
        "solution": "By the work–energy theorem KE = mgh = 1 × 10 × 5 = 50 J.",
    },
    {
        "chapter": "mechanics", "difficulty": "Medium", "concept": "Circular Motion", "type": "multiple_correct",
        "prompt": "For a particle in uniform circular motion, which quantities remain constant?",
        "options": ["Speed", "Velocity", "Kinetic energy", "Acceleration"], "correct": [0, 2],
        "solution": "Speed and kinetic energy are constant. Velocity changes (direction), and acceleration changes direction (it always points to the centre), so neither is constant.",
    },
    {
        "chapter": "mechanics", "difficulty": "Advanced", "concept": "Projectile Motion", "type": "numerical",
        "prompt": "A projectile is launched at 45° with speed 20 m/s (g = 10 m/s²). Find its horizontal range in metres.",
        "correct": 40.0, "tolerance": 0.5, "unit": "m",
        "solution": "R = v²·sin(2θ)/g = (400 × sin90°)/10 = 400/10 = 40 m.",
    },
    # ---------------- Waves ----------------
    {
        "chapter": "waves", "difficulty": "Medium", "concept": "Simple Harmonic Motion", "type": "single_correct",
        "prompt": "A mass of 1 kg on a spring of stiffness 100 N/m executes SHM. Its time period is closest to:",
        "options": ["0.63 s", "6.28 s", "0.10 s", "1.0 s"], "correct": 0,
        "solution": "T = 2π√(m/k) = 2π√(1/100) = 2π/10 ≈ 0.63 s.",
    },
    {
        "chapter": "waves", "difficulty": "Easy", "concept": "Wave Speed", "type": "single_correct",
        "prompt": "A wave is described by y = A sin(50x − 100t) (SI units). Its speed is:",
        "options": ["2 m/s", "5 m/s", "0.5 m/s", "50 m/s"], "correct": 0,
        "solution": "Speed v = ω/k = 100/50 = 2 m/s.",
    },
    {
        "chapter": "waves", "difficulty": "Easy", "concept": "Beats", "type": "integer",
        "prompt": "Two tuning forks of frequencies 256 Hz and 260 Hz are sounded together. The number of beats heard per second is:",
        "correct": 4,
        "solution": "Beat frequency = |f₁ − f₂| = |260 − 256| = 4 Hz.",
    },
    {
        "chapter": "waves", "difficulty": "Medium", "concept": "Organ Pipes", "type": "single_correct",
        "prompt": "The fundamental frequency of a closed organ pipe of length L compared with that of an open pipe of the same length is:",
        "options": ["Half", "Double", "Equal", "One quarter"], "correct": 0,
        "solution": "Closed pipe: f = v/4L. Open pipe: f = v/2L. So the closed pipe's fundamental is half that of the open pipe.",
    },
    # ---------------- Thermodynamics ----------------
    {
        "chapter": "thermodynamics", "difficulty": "Easy", "concept": "First Law", "type": "single_correct",
        "prompt": "A gas absorbs 100 J of heat and does 40 J of work on its surroundings. The change in its internal energy is:",
        "options": ["60 J", "140 J", "−60 J", "40 J"], "correct": 0,
        "solution": "ΔU = Q − W = 100 − 40 = 60 J.",
    },
    {
        "chapter": "thermodynamics", "difficulty": "Medium", "concept": "Isothermal Process", "type": "single_correct",
        "prompt": "For an isothermal process involving an ideal gas, the change in internal energy ΔU is:",
        "options": ["Zero", "Positive", "Negative", "Equal to nRT"], "correct": 0,
        "solution": "Internal energy of an ideal gas depends only on temperature; in an isothermal process T is constant, so ΔU = 0.",
    },
    {
        "chapter": "thermodynamics", "difficulty": "Medium", "concept": "Carnot Efficiency", "type": "integer",
        "prompt": "A Carnot engine operates between reservoirs at 400 K and 300 K. Its efficiency, expressed as a percentage, is:",
        "correct": 25,
        "solution": "η = 1 − T_c/T_h = 1 − 300/400 = 0.25 = 25%.",
    },
    {
        "chapter": "thermodynamics", "difficulty": "Advanced", "concept": "Adiabatic Process", "type": "multiple_correct",
        "prompt": "For a reversible adiabatic process on an ideal gas, which statements are correct?",
        "options": ["Q = 0", "ΔU = −W", "PVᵞ = constant", "Temperature stays constant"], "correct": [0, 1, 2],
        "solution": "Adiabatic means Q = 0, so the first law gives ΔU = −W. PVᵞ = constant holds. Temperature changes, so the last option is false.",
    },
    # ---------------- Electrostatics ----------------
    {
        "chapter": "electrostatics", "difficulty": "Easy", "concept": "Coulomb's Law", "type": "single_correct",
        "prompt": "Two equal point charges separated by a distance r experience a force F. If the separation is doubled, the new force is:",
        "options": ["F/4", "F/2", "2F", "4F"], "correct": 0,
        "solution": "F ∝ 1/r². Doubling r divides the force by 4.",
    },
    {
        "chapter": "electrostatics", "difficulty": "Medium", "concept": "Gauss's Law", "type": "single_correct",
        "prompt": "The net electric flux through a closed surface enclosing a total charge Q is:",
        "options": ["Q/ε₀", "Q/2ε₀", "Zero", "Qε₀"], "correct": 0,
        "solution": "By Gauss's law, Φ = Q_enclosed/ε₀.",
    },
    {
        "chapter": "electrostatics", "difficulty": "Medium", "concept": "Capacitor Energy", "type": "integer",
        "prompt": "A 2 μF capacitor is charged to 10 V. The energy stored, in microjoules (μJ), is:",
        "correct": 100,
        "solution": "U = ½CV² = ½ × 2 μF × (10)² = 100 μJ.",
    },
    {
        "chapter": "electrostatics", "difficulty": "Easy", "concept": "Electric Potential", "type": "single_correct",
        "prompt": "The work done in moving a charge between two points that are at the same potential is:",
        "options": ["Zero", "qV", "Positive", "Infinite"], "correct": 0,
        "solution": "W = qΔV. If the potential difference is zero, the work done is zero.",
    },
    {
        "chapter": "electrostatics", "difficulty": "Advanced", "concept": "Electric Field", "type": "numerical",
        "prompt": "Find the electric field (in N/C) at a distance of 1 m from a point charge of 1 nC. Take k = 9 × 10⁹ N·m²/C².",
        "correct": 9.0, "tolerance": 0.1, "unit": "N/C",
        "solution": "E = kq/r² = (9 × 10⁹ × 1 × 10⁻⁹)/1² = 9 N/C.",
    },
    # ---------------- Current Electricity ----------------
    {
        "chapter": "current-electricity", "difficulty": "Easy", "concept": "Ohm's Law", "type": "single_correct",
        "prompt": "A potential difference of 10 V is applied across a 5 Ω resistor. The current through it is:",
        "options": ["2 A", "0.5 A", "50 A", "5 A"], "correct": 0,
        "solution": "I = V/R = 10/5 = 2 A.",
    },
    {
        "chapter": "current-electricity", "difficulty": "Easy", "concept": "Resistor Combinations", "type": "single_correct",
        "prompt": "Two 6 Ω resistors are connected in parallel. The equivalent resistance is:",
        "options": ["3 Ω", "12 Ω", "6 Ω", "2 Ω"], "correct": 0,
        "solution": "1/R = 1/6 + 1/6 = 2/6 ⇒ R = 3 Ω.",
    },
    {
        "chapter": "current-electricity", "difficulty": "Medium", "concept": "Electrical Power", "type": "integer",
        "prompt": "A bulb rated 60 W operates at 120 V. Its resistance, in ohms, is:",
        "correct": 240,
        "solution": "R = V²/P = (120)²/60 = 14400/60 = 240 Ω.",
    },
    {
        "chapter": "current-electricity", "difficulty": "Medium", "concept": "Kirchhoff's Laws", "type": "single_correct",
        "prompt": "Kirchhoff's current law (junction rule) is a direct consequence of the conservation of:",
        "options": ["Charge", "Energy", "Momentum", "Mass"], "correct": 0,
        "solution": "The junction rule states that charge entering a node equals charge leaving it, conservation of charge.",
    },
    # ---------------- Magnetism ----------------
    {
        "chapter": "magnetism", "difficulty": "Easy", "concept": "Lorentz Force", "type": "single_correct",
        "prompt": "A charged particle moves parallel to a uniform magnetic field B. The magnetic force on it is:",
        "options": ["Zero", "qvB", "Maximum", "qE"], "correct": 0,
        "solution": "F = qv × B = qvB·sinθ. With θ = 0, sinθ = 0, so the force is zero.",
    },
    {
        "chapter": "magnetism", "difficulty": "Easy", "concept": "Force on a Conductor", "type": "single_correct",
        "prompt": "A straight wire of length L carrying current I in a field B feels a force F = BIL. If the current is doubled, the force becomes:",
        "options": ["2F", "F/2", "4F", "F"], "correct": 0,
        "solution": "F ∝ I, so doubling I doubles the force.",
    },
    {
        "chapter": "magnetism", "difficulty": "Medium", "concept": "Charged Particle in a Field", "type": "single_correct",
        "prompt": "A charged particle moves in a circle of radius r = mv/qB in a magnetic field. If its speed doubles, the radius becomes:",
        "options": ["Doubles", "Halves", "Unchanged", "Quadruples"], "correct": 0,
        "solution": "r ∝ v, so doubling the speed doubles the radius.",
    },
    {
        "chapter": "magnetism", "difficulty": "Advanced", "concept": "Magnetic Materials", "type": "multiple_correct",
        "prompt": "Which statements are true for diamagnetic materials?",
        "options": ["They are weakly repelled by a magnet", "Their relative permeability is slightly less than 1", "They have a permanent magnetic dipole moment", "They are strongly attracted to magnets"], "correct": [0, 1],
        "solution": "Diamagnetics are weakly repelled and have μ_r slightly < 1. They have no permanent dipole moment and are not strongly attracted (that describes ferromagnetics).",
    },
    # ---------------- EMI ----------------
    {
        "chapter": "emi", "difficulty": "Easy", "concept": "Faraday's Law", "type": "single_correct",
        "prompt": "According to Faraday's law, the magnitude of the induced EMF in a loop is proportional to the:",
        "options": ["Rate of change of magnetic flux", "Magnetic flux", "Current in the loop", "Resistance of the loop"], "correct": 0,
        "solution": "ε = −dΦ/dt: the induced EMF equals the rate of change of magnetic flux.",
    },
    {
        "chapter": "emi", "difficulty": "Medium", "concept": "Lenz's Law", "type": "single_correct",
        "prompt": "Lenz's law, which fixes the direction of the induced current, is a manifestation of the conservation of:",
        "options": ["Energy", "Charge", "Momentum", "Mass"], "correct": 0,
        "solution": "The induced current opposes the change producing it; otherwise energy would be created from nothing. It expresses conservation of energy.",
    },
    {
        "chapter": "emi", "difficulty": "Medium", "concept": "Inductor Energy", "type": "integer",
        "prompt": "A 2 H inductor carries a steady current of 3 A. The energy stored in its magnetic field, in joules, is:",
        "correct": 9,
        "solution": "U = ½LI² = ½ × 2 × 3² = 9 J.",
    },
    {
        "chapter": "emi", "difficulty": "Easy", "concept": "Transformers", "type": "single_correct",
        "prompt": "In an ideal step-up transformer, the secondary winding compared with the primary has:",
        "options": ["More turns", "Fewer turns", "Equal turns", "No turns"], "correct": 0,
        "solution": "V_s/V_p = N_s/N_p. To step the voltage up, the secondary needs more turns.",
    },
    # ---------------- Optics ----------------
    {
        "chapter": "optics", "difficulty": "Medium", "concept": "Lens Imaging", "type": "single_correct",
        "prompt": "An object is placed at a distance 2f from a thin convex lens of focal length f. The image is formed at:",
        "options": ["2f on the other side", "f", "Infinity", "At the lens"], "correct": 0,
        "solution": "Using 1/v − 1/u = 1/f with u = −2f gives v = 2f: a real, inverted, same-size image at 2f.",
    },
    {
        "chapter": "optics", "difficulty": "Easy", "concept": "Refraction", "type": "single_correct",
        "prompt": "When light travels from a denser medium into a rarer medium, it bends:",
        "options": ["Away from the normal", "Towards the normal", "Without bending", "Straight back"], "correct": 0,
        "solution": "Going to a rarer (lower-index) medium, the ray bends away from the normal.",
    },
    {
        "chapter": "optics", "difficulty": "Medium", "concept": "Young's Double Slit", "type": "integer",
        "prompt": "In Young's double-slit experiment the fringe width is β = λD/d. If the screen distance D is doubled (λ and d unchanged), the fringe width becomes how many times the original?",
        "correct": 2,
        "solution": "β ∝ D, so doubling D doubles the fringe width, a factor of 2.",
    },
    {
        "chapter": "optics", "difficulty": "Easy", "concept": "Power of a Lens", "type": "single_correct",
        "prompt": "A convex lens has a focal length of 50 cm. Its power is:",
        "options": ["2 D", "0.5 D", "50 D", "5 D"], "correct": 0,
        "solution": "P = 1/f(in metres) = 1/0.5 = 2 dioptre.",
    },
    # ---------------- Modern Physics ----------------
    {
        "chapter": "modern-physics", "difficulty": "Medium", "concept": "Photoelectric Effect", "type": "single_correct",
        "prompt": "In the photoelectric effect, increasing the intensity of light (at fixed frequency above threshold) increases the:",
        "options": ["Number of emitted photoelectrons", "Kinetic energy of each electron", "Threshold frequency", "Work function"], "correct": 0,
        "solution": "Intensity sets the photon rate, hence the number of photoelectrons. The maximum KE depends on frequency, not intensity.",
    },
    {
        "chapter": "modern-physics", "difficulty": "Medium", "concept": "Bohr Model", "type": "single_correct",
        "prompt": "In the Bohr model of the hydrogen atom, the energy of the nth orbit is:",
        "options": ["−13.6/n² eV", "−13.6n² eV", "13.6/n eV", "−13.6 eV (independent of n)"], "correct": 0,
        "solution": "E_n = −13.6/n² eV for hydrogen.",
    },
    {
        "chapter": "modern-physics", "difficulty": "Easy", "concept": "Nuclear Structure", "type": "integer",
        "prompt": "A nucleus contains 92 protons and 146 neutrons. Its mass number A is:",
        "correct": 238,
        "solution": "A = Z + N = 92 + 146 = 238.",
    },
    {
        "chapter": "modern-physics", "difficulty": "Easy", "concept": "Radioactive Decay", "type": "single_correct",
        "prompt": "After two half-lives, the fraction of the original radioactive nuclei that remains undecayed is:",
        "options": ["1/4", "1/2", "1/8", "0"], "correct": 0,
        "solution": "Each half-life halves the amount: (½)² = ¼.",
    },
    {
        "chapter": "modern-physics", "difficulty": "Advanced", "concept": "Photon Energy", "type": "numerical",
        "prompt": "Using E(eV) = 1240/λ(nm), find the energy (in eV) of a photon of wavelength 620 nm.",
        "correct": 2.0, "tolerance": 0.05, "unit": "eV",
        "solution": "E = 1240/620 = 2.0 eV.",
    },
]
