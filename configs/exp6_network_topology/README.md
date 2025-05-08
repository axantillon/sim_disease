# Experiment Suite A: Network Topology

**Objective:** To evaluate the impact of different network graph structures on disease spread dynamics while keeping other simulation parameters consistent.

This suite explores three common network generation models:

1.  **`expA_erdos_renyi.json`**: 
    *   **Graph Type:** Erdos-Renyi (ER)
    *   **Description:** In an ER graph, each possible edge between pairs of nodes is created with a fixed probability `p` (specified by the `"connections"` parameter in the config). This model tends to produce relatively homogeneous random graphs.

2.  **`expA_barabasi_albert.json`**:
    *   **Graph Type:** Barabasi-Albert (BA)
    *   **Description:** BA graphs are generated using a preferential attachment mechanism, where new nodes are more likely to connect to existing nodes that already have a high degree (many connections). This results in scale-free networks with a few highly connected hubs, often seen in real-world social networks. The `"connections"` parameter specifies `m`, the number of edges to attach from a new node to existing nodes.

3.  **`expA_watts_strogatz.json`**:
    *   **Graph Type:** Watts-Strogatz (WS)
    *   **Description:** WS graphs model small-world networks, characterized by high clustering (nodes tend to form tight-knit communities) and short average path lengths. They start from a regular ring lattice and then randomly rewire some edges. The `"connections"` parameter specifies `k`, the initial number of neighbors for each node in the ring lattice, and a `rewiring_prob` (e.g., 0.1) is also typically specified within the config file for this graph type (though not explicitly called `connections`).

**Common Parameters:**

Across all configurations in this suite, the following are generally kept consistent to isolate the effect of network topology:

*   `population_size`
*   `initial_binomial_probability` (initial number of infected individuals)
*   `number_of_days` (simulation duration)
*   `individual_parameters` (distributions for immune level, vaccine effectiveness, contact chance)
*   `infection_model` (e.g., 'independent' model with specific parameters like `base_prob_transmission`)

By comparing the simulation outputs (e.g., infection curves, peak infected, total infected) from these configurations, we can gain insights into how network structure influences the spread of a disease.
