import zipfile
from io import BytesIO

import pandas as pd
import requests
from great_expectations.data_context import BaseDataContext
from prefect import task, flow
from sklearn.model_selection import train_test_split
import great_expectations as gx
import config


@task(name="Download data")
def download_data(download_url: str) -> pd.DataFrame:
    """
    Downloading the dataset from the UCI-ML Repository
    """
    # URL of the zip file

    response = requests.get(download_url)

    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content), 'r') as outer_zip_ref:
            inner_zip_name = 'bank-additional.zip'
            with outer_zip_ref.open(inner_zip_name) as inner_zip_file:
                with zipfile.ZipFile(inner_zip_file, 'r') as inner_zip_ref:
                    csv_file_name = 'bank-additional/bank-additional-full.csv'
                    with inner_zip_ref.open(csv_file_name) as file:
                        df = pd.read_csv(file)
                    return df
    else:
        raise Exception(f"Failed to download the file. Status code: {response.status_code}")


@task(name="Great Expectations checks")
def run_great_expectations_check() -> bool:
    """
    Run great expectations checks, return true if all checks passed
    """
    # Load the Great Expectations data context
    context = gx.get_context(context_root_dir="gx/")
    context.list_checkpoints()
    return context.run_checkpoint(checkpoint_name="checkpoint").success


@flow(name="Loading train and test dataframes and running great expectations checks")
def load_data(download_path: str = config.DATA_DOWNLOAD_PATH) -> dict:
    """
    TODO
    """
    df = download_data(download_path)
    great_expectation_tests_result = run_great_expectations_check()
    train_df, test_df = train_test_split(df, stratify=df['y'], test_size=0.2)

    return {'train_df': train_df, 'test_df': test_df,
            'are_great_expectation_tests_passed': great_expectation_tests_result}
