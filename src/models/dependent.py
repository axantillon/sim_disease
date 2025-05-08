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
    alpha = infection_params.get('alpha', 0.1)  # Default alpha if not specified
    beta = infection_params.get('beta', 0.3)    # Default beta if not specified

    # Calculate sigmoid probability
    try:
        # Original logic: sigmoid_prob = 1 / (1 + math.exp(-alpha * k + beta))
        # This means a higher 'beta' increases probability for k=0, and shifts curve left.
        # A more standard sigmoid increasing with k might be 1 / (1 + math.exp(-(alpha * k - beta)))
        # Sticking to the existing formula's behavior.
        exponent_val = -alpha * k + beta 
        sigmoid_prob = 1 / (1 + math.exp(exponent_val))
    except OverflowError:
        # If exponent_val is very large positive, exp() overflows, sigmoid_prob approaches 0.
        # If exponent_val is very large negative, exp() approaches 0, sigmoid_prob approaches 1.
        if exponent_val > 0: # Likely means exp() overflowed
            sigmoid_prob = 0.0
        else: # Likely means exp() underflowed (approached 0)
            sigmoid_prob = 1.0
            
    # Adjust based on immunity and vaccine effectiveness
    final_prob_infection = sigmoid_prob * (1 - immune_level) * (1 - vaccine_effectiveness)
    return max(0.0, min(1.0, final_prob_infection)) # Ensure probability is bounded