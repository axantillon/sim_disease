import networkx as nx
import numpy as np
from typing import Dict, Any

def _sample_and_clip(mu: float, sigma: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Samples from a normal distribution and clips the value."""
    value = np.random.normal(loc=mu, scale=sigma)
    return np.clip(value, min_val, max_val)

def create_population_graph(config: Dict[str, Any]) -> nx.Graph:
    """
    Creates a NetworkX graph representing the population and initializes
    node and edge attributes based on the provided configuration.

    Args:
        config: A dictionary containing simulation parameters, including:
            - population_size (int): Number of nodes.
            - graph_type (str): Type of graph to generate. 
                                Supported: 'erdos_renyi', 'barabasi_albert', 'watts_strogatz'.
                                Defaults to 'erdos_renyi'.
            - connections (float/int): Meaning depends on graph_type:
                - 'erdos_renyi': Probability for edge creation (p).
                - 'barabasi_albert': Number of edges to attach from a new node to existing nodes (m).
                                     Must be an integer.
                - 'watts_strogatz': Number of nearest neighbors in ring (k).
                                    Must be an even integer.
            - initial_binomial_probability (float): Prob. of initial infection.
            - individual_parameters (dict): Contains distribution params for:
                - immune_level (dict): {'mu': float, 'sigma': float}
                - vaccine_effectiveness (dict): {'mu': float, 'sigma': float}
                - contact_chance (dict): {'mu': float, 'sigma': float}
                    (Note: threshold logic not implemented yet, only clipping)

    Returns:
        A NetworkX graph with initialized node and edge attributes.
    """
    n = config['population_size']
    connection_param = config['connections']
    initial_infection_prob = config['initial_binomial_probability']
    params = config['individual_parameters']
    graph_type = config.get('graph_type', 'erdos_renyi').lower()

    # Create the graph structure
    if graph_type == 'erdos_renyi':
        graph = nx.erdos_renyi_graph(n=n, p=float(connection_param))
    elif graph_type == 'barabasi_albert':
        m = int(connection_param)
        if m < 1 or m >= n:
            raise ValueError(f"For Barabasi-Albert graph, 'connections' (m) must be an integer >= 1 and < population_size. Got {m}")
        graph = nx.barabasi_albert_graph(n=n, m=m)
    elif graph_type == 'watts_strogatz':
        k = int(connection_param)
        if k % 2 != 0 or k >= n or k < 2:
            raise ValueError(f"For Watts-Strogatz graph, 'connections' (k) must be an even integer >= 2 and < population_size. Got {k}")
        graph = nx.watts_strogatz_graph(n=n, k=k, p=0.1)
    else:
        raise ValueError(f"Unsupported graph_type: {graph_type}. Supported types are 'erdos_renyi', 'barabasi_albert', 'watts_strogatz'.")

    # Initialize node attributes
    for node_id in graph.nodes():
        # Sample and assign immune level
        immune_params = params['immune_level']
        graph.nodes[node_id]['immune_level'] = _sample_and_clip(
            immune_params['mu'], immune_params['sigma']
        )

        # Sample and assign vaccine effectiveness
        vaccine_params = params['vaccine_effectiveness']
        graph.nodes[node_id]['vaccine_effectiveness'] = _sample_and_clip(
            vaccine_params['mu'], vaccine_params['sigma']
        )

        # Assign initial infection state
        is_infected = np.random.binomial(1, initial_infection_prob)
        graph.nodes[node_id]['infection_state'] = 'infected' if is_infected else 'susceptible'

    # Initialize edge attributes
    contact_params = params['contact_chance']
    for u, v in graph.edges():
        # Sample and assign contact chance
        # TODO: Clarify and implement threshold logic if needed beyond clipping
        graph.edges[u, v]['contact_chance'] = _sample_and_clip(
            contact_params['mu'], contact_params['sigma']
        )

    return graph
