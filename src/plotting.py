import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Union

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
    print(f"Infection curve plot saved to {output_path}")
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
    else: # Fallback: calculate based on change in susceptible (less robust if R can go to S)
        initial_susceptible = df.loc[df['day'] == 0, 'susceptible'].iloc[0] if not df.empty else population_size_from_config
        final_susceptible = df['susceptible'].iloc[-1] if not df.empty else population_size_from_config
        metrics['total_ever_infected'] = initial_susceptible - final_susceptible + (population_size_from_config - initial_susceptible) # S_0 - S_final + I_0
        # This fallback needs to consider initial infected count for accuracy.
        # For now, assuming 'newly_infected_today' is the primary source.
        # A more robust fallback: initial_infected_count + sum of positive changes in 'infected' or 'recovered'

    metrics['final_susceptible_count'] = df['susceptible'].iloc[-1] if not df.empty else population_size_from_config
    # metrics['final_recovered_count'] = df['recovered'].iloc[-1] if not df.empty else 0
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
        print("No summary metrics to plot.")
        return

    # Ensure sim_names are assigned to the metrics before creating DataFrame if not already present
    # This step is usually done in main.py before calling this function.
    # df_metrics = pd.DataFrame(summary_metrics_list, index=sim_names) 
    # Let's assume 'simulation_name' is a key in each dict in summary_metrics_list
    df_metrics = pd.DataFrame(summary_metrics_list)
    if 'simulation_name' not in df_metrics.columns and sim_names and len(sim_names) == len(df_metrics):
        df_metrics['simulation_name'] = sim_names 
    
    if 'simulation_name' in df_metrics.columns:
        df_metrics.set_index('simulation_name', inplace=True)
    else:
        # Fallback if simulation_name is somehow missing, use provided sim_names if lengths match
        if sim_names and len(sim_names) == len(df_metrics):
            df_metrics.index = sim_names
        else:
            print("Warning: Cannot set simulation names as index for summary metrics plot.")
            # Proceed with default numerical index if names are problematic

    # Select only the metrics we want to plot
    metrics_to_plot = [
        'peak_infected_count',
        'days_to_peak',
        'total_ever_infected',
        'final_susceptible_count'
    ]
    # Filter out metrics not present in the DataFrame to avoid KeyErrors
    plottable_metrics = [metric for metric in metrics_to_plot if metric in df_metrics.columns]
    df_plot = df_metrics[plottable_metrics]

    if df_plot.empty:
        print("No data available for the selected metrics to plot.")
        return

    num_metrics = len(df_plot.columns)
    num_simulations = len(df_plot.index)

    fig, ax = plt.subplots(figsize=(max(10, num_simulations * num_metrics * 0.5), 7))
    
    metric_name_map = {
        'peak_infected_count': 'Peak Infected',
        'days_to_peak': 'Days to Peak',
        'total_ever_infected': 'Total Infected',
        'final_susceptible_count': 'Final Susceptible'
    }
    df_plot = df_plot.rename(columns=metric_name_map)

    df_plot.plot(kind='bar', ax=ax, width=0.8)

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
    print(f"Consolidated summary metrics bar plot saved to {output_filename}")
    plt.close(fig)
