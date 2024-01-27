import os

import numpy as np
from prefect import flow
from prefect.client.schemas.schedules import IntervalSchedule
from prefect.deployments import Deployment

import config
from load_data_flow import load_data
from logging_flow import mlflow_logging
from model_flow import train_and_evaluate_model
from process_data_flow import process_data


@flow(name="mflow")
def main_flow(local_storage: str = config.LOCAL_STORAGE) -> None:
    """
    TODO
    """
    if not os.path.exists(local_storage):
        os.makedirs(local_storage)
    data_dict = load_data()
    if data_dict['are_great_expectation_tests_passed']:
        train_data = process_data(df=data_dict["train_df"])
        test_data = process_data(df=data_dict["test_df"], preprocessor=train_data['preprocessor'])
        model_dict = train_and_evaluate_model(train_data['x'], np.array(train_data['y']),
                                              test_data['x'], np.array(test_data['y']))
        # Le model a t'il une précision globale supérieur au seuil fixé ? Si oui on déploiera en 'Production'
        is_releasable: bool = model_dict['metrics']['global_accuracy'] > config.RELEASE_ACCURACY_THRESHOLD
        mlflow_logging(input_infos=data_dict, model=model_dict['model'], preprocessor=train_data['preprocessor'],
                       metrics_dict=model_dict['metrics'], is_releasable=is_releasable)


modeling_deployment_every_sunday = Deployment.build_from_flow(
    name="KNN Model Deployment",
    flow=main_flow,
    version="1.0",
    tags=["model"],
    schedule=IntervalSchedule(interval=86400)
)

if __name__ == "__main__":
    modeling_deployment_every_sunday.apply()
