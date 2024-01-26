import pandas as pd
from prefect import task, flow
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder


@task(name="Drop biased column")
def drop_biased_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop the column 'duration' because it induces a bias
    """
    df.drop("duration", axis=1, inplace=True)
    return df


@task(name="Prepare the data")
def binarize_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    transform the y column to be numeric 1 and 0 instead of 'yes' or 'no'
    """
    df["y"].loc[df["y"] == 'yes'] = 1
    df["y"].loc[df["y"] == 'no'] = 0
    df["y"] = pd.to_numeric(df['y'])
    return df


@task(name="Get column by type")
def get_col_by_type(x: pd.DataFrame) -> dict:
    """
    TODO: Docstring for get_col_by_type
    """
    num_feat = ['age', 'campaign', 'emp.var.rate', 'cons.price.idx', 'cons.conf.idx', 'euribor3m', 'nr.employed',
                'previous']
    cat_feat = []
    for column in x.columns:
        if not num_feat.__contains__(column):
            cat_feat.append(column)
    return {'num_feat': num_feat, 'cat_feat': cat_feat}


def transform_col_data(x: pd.DataFrame, cat_feat: [str], num_feat: [str], preprocessor: ColumnTransformer) -> dict:
    if preprocessor is None:
        categorical_transformer = Pipeline(
            steps=[('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
                   ('encoder', OneHotEncoder())])

        numeric_transformer = Pipeline(
            steps=[("imputer", SimpleImputer(strategy='median')),
                   ("scaler", MinMaxScaler())])

        preprocessor = ColumnTransformer(transformers=[
            ("categorical", categorical_transformer, cat_feat),
            ("numeric", numeric_transformer, num_feat)
        ])
        x = preprocessor.fit_transform(x)
    else:
        x = preprocessor.transform(x)
    return {'x': x, 'preprocessor': preprocessor}


@task(name="Extract input and output data")
def extract_x_y(df: pd.DataFrame, with_target: bool = True) -> dict:
    """
    TODO
    """
    x = df
    y = None
    if with_target:
        x.drop('y', axis=1, inplace=True)
        y = df['y']
    return {'x': x, 'y': y}


@flow(name="Preprocessing data")
def process_data(path: str = None, df: pd.DataFrame = None, preprocessor: ColumnTransformer = None,
                 with_target: bool = True) -> dict:
    """
    TODO
    """

    if df is None:
        df = load_data(path)
    if with_target:
        binarize_target(df)
    dict_xy = extract_x_y(df, with_target=with_target)
    x = dict_xy['x']

    x = drop_biased_col(x)

    dict_col_type = get_col_by_type(x)

    dict_preprocessor = transform_col_data(x=x, cat_feat=dict_col_type['cat_feat'], num_feat=dict_col_type['num_feat'],
                                           preprocessor=preprocessor)

    return {'x': dict_preprocessor['x'], 'y': dict_xy['y'], 'preprocessor': dict_preprocessor['preprocessor']}
