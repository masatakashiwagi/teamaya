import numpy as np
import pytest
from consumer import tasks
from numpy.testing import assert_equal


@ pytest.mark.usefixtures("diabetes_regression_df")
class TestTrain:
    @ pytest.mark.parametrize(
        ("params"),
        [
            {
                "features": ["age", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"],
                "target": "target"
            }
        ]
    )
    def test_train(self, diabetes_regression_df, params):
        """Test train method.

        Args:
            diabetes_regression_df (pd.DataFrame): dataset for test
            params (dict): train parameters
        """
        test_size = 0.2
        test_data_size = len(diabetes_regression_df) * test_size
        result = tasks.train(diabetes_regression_df, params)

        assert_equal(result['y_pred'].shape[0], test_data_size)
        assert_equal(result['y_pred'].shape[0], result['y_true'].shape[0])
        assert isinstance(result['y_pred'], np.ndarray)
        assert isinstance(result['y_pred'][0], float)
        assert isinstance(result['y_true'], np.ndarray)
        assert isinstance(result['y_true'][0], float)


@ pytest.mark.usefixtures("diabetes_regression_df")
class TestPredict:
    @ pytest.mark.parametrize(
        ("params"),
        [
            {
                "features": ["age", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"],
                "target": "target",
                "input_data": {
                    "age": 0.038076,
                    "bmi": 0.061696,
                    "bp": 0.021872,
                    "s1": -0.044223,
                    "s2": -0.034821,
                    "s3": -0.043401,
                    "s4": -0.002592,
                    "s5": 0.019908,
                    "s6": -0.017646
                }
            }
        ]
    )
    def test_predict(self, diabetes_regression_df, params):
        """Test predict method.

        Args:
            diabetes_regression_df (pd.DataFrame): dataset for test
            params (dict): predict parameters
        """
        train_result = tasks.train(diabetes_regression_df, params)
        model = train_result['model']

        result = tasks.predict(model, params)

        assert isinstance(result['pred_proba'], float)
