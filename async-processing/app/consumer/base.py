import ast
import os
import pickle
import sys
import traceback
from typing import Literal

import boto3
import numpy as np
import pika
from logger import get_logger
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

LOGGER = get_logger()

# Possible values as queue name
QueueNames = Literal['queue.model.train', 'queue.model.predict']


class BaseConsumer:
    def __init__(self, queue_name: QueueNames):
        self.queue_name = queue_name
        self.pika_params = pika.ConnectionParameters(
            host="rabbitmq",
            port=os.getenv('RABBITMQ_PORT', 5672),
            connection_attempts=10,
            heartbeat=0
        )
        self.connection = pika.BlockingConnection(self.pika_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, auto_delete=False, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        LOGGER.info('Pika connection initialized.')

    def callback(self):
        raise NotImplementedError()

    def run(self):
        """The consumer in standby mode
        """
        LOGGER.info(f" [*] Waiting for messages in {self.__class__.__name__}. To exit press CTRL+C.")
        try:
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            _, _, tb = sys.exc_info()
            LOGGER.error(
                f'Exception Error: {e} || Type: {str(type(e))} || Traceback Message: {traceback.format_tb(tb)}')

    @staticmethod
    def body2dict(body: str):
        """Convert body message to dict
        """
        body_str = body.decode("UTF-8")
        body = ast.literal_eval(body_str)
        LOGGER.info("Convert message to dict type.")

        return body

    @staticmethod
    def download_from_s3(
        s3_bucket_name: str,
        s3_dir_path: str,
        file_path: str,
        file_name: str
    ):
        """Download from s3

        Args:
            s3_bucket_name (str): target bucket name
            s3_dir_path (str): s3 directory path for download
            file_path (str): local directory path
            file_name (str): target filename
        """
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(s3_bucket_name)
        s3_file_path = s3_dir_path + file_name

        # workaround for bug
        tmp_split_list = file_name.split('.csv')
        if len(tmp_split_list) > 1:
            new_file_name = file_name.split('.csv')[0] + '.csv'
        else:
            new_file_name = file_name.split('.csv')[0]
        bucket.download_file(s3_file_path, file_path + new_file_name)

    @staticmethod
    def upload_to_s3(
        s3_bucket_name: str,
        s3_dir_path: str,
        file_path: str,
        file_name: str
    ):
        """Upload to s3

        Args:
            s3_bucket_name (str): target bucket name
            s3_dir_path (str): s3 directory path for upload
            file_path (str): local directory path
            file_name (str): target filename
        """
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(s3_bucket_name)
        s3_file_path = s3_dir_path + file_name
        bucket.upload_file(file_path + file_name, s3_file_path)

    @staticmethod
    def save_model(model: object, filename: str):
        """Save trained model

        Args:
            model (object): model object
            filename (str): model filename & filepath
        """
        with open(filename, mode='wb') as f:
            pickle.dump(model, f)

        return None

    @staticmethod
    def load_model(filename: str):
        """Load ML model

        Args:
            filename (str): model filename & filepath
        """
        with open(filename, mode='rb') as f:
            model = pickle.load(f)

        return model


class EvalMetrics(object):
    """Model evaluation metrics
    """

    def __init__(self):
        """initialize
        """

    def rmse_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Root Mean Square Error

        Args:
            y_true (np.ndarray): true y-values
            y_pred (np.ndarray): pred y-values

        Returns:
            float: rmse values
        """
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)

        return rmse

    def mae_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Error

        Args:
            y_true (np.ndarray): true y-values
            y_pred (np.ndarray): pred y-values

        Returns:
            float: mae values
        """
        mae = mean_absolute_error(y_true, y_pred)

        return mae

    def r2_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R^2: coefficient of determination

        Args:
            y_true (np.ndarray): true y-values
            y_pred (np.ndarray): pred y-values

        Returns:
            float: mae values
        """
        r2 = r2_score(y_true, y_pred)

        return r2
