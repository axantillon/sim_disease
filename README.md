# Disease Spread Simulation: Exploring Discrete Probability

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project simulates the spread of a disease through a networked population. The primary focus is **not** on creating a highly realistic epidemiological model, but rather on using the simulation framework as a tool to **explore and demonstrate various discrete probability concepts**. We investigate how different probabilistic assumptions for infection transmission, individual heterogeneity, and network structure influence the overall dynamics of the spread.

## Features

*   **Network-Based Simulation:** Models disease spread on a graph of individuals.
*   **SIR Model:** Individuals transition between Susceptible, Infected, and Recovered states.
*   **Multiple Graph Models:** Supports different network structures:
    *   Erdos-Renyi
    *   Barabasi-Albert
    *   Watts-Strogatz
*   **Modular Infection Models:** Allows for easy comparison of different transmission dynamics:
    *   **Independent Model:** Each infected neighbor poses an independent transmission risk.
    *   **Dependent Model:** Infection risk is a non-linear function of the number of infected neighbors.
    *   **Superspreader Dynamic Model:** Some individuals can become temporary superspreaders with increased infectivity.
*   **Configurable Individual Attributes:** Samples attributes like `immune_level` and `vaccine_effectiveness` from probability distributions.
*   **JSON-Based Configuration:** Flexible experiment setup using JSON files.
*   **Automated Outputs:** Generates infection curve plots and summary metrics (CSV) for analysis.

## Getting Started

Follow these steps to set up and run the simulation environment.

### Prerequisites

*   Python (3.9 or higher recommended)
*   `uv` (for environment and package management - highly recommended)

### Installation

