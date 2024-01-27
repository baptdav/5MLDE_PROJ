import mlflow
import mlflow.data
from mlflow import MlflowClient
from mlflow.models import set_signature, ModelSignature
from mlflow.types import ColSpec, Schema
from prefect import task, flow

import config


@task(name="Log model metric to MLFlow")
def log_metrics(metrics_dict: dict):
    """
    TODO: Docstring for log_metric
    """
    for metric_name, metric_value in metrics_dict.items():
        mlflow.log_metric(metric_name, metric_value)


@task(name="Log model training input to MLFlow")
def log_input_infos(input_infos: dict):
    """
    TODO: Docstring for log_input_infos
    """
    mlflow.log_dict(input_infos['great_expectation_tests_results'],
                    'great_expectation_results/great_expectation_results.json')
    # mlflow.log_input(mlflow.data.from_pandas(input_infos['train_df'], source=config.DATA_DOWNLOAD_PATH), 'training')
    # mlflow.log_input(mlflow.data.from_pandas(input_infos['test_df'], source=config.DATA_DOWNLOAD_PATH), 'testing')


@task(name="Log and register preprocessor to MLFlow")
def log_preprocessor(preprocessor, run_id, artifact_path: str = "preprocessor"):
    """
    TODO: Docstring for log_metric
    """
    preprocessor_uri = f"runs:/{run_id}/{artifact_path}"
    mlflow.sklearn.log_model(preprocessor, artifact_path)
    mlflow.register_model(preprocessor_uri, config.MLFLOW_PREPROCESSOR_NAME,
                          tags={"env": config.MLFLOW_UNRELEASED_MODEL_TAG})


@task(name="Log and register model to MLFlow")
def log_and_save_model(model, run_id, artifact_path: str = "models"):
    """
    TODO: Docstring for log_and_save_model
    """
    input_schema = Schema(
        [
            ColSpec("string", "job"),
            ColSpec("string", "marital"),
            ColSpec("string", "education"),
            ColSpec("string", "default"),
            ColSpec("double", "age"),
            ColSpec("double", "balance"),
            ColSpec("string", "housing"),
            ColSpec("string", "loan"),
            ColSpec("string", "contact"),
            ColSpec("double", "day"),
            ColSpec("double", "month"),
            ColSpec("double", "campaign"),
            ColSpec("double", "pdays"),
            ColSpec("double", "previous"),
            ColSpec("string", "poutcome"),
        ]
    )
    output_schema = Schema([ColSpec("boolean", "y")])
    signature = ModelSignature(inputs=input_schema, outputs=output_schema)

    model_uri = f"runs:/{run_id}/{artifact_path}"

    mlflow.sklearn.log_model(model, artifact_path)
    set_signature(model_uri, signature)
    mlflow.register_model(model_uri, config.MLFLOW_MODEL_NAME, tags={"env": config.MLFLOW_UNRELEASED_MODEL_TAG})


@task(name="Release model to production")
def release_model(client: MlflowClient) -> None:
    """
    Release model to production
    Since Model Stages are deprecated we used model aliases and tags instead as recommended in the official documentation
    cf : https://mlflow.org/docs/latest/model-registry.html#migrating-from-stages
    """
    # RELEASE MODEL
    latest_model_version = client.get_latest_versions(config.MLFLOW_MODEL_NAME)[0].version
    client.set_registered_model_alias(config.MLFLOW_MODEL_NAME, config.MLFLOW_MODEL_ALIAS, latest_model_version)
    client.set_registered_model_tag(config.MLFLOW_MODEL_NAME, "env", config.MLFLOW_RELEASE_MODEL_TAG)
    # RELEASE PREPROCESSOR
    latest_preprocessor_version = client.get_latest_versions(config.MLFLOW_PREPROCESSOR_NAME)[0].version
    client.set_registered_model_alias(config.MLFLOW_PREPROCESSOR_NAME, config.MLFLOW_MODEL_ALIAS,
                                      latest_preprocessor_version)
    client.set_registered_model_tag(config.MLFLOW_PREPROCESSOR_NAME, "env", config.MLFLOW_RELEASE_MODEL_TAG)


@flow(name="Logging to MLFlow")
def mlflow_logging(input_infos: dict, model=None, preprocessor=None, metrics_dict: dict = None,
                   is_releasable: bool = None, artifact_path: str = "models"):
    """
    Flow to make all MLFlow operations(logging model and model's metrics and signature, releasing model's artifacts)
    """
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.MLFLOW_EXPERIMENT_NAME)
    client = MlflowClient()
    with mlflow.start_run() as run:
        log_input_infos(input_infos)
        if preprocessor is not None and model is not None and metrics_dict is not None:
            log_and_save_model(model=model, artifact_path=artifact_path, run_id=run.info.run_id)
            log_metrics(metrics_dict)
            log_preprocessor(preprocessor, run.info.run_id)
            if is_releasable:
                release_model(client)
