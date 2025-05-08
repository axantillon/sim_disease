import networkx as nx
from typing import Dict, Any

def calculate_probability(graph: nx.Graph, susceptible_node_id: int, config: Dict[str, Any]) -> float:
    """
    Calculates the total probability of infection for a susceptible node for the current day,
    based on the Independent Model.

    In this model, each infected neighbor contributes an independent chance of infection.
    The base probability of transmission from any single infected neighbor is adjusted by
    the susceptible node's immune level and vaccine effectiveness.

    The overall probability for the susceptible node is calculated by considering each
    infected neighbor: P(infection) = 1 - [ P(no infection from neighbor_1) *
                                            P(no infection from neighbor_2) * ... ]
    """
    susceptible_node = graph.nodes[susceptible_node_id]
    immune_level = susceptible_node.get('immune_level', 0.0)
    vaccine_effectiveness = susceptible_node.get('vaccine_effectiveness', 0.0)

    infection_params = config.get('infection_model', {}).get('infection_parameters', {})
    base_prob_transmission = infection_params.get('base_prob_transmission', 0.05) # Default if not specified

    prob_not_infected_by_any_neighbor = 1.0

    for neighbor_id in graph.neighbors(susceptible_node_id):
        if graph.nodes[neighbor_id].get('infection_state') == 'infected':
            # Probability of infection from THIS specific infected neighbor, adjusted by susceptible's defenses
            prob_infection_from_this_neighbor = base_prob_transmission * \
                                                (1 - immune_level) * \
                                                (1 - vaccine_effectiveness)
            # Ensure probability is bounded [0, 1]
            prob_infection_from_this_neighbor = max(0.0, min(1.0, prob_infection_from_this_neighbor))

            prob_not_infected_by_any_neighbor *= (1.0 - prob_infection_from_this_neighbor)

    final_prob_infection = 1.0 - prob_not_infected_by_any_neighbor
    return max(0.0, min(1.0, final_prob_infection)) # Ensure probability is bounded