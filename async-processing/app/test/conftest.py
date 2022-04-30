import sys; sys.path.append("/opt/program/consumer"), sys.path.append("/opt/program/producer")

import pandas as pd
import pytest


@pytest.fixture
def diabetes_regression_df():
    """sample diabetes dataset for test.
    """
    path = 'test/data/test_diabetes.csv'
    df = pd.read_csv(path)

    return df
