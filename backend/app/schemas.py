from typing import List
from pydantic import BaseModel


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox


class DetectionResponse(BaseModel):
    success: bool
    model: str
    image_width: int
    image_height: int
    detection_count: int
    detections: List[Detection]


class ReasoningResponse(BaseModel):
    success: bool
    query: str
    intent: str
    answer: str
    safety_status: str
    confidence: str
    evidence: dict
    detections: List[Detection]