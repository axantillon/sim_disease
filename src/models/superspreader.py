"""
Implements the 'superspreader_dynamic' infection probability model.

This model simulates scenarios where infected individuals can temporarily become
superspreaders, significantly increasing their infectivity. It consists of two main parts:
1. Daily Status Determination: Each infected individual has a daily probability
   of becoming a superspreader.
2. Probability Calculation: The chance of a susceptible individual getting infected
   depends on whether their infected neighbors are currently superspreaders.
   Superspreaders have their base infectivity amplified by a multiplier.

Parameters (from config):
- `p_becomes_superspreader`: Daily chance an infected person becomes a superspreader.
- `normal_base_infectivity`: Base infectivity for non-superspreaders.
- `superspreader_multiplier`: Factor by which `normal_base_infectivity` is multiplied
  for superspreaders.

The model also accounts for the susceptible individual's immune level and
vaccine effectiveness.
"""
import networkx as nx
import random
from typing import Dict, Any, Tuple

def determine_daily_status(
    graph: nx.Graph, 
    config: Dict[str, Any],
    current_day: int,
    last_status_update_day: int,
    existing_status: Dict[int, bool]
) -> Tuple[Dict[int, bool], int]:
    """
    Determines and returns the superspreader status for all infected individuals for the current day.
    The status is only recalculated if the current_day is different from last_status_update_day.
    This ensures the "dice roll" for becoming a superspreader happens once per infected person per day.

    Args:
        graph: The population graph.
        config: The simulation configuration.
        current_day: The current simulation day.
        last_status_update_day: The day on which the status was last updated.
        existing_status: The previously calculated daily superspreader status map.

    Returns:
        A tuple containing:
            - A dictionary mapping infected node_id to boolean (True if superspreader today, False otherwise).
            - The updated last_status_update_day (which will be current_day if updated).
    """
    if current_day == last_status_update_day:
        return existing_status, last_status_update_day # Status already up-to-date for today

    # It's a new day, or first time, so update the statuses
    new_daily_status: Dict[int, bool] = {}
    infection_params = config.get('infection_model', {}).get('infection_parameters', {})
    p_becomes_superspreader = infection_params.get('p_becomes_superspreader', 0.01) # Default if not in config

    for node_id, data in graph.nodes(data=True):
        if data.get('infection_state') == 'infected':
            if random.random() < p_becomes_superspreader:
                new_daily_status[node_id] = True
            else:
                new_daily_status[node_id] = False
    
    return new_daily_status, current_day

def calculate_probability(
    graph: nx.Graph, 
    susceptible_node_id: int, 
    config: Dict[str, Any], 
    daily_superspreader_status: Dict[int, bool]
) -> float:
    """
    Calculates the total probability of infection for a susceptible node for the current day,
    based on the "Superspreader Dynamic" model, using pre-determined daily superspreader statuses.
    
    Inspired by COVID-19, where some individuals become highly infectious.
    Superspreaders have their infectivity multiplied. Immunity and vaccine effectiveness reduce risk.
    """
    susceptible_node = graph.nodes[susceptible_node_id]
    immune_level = susceptible_node.get('immune_level', 0.0)
    vaccine_effectiveness = susceptible_node.get('vaccine_effectiveness', 0.0)

    infection_params = config.get('infection_model', {}).get('infection_parameters', {})
    normal_base_infectivity = infection_params.get('normal_base_infectivity', 0.05)
    superspreader_multiplier = infection_params.get('superspreader_multiplier', 10.0)

    prob_not_infected_by_any_neighbor = 1.0

    for neighbor_id in graph.neighbors(susceptible_node_id):
        if graph.nodes[neighbor_id].get('infection_state') == 'infected':
            is_superspreader = daily_superspreader_status.get(neighbor_id, False)

            current_base_infectivity = normal_base_infectivity
            if is_superspreader:
                current_base_infectivity *= superspreader_multiplier
            
            prob_infection_from_this_neighbor = current_base_infectivity * \
                                                (1 - immune_level) * \
                                                (1 - vaccine_effectiveness)
            prob_infection_from_this_neighbor = max(0.0, min(1.0, prob_infection_from_this_neighbor))

            prob_not_infected_by_any_neighbor *= (1.0 - prob_infection_from_this_neighbor)

    final_prob_infection = 1.0 - prob_not_infected_by_any_neighbor
    return max(0.0, min(1.0, final_prob_infection))