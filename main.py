import argparse
import json
from pathlib import Path
from typing import List, Tuple, Optional # For type hints
import pandas as pd
import logging
import sys
import jsonschema

# Assumes main.py is in the root, and src/ contains the modules
from src.config import load_config, SIMULATION_CONFIG_SCHEMA
from src.simulation import Simulation
# Updated import to reflect new function names and additions
from src.plotting import plot_infection_curves, extract_summary_metrics, plot_summary_metrics_bars

# Configure basic logging
# This will be configured further inside main() to allow for different levels if needed in future
logger = logging.getLogger(__name__)


def _process_config_paths(config_file_args: List[str], initial_comparison_name: Optional[str]) -> Tuple[List[Path], str]:
    """
    Processes input configuration file arguments to determine actual config files and comparison name.

    Args:
        config_file_args: List of strings from command line (paths to files or a single directory).
        initial_comparison_name: The comparison name provided via command line, if any.

    Returns:
        A tuple containing:
            - A list of Path objects for the configuration files.
            - The determined comparison name (string).

    Raises:
        SystemExit: If config paths are invalid or no .json files are found in a directory.
    """
    actual_config_files: List[Path] = []
    final_comparison_name: str

    config_input_path_str = config_file_args[0]
    config_input_path = Path(config_input_path_str)

    if len(config_file_args) == 1 and config_input_path.is_dir():
        logger.info(f"Processing config suite from directory: {config_input_path}")
        actual_config_files = sorted(list(config_input_path.glob('*.json')))
        if not actual_config_files:
            logger.error(f"No .json files found in directory {config_input_path}. Exiting.")
            sys.exit(1)
        if initial_comparison_name is None:
            final_comparison_name = config_input_path.name
            logger.info(f"Using suite directory name '{final_comparison_name}' as comparison_name.")
        else:
            final_comparison_name = initial_comparison_name
    elif all(Path(f).is_file() and f.endswith('.json') for f in config_file_args):
        actual_config_files = [Path(f) for f in config_file_args]
        if initial_comparison_name is None:
            # If multiple files are given but no comparison name, create one from the first file's stem
            # or default to 'comparison' if only one non-suite file.
            if len(actual_config_files) > 1:
                 final_comparison_name = f"{actual_config_files[0].stem}_comparison"
            else:
                 final_comparison_name = actual_config_files[0].stem
            logger.info(f"Using '{final_comparison_name}' as comparison_name.")
        else:
            final_comparison_name = initial_comparison_name
    else:
        logger.error("Error: config_files must be a list of .json files or a single directory containing .json files.")
        invalid_paths = [f for f in config_file_args if not (Path(f).is_file() and f.endswith('.json')) and not (len(config_file_args) == 1 and Path(f).is_dir())]
        if invalid_paths:
            logger.error(f"Invalid paths provided or non-JSON files: {invalid_paths}")
        sys.exit(1)
    
    # Fallback if somehow still None (should be covered by logic above)
    if final_comparison_name is None:
        final_comparison_name = "comparison" 
        logger.info(f"Defaulting to 'comparison' as comparison_name.")

    return actual_config_files, final_comparison_name


def main():
    """
    Main entry point for running disease simulations.
    Parses command-line arguments for configuration files,
    runs the simulation(s), and saves the results plots, including comparative plots.
    """
    # Setup logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout) # Log to stdout
        ]
    )

    parser = argparse.ArgumentParser(
        description="Run disease simulations with specified configurations and plot results."
    )
    parser.add_argument(
        "config_files",
        nargs='+',
        help="Paths to configuration JSON files or a single path to a directory containing .json config files for a suite."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="Directory to save plots and summary CSV."
    )
    parser.add_argument(
        "--comparison_name",
        type=str,
        default=None, # Default to None, will be set later if a suite is run
        help="Base name for comparative plots and summary CSV. Defaults to the suite directory name if a directory is provided for config_files."
    )
    args = parser.parse_args()

    # --- Determine config file paths and comparison name using helper ---
    try:
        actual_config_files, comparison_name = _process_config_paths(args.config_files, args.comparison_name)
    except SystemExit:
        return # Exit if _process_config_paths decided to terminate

    base_output_dir = Path(args.output_dir)
    # Create a specific directory for this run/comparison suite
    run_output_dir = base_output_dir / comparison_name 
    run_output_dir.mkdir(parents=True, exist_ok=True)

    all_simulation_results = [] # Store raw results for each simulation
    all_configs = []  # To store loaded configs for metric extraction
    simulation_names = [] # To store names for plot legends

    logger.info(f"Processing {len(actual_config_files)} configuration(s)...")

    for config_file_path_obj in actual_config_files:
        config_file_path = str(config_file_path_obj) # Convert Path object to string for load_config
        logger.info(f"\n--- Processing configuration: {config_file_path} ---")
        try:
            config = load_config(config_file_path)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_file_path}. Skipping.")
            continue
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {config_file_path}: {e}. Skipping.")
            continue
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Invalid configuration in {config_file_path}:\n{e.message}\nSkipping.")
            # logger.debug(e) # Optionally log full validation error details for debugging
            continue

        all_configs.append(config)

        # Determine simulation name for plots/CSV
        sim_name = config.get("simulation_name", config_file_path_obj.stem) 
        simulation_names.append(sim_name)
        
        logger.info(f"--- Running Simulation: {sim_name} ---")
        simulation = Simulation(config)
        simulation.run()

        results = simulation.get_results()
        all_simulation_results.append(results)

    # --- Generate Plots and Metrics ----

    if not all_simulation_results:
        logger.warning("No simulation results to process for plots or CSV. Exiting.")
        # If running in a loop or called as a function, might prefer return over sys.exit
        sys.exit(0) # Not an error, just nothing to do

    logger.info(f"\n--- Generating Infection Curve Plot(s) for {comparison_name} (saved in {run_output_dir}) ---")
    curves_plot_filename = run_output_dir / "infection_curves.pdf"
    plot_infection_curves(all_simulation_results, simulation_names, curves_plot_filename, comparison_name)

    logger.info(f"\n--- Extracting Summary Metrics for {comparison_name} ---")
    summary_metrics_list = []
    for i, results_data in enumerate(all_simulation_results):
        # Pass the corresponding config for population_size access
        current_sim_config = all_configs[i] # Use the config corresponding to this simulation result
        metrics = extract_summary_metrics(results_data, current_sim_config)
        metrics['simulation_name'] = simulation_names[i]
        summary_metrics_list.append(metrics)
    
    # Call the updated plotting function once to generate a single grouped bar chart PDF
    # The plot_summary_metrics_bars function will append its own suffix like "_grouped_summary.pdf"
    metrics_plot_base_filename = run_output_dir / "summary_metrics"
    plot_summary_metrics_bars(summary_metrics_list, simulation_names, metrics_plot_base_filename, comparison_name)

    # --- Save Summary Metrics to CSV ---
    if summary_metrics_list:
        summary_df = pd.DataFrame(summary_metrics_list)
        if 'simulation_name' in summary_df.columns:
            cols = ['simulation_name'] + [col for col in summary_df.columns if col != 'simulation_name']
            summary_df = summary_df[cols]
        
        csv_filename = run_output_dir / "summary_metrics.csv"
        summary_df.to_csv(csv_filename, index=False)
        logger.info(f"Summary metrics CSV saved to {csv_filename}")

    logger.info(f"\nAll simulations processed. Outputs for '{comparison_name}' are in {run_output_dir}.")


if __name__ == "__main__":
    main()