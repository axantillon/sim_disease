import json
from pathlib import Path
from typing import Dict, Any
import jsonschema # New import

# Schema for validating the simulation configuration files
SIMULATION_CONFIG_SCHEMA = {
  "type": "object",
  "properties": {
    "simulation_name": {
      "type": "string",
      "description": "Optional descriptive name for the simulation run, used for output file naming by main.py."
    },
    "population_size": {
      "type": "integer",
      "description": "Total number of individuals in the network.",
      "minimum": 1
    },
    "connections": {
      "type": "number",
      "description": "Graph connections parameter. For Erdos-Renyi: probability 'p' (0.0-1.0). For Barabasi-Albert: integer 'm' (>=1). For Watts-Strogatz: integer 'k' (>=1).",
      "minimum": 0.0
    },
    "initial_binomial_probability": {
      "type": "number",
      "description": "Probability that any given individual is infected at the start of the simulation.",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "number_of_days": {
      "type": "integer",
      "description": "Duration of the simulation in days.",
      "minimum": 1
    },
    "individual_parameters": {
      "type": "object",
      "description": "Parameters for sampling individual attributes.",
      "properties": {
        "immune_level": {
          "type": "object",
          "description": "Distribution parameters for individual immune levels.",
          "properties": {
            "mu": {"type": "number", "description": "Mean of the normal distribution for immune level."},
            "sigma": {"type": "number", "description": "Standard deviation of the normal distribution for immune level.", "minimum": 0.0}
          },
          "required": ["mu", "sigma"]
        },
        "vaccine_effectiveness": {
          "type": "object",
          "description": "Distribution parameters for individual vaccine effectiveness.",
          "properties": {
            "mu": {"type": "number", "description": "Mean of the normal distribution for vaccine effectiveness."},
            "sigma": {"type": "number", "description": "Standard deviation of the normal distribution for vaccine effectiveness.", "minimum": 0.0}
          },
          "required": ["mu", "sigma"]
        },
        "contact_chance": {
          "type": "object",
          "description": "Distribution parameters for contact chance on edges. Note: This attribute is defined but not currently used by infection models.",
          "properties": {
            "mu": {"type": "number", "description": "Mean of the normal distribution for contact chance."},
            "sigma": {"type": "number", "description": "Standard deviation of the normal distribution for contact chance.", "minimum": 0.0}
          },
          "required": ["mu", "sigma"]
        }
      },
      "required": ["immune_level", "vaccine_effectiveness", "contact_chance"]
    },
    "infection_model": {
      "type": "object",
      "description": "Configuration for the infection model.",
      "properties": {
        "type": {
          "type": "string",
          "description": "Specifies the infection model to use.",
          "enum": ["independent", "dependent", "superspreader_dynamic"]
        },
        "recovery_duration": {
          "type": "integer",
          "description": "Number of days an individual remains infected before recovering. Defaults to 14 if not specified.",
          "minimum": 1
        },
        "infection_parameters": {
          "type": "object",
          "description": "Model-specific parameters. Code provides defaults if parameters are not specified.",
          "properties": {
            "base_prob_transmission": {
              "type": "number",
              "description": "Used by 'independent' model. Base probability of transmission. Default: 0.05.",
              "minimum": 0.0, "maximum": 1.0
            },
            "alpha": {
              "type": "number",
              "description": "Used by 'dependent' model (sigmoid). Controls steepness. Default: 0.1."
            },
            "beta": {
              "type": "number",
              "description": "Used by 'dependent' model (sigmoid). Shifts the curve. Default: 0.3."
            },
            "p_becomes_superspreader": {
              "type": "number",
              "description": "Used by 'superspreader_dynamic' model. Daily probability of becoming a superspreader. Default: 0.01.",
              "minimum": 0.0, "maximum": 1.0
            },
            "normal_base_infectivity": {
              "type": "number",
              "description": "Used by 'superspreader_dynamic' model. Base infectivity. Default: 0.05.",
              "minimum": 0.0, "maximum": 1.0
            },
            "superspreader_multiplier": {
              "type": "number",
              "description": "Used by 'superspreader_dynamic' model. Infectivity multiplier for superspreaders. Default: 10.0.",
              "minimum": 0.0
            }
          },
          "additionalProperties": False # Only allows defined parameters for specific models
        }
      },
      "required": ["type"]
    },
    "graph_type": {
        "type": "string",
        "description": "Specifies the graph generation model to be used.",
        "enum": ["erdos_renyi", "barabasi_albert", "watts_strogatz"],
        "default": "erdos_renyi" # Optional: Explicitly state default, though graph_setup handles it
    }
  },
  "required": [
    "population_size",
    "connections",
    "initial_binomial_probability",
    "number_of_days",
    "individual_parameters",
    "infection_model"
  ],
  "additionalProperties": True # Allow other top-level keys like graph_type for now
}

def load_config(filepath: str | Path) -> Dict[str, Any]:
    """
    Loads a simulation configuration from a JSON file and validates it against the schema.

    Args:
        filepath: The path to the JSON configuration file.

    Returns:
        A dictionary containing the configuration parameters.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        jsonschema.exceptions.ValidationError: If the configuration does not match the schema.
    """
    config_path = Path(filepath)
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {filepath}")

    with open(config_path, 'r') as f:
        try:
            config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error decoding JSON from {filepath}: {e.msg}", e.doc, e.pos) from e

    try:
        jsonschema.validate(instance=config_data, schema=SIMULATION_CONFIG_SCHEMA)
        print(f"Configuration from '{filepath}' loaded and validated successfully.")
        return config_data
    except jsonschema.exceptions.ValidationError as e:
        error_message = f"Configuration file '{filepath}' is invalid.\n"
        error_message += f"Error: {e.message}\n"
        error_message += f"Path to error in config: {list(e.path)}\n"
        
        # Provide more context if available
        if e.context:
            error_message += "Detailed errors:\n"
            for suberror in sorted(e.context, key=lambda x: x.path): # type: ignore
                error_message += f"  - Path: {list(suberror.path)}, Message: {suberror.message}\n" # type: ignore
        raise jsonschema.exceptions.ValidationError(error_message) from e
