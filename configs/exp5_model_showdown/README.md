# Experiment 5: Unified Model Showdown - How Different Probabilistic Assumptions Compare

## Focus

This experiment provides a direct, side-by-side comparison of all three implemented infection models: Independent, Dependent (Sigmoid), and the custom Superspreader Dynamic. By running simulations with each model under a consistent set of baseline parameters (population size, network structure, initial conditions, individual defense profiles), this suite aims to highlight how their fundamentally different probabilistic assumptions about disease transmission lead to divergent epidemic outcomes.

## Discrete Probability Concepts Explored

This suite serves as a comparative showcase for the discrete probability concepts detailed in Experiments 3 and 4:

1.  **Independent Model:** Emphasizes combined probability from multiple independent Bernoulli trials (each infected neighbor's transmission attempt).
    *   `P(Infection) = 1 - Π(1 - P_i)`

2.  **Dependent Model:** Highlights non-linear response to a count of discrete events (number of infected neighbors `k`), often using a sigmoid function.
    *   `P(Infection | k) = sigmoid(f(k)) * (adjustments)`

3.  **Superspreader Dynamic Model:** Introduces conditional probabilities based on a stochastic daily state (being a superspreader, determined by a Bernoulli trial) and the impact of rare, high-magnitude events.
    *   `P(Transmit | Is Superspreader)` vs. `P(Transmit | Not Superspreader)`.
    *   Daily `P(Become Superspreader)`.

By comparing these models, we can see how different ways of structuring probabilistic dependencies and events result in varied simulation behaviors.

## Key Parameters to Vary

*   The core variation is the `infection_model.type` itself (`"independent"`, `"dependent"`, `"superspreader_dynamic`).
*   For each model type, a representative "baseline" set of its specific `infection_parameters` will be used to ensure a fair comparison. For example:
    *   **Independent:** A standard `base_prob_transmission`.
    *   **Dependent:** A chosen `alpha` and `beta` that represent a moderate response.
    *   **Superspreader Dynamic:** Chosen `p_becomes_superspreader`, `normal_base_infectivity`, and `superspreader_multiplier` that represent a moderate version of this phenomenon.

All other simulation parameters (e.g., `population_size`, `connections`, `initial_binomial_probability`, `number_of_days`, `individual_parameters`) will be kept **constant** across the configurations in this suite to isolate the impact of the infection model's logic.

## Expected Outcomes

*   Clear visual and statistical comparison of epidemic curves (e.g., onset speed, peak prevalence, total infected) produced by each of the three models under identical baseline conditions.
*   Understanding of which model might produce more aggressive or contained outbreaks given its underlying probabilistic rules.
*   Appreciation for how different assumptions about the nature of infectious contact and individual infectivity (uniform, cumulative, or event-driven) translate into macroscopic differences in simulated epidemics.

## Example Configuration Files in this Suite:

*   `exp5_compare_independent.json`
*   `exp5_compare_dependent.json`
*   `exp5_compare_superspreader.json`

*(These three files will be largely identical except for the `infection_model` block, which will specify the type and its baseline parameters.)*
