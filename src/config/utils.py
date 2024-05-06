from omegaconf import DictConfig, ListConfig, OmegaConf


def flatten_dict(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def to_native_python(obj):
    if isinstance(obj, (ListConfig, DictConfig)):
        # Convert OmegaConf types to native Python types
        return OmegaConf.to_container(obj, resolve=True)
    return obj
