"""Main entry point for the smartphone MVP demo.

This script wires together the voice assistant with navigation, object
 detection, and reading assistants using dummy backends.
"""

from __future__ import annotations

from typing import Iterable, List

from navigation_module import (
    DummyAudioOutput,
    DummyObstacleDetector,
    NavigationAssistant,
    Obstacle,
)
from object_detection import (
    DetectedObject,
    DummyObjectDetector,
    ObjectDetectionAssistant,
)
from reading_module import DummyOcrEngine, ReadingAssistant
from voice_assistance import Transcriber, VoiceAssistant


class DummyCamera:
    """Simple camera stub for demo purposes."""

    def get_frame(self) -> object:
        return object()


class ScriptedTranscriber(Transcriber):
    """Transcriber that returns scripted phrases for the demo."""

    def __init__(self, transcripts: Iterable[str]) -> None:
        self._transcripts = list(transcripts)
        self._index = 0

    def listen(self, audio_source: object) -> str:
        if self._index >= len(self._transcripts):
            return ""
        transcript = self._transcripts[self._index]
        self._index += 1
        return transcript


def build_navigation_assistant(camera: DummyCamera, audio: DummyAudioOutput) -> NavigationAssistant:
    return NavigationAssistant(
        camera=camera,
        detector=DummyObstacleDetector(
            obstacles=[
                Obstacle(bbox=(20, 0, 80, 60), label="chair", confidence=0.91),
                Obstacle(bbox=(200, 0, 260, 80), label="desk", confidence=0.87),
            ]
        ),
        audio=audio,
        frame_width=320,
    )


def build_object_detection_assistant(
    camera: DummyCamera, audio: DummyAudioOutput
) -> ObjectDetectionAssistant:
    return ObjectDetectionAssistant(
        camera=camera,
        detector=DummyObjectDetector(
            objects=[
                DetectedObject(label="person", bbox=(10, 10, 100, 200), confidence=0.95),
                DetectedObject(label="book", bbox=(140, 40, 220, 120), confidence=0.89),
            ]
        ),
        audio=audio,
    )


def build_reading_assistant(camera: DummyCamera, audio: DummyAudioOutput) -> ReadingAssistant:
    return ReadingAssistant(
        camera=camera,
        ocr_engine=DummyOcrEngine(text="Welcome to the campus library"),
        audio=audio,
    )


def run_demo(transcripts: Iterable[str]) -> List[str]:
    scripted_transcripts = list(transcripts)
    camera = DummyCamera()
    audio = DummyAudioOutput()
    voice_assistant = VoiceAssistant(ScriptedTranscriber(scripted_transcripts))

    navigation_assistant = build_navigation_assistant(camera, audio)
    object_detection_assistant = build_object_detection_assistant(camera, audio)
    reading_assistant = build_reading_assistant(camera, audio)

    for _ in range(len(scripted_transcripts)):
        voice_assistant.listen_and_handle(audio_source=None)
        mode = voice_assistant.active_mode
        if mode == "navigation":
            navigation_assistant.process_frame()
        elif mode == "object_detection":
            object_detection_assistant.process_frame()
        elif mode == "reading":
            reading_assistant.process_frame()

    return audio.messages


if __name__ == "__main__":
    demo_transcripts = [
        "switch to navigation",
        "switch to object detection",
        "switch to reading",
    ]
    spoken_messages = run_demo(demo_transcripts)
    for message in spoken_messages:
        print(message)
