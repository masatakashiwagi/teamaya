from typing import Dict, List

from pydantic import BaseModel


class ApiSchemaTrain(BaseModel):
    """Schema for train model
    """
    dataset_id: str
    features: List[str]
    target: str


class ApiSchemaPredict(BaseModel):
    """Schema for predict using trained model
    """
    model_id: str
    dataset_id: str
    input_data: Dict[str, float]


class ProducerResult(BaseModel):
    """Result for Producer
    """
    message: dict
