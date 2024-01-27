import mlflow.pyfunc
import pandas as pd
from flask import Flask, request, jsonify

import config
from process_data_flow import process_data

app = Flask(__name__)


# Define an endpoint for predictions
@app.route('/predict', methods=['POST'])
def predict():
    """
    TODO
    """
    try:
        mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(config.MLFLOW_EXPERIMENT_NAME)

        data = request.json
        df = pd.DataFrame([data])

        model = mlflow.sklearn.load_model(f"models:/{config.MLFLOW_MODEL_NAME}@{config.MLFLOW_MODEL_ALIAS}")
        preprocessor = mlflow.sklearn.load_model(
            f"models:/{config.MLFLOW_PREPROCESSOR_NAME}@{config.MLFLOW_MODEL_ALIAS}")

        x_test = process_data(df=df, preprocessor=preprocessor, with_target=False)['x']

        result = model.predict(x_test)
        return jsonify({'will the client subscribe a term deposit ': 'yes' if bool(result[0]) else 'no'})

    except Exception as e:
        return jsonify({'error': str(e)})


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
