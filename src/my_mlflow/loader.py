import mlflow
import os
from hydra.utils import get_original_cwd


def init_mlflow(experiment_name: str, tracking_uri: str):
    os.path.join(f"file:///{get_original_cwd()}", tracking_uri)

    mlflow.set_tracking_uri(tracking_uri)
    if mlflow.get_experiment_by_name(experiment_name) is None:
        mlflow.create_experiment(experiment_name)
    mlflow.set_experiment(experiment_name)
    mlflow.set_tracking_uri(tracking_uri)
    return None
