import json
import os
import sys
import traceback
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pika
from logger import get_logger
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

from base import BaseConsumer, EvalMetrics, QueueNames

LOGGER = get_logger()
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
S3_PATH_NAME = os.environ['S3_PATH_NAME']
S3_MODEL_PATH_NAME = os.environ['S3_MODEL_PATH_NAME']


class TrainConsumer(BaseConsumer):
    def __init__(self, queue_name: QueueNames):
        BaseConsumer.__init__(self, queue_name)

    def callback(self, ch, method, props, body):
        params = self.body2dict(body)
        self.download_from_s3(S3_BUCKET_NAME, S3_PATH_NAME, 'data/', params['dataset_id'] + '.csv')
        LOGGER.info("Download dataset from S3.")

        dataset_path = 'data/' + params['dataset_id'] + '.csv'
        df = pd.read_csv(dataset_path)
        LOGGER.info("Read csv file and transform to dataframe.")

        try:
            result = train(df, params)

            # save model
            model_path = 'data/model.pkl'
            self.save_model(result['model'], model_path)
            LOGGER.info("Save trained model to local.")

            # upload model to cloud storage
            model_id = params['model_id']
            self.upload_to_s3(S3_BUCKET_NAME, S3_MODEL_PATH_NAME + f'{model_id}/', 'data/', 'model.pkl')
            LOGGER.info("Upload trained model to S3.")

            payload = {
                'status': 'TASK_COMPLETED',
                'model_id': params['model_id']
            }
            response = json.dumps(payload)
        except Exception as e:
            _, _, tb = sys.exc_info()
            LOGGER.error(
                f'Exception Error: {e} || Type: {str(type(e))} || Traceback Message: {traceback.format_tb(tb)}')

            payload = {
                'status': 'TASK_ERROR',
                'model_id': params['model_id']
            }
            response = json.dumps(payload)

        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)


class PredictConsumer(BaseConsumer):
    def __init__(self, queue_name: QueueNames):
        BaseConsumer.__init__(self, queue_name)

    def callback(self, ch, method, props, body):
        params = self.body2dict(body)
        model_id = params['model_id']
        self.download_from_s3(S3_BUCKET_NAME, S3_MODEL_PATH_NAME + f'{model_id}/', 'data/', 'model.pkl')
        LOGGER.info("Download model file from S3.")

        model_path = 'data/model.pkl'
        model = self.load_model(model_path)
        LOGGER.info("Load model for prediction.")

        try:
            result = predict(model, params)

            payload = {
                'status': 'TASK_COMPLETED',
                'pred_proba': result['pred_proba']
            }
            response = json.dumps(payload)
        except Exception as e:
            _, _, tb = sys.exc_info()
            LOGGER.error(
                f'Exception Error: {e} || Type: {str(type(e))} || Traceback Message: {traceback.format_tb(tb)}')

            payload = {
                'status': 'TASK_ERROR',
                'pred_proba': None
            }
            response = json.dumps(payload)

        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)


def train(df: pd.DataFrame, params) -> Dict[str, Any]:
    """Train machine learning model (RandomForestRegressor)

    Args:
        df (pd.DataFrame): dataset for training model
        params (dict): parameters for training
    """
    features = params['features']
    target = params['target']
    X, y = df[features], df[target].values

    # train/test split
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

    LOGGER.info("Start model training.")
    # machine learning model: RandomForestRegressor
    reg_model = RandomForestRegressor(max_depth=3, random_state=42, n_estimators=100)
    reg_model.fit(X_train, y_train)
    LOGGER.info("Model fit for training.")

    # evaluate model
    pred = reg_model.predict(X_valid)

    # evaluate metrics
    eval_metrics = EvalMetrics()
    rmse = eval_metrics.rmse_score(y_valid, pred)
    LOGGER.info("Evaluate metrics=RMSE for valid dataset : %.3f" % rmse)
    LOGGER.info("Finish model training.")

    result = {
        'y_pred': pred,
        'y_true': y_valid,
        'metrics': {'rmse': rmse},
        'model': reg_model
    }

    return result


