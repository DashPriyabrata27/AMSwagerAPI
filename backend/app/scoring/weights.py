# ============================================================
# Scoring Configuration
# Author Misattribution Detection System
# ============================================================


# 1. PROBLEM NAMES

PROBLEM_NAMES = {

    # Problem 1
    "P1": "Invalid or Future Work Years",

    # Problem 2
    "P2.a": "Extremely Yearly Publication Burst (10× Baseline)",
    "P2.b": "Short-Series Publication Burst Detection (2–4 Years)",

    # Problem 3
    "P3": "Long Work Span (>80 Years)",

    # Problem 4
    "P4": "Extreme Affiliations Detection",

    # Problem 5
    "P5.a": "Multiple ORCID IDs (2–3 ORCIDs)",
    "P5.b": "Excessive ORCID IDs (>3 ORCIDs)",

    # Problem 6
    "P6": "Empty Topics With Multiple Works",

    # Problem 7
    "P7": "Dominant Topic Share (topic share ≥ 50%)",

    # Problem 8
    "P8": "Name Quality Mismatch",

    # Problem 9
    "P9": "No Affiliation, Zero Impact, and High Work Count",

    # Problem 10
    "P10": "5 or More Countries in One Year",
}



# 2. INDIVIDUAL PROBLEM WEIGHTS

PROBLEM_WEIGHTS = {

    # Problem 1
    "P1": 2,

    # Problem 2
    "P2.a": 5,
    "P2.b": 5,

    # Problem 3
    "P3": 6,

    # Problem 4
    "P4": 3,

    # Problem 5
    "P5.a": 2,
    "P5.b": 9,

    # Problem 6
    "P6": 8,

    # Problem 7
    "P7": 1,

    # Problem 8
    "P8": 4,

    # Problem 9
    "P9": 7,

    # Problem 10
    "P10": 6,
}

# 3. SCORE CLASSIFICATIONS

SCORE_CLASSIFICATIONS = {

    "GOOD": {
        "min_score": 0,
        "max_score": 0,
    },

    "CANT_SAY": {
        "min_score": 1,
        "max_score": 3,
    },

    "SUSPICIOUS": {
        "min_score": 4,
        "max_score": None,
    },

}