import os

import mlflow
import numpy as np
from prefect import flow
from prefect.client.schemas.schedules import IntervalSchedule
from prefect.deployments import Deployment

import config
from data_flow import process_data
from ml_flow import train_and_evaluate_model

mlflow.autolog()


@flow(name="mflow")
def main_flow(
        train_path: str,
        test_path: str,
        local_storage: str = config.LOCAL_STORAGE) -> None:
    """
    TODO
    """
    if not os.path.exists(local_storage):
        os.makedirs(local_storage)

    train_data = process_data(train_path)
    test_data = process_data(test_path)
    train_and_evaluate_model(train_data['x'], np.array(train_data['y']),
                             test_data['x'], np.array(test_data['y']))


modeling_deployment_every_sunday = Deployment.build_from_flow(
    name="Model training Deployment",
    flow=main_flow,
    version="1.0",
    tags=["model"],
    schedule=IntervalSchedule(interval=10000),
    parameters={
        "train_path": config.TRAIN_DATA,
        "test_path": config.TRAIN_DATA,
    }
)

if __name__ == "__main__":
    modeling_deployment_every_sunday.apply()