import pandas as pd
from great_expectations.data_context import BaseDataContext
from prefect import task, flow
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler

import config


@task()
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path, sep=';', encoding="utf-8")


@task()
def drop_biased_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop the column 'duration' because it induces a bias
    """
    df.drop("duration", axis=1, inplace=True)
    return df


@task()
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    transform the y column to be numeric 1 and 0 instead of 'yes' or 'no'
    """
    df["y"].loc[df["y"] == 'yes'] = 1
    df["y"].loc[df["y"] == 'no'] = 0
    df["y"] = pd.to_numeric(df['y'])
    return df


@task()
def get_col_by_type(x: pd.DataFrame) -> dict:
    num_feat = ['age', 'campaign', 'emp.var.rate', 'cons.price.idx', 'cons.conf.idx', 'euribor3m', 'nr.employed',
                'previous']
    cat_feat = []
    for column in x.columns:
        if not num_feat.__contains__(column):
            cat_feat.append(column)
    return {'num_feat': num_feat, 'cat_feat': cat_feat}


##########################################################################################################
# GREAT EXPECTATIONS 

@task()
def run_great_expectations_check() -> bool:
    """
    Lance les tests great-expectations et retourne true si 
    tous les tests résultent en un succès
    """
    # Load the Great Expectations data context
    context = BaseDataContext("/great_expectation/")
    context.list_checkpoints()
    return context.run_checkpoint(checkpoint_name="checkpoint").success


##########################################################################################################
#  CATEGORICAL FEATURES PREPROCESS TASKS

@task
def encode_categorical_cols(df: pd.DataFrame, categorical_cols) -> pd.DataFrame:
    """
    Encode categorical columns using OneHotEncoder.
    """
    for col in categorical_cols:
        df = pd.concat([df, pd.get_dummies(df[col], prefix=col)], axis=1)
        df = df.drop(col, axis=1)
    return df


@task
def impute_categorical_cols(df: pd.DataFrame, categorical_cols) -> pd.DataFrame:
    """
    Impute missing values in categorical columns with a constant value.
    """
    for col in categorical_cols:
        df[col].fillna('missing', inplace=True)
    return df


@task
def normalize_numeric_cols(df: pd.DataFrame, numeric_cols) -> pd.DataFrame:
    """
    Normalize numeric columns using MinMaxScaler.
    """
    for col in numeric_cols:
        scaler = MinMaxScaler()
        df[col] = scaler.fit_transform(df[[col]])
    return df


@task
def impute_numeric_cols(df: pd.DataFrame, numeric_cols) -> pd.DataFrame:
    """
    Impute missing values in numeric columns with the median.
    """
    for col in numeric_cols:
        imputer = SimpleImputer(strategy='median')
        df[col] = imputer.fit_transform(df[[col]])
    return df


##########################################################################################################

@task()
def extract_x_y(df: pd.DataFrame, with_target: bool = True) -> dict:
    """
    TODO
    """
    X = df.drop('y', axis=1)
    y = None
    if with_target:
        y = df['y']
    return {'x': X, 'y': y}


@flow(name="Preprocessing data")
def process_data(path: str, with_target: bool = True) -> dict:
    """
    TODO
    """
    df = load_data(path)
    df = prepare_data(df)

    dictXY = extract_x_y(df, with_target=with_target)
    X = dictXY['x']

    X = drop_biased_col(X)

    dict_col_type = get_col_by_type(X)
    numeric_features = dict_col_type['num_feat']
    cat_features = dict_col_type['cat_feat']

    X = impute_numeric_cols(X, numeric_features)
    X = normalize_numeric_cols(X, numeric_features)
    X = impute_categorical_cols(X, cat_features)
    X = encode_categorical_cols(X, cat_features)

    return {'x': X, 'y': dictXY['y']}


if __name__ == '__main__':
    processed_data = process_data(config.TRAIN_DATA)
