"""
Implements the 'dependent' (sigmoid-based) infection probability model.

In this model, the probability of a susceptible individual getting infected depends
on the *number* of its infected neighbors. This relationship is modeled using a
sigmoid function, where the probability increases as the count of infected
neighbors rises.

The sigmoid function's shape is controlled by 'alpha' (steepness) and 'beta'
(shift) parameters from the configuration. The resulting probability is then
adjusted by the susceptible individual's immune level and vaccine effectiveness.
"""
import networkx as nx
import math
from typing import Dict, Any

def calculate_probability(graph: nx.Graph, susceptible_node_id: int, config: Dict[str, Any]) -> float:
    """
    Calculates infection probability based on the Dependent (Sigmoid) Model.

    This model assumes the probability of infection for a susceptible node is a sigmoid
    function of the number of its infected neighbors (k). The probability is further
    adjusted by the susceptible node's immune level and vaccine effectiveness.
    
    P_infection = sigmoid(alpha * k - beta) * (1 - immune_level) * (1 - vaccine_effectiveness)
    (Note: Original code had +beta, common sigmoid form is -beta or a shift parameter,
     retaining +beta as per original internal logic: 1 / (1 + exp(-alpha * k + beta)))
    """
    susceptible_node = graph.nodes[susceptible_node_id]
    immune_level = susceptible_node.get('immune_level', 0.0)
    vaccine_effectiveness = susceptible_node.get('vaccine_effectiveness', 0.0)

    infected_neighbor_count = 0
    for neighbor_id in graph.neighbors(susceptible_node_id):
        if graph.nodes[neighbor_id].get('infection_state') == 'infected':
            infected_neighbor_count += 1

    k = infected_neighbor_count
    infection_params = config.get('infection_model', {}).get('infection_parameters', {})
    alpha = infection_params.get('alpha', 0.1)  # Steepness of the sigmoid
    beta = infection_params.get('beta', 3)    # Shift of the sigmoid

    exponent_val = -alpha * k + beta
    # Sticking to the existing formula's behavior.
    try:
        sigmoid_prob = 1 / (1 + math.exp(exponent_val))
    except OverflowError:
        # If exponent_val is very large positive, exp() overflows, sigmoid_prob approaches 0.
        # If exponent_val is very large negative, exp() approaches 0, sigmoid_prob approaches 1.
        sigmoid_prob = 0.0 if exponent_val > 0 else 1.0
            
    final_prob_infection = sigmoid_prob * (1 - immune_level) * (1 - vaccine_effectiveness)
    return max(0.0, min(1.0, final_prob_infection)) # Ensure probability is bounded