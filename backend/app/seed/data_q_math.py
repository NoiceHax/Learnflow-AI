"""Advanced Mathematics question bank (JEE Advanced level)."""

QUESTIONS = [
    # ---------------- Algebra ----------------
    {
        "chapter": "algebra", "difficulty": "Easy", "concept": "Quadratic Equations", "type": "single_correct",
        "prompt": "The sum of the roots of the equation x² − 5x + 6 = 0 is:",
        "options": ["5", "6", "−5", "1"], "correct": 0,
        "solution": "For ax² + bx + c = 0, the sum of roots is −b/a = 5.",
    },
    {
        "chapter": "algebra", "difficulty": "Easy", "concept": "Complex Numbers", "type": "single_correct",
        "prompt": "The value of i² (where i = √−1) is:",
        "options": ["−1", "1", "i", "−i"], "correct": 0,
        "solution": "By definition i = √−1, so i² = −1.",
    },
    {
        "chapter": "algebra", "difficulty": "Medium", "concept": "Binomial Theorem", "type": "integer",
        "prompt": "The number of terms in the binomial expansion of (x + y)¹⁰ is:",
        "correct": 11,
        "solution": "The expansion of (x + y)ⁿ has (n + 1) terms, so 10 + 1 = 11.",
    },
    {
        "chapter": "algebra", "difficulty": "Easy", "concept": "Sequences and Series", "type": "single_correct",
        "prompt": "The sum of the first n natural numbers is:",
        "options": ["n(n + 1)/2", "n²", "n(n − 1)/2", "n(n + 1)"], "correct": 0,
        "solution": "1 + 2 + … + n = n(n + 1)/2.",
    },
    {
        "chapter": "algebra", "difficulty": "Advanced", "concept": "Nature of Roots", "type": "multiple_correct",
        "prompt": "For the equation x² + x + 1 = 0, which statements are correct?",
        "options": ["Its discriminant is negative", "Its roots are complex conjugates", "Its roots are real", "The product of its roots is 1"], "correct": [0, 1, 3],
        "solution": "D = 1 − 4 = −3 < 0, so the roots are a pair of complex conjugates; they are not real. Product of roots = c/a = 1.",
    },
    # ---------------- Trigonometry ----------------
    {
        "chapter": "trigonometry", "difficulty": "Easy", "concept": "Fundamental Identity", "type": "single_correct",
        "prompt": "For any angle θ, the value of sin²θ + cos²θ is:",
        "options": ["1", "0", "2", "sin 2θ"], "correct": 0,
        "solution": "This is the Pythagorean identity: sin²θ + cos²θ = 1.",
    },
    {
        "chapter": "trigonometry", "difficulty": "Easy", "concept": "Standard Values", "type": "single_correct",
        "prompt": "The value of sin 30° is:",
        "options": ["1/2", "√3/2", "1", "0"], "correct": 0,
        "solution": "sin 30° = 1/2.",
    },
    {
        "chapter": "trigonometry", "difficulty": "Medium", "concept": "Maximum and Minimum", "type": "integer",
        "prompt": "The maximum value of the expression 3 sin θ + 4 cos θ is:",
        "correct": 5,
        "solution": "The maximum of a sin θ + b cos θ is √(a² + b²) = √(9 + 16) = 5.",
    },
    {
        "chapter": "trigonometry", "difficulty": "Medium", "concept": "Periodicity", "type": "single_correct",
        "prompt": "The fundamental period of the function f(x) = sin x is:",
        "options": ["2π", "π", "π/2", "4π"], "correct": 0,
        "solution": "sin x repeats every 2π, so its period is 2π.",
    },
    # ---------------- Coordinate Geometry ----------------
    {
        "chapter": "coordinate-geometry", "difficulty": "Easy", "concept": "Straight Lines", "type": "single_correct",
        "prompt": "The slope of the line 2x + 3y = 6 is:",
        "options": ["−2/3", "2/3", "3/2", "−3/2"], "correct": 0,
        "solution": "Rewrite as y = −(2/3)x + 2; the coefficient of x is the slope, −2/3.",
    },
    {
        "chapter": "coordinate-geometry", "difficulty": "Easy", "concept": "Distance Formula", "type": "single_correct",
        "prompt": "The distance of the point (3, 4) from the origin is:",
        "options": ["5", "7", "1", "25"], "correct": 0,
        "solution": "d = √(3² + 4²) = √25 = 5.",
    },
    {
        "chapter": "coordinate-geometry", "difficulty": "Easy", "concept": "Circles", "type": "integer",
        "prompt": "The radius of the circle x² + y² = 49 is:",
        "correct": 7,
        "solution": "x² + y² = r² with r² = 49, so r = 7.",
    },
    {
        "chapter": "coordinate-geometry", "difficulty": "Medium", "concept": "Conic Sections", "type": "single_correct",
        "prompt": "The eccentricity of a circle is:",
        "options": ["0", "1", "Between 0 and 1", "Greater than 1"], "correct": 0,
        "solution": "A circle is the special conic with eccentricity e = 0.",
    },
    # ---------------- Calculus ----------------
    {
        "chapter": "calculus", "difficulty": "Easy", "concept": "Differentiation", "type": "single_correct",
        "prompt": "The derivative of x² with respect to x is:",
        "options": ["2x", "x", "x²/2", "2"], "correct": 0,
        "solution": "d/dx (xⁿ) = n·xⁿ⁻¹, so d/dx (x²) = 2x.",
    },
    {
        "chapter": "calculus", "difficulty": "Easy", "concept": "Integration", "type": "single_correct",
        "prompt": "The indefinite integral ∫ x dx equals:",
        "options": ["x²/2 + C", "x² + C", "1 + C", "2x + C"], "correct": 0,
        "solution": "∫ xⁿ dx = xⁿ⁺¹/(n + 1) + C, giving x²/2 + C.",
    },
    {
        "chapter": "calculus", "difficulty": "Medium", "concept": "Limits", "type": "integer",
        "prompt": "The value of the limit limₓ→₀ (sin x)/x is:",
        "correct": 1,
        "solution": "This is the standard limit limₓ→₀ (sin x)/x = 1.",
    },
    {
        "chapter": "calculus", "difficulty": "Easy", "concept": "Differentiation", "type": "single_correct",
        "prompt": "The derivative of sin x with respect to x is:",
        "options": ["cos x", "−cos x", "sin x", "−sin x"], "correct": 0,
        "solution": "d/dx (sin x) = cos x.",
    },
    {
        "chapter": "calculus", "difficulty": "Medium", "concept": "Definite Integrals", "type": "numerical",
        "prompt": "Evaluate the definite integral ∫₀² x dx.",
        "correct": 2.0, "tolerance": 0.01,
        "solution": "∫₀² x dx = [x²/2]₀² = 4/2 − 0 = 2.",
    },
    # ---------------- Vectors ----------------
    {
        "chapter": "vectors", "difficulty": "Easy", "concept": "Dot Product", "type": "single_correct",
        "prompt": "The dot product of two non-zero perpendicular vectors is:",
        "options": ["0", "1", "The product of their magnitudes", "Undefined"], "correct": 0,
        "solution": "a·b = |a||b|cos θ; for θ = 90°, cos θ = 0, so the dot product is 0.",
    },
    {
        "chapter": "vectors", "difficulty": "Medium", "concept": "Cross Product", "type": "single_correct",
        "prompt": "For the standard unit vectors, î × ĵ equals:",
        "options": ["k̂", "−k̂", "ĵ", "0"], "correct": 0,
        "solution": "By the right-hand rule, î × ĵ = k̂.",
    },
    {
        "chapter": "vectors", "difficulty": "Easy", "concept": "Magnitude", "type": "integer",
        "prompt": "The magnitude of the vector 3î + 4ĵ + 0k̂ is:",
        "correct": 5,
        "solution": "|v| = √(3² + 4² + 0²) = √25 = 5.",
    },
    {
        "chapter": "vectors", "difficulty": "Advanced", "concept": "Cross Product Properties", "type": "multiple_correct",
        "prompt": "Which statements about the cross product a × b are correct?",
        "options": ["It is perpendicular to both a and b", "Its magnitude is |a||b| sin θ", "It is commutative", "Its result is a scalar"], "correct": [0, 1],
        "solution": "The cross product is a vector perpendicular to both inputs with magnitude |a||b| sin θ. It is anti-commutative (a × b = −b × a), not commutative.",
    },
    # ---------------- Probability ----------------
    {
        "chapter": "probability", "difficulty": "Easy", "concept": "Basic Probability", "type": "single_correct",
        "prompt": "The probability of obtaining a head in a single toss of a fair coin is:",
        "options": ["1/2", "1", "0", "1/4"], "correct": 0,
        "solution": "One favourable outcome out of two equally likely: 1/2.",
    },
    {
        "chapter": "probability", "difficulty": "Easy", "concept": "Axioms of Probability", "type": "single_correct",
        "prompt": "The probability of a certain (sure) event is:",
        "options": ["1", "0", "0.5", "Infinite"], "correct": 0,
        "solution": "A sure event always occurs, so its probability is 1.",
    },
    {
        "chapter": "probability", "difficulty": "Medium", "concept": "Permutations", "type": "integer",
        "prompt": "The number of ways to arrange 3 distinct books in a row on a shelf is:",
        "correct": 6,
        "solution": "3! = 3 × 2 × 1 = 6.",
    },
    {
        "chapter": "probability", "difficulty": "Medium", "concept": "Probability with Dice", "type": "single_correct",
        "prompt": "Two fair dice are rolled. The probability that the sum of the numbers shown is 7 is:",
        "options": ["1/6", "1/12", "1/36", "1/9"], "correct": 0,
        "solution": "There are 6 favourable pairs out of 36 outcomes: 6/36 = 1/6.",
    },
]