def predict(model: object, params) -> Dict[str, Any]:
    """Prediction for dataset using trained model

    Args:
        model (object): trained model
        params (_type_): parameters for prediction

    Returns:
        float: predict probability
    """
    input_data = params['input_data']
    pred_proba = model.predict(pd.DataFrame([input_data]))
    result = {
        'pred_proba': pred_proba[0]
    }

    return result


if __name__ == "__main__":
    def plot_yy(y_valid, y_pred, metrics, savepath):
        """Vizualize the results using yy-plot
        """
        y_max = np.max(y_valid)
        y_min = np.min(y_valid)

        # calculate max and min of y_pred
        predict_y_max = np.max(y_pred)
        predict_y_min = np.min(y_pred)

        # use the smallest and largest value of either of both y_valid and y_pred
        # as the range of the vertical axis horizontal axis
        axis_max = max(y_max, predict_y_max)
        axis_min = min(y_min, predict_y_min)

        # margin of 5% of the length
        axis_max = axis_max + (axis_max - axis_min) * 0.05
        axis_min = axis_min - (axis_max - axis_min) * 0.05

        plt.figure(figsize=(10, 6))
        plt.subplots_adjust(wspace=0.2, hspace=0.3)
        plt.scatter(y_pred, y_valid, c='r', s=50, zorder=2, edgecolors=(0, 0, 0), alpha=0.6)
        plt.plot([axis_min, axis_max], [axis_min, axis_max], c="#1560bd")

        plt.xlabel('Predict Values', fontsize=20)
        plt.ylabel('True Values', fontsize=20)
        plt.title(r'RMSE=%.2f' % (metrics), fontsize=15)
        plt.tick_params(labelsize=20)
        plt.tight_layout()
        plt.grid(True)
        plt.savefig(savepath, dpi=100, bbox_inches='tight', pad_inches=0.1)
        plt.close()

    def plot_residual(y_valid, y_pred, savepath):
        residual = y_pred - y_valid
        xmax = np.max(y_pred) + (np.max(y_pred) - np.min(y_pred)) * 0.05
        xmin = np.min(y_pred) - (np.max(y_pred) - np.min(y_pred)) * 0.05

        plt.figure(figsize=(10, 6))
        plt.subplots_adjust(wspace=0.2, hspace=0.3)
        plt.scatter(y_pred, residual, c='r', s=50, zorder=2, edgecolors=(0, 0, 0), alpha=0.6)
        plt.hlines(y=0, xmin=xmin, xmax=xmax, color='#1560bd')
        plt.title('Residual Plot', fontsize=20)
        plt.xlabel('Predict Values', fontsize=20)
        plt.ylabel('Residuals', fontsize=20)
        plt.tick_params(labelsize=20)
        plt.tight_layout()
        plt.grid(True)
        plt.savefig(savepath, dpi=100, bbox_inches='tight', pad_inches=0.1)
        plt.close()

    params = {
        "model_id": "sample_test",
        "dataset_id": "test_diabetes",
        "features": ["age", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"],
        "target": "target"
    }
    dataset_path = 'test/' + params['dataset_id'] + '.csv'
    df = pd.read_csv(dataset_path)
    result = train(df, params)

    rmse = result['metrics']['rmse']

    # Record the metrics
    outfile = "data/metrics.txt"
    if not os.path.isdir("data"):
        os.mkdir("data")
    with open(outfile, "w") as f:
        f.write("RMSE: " + f"{rmse:.2f}" + "\n")

    # Plot results
    y_valid = result['y_true']
    y_pred = result['y_pred']
    savepath_yy = "data/yy_plot.png"
    plot_yy(y_valid, y_pred, metrics=rmse, savepath=savepath_yy)
    savepath_residual = "data/residual_plot.png"
    plot_residual(y_valid, y_pred, savepath=savepath_residual)
