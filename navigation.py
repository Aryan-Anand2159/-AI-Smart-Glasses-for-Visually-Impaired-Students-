"""Navigation module for obstacle detection and audio guidance.

This module processes camera input to detect obstacles and emits left/right/
forward guidance cues for safe navigation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Protocol, Sequence


audio_guidance = ("left", "right", "forward")


@dataclass(frozen=True)
class Obstacle:
    """Represents a detected obstacle in the camera frame."""

    bbox: Sequence[int]
    label: str
    confidence: float


class CameraInput(Protocol):
    """Protocol for camera input providers."""

    def get_frame(self) -> object:
        raise NotImplementedError


class ObstacleDetector(Protocol):
    """Protocol for obstacle detection backends."""

    def detect(self, frame: object) -> Iterable[Obstacle]:
        raise NotImplementedError


class AudioOutput(Protocol):
    """Protocol for audio output backends."""

    def speak(self, message: str) -> None:
        raise NotImplementedError


@dataclass
class GuidanceResult:
    """Result of processing a frame for navigation guidance."""

    direction: str
    obstacles: List[Obstacle]


class NavigationAssistant:
    """Detects obstacles and provides navigation guidance."""

    def __init__(
        self,
        camera: CameraInput,
        detector: ObstacleDetector,
        audio: AudioOutput,
        frame_width: int,
    ) -> None:
        if frame_width <= 0:
            raise ValueError("frame_width must be positive")
        self._camera = camera
        self._detector = detector
        self._audio = audio
        self._frame_width = frame_width

    def process_frame(self) -> GuidanceResult:
        frame = self._camera.get_frame()
        obstacles = list(self._detector.detect(frame))
        direction = self._compute_guidance(obstacles)
        self._audio.speak(direction)
        return GuidanceResult(direction=direction, obstacles=obstacles)

    def _compute_guidance(self, obstacles: List[Obstacle]) -> str:
        if not obstacles:
            return "forward"

        left_count = 0
        right_count = 0
        for obstacle in obstacles:
            center_x = (obstacle.bbox[0] + obstacle.bbox[2]) / 2
            if center_x < self._frame_width / 2:
                left_count += 1
            else:
                right_count += 1

        if left_count > right_count:
            return "right"
        if right_count > left_count:
            return "left"
        return "forward"


def choose_direction_from_obstacles(
    obstacles: Iterable[Obstacle], frame_width: int
) -> Optional[str]:
    """Helper to compute guidance without instantiating NavigationAssistant."""

    if frame_width <= 0:
        raise ValueError("frame_width must be positive")
    obstacle_list = list(obstacles)
    if not obstacle_list:
        return "forward"
    left_count = 0
    right_count = 0
    for obstacle in obstacle_list:
        center_x = (obstacle.bbox[0] + obstacle.bbox[2]) / 2
        if center_x < frame_width / 2:
            left_count += 1
        else:
            right_count += 1
    if left_count > right_count:
        return "right"
    if right_count > left_count:
        return "left"
    return "forward"
