import os
import pickle

import numpy as np
import pandas as pd
from prefect import task, flow
from sklearn.metrics import mean_squared_error, classification_report
from sklearn.neighbors import KNeighborsClassifier

import config


@task(name="Model training")
def train_model(
        x_train: pd.DataFrame,
        y_train
) -> KNeighborsClassifier:
    """Train and return a KNN model"""
    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(x_train, y_train)
    return model


@task(name="Model prediction")
def predict_if_client_will_subscribe(
        input_data: pd.DataFrame,
        model: KNeighborsClassifier
) -> np.ndarray:
    """
    Use trained KNN model
    to predict target from input data
    :return array of predictions
    """
    return model.predict(input_data)


@task(name="Model evaluation")
def evaluate_model(
        y_true: np.ndarray,
        y_pred: np.ndarray
) -> dict:
    """Calculate mean squared error for two arrays"""
    classification_report_str = classification_report(y_true, y_pred, output_dict=True)

    classification_report_dict = {"global_accuracy": classification_report_str.get('accuracy'),
                                  "MSE": mean_squared_error(y_true, y_pred, squared=False)}

    for key, value in classification_report_str.get('0').items():
        classification_report_dict[f"{key}_over_negative_prediction"] = value
    for key, value in classification_report_str.get('1').items():
        classification_report_dict[f"{key}_over_positive_prediction"] = value

    return classification_report_dict


@task(name="Model loading from pickle file")
def load_pickle(path: str):
    with open(path, 'rb') as f:
        loaded_obj = pickle.load(f)
    return loaded_obj


@task(name="Model saving to pickle file")
def save_pickle(path: str, obj: dict):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


@flow(name="Training and evaluating model flow")
def train_and_evaluate_model(
        x_train,
        y_train,
        x_test,
        y_test,
        local_storage: str = config.LOCAL_STORAGE
) -> dict:
    """
    TODO
    """
    if not os.path.exists(local_storage):
        os.makedirs(local_storage)

    model = train_model(x_train, y_train)
    prediction = predict_if_client_will_subscribe(x_test, model)
    metrics_dict = evaluate_model(y_test, prediction)
    model_obj = {'model': model, 'metrics': metrics_dict}
    save_pickle(f"{local_storage}/model.pickle", model_obj)
    return model_obj
