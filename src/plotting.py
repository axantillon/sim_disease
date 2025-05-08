"""
Handles the generation of plots and extraction of summary metrics from simulation data.

This module provides functions to:
- Plot infection curves over time for one or more simulations.
- Extract key summary statistics (e.g., peak infected, total infected) from results.
- Plot grouped bar charts comparing summary metrics across multiple simulations.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

def plot_infection_curves(all_results: List[Dict[str, List[Any]]], 
                          sim_names: List[str], 
                          filename: str | Path,
                          comparison_name: str):
    """
    Generates and saves a plot showing the number of infected
    individuals over time from multiple simulation results on the same axes.

    Args:
        all_results: A list of dictionaries, where each dictionary contains
                     simulation results (e.g., 'day', 'infected').
        sim_names: A list of names corresponding to each simulation result, for labeling.
        filename: The path where the plot image will be saved.
        comparison_name: The name of the experiment suite/comparison.
    """
    plt.figure(figsize=(12, 7))

    colors = plt.cm.get_cmap('tab10', len(all_results)) # Get a colormap

    for i, results_data in enumerate(all_results):
        df = pd.DataFrame(results_data)
        sim_label_infected = f"{sim_names[i]} - Infected"

        plt.plot(df['day'], df['infected'], label=sim_label_infected, color=colors(i), linestyle='-')

    plt.xlabel("Days")
    plt.ylabel("Number of Individuals")
    plt.title(f"Infection Curves for {comparison_name}")
    plt.legend()
    plt.grid(True)

    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output_path, format='pdf', dpi=300, bbox_inches='tight')
    logger.info(f"Infection curve plot saved to {output_path}")
    plt.close()


def extract_summary_metrics(results_data: List[Dict[str, int]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts key summary metrics from simulation results data.

    Args:
        results_data: A list of dictionaries, where each dictionary contains
                      daily simulation results (e.g., 'day', 'susceptible', 'infected').
        config: The configuration dictionary for this simulation run.

    Returns:
        A dictionary containing summary metrics.
    """
    df = pd.DataFrame(results_data)
    metrics: Dict[str, Any] = {}

    population_size_from_config = config.get('population_size', 0)
    metrics['population_size_cfg'] = population_size_from_config

    if df.empty:
        metrics['peak_infected_count'] = 0
        metrics['peak_infected_percentage'] = 0.0
        metrics['days_to_peak'] = 0
        metrics['total_ever_infected'] = 0
        metrics['final_susceptible_count'] = population_size_from_config 
        return metrics

    # Calculate metrics
    metrics['peak_infected_count'] = df['infected'].max()
    if population_size_from_config > 0:
        metrics['peak_infected_percentage'] = (df['infected'].max() / population_size_from_config) * 100
    else:
        metrics['peak_infected_percentage'] = 0.0
    metrics['days_to_peak'] = df['infected'].idxmax() # Day number (index) of peak
    
    # Total ever infected: sum of newly_infected_today, or initial_infected + subsequent_newly_infected
    # If 'newly_infected_today' column exists and is accurate (includes day 0 as 0)
    if 'newly_infected_today' in df.columns:
        metrics['total_ever_infected'] = df['newly_infected_today'].sum()
    else: # Fallback: if 'newly_infected_today' column is missing.
        # This fallback calculates Total Ever Infected as: (Population at Day 0) - (Final Susceptible Count).
        # This is equivalent to I_0 + (S_0 - S_final) for a standard SIR model where S->I->R.
        # It relies on data from the DataFrame itself, which is more robust if config population is missing/zero.
        population_day_0 = df['susceptible'].iloc[0] + df['infected'].iloc[0] + df['recovered'].iloc[0]
        metrics['total_ever_infected'] = population_day_0 - df['susceptible'].iloc[-1]

    metrics['peak_infected_count'] = df['infected'].max() if not df.empty else 0
    peak_day_series = df[df['infected'] == metrics['peak_infected_count']].index
    metrics['days_to_peak'] = peak_day_series[0] if not peak_day_series.empty else 0

    metrics['final_susceptible_count'] = df['susceptible'].iloc[-1] if not df.empty else population_size_from_config
    return metrics


def plot_summary_metrics_bars(summary_metrics_list: List[Dict[str, Any]], 
                              sim_names: List[str], 
                              base_filename: Union[str, Path],
                              comparison_name: str):
    """
    Generates and saves a single grouped bar chart comparing key summary metrics 
    across multiple simulations.

    Args:
        summary_metrics_list: A list of dictionaries, where each dictionary contains
                              summary metrics for one simulation.
        sim_names: A list of names corresponding to each simulation, for labeling.
        base_filename: The base path and name for the output PDF file (e.g., "results/comp_summary").
        comparison_name: The name of the experiment suite/comparison.
    """
    if not summary_metrics_list:
        logger.warning("No summary metrics to plot.")
        return

    # Ensure sim_names are provided and match the length of summary_metrics_list
    if not sim_names or len(sim_names) != len(summary_metrics_list):
        logger.warning("Simulation names not provided or mismatch length with metrics list. Using default indexing for plot.")
        # Fallback: use default names or ensure 'simulation_name' key exists in metrics
        df_metrics = pd.DataFrame(summary_metrics_list)
    else:
        # Check if 'simulation_name' is already a key in the dictionaries
        if all('simulation_name' in m for m in summary_metrics_list):
            df_metrics = pd.DataFrame(summary_metrics_list)
            if not pd.Series(sim_names).equals(df_metrics['simulation_name']): # if provided sim_names differ from internal, warn or prioritize?
                logger.debug("Provided sim_names differ from 'simulation_name' key in metrics; using internal 'simulation_name'.")
        else: # 'simulation_name' is not in the dicts, so use sim_names as index
            for i, metric_dict in enumerate(summary_metrics_list):
                metric_dict['simulation_name'] = sim_names[i] # Add sim_name to each dict
            df_metrics = pd.DataFrame(summary_metrics_list)

    if 'simulation_name' in df_metrics.columns:
        df_metrics.set_index('simulation_name', inplace=True)
    else:
        logger.warning("Could not set 'simulation_name' as index.")
        # Proceed with default numerical index if names are problematic

    metrics_to_plot = [
        'peak_infected_count',
        'days_to_peak',
        'total_ever_infected',
        'final_susceptible_count'
    ]
    plot_df = df_metrics[[col for col in metrics_to_plot if col in df_metrics.columns]].copy()

    num_metrics = len(plot_df.columns)
    num_simulations = len(plot_df.index)

    fig, ax = plt.subplots(figsize=(max(10, num_simulations * num_metrics * 0.5), 7))
    
    metric_name_map = {
        'peak_infected_count': 'Peak Infected',
        'days_to_peak': 'Days to Peak',
        'total_ever_infected': 'Total Infected',
        'final_susceptible_count': 'Final Susceptible'
    }
    plot_df = plot_df.rename(columns=metric_name_map)

    plot_df.plot(kind='bar', ax=ax, width=0.8)

    ax.set_xlabel("Configuration Scenario")
    ax.set_ylabel("Metric Value")
    ax.set_title(f"Summary Metrics for {comparison_name}")
    ax.legend(title="Metrics")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, axis='y', linestyle='--')
    plt.tight_layout() # Adjust layout to make room for labels

    output_filename = Path(f"{base_filename}_grouped_summary.pdf")
    output_filename.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_filename, format='pdf', dpi=300, bbox_inches='tight')
    logger.info(f"Consolidated summary metrics bar plot saved to {output_filename}")
    plt.close(fig)
