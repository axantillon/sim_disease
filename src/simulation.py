"""
Core simulation logic for the disease spread model.

This module defines the `Simulation` class, which manages the setup,
execution (step-by-step), and results collection of a disease spread
simulation over a networked population.
"""
import networkx as nx
import numpy as np
from typing import Dict, Any, List, Set
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

from src.graph_setup import create_population_graph
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
        self.results: Dict[str, List[Any]] = {
            'day': [],
            'susceptible': [],
            'infected': [],
            'recovered': [],
            'newly_infected_today': []
        }
        self.results['newly_infected_today'].append(0) # Day 0 has 0 new infections

        self.last_superspreader_status_update_day = -1
        self.daily_superspreader_status_map: Dict[int, bool] = {}

        self._record_initial_state() 

    def run(self):
        """Runs the simulation for the configured number of days."""
        num_days = self.config.get('number_of_days', 100)
        logger.info(f"Starting simulation: {self.config.get('simulation_name', 'Unnamed Simulation')}")
        logger.info(f"Total days: {num_days}, Population size: {self.config.get('population_size')}")

        for day in range(1, num_days + 1): 
            self.step()

        logger.info("Simulation finished.")

    def step(self):
        """Advances the simulation by one day."""
        self.current_day += 1

        recovery_duration = self.config.get('recovery_duration_days', 14)
        newly_infected_today_count = 0 

        # --- Daily Superspreader Status Update (if model is superspreader_dynamic) ---
        infection_model_config = self.config.get('infection_model', {})
        model_type = infection_model_config.get('type', 'independent') # Default to 'independent'

        if model_type == "superspreader_dynamic":
            self.daily_superspreader_status_map, self.last_superspreader_status_update_day = \
                superspreader_model.determine_daily_status(
                    self.graph, 
                    self.config, 
                    self.current_day, 
                    self.last_superspreader_status_update_day, 
                    self.daily_superspreader_status_map
                )
        # --- End Daily Superspreader Status Update ---

        # --- Recovery Process ---
        for node_id, data in list(self.graph.nodes(data=True)):
            if data.get('infection_state') == 'infected':
                data['days_infected'] = data.get('days_infected', 0) + 1
                if data['days_infected'] >= recovery_duration:
                    self.graph.nodes[node_id]['infection_state'] = 'recovered'

        # --- Infection Process ---
        newly_infected_nodes: Set[int] = set() 

        # Pre-calculate daily superspreader status if using the dynamic model

        # --- Calculate New Infections ---
        for node_id, data in self.graph.nodes(data=True):
            if data.get('infection_state') == 'susceptible': 
                prob_infection_today = 0.0
                has_infected_neighbor = any(
                    self.graph.nodes[neighbor_id].get('infection_state') == 'infected' 
                    for neighbor_id in self.graph.neighbors(node_id)
                )

                if has_infected_neighbor:
                    if model_type == "independent":
                        prob_infection_today = independent_model.calculate_probability(
                            self.graph, node_id, self.config
                        )
                    elif model_type == "dependent": 
                        prob_infection_today = dependent_model.calculate_probability(
                            self.graph, node_id, self.config
                        )
                    elif model_type == "superspreader_dynamic":
                        prob_infection_today = superspreader_model.calculate_probability(
                            self.graph, node_id, self.config, self.daily_superspreader_status_map
                        )
                    else:
                        logger.error(f"Invalid or missing infection model type: {model_type}")
                        # Potentially fall back to a default model or raise an error
                        # For now, effectively disables infection if model is unknown.
                        pass 

                if np.random.rand() < prob_infection_today:
                    newly_infected_nodes.add(node_id)

        self.results['newly_infected_today'].append(len(newly_infected_nodes))

        # --- Update States for Newly Infected ---
        for node_id in newly_infected_nodes:
            self.graph.nodes[node_id]['infection_state'] = 'infected'
            self.graph.nodes[node_id]['days_infected'] = 0 # Reset days infected count

        # --- Record Daily Counts ---
        self._update_daily_counts()

    def _record_initial_state(self):
        """Records the initial state of the simulation (Day 0)."""
        s_count, i_count, r_count = 0, 0, 0
        for node_id, data in self.graph.nodes(data=True):
            if data['infection_state'] == 'susceptible':
                s_count += 1
            elif data['infection_state'] == 'infected':
                i_count += 1
            elif data['infection_state'] == 'recovered':
                r_count += 1
        
        self.results['day'].append(0)
        self.results['susceptible'].append(s_count)
        self.results['infected'].append(i_count)
        self.results['recovered'].append(r_count)
        # 'newly_infected_today' for day 0 is already set to 0 in __init__

    def _update_daily_counts(self):
        """Updates the daily counts for the current day."""
        s_count, i_count, r_count = 0, 0, 0
        for node_id, data in self.graph.nodes(data=True):
            if data['infection_state'] == 'susceptible':
                s_count += 1
            elif data['infection_state'] == 'infected':
                i_count += 1
            elif data['infection_state'] == 'recovered':
                r_count += 1
        
        self.results['day'].append(self.current_day)
        self.results['susceptible'].append(s_count)
        self.results['infected'].append(i_count)
        self.results['recovered'].append(r_count)

    def get_results(self) -> Dict[str, List]:
        """Returns the simulation results."""
        return self.results