1.  **Install `uv`** (if you haven't already):
    Refer to the official `uv` installation guide: [https://github.com/astral-sh/uv#installation](https://github.com/astral-sh/uv#installation)
    A common method is:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clone the Repository** (if you haven't already):
    ```bash
    git clone <your-repository-url>
    cd sim_disease 
    ```

3.  **Create a Virtual Environment and Install Dependencies:**
    Navigate to the project root directory (where `pyproject.toml` is located) and run:
    ```bash
    uv venv  # Creates a .venv directory
    uv sync  # Installs dependencies from pyproject.toml into the .venv
    ```

4.  **Activate the Virtual Environment:**
    ```bash
    source .venv/bin/activate
    ```
    (On Windows, use `.venv\Scripts\activate`)

### Verify Setup

Run a basic simulation to ensure everything is working:
```bash
python main.py configs/exp1_foundations/
```
This should create an output directory (e.g., `results/exp1_foundations/`) with plots and a CSV file.

## Running Simulations

The main script for running simulations is `main.py`.

### Command-Line Interface

```bash
python main.py <config_files_or_directory> [options]
```

**Arguments:**

*   `config_files_or_directory` (required): 
    *   Path to a single JSON configuration file.
    *   Paths to multiple JSON configuration files (space-separated).
    *   Path to a directory containing multiple JSON configuration files (a "suite").
*   `--output_dir <directory_name>` (optional):
    *   Specifies the base directory to save results. Defaults to `results/`.
*   `--comparison_name <name>` (optional):
    *   A name for the simulation run or suite. This is used for naming output subdirectories and plot titles. 
    *   Defaults to the input configuration file's stem (for single runs) or the directory name (for suites).

### Examples

*   **Running a Single Configuration:**
    ```bash
    python main.py configs/exp1_foundations/exp1_high_density_high_initial.json
    ```

*   **Running a Suite of Simulations (e.g., all configurations in a directory):**
    ```bash
    python main.py configs/exp_A_network_topology/
    ```
    This will process all `.json` files within the `configs/exp_A_network_topology/` directory.

*   **Specifying an Output Directory and Comparison Name:**
    ```bash
    python main.py configs/exp_A_network_topology/ --output_dir custom_runs --comparison_name topology_study_v1
    ```

### Output

*   Results are saved in a subdirectory within the specified `output_dir` (or `results/` by default). The subdirectory is named using the `comparison_name`.
*   **Plots:**
    *   `infection_curves.pdf`: Shows susceptible, infected, and recovered counts over time.
    *   `summary_metrics_grouped_summary.pdf`: Bar plots for key summary metrics (e.g., peak infected, total infected).
*   **Data:**
    *   `summary_metrics.csv`: A CSV file containing key metrics and configuration parameters for each simulation run in the suite.

## Configuration

Simulations are controlled by JSON configuration files located in the `configs/` directory. Each file defines the parameters for a single simulation run.

**Key Configuration Parameters:**

*   `simulation_name` (string, optional): A descriptive name for the simulation run.
*   `population_size` (integer): Total number of individuals in the network.
*   `graph_type` (string): Specifies the graph generation model. Options:
    *   `"erdos_renyi"`
    *   `"barabasi_albert"`
    *   `"watts_strogatz"`
*   `connections` (number): The meaning depends on `graph_type`:
    *   Erdos-Renyi: Probability `p` of an edge (0.0-1.0).
    *   Barabasi-Albert: Integer `m`, number of edges for new nodes (>=1).
    *   Watts-Strogatz: Integer `k`, initial number of neighbors (>=1). Also requires `rewiring_prob` (typically 0.0-1.0) within the config for WS graphs.
*   `initial_binomial_probability` (float): Probability that any individual is infected at Day 0.
*   `number_of_days` (integer): Duration of the simulation.
*   `individual_parameters` (object): Defines distributions (mean `mu`, std dev `sigma`) for:
    *   `immune_level`
    *   `vaccine_effectiveness`
    *   `contact_chance`
*   `infection_model` (object): Specifies the infection dynamics:
    *   `type` (string): Model type (e.g., `"independent"`, `"dependent"`, `"superspreader_dynamic"`).
    *   `recovery_duration` (integer): Days an individual stays infected.
    *   `infection_parameters` (object): Model-specific parameters (e.g., `base_prob_transmission` for independent model).

For detailed schema, refer to `SIMULATION_CONFIG_SCHEMA` in `src/config.py`. For concrete examples, see the README files and JSON configurations within the subdirectories of `configs/` (e.g., `configs/exp_A_network_topology/README.md`).

## Core Simulation Mechanics

*   **Population Network:** Individuals are nodes in a graph (`networkx`). The graph structure is determined by `graph_type` and `connections` (see Configuration section). Handled in `src/graph_setup.py`.
*   **Individual Attributes:** Sampled from distributions (configured via `individual_parameters`):
    *   `immune_level`: Base resistance (0.0-1.0).
    *   `vaccine_effectiveness`: Reduction in susceptibility (0.0-1.0).
    *   `contact_chance` (edge attribute): Baseline probability of effective contact. **Note:** This attribute is initialized but **not currently used** by infection models in `src/models/` for transmission probability calculation.
*   **Time Steps:** Discrete daily steps, up to `number_of_days`.
*   **SIR Model:** Individuals transition: Susceptible -> Infected -> Recovered.
    *   Recovery occurs after `recovery_duration` days (from `infection_model.recovery_duration`, defaults to 14).

## Modular Infection Models

Located in `src/models/`, these define how infection spreads. Chosen via `infection_model.type`.

1.  **Independent Model (`src/models/independent.py`)**
    *   Each infected neighbor is an independent transmission chance.
    *   `P_neighbor = base_prob_transmission * (1 - immune_level_susceptible) * (1 - vaccine_effectiveness_susceptible)`.
    *   `P_infection_overall = 1 - Π(1 - P_neighbor_i)`.
    *   Key config: `infection_model.infection_parameters.base_prob_transmission`.

2.  **Dependent Model (`src/models/dependent.py`)**
    *   Infection risk is a sigmoid function of the *number* of infected neighbors (`k`).
    *   `P_infection = sigmoid_base * (1 - immune_level_susceptible) * (1 - vaccine_effectiveness_susceptible)`,
        where `sigmoid_base = 1 / (1 + exp(-alpha * k + beta))`.
    *   Key configs: `alpha`, `beta` in `infection_parameters`.

3.  **Superspreader Dynamic Model (`src/models/superspreader.py`)**
    *   Individuals can stochastically become temporary 'superspreaders'.
    *   Superspreaders have a `superspreader_multiplier` applied to their base infectivity.
    *   Key configs: `p_becomes_superspreader`, `normal_base_infectivity`, `superspreader_multiplier` in `infection_parameters`.

## Experiment Suites Overview

The `configs/` directory contains subdirectories, each representing an experimental suite with its own `README.md` explaining its objectives:

*   **[Experiment 1: Foundations](./configs/exp1_foundations/README.md)**: Initial conditions and network reach.
*   **[Experiment 2: Individual Heterogeneity](./configs/exp2_heterogeneity/README.md)**: Probabilistic defense mechanisms.
*   **[Experiment 3: Core Transmission Mechanisms](./configs/exp3_core_mechanisms/README.md)**: Independent vs. cumulative risk.
*   **[Experiment 4: Superspreader Phenomenon](./configs/exp4_superspreader_phenomenon/README.md)**: Exploring the impact of superspreading events.
*   **[Experiment 5: Model Showdown](./configs/exp5_model_showdown/README.md)**: Comparing all implemented infection models.
*   **[Experiment A: Network Topology](./configs/exp_A_network_topology/README.md)**: Impact of Erdos-Renyi, Barabasi-Albert, and Watts-Strogatz graph structures.

## Project Structure

```
.sim_disease/
├── configs/                # Simulation configuration files (JSON) & suite READMEs
│   ├── exp1_foundations/
│   ├── exp2_heterogeneity/
│   ├── exp3_core_mechanisms/
│   ├── exp4_superspreader_phenomenon/
│   ├── exp5_model_showdown/
│   └── exp_A_network_topology/
├── results/                # Default output directory for simulation results
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py           # Configuration loading, schema validation
│   ├── simulation.py       # Main Simulation class (SIR model, daily steps)
│   ├── graph_setup.py      # Population graph generation & attribute initialization
│   ├── models/             # Infection model implementations
│   │   ├── __init__.py
│   │   ├── independent.py
│   │   ├── dependent.py
│   │   └── superspreader.py
│   └── plotting.py         # Plotting & summary metric functions
├── .gitignore
├── LICENSE
├── main.py                 # Main script to run simulations
├── PLAN.md                 # Project planning document (if used)
├── README.md               # This file
└── pyproject.toml          # Project dependencies (for uv/pip)
```

## Contributing

Contributions are welcome! If you have suggestions or find issues, please open an issue on the project's repository. For code contributions, please consider opening an issue first to discuss the proposed changes.

## Future Work

*   Explicitly model immunity waning (SIRS dynamics).
*   Integrate `contact_chance` edge attribute into infection probability calculations for relevant models.
*   Add more network generation models or allow importing pre-defined networks.
*   Enhance analysis and visualization tools (e.g., network visualizations of spread, statistical tests).
*   Introduce agent-based behaviors or spatial components.
*   Develop a more comprehensive automated test suite.
*   Explore optimization of simulation performance for larger networks/longer durations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
