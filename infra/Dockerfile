FROM ghcr.io/mlflow/mlflow:latest

WORKDIR /mlflow/
EXPOSE 5000

ENV BACKEND_URI sqlite:////mlflow/mlflow.db
ENV ARTIFACT_ROOT http://localhost:5000
ENV ARTIFACT_DESTINATION http://localhost:5000

CMD mlflow server --backend-store-uri ${BACKEND_URI} --host 0.0.0.0 --port 5000
