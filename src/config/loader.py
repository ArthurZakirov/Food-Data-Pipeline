import json
import yaml
import hydra.utils
import os


def load_file(filepath):
    """Load content based on file extension."""
    # Debug: Print the absolute path of the file being loaded
    abs_path = os.path.abspath(filepath)

    # Debug: Check if the file exists
    if not os.path.isfile(abs_path):
        print(f"File does not exist: {abs_path}")
        return None
    if filepath.endswith(".txt"):
        with open(abs_path, "r", encoding="utf-8") as file:
            return file.read()
    elif filepath.endswith(".json"):
        with open(abs_path, "r", encoding="utf-8") as file:
            return json.load(file)
    elif filepath.endswith(".yaml"):
        with open(abs_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    else:
        print(f"Unsupported file type: {abs_path}")
        return None


from omegaconf import DictConfig, OmegaConf
import os

# Other function definitions...


def init_config(cfg: DictConfig) -> DictConfig:
    """Recursively load configuration files and content."""
    # You can iterate over DictConfig as if it's a dictionary
    for key, value in cfg.items():
        if isinstance(value, DictConfig) and "file" in value and "content" in value:
            # Use Hydra to get the absolute path to the file
            file_path = hydra.utils.to_absolute_path(value["file"])
            # Load the content of the file
            cfg[key]["content"] = load_file(file_path)

        elif isinstance(value, DictConfig):
            # If it's a DictConfig, recurse
            cfg[key] = init_config(value)
    return cfg


def load_config(config_path):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return init_config(config)
