import os

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

LOCAL_STORAGE = os.path.join(BASE_PATH, "data")
MLFLOW_EXPERIMENT_NAME="5MLDE_PROJ"
MLFLOW_TRACKING_URI="http://mlflow-server:5000"
MLFLOW_MODEL_NAME="KNeighborsClassifier_test"
MLFLOW_PREPROCESSOR_NAME="Preprocessor"
MLFLOW_MODEL_ALIAS="Production"
MLFLOW_UNRELEASED_MODEL_TAG="Unrealesed"
MLFLOW_RELEASE_MODEL_TAG="Release"
DATA_DOWNLOAD_PATH = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"
RELEASE_ACCURACY_THRESHOLD = 0.87