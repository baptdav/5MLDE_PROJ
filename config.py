import os

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DATA_DIR = os.path.join(BASE_PATH, "00-data")
LOCAL_STORAGE = os.path.join(BASE_PATH, "02-pipeline-and-orchestration/results")
TRAIN_DATA = os.path.join(BASE_PATH, "5MLDE_PROJ/data/base_data.csv")
TEST_DATA = os.path.join(BASE_PATH, "00-data/yellow_tripdata_2021-02.parquet")
INFERENCE_DATA = os.path.join(BASE_PATH, "00-data/yellow_tripdata_2021-03.parquet")
CATEGORICAL_VARS = ['PULocationID', 'DOLocationID', 'passenger_count']
MLFLOW_EXPERIMENT_NAME="5MLDE_PROJ"
MLFLOW_TRACKING_URI="http://localhost:5000"
MLFLOW_MODEL_NAME="KNeighborsClassifier_test"
MLFLOW_PREPROCESSOR_NAME="Preprocessor"
MLFLOW_MODEL_ALIAS="Production"
MLFLOW_UNRELEASED_MODEL_TAG="Unrealesed"
MLFLOW_RELEASE_MODEL_TAG="Release"
DATA_DOWNLOAD_PATH = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"