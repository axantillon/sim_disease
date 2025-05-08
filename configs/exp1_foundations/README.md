# Experiment 1: Foundations - Initial Conditions & Network Reach

## Focus

This experiment investigates how the initial conditions of the simulation, specifically the number of initially infected individuals and the overall connectivity of the population network, influence the early stages and overall trajectory of an epidemic. It explores how these foundational elements, governed by discrete probability, set the stage for disease spread.

## Discrete Probability Concepts Explored

1.  **Initial Infections (Binomial Process):**
    *   The number of individuals initially infected is determined by a Binomial distribution, where each individual in the population `N` has an `initial_binomial_probability` (`p`) of being infected at Day 0.
    *   The probability of exactly `k` individuals being initially infected is given by: `P(X=k) = C(N, k) * p^k * (1-p)^(N-k)`.
    *   This experiment will vary `initial_binomial_probability` to see how different starting numbers of infected individuals affect the outbreak.

2.  **Network Connectivity (Graph Density):**
    *   The `connections` parameter (influencing the average degree or edge probability, see `src/graph_setup.py` for implementation details, e.g., if it's a Barabasi-Albert `m` or Erdos-Renyi `p`) determines the density of the population graph.
    *   A denser graph means more potential discrete pathways (edges) for the disease to transmit along.
    *   This experiment will vary `connections` to study how the number of available transmission routes influences the speed and extent of the spread.

## Key Parameters to Vary

*   `initial_binomial_probability`: To see the effect of starting with fewer or more infected individuals (e.g., 0.005, 0.01, 0.02).
*   `connections` (or its equivalent like `m` for BA graphs or `p_edge` for ER graphs): To observe how network structure facilitates or hinders spread (e.g., sparse, medium, dense settings appropriate for the chosen graph model).

## Expected Outcomes

*   Demonstrate how a higher initial number of infected individuals leads to a faster and potentially larger outbreak.
*   Show that denser networks (more connections) typically result in more rapid and widespread epidemics due to increased opportunities for transmission.
*   Illustrate the stochastic nature of early spread based on these initial probabilistic conditions.

## Example Configuration Files in this Suite:

*   `exp1_low_density_low_initial.json`
*   `exp1_medium_density_high_initial.json`
*   `exp1_high_density_medium_initial.json`

*(These files will contain specific parameter settings for `population_size`, `connections` (or equivalent), `graph_type`, `initial_binomial_probability`, `number_of_days`, `individual_parameters`, and a chosen baseline `infection_model`.)*
