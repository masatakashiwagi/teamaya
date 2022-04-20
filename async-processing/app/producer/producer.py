import ast
import uuid

from fastapi import APIRouter
from logger import get_logger

from producer.base import BaseProducer, QueueNames, RepQueueNames
from producer.schema import ApiSchemaPredict, ApiSchemaTrain, ProducerResult

LOGGER = get_logger()

router = APIRouter(prefix='', tags=["producers"])


class ProducerTrain(BaseProducer):
    def __init__(self, queue_name: QueueNames, rep_queue_name: RepQueueNames):
        BaseProducer.__init__(self, queue_name, rep_queue_name)

    def run(self, params: ApiSchemaTrain):
        """Run to send message to train consumer

        Args:
            params (ApiSchemaTrain): schema for train
        """
        model_id = str(uuid.uuid4())
        message = {
            "model_id": model_id,
            "dataset_id": params.dataset_id,
            "features": params.features,
            "target": params.target
        }

        # self.send_message_to_consumer(message)
        LOGGER.info("Produce message for train.")
        response = self.send_message_to_consumer(message)
        response = ast.literal_eval(response.decode())
        LOGGER.info(f"Reply Response from consumer: {response}")

        return ProducerResult(message=response)


class ProducerPredict(BaseProducer):
    def __init__(self, queue_name: QueueNames, rep_queue_name: RepQueueNames):
        BaseProducer.__init__(self, queue_name, rep_queue_name)

    def run(self, params: ApiSchemaPredict):
        """Run to send message to predict consumer

        Args:
            params (ApiSchemaPredict): schema for predict
        """
        message = {
            "model_id": params.model_id,
            "dataset_id": params.dataset_id,
            "input_data": params.input_data
        }

        LOGGER.info("Produce message for predict.")
        response = self.send_message_to_consumer(message)
        response = ast.literal_eval(response.decode())
        LOGGER.info(f"Reply Response from consumer: {response}")

        return ProducerResult(message=response)


@router.post("/train", response_model=ProducerResult, name="train")
async def train(params: ApiSchemaTrain) -> ProducerResult:
    """Train model"""
    return ProducerTrain(queue_name='queue.model.train', rep_queue_name='queue.reply.train').run(params)


@router.post("/predict", response_model=ProducerResult, name="predict")
async def predict(params: ApiSchemaPredict) -> ProducerResult:
    """Predict model"""
    return ProducerPredict(queue_name='queue.model.predict', rep_queue_name='queue.reply.predict').run(params)
