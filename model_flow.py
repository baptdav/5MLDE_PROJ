import os
import pickle

import numpy as np
import pandas as pd
from prefect import task, flow
from sklearn.metrics import mean_squared_error
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
) -> float:
    """Calculate mean squared error for two arrays"""
    return mean_squared_error(y_true, y_pred, squared=False)


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
    mse = evaluate_model(y_test, prediction)
    model_obj = {'model': model, 'metric': mse, 'metric_name': 'mse'}
    save_pickle(f"{local_storage}/model.pickle", model_obj)
    return model_obj
