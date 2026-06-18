"""Premium lesson content: Advanced Mathematics."""

LESSONS = [
    {
        "chapter": "algebra",
        "theory": "Algebra is the language of structure and pattern. JEE algebra spans quadratic equations, complex numbers, sequences and series, the binomial theorem, and matrices and determinants. Mastery comes from knowing the standard results cold and recognising which tool a problem invites.",
        "key_concepts": [
            "For ax² + bx + c = 0: sum of roots = −b/a, product = c/a.",
            "The discriminant b² − 4ac decides the nature of the roots.",
            "Complex numbers obey i² = −1; use modulus–argument form for powers and roots.",
            "AP, GP and the binomial theorem each have a small set of must-know formulas.",
        ],
        "formulas": [
            {"name": "Quadratic roots", "expr": "x = [−b ± √(b² − 4ac)] / 2a"},
            {"name": "Sum of n naturals", "expr": "Σk = n(n+1)/2"},
            {"name": "GP sum", "expr": "S_n = a(rⁿ − 1)/(r − 1)"},
            {"name": "Binomial term", "expr": "T_{r+1} = ⁿC_r · aⁿ⁻ʳ · bʳ"},
        ],
        "examples": [
            {"problem": "Find the sum of the roots of x² − 5x + 6 = 0.", "solution": "Sum = −b/a = 5."},
            {"problem": "How many terms are in (x + y)¹⁰?", "solution": "n + 1 = 11 terms."},
        ],
        "common_mistakes": [
            "Forgetting to check the discriminant before assuming real roots.",
            "Sign slips in the quadratic formula and in root relations.",
        ],
        "pyq_highlights": [
            "Common roots of two quadratics and condition problems.",
            "Greatest term and middle term in binomial expansions.",
        ],
        "practice": {"easy": "Root sums/products and AP–GP sums.", "medium": "Complex-number loci and binomial coefficients.", "advanced": "Matrix equations and determinant identities."},
    },
    {
        "chapter": "trigonometry",
        "theory": "Trigonometry studies angles and the periodic functions built from them. Beyond the basic ratios, the identities (Pythagorean, sum/difference, multiple-angle) let you simplify and solve equations. Inverse trigonometric functions and their principal ranges are a frequent JEE theme.",
        "key_concepts": [
            "sin²θ + cos²θ = 1 underlies most simplifications.",
            "Know the exact values at 0°, 30°, 45°, 60°, 90°.",
            "a·sinθ + b·cosθ has amplitude √(a² + b²).",
            "Always respect the principal-value range of inverse functions.",
        ],
        "formulas": [
            {"name": "Pythagorean identity", "expr": "sin²θ + cos²θ = 1"},
            {"name": "Compound angle", "expr": "sin(A ± B) = sinA·cosB ± cosA·sinB"},
            {"name": "Double angle", "expr": "sin2θ = 2sinθ·cosθ,  cos2θ = 1 − 2sin²θ"},
            {"name": "Max of a sinθ + b cosθ", "expr": "√(a² + b²)"},
        ],
        "examples": [
            {"problem": "Maximum value of 3sinθ + 4cosθ?", "solution": "√(3² + 4²) = 5."},
            {"problem": "Period of sin x?", "solution": "2π."},
        ],
        "common_mistakes": [
            "Losing solutions when squaring a trigonometric equation.",
            "Ignoring the domain/range restrictions of inverse trig functions.",
        ],
        "pyq_highlights": [
            "General solutions of trigonometric equations.",
            "Identities involving inverse trigonometric functions.",
        ],
        "practice": {"easy": "Standard values and basic identities.", "medium": "Solving trig equations on an interval.", "advanced": "Inverse-trig identities and conditional maxima."},
    },
    {
        "chapter": "coordinate-geometry",
        "theory": "Coordinate geometry turns geometric questions into algebra on the Cartesian plane. Straight lines, circles and the conic sections (parabola, ellipse, hyperbola) each have standard forms whose parameters carry geometric meaning: slope, radius, foci and eccentricity.",
        "key_concepts": [
            "Slope and intercept read directly off y = mx + c.",
            "A circle x² + y² = r² is centred at the origin with radius r.",
            "Eccentricity classifies conics: circle 0, ellipse <1, parabola 1, hyperbola >1.",
            "Distance and section formulas solve most point-based questions.",
        ],
        "formulas": [
            {"name": "Distance", "expr": "d = √[(x₂−x₁)² + (y₂−y₁)²]"},
            {"name": "Slope form", "expr": "y = mx + c"},
            {"name": "Circle", "expr": "(x−h)² + (y−k)² = r²"},
            {"name": "Parabola", "expr": "y² = 4ax (focus at (a,0))"},
        ],
        "examples": [
            {"problem": "Slope of 2x + 3y = 6?", "solution": "y = −(2/3)x + 2 ⇒ slope = −2/3."},
            {"problem": "Radius of x² + y² = 49?", "solution": "r = √49 = 7."},
        ],
        "common_mistakes": [
            "Confusing the standard forms of ellipse and hyperbola.",
            "Sign errors when completing the square to find a circle's centre.",
        ],
        "pyq_highlights": [
            "Tangents and normals to conics.",
            "Locus problems combining distance conditions.",
        ],
        "practice": {"easy": "Lines, distances and circle radii.", "medium": "Tangent and chord problems.", "advanced": "Conic loci and director circles."},
    },
    {
        "chapter": "calculus",
        "theory": "Calculus is the study of change and accumulation. Limits formalise the idea of approaching a value; derivatives measure instantaneous rate; integrals accumulate quantities and measure area. Differential equations then describe systems that evolve. It is the highest-weightage area in JEE mathematics.",
        "key_concepts": [
            "A function is differentiable only where it is continuous (not conversely).",
            "The standard limit limₓ→₀ (sin x)/x = 1 unlocks many others.",
            "Differentiation and integration are inverse operations (Fundamental Theorem).",
            "Definite integrals give signed area; use properties to simplify before integrating.",
        ],
        "formulas": [
            {"name": "Power rule", "expr": "d/dx(xⁿ) = n·xⁿ⁻¹"},
            {"name": "Product rule", "expr": "(uv)' = u'v + uv'"},
            {"name": "Standard integral", "expr": "∫xⁿ dx = xⁿ⁺¹/(n+1) + C"},
            {"name": "Fundamental theorem", "expr": "∫ₐᵇ f'(x) dx = f(b) − f(a)"},
        ],
        "examples": [
            {"problem": "Evaluate ∫₀² x dx.", "solution": "[x²/2]₀² = 4/2 − 0 = 2."},
            {"problem": "limₓ→₀ (sin x)/x?", "solution": "= 1 (standard limit)."},
        ],
        "common_mistakes": [
            "Forgetting the constant of integration in indefinite integrals.",
            "Applying L'Hôpital's rule to a limit that is not of indeterminate form.",
            "Differentiating a product term by term instead of using the product rule.",
        ],
        "pyq_highlights": [
            "Maxima/minima and monotonicity using the first/second derivative.",
            "Definite integrals using symmetry and king's-property.",
        ],
        "practice": {"easy": "Power-rule derivatives and basic integrals.", "medium": "Chain/product rule and definite integrals.", "advanced": "Maxima–minima, area between curves and differential equations."},
    },
    {
        "chapter": "vectors",
        "theory": "Vectors carry both magnitude and direction, making them ideal for geometry and physics in three dimensions. The dot product extracts the component along a direction (and detects perpendicularity); the cross product produces a perpendicular vector whose magnitude is an area.",
        "key_concepts": [
            "a·b = |a||b|cosθ; it is zero for perpendicular vectors.",
            "a×b is perpendicular to both a and b; |a×b| = |a||b|sinθ.",
            "The cross product is anti-commutative: a×b = −b×a.",
            "Scalar triple product [a b c] gives the volume of a parallelepiped.",
        ],
        "formulas": [
            {"name": "Magnitude", "expr": "|v| = √(x² + y² + z²)"},
            {"name": "Dot product", "expr": "a·b = |a||b|cosθ"},
            {"name": "Cross product magnitude", "expr": "|a×b| = |a||b|sinθ"},
            {"name": "Scalar triple product", "expr": "[a b c] = a·(b×c)"},
        ],
        "examples": [
            {"problem": "Magnitude of 3î + 4ĵ?", "solution": "√(9 + 16) = 5."},
            {"problem": "Dot product of two perpendicular vectors?", "solution": "cos90° = 0, so the dot product is 0."},
        ],
        "common_mistakes": [
            "Treating the cross product as commutative.",
            "Confusing the scalar (dot) and vector (cross) products.",
        ],
        "pyq_highlights": [
            "Coplanarity via the scalar triple product.",
            "Shortest distance between skew lines in 3D.",
        ],
        "practice": {"easy": "Magnitudes, dot and cross products.", "medium": "Projections, areas and angles.", "advanced": "3D lines, planes and shortest-distance problems."},
    },
    {
        "chapter": "probability",
        "theory": "Probability quantifies uncertainty. It begins with counting (permutations and combinations), then builds to conditional probability, independence, Bayes' theorem and random variables with their distributions. Careful definition of the sample space prevents most errors.",
        "key_concepts": [
            "Define the sample space precisely before counting outcomes.",
            "P(A∩B) = P(A)·P(B) only when A and B are independent.",
            "Conditional probability: P(A|B) = P(A∩B)/P(B).",
            "Bayes' theorem updates a prior using new evidence.",
        ],
        "formulas": [
            {"name": "Permutations", "expr": "ⁿP_r = n!/(n−r)!"},
            {"name": "Combinations", "expr": "ⁿC_r = n!/[r!(n−r)!]"},
            {"name": "Conditional probability", "expr": "P(A|B) = P(A∩B)/P(B)"},
            {"name": "Bayes' theorem", "expr": "P(A|B) = P(B|A)P(A)/P(B)"},
        ],
        "examples": [
            {"problem": "Arrange 3 distinct books in a row.", "solution": "3! = 6 ways."},
            {"problem": "Two dice: P(sum = 7)?", "solution": "6 favourable / 36 = 1/6."},
        ],
        "common_mistakes": [
            "Multiplying probabilities of events that are not independent.",
            "Double-counting outcomes or mis-specifying the sample space.",
        ],
        "pyq_highlights": [
            "Bayes'-theorem 'which urn / which machine' problems.",
            "Binomial-distribution expectation and variance.",
        ],
        "practice": {"easy": "Basic counting and equally-likely outcomes.", "medium": "Conditional probability and independence.", "advanced": "Bayes' theorem and binomial random variables."},
    },
]
