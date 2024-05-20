import pytest
from src.jobs.train import train_and_evaluate
import pandas as pd


def test_train_and_evaluate_missing_column(mocker):
    # Arrange
    x_train = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    y_train = pd.DataFrame({"C": [5, 6]})
    x_test = x_train.copy()
    y_test = y_train.copy()

    mock_model = mocker.Mock()
    mock_pipeline = mocker.Mock()

    # Act and Assert
    with pytest.raises(ValueError):
        train_and_evaluate(
            model=mock_model,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )


def test_train_and_evaluate_not_enough_data(mocker):
    # Arrange
    x_train = pd.DataFrame({"A": [1], "B": [2]})
    y_train = pd.DataFrame({"C": [3]})
    x_test = x_train.copy()
    y_test = y_train.copy()

    mock_model = mocker.Mock()
    mock_pipeline = mocker.Mock()

    # Act and Assert
    with pytest.raises(ValueError):
        train_and_evaluate(
            model=mock_model,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )
