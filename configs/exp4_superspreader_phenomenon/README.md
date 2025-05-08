# Experiment 4: The "Superspreader" Phenomenon - Rare Events, Large Impact

## Focus

This experiment delves into the custom "Superspreader Dynamic" infection model. It aims to understand how the introduction of individuals who can temporarily become highly infectious (superspreaders) – a phenomenon observed in real-world epidemics like COVID-19 – alters disease spread dynamics compared to models with more uniform infectivity.

## Discrete Probability Concepts Explored

1.  **Daily Bernoulli Trial for Superspreader Status:**
    *   Each infected individual undergoes a daily, independent Bernoulli trial with probability `p_becomes_superspreader` to determine if they become a superspreader for that day.
    *   This introduces a stochastic element where only a subset of infected individuals might amplify transmission on any given day.

2.  **Conditional Transmission Probability:**
    *   The probability of an infected individual transmitting the disease is conditional on their superspreader status for that day.
    *   If an individual is a superspreader, their `normal_base_infectivity` is multiplied by a `superspreader_multiplier`.
    *   `P(Transmit | Is Superspreader)` >> `P(Transmit | Is Not Superspreader)`.

3.  **Impact of Low-Frequency, High-Magnitude Events:**
    *   Superspreading events, even if individually rare (low `p_becomes_superspreader`), can have a disproportionately large impact on the overall number of infections due to the significantly increased infectivity (`superspreader_multiplier`).
    *   This experiment explores how these rare but potent events can drive epidemic trajectories.

## Key Parameters to Vary

Within the `infection_model.infection_parameters` for the `superspreader_dynamic` model:
*   `p_becomes_superspreader`: The daily probability an infected individual becomes a superspreader (e.g., 0.005, 0.01, 0.05).
*   `superspreader_multiplier`: The factor by which a superspreader's infectivity is increased (e.g., 5x, 10x, 20x).
*   `normal_base_infectivity`: The baseline infectivity for non-superspreader infected individuals.

## Expected Outcomes

*   Demonstrate that even a small probability of becoming a superspreader can significantly accelerate disease spread and increase the total number of infections if the infectivity multiplier is high.
*   Show scenarios where the epidemic is primarily driven by a few superspreading events, leading to more volatile or burst-like infection patterns.
*   Highlight the sensitivity of the model to both the chance of becoming a superspreader and the magnitude of increased infectivity when one does.

## Example Configuration Files in this Suite:

*   `exp4_superspreader_low_chance_low_impact.json` (low `p_becomes_superspreader`, low `superspreader_multiplier`)
*   `exp4_superspreader_high_chance_high_impact.json` (high `p_becomes_superspreader`, high `superspreader_multiplier`)
*   `exp4_superspreader_low_chance_high_impact.json` (low `p_becomes_superspreader`, high `superspreader_multiplier`)
*   `exp4_superspreader_baseline.json` (using default/medium parameters for this model)

*(These files will share common baseline parameters for `population_size`, `connections`, etc., primarily varying the `infection_parameters` within the `superspreader_dynamic` model.)*
