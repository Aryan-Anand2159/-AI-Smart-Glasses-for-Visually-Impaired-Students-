"""Object detection module for a smartphone-based MVP.

This module defines camera input and object detection interfaces, a dummy
object detector for rapid prototyping, and a detection assistant that speaks
object names via the existing AudioOutput protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Protocol, Sequence

from navigation_module import AudioOutput


COMMON_OBJECTS = ("chair", "table", "person", "book", "bottle")


@dataclass(frozen=True)
class DetectedObject:
    """Represents a detected object in the camera frame."""

    label: str
    bbox: Sequence[int]
    confidence: float


class CameraInput(Protocol):
    """Protocol for camera input providers."""

    def get_frame(self) -> object:
        raise NotImplementedError


class ObjectDetector(Protocol):
    """Protocol for object detection backends."""

    def detect(self, frame: object) -> Iterable[DetectedObject]:
        raise NotImplementedError


class DummyObjectDetector:
    """Dummy detector that returns a predefined list of objects."""

    def __init__(self, objects: Optional[Iterable[DetectedObject]] = None) -> None:
        self._objects = list(objects) if objects is not None else []

    def detect(self, frame: object) -> Iterable[DetectedObject]:
        return list(self._objects)


@dataclass
class DetectionResult:
    """Result of processing a frame for object detection."""

    objects: List[DetectedObject]


class ObjectDetectionAssistant:
    """Detects objects from camera input and speaks their names."""

    def __init__(
        self,
        camera: CameraInput,
        detector: ObjectDetector,
        audio: AudioOutput,
    ) -> None:
        self._camera = camera
        self._detector = detector
        self._audio = audio

    def process_frame(self) -> DetectionResult:
        frame = self._camera.get_frame()
        objects = list(self._detector.detect(frame))
        self._announce(objects)
        return DetectionResult(objects=objects)

    def _announce(self, objects: List[DetectedObject]) -> None:
        if not objects:
            self._audio.speak("no objects detected")
            return
        for detected in objects:
            self._audio.speak(detected.label)
