import networkx as nx
import numpy as np
import math # For exp in sigmoid, though now in models.dependent
import random # Though now primarily in models.superspreader
from typing import Dict, Any, List, Set # Added Set

from src.graph_setup import create_population_graph # Adjusted import path assuming src is on PYTHONPATH or relative
# Import model-specific functions
from src.models import independent as independent_model
from src.models import dependent as dependent_model
from src.models import superspreader as superspreader_model

class Simulation:
    """
    Manages the disease spread simulation process over a population graph.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the simulation environment.

        Args:
            config: A dictionary containing the simulation configuration parameters.
        """
        self.config = config
        self.graph = create_population_graph(config)
        self.current_day = 0
        # Initialize results structure - stores daily counts for now
        self.results: Dict[str, List[Any]] = {
            'day': [],
            'susceptible': [],
            'infected': [],
            'recovered': [],
            'newly_infected_today': [] # Added to track daily new infections
        }
        # Ensure newly_infected_today also has an entry for day 0
        self.results['newly_infected_today'].append(0) # Assume 0 newly infected on Day 0 itself
        self.record_stats() # Record initial state (Day 0)

        # For superspreader model state management
        self.daily_superspreader_status: Dict[int, bool] = {} 
        self.last_superspreader_status_update_day: int = -1

    def run(self):
        """Runs the simulation for the configured number of days."""
        print(f"Starting simulation for {self.config['number_of_days']} days...")
        for day in range(1, self.config['number_of_days'] + 1): # Start from Day 1
            self.step()
            if day % 10 == 0: # Optional progress update
                 print(f"--- Day {day} completed ---")
        print("Simulation finished.")

    def step(self):
        """Executes one time step (day) of the simulation."""
        if self.current_day >= self.config['number_of_days']:
            return

        newly_infected_today: Set[int] = set()
        newly_recovered_today: Set[int] = set()

        model_type = self.config.get('infection_model', {}).get('type', 'independent')

        # --- Daily Superspreader Status Update (if model is superspreader_dynamic) ---
        if model_type == "superspreader_dynamic":
            self.daily_superspreader_status, self.last_superspreader_status_update_day = \
                superspreader_model.determine_daily_status(
                    self.graph, 
                    self.config, 
                    self.current_day, 
                    self.last_superspreader_status_update_day, 
                    self.daily_superspreader_status
                )
        # --- End Daily Superspreader Status Update ---

        susceptible_nodes: List[int] = [] 
        for node_id, data in self.graph.nodes(data=True):
            if data.get('infection_state') == 'susceptible': # Use .get() for safety
                susceptible_nodes.append(node_id)
            elif data.get('infection_state') == 'infected':
                # Process recovery for infected nodes
                data['days_infected'] = data.get('days_infected', 0) + 1
                if data['days_infected'] >= data.get('recovery_duration', float('inf')):
                    newly_recovered_today.add(node_id)

        for susceptible_node_id in susceptible_nodes:
            prob_infection_today = 0.0
            has_infected_neighbor = any(
                self.graph.nodes[neighbor_id].get('infection_state') == 'infected' 
                for neighbor_id in self.graph.neighbors(susceptible_node_id)
            )

            if has_infected_neighbor:
                if model_type == "independent":
                    prob_infection_today = independent_model.calculate_probability(
                        self.graph, susceptible_node_id, self.config
                    )
                elif model_type == "dependent": 
                    prob_infection_today = dependent_model.calculate_probability(
                        self.graph, susceptible_node_id, self.config
                    )
                elif model_type == "superspreader_dynamic":
                    prob_infection_today = superspreader_model.calculate_probability(
                        self.graph, susceptible_node_id, self.config, self.daily_superspreader_status
                    )
                else:
                    # Fallback to independent if model type is unrecognized or not implemented
                    print(f"Warning: Unknown or unimplemented infection model type '{model_type}'. Defaulting to 'independent'.")
                    prob_infection_today = independent_model.calculate_probability(
                        self.graph, susceptible_node_id, self.config
                    )

            if np.random.rand() < prob_infection_today:
                newly_infected_today.add(susceptible_node_id)

        # Update states
        for node_id in newly_infected_today:
            self.graph.nodes[node_id]['infection_state'] = 'infected'
            self.graph.nodes[node_id]['days_infected'] = 0 # Reset days infected count
            # Symptomatic day calculation could also be reset/initialized here if needed
            # For now, assuming 'days_until_symptomatic' is set at graph creation and doesn't change

        for node_id in newly_recovered_today:
            self.graph.nodes[node_id]['infection_state'] = 'recovered'

        self.current_day += 1
        self.results['newly_infected_today'].append(len(newly_infected_today)) # Store count for this day
        self.record_stats()

    def record_stats(self):
        """Records the current state of the simulation (counts of S, I, R)."""
        susceptible_count = 0
        infected_count = 0
        recovered_count = 0
        for node_id in self.graph.nodes():
            state = self.graph.nodes[node_id].get('infection_state')
            if state == 'susceptible':
                susceptible_count += 1
            elif state == 'infected':
                infected_count += 1
            elif state == 'recovered':
                recovered_count += 1

        self.results['day'].append(self.current_day)
        self.results['susceptible'].append(susceptible_count)
        self.results['infected'].append(infected_count)
        self.results['recovered'].append(recovered_count)

    def get_results(self) -> Dict[str, List]:
        """Returns the simulation results."""
        return self.results
