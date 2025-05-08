# Experiment 2: Individual Heterogeneity & Probabilistic Defense

## Focus

This experiment explores how variability in individual-level defenses against infection, such as immune response and vaccine effectiveness, impacts the spread of a disease. Each individual's defensive attributes are sampled from probability distributions, introducing heterogeneity into the population's susceptibility.

## Discrete Probability Concepts Explored

1.  **Probabilistic Assignment of Attributes:**
    *   Individual characteristics like `immune_level` and `vaccine_effectiveness` are not uniform. Instead, they are sampled from specified probability distributions (e.g., Normal distributions defined by a mean `mu` and standard deviation `sigma`), as detailed in `src/graph_setup.py`.
    *   This sampling creates a population where each member has a distinct, probabilistically determined level of defense.

2.  **Conditional Infection Probability:**
    *   The probability of an individual becoming infected upon exposure is conditional on their specific `immune_level` and `vaccine_effectiveness`.
    *   For example, in the independent model, `P(Infection | Attributes) = base_prob * (1 - immune_level) * (1 - vaccine_effectiveness)`.
    *   This experiment will highlight how these conditional probabilities, varying across individuals, shape the epidemic.

3.  **Impact of Distribution Parameters:**
    *   By varying the `mu` (average) and `sigma` (spread) of the distributions for `immune_level` and/or `vaccine_effectiveness`, we can study how different population-wide defense profiles affect outcomes.
    *   For example, a high average `vaccine_effectiveness` with low variance should be more protective than a low average with high variance.

## Key Parameters to Vary

Within the `individual_parameters` section of the configuration:
*   `immune_level`: Vary `mu` and `sigma`.
*   `vaccine_effectiveness`: Vary `mu` and `sigma`.
    *   Focus will likely be on varying these for `vaccine_effectiveness` as per original Suite 3, or a combination.

## Expected Outcomes

*   Demonstrate that higher average levels of immunity or vaccine effectiveness in the population lead to smaller and slower outbreaks.
*   Show how higher variance (`sigma`) in these defensive attributes can lead to more unpredictable outcomes, potentially allowing for pockets of high susceptibility even if the average defense is reasonable.
*   Illustrate how individual probabilistic defenses collectively contribute to herd immunity effects (or lack thereof).

## Example Configuration Files in this Suite:

*   `exp2_low_avg_defense_low_variance.json` (e.g., low `vaccine_effectiveness.mu`, low `vaccine_effectiveness.sigma`)
*   `exp2_high_avg_defense_low_variance.json` (e.g., high `vaccine_effectiveness.mu`, low `vaccine_effectiveness.sigma`)
*   `exp2_medium_avg_defense_high_variance.json` (e.g., medium `vaccine_effectiveness.mu`, high `vaccine_effectiveness.sigma`)

*(These files will share common baseline parameters for `population_size`, `connections`, `initial_binomial_probability`, etc., while varying the specified `individual_parameters`.)*
