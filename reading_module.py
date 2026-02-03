"""Reading module for a smartphone-based MVP.

This module captures an image from a camera input, performs OCR via a dummy
implementation, and speaks the extracted text using the shared AudioOutput
protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from navigation_module import AudioOutput


class CameraInput(Protocol):
    """Protocol for camera input providers."""

    def get_frame(self) -> object:
        raise NotImplementedError


class OcrEngine(Protocol):
    """Protocol for OCR backends."""

    def extract_text(self, frame: object) -> str:
        raise NotImplementedError


class DummyOcrEngine:
    """Dummy OCR engine that returns predefined text."""

    def __init__(self, text: str = "") -> None:
        self._text = text

    def extract_text(self, frame: object) -> str:
        return self._text


@dataclass
class ReadingResult:
    """Result of processing a frame for reading."""

    text: str


class ReadingAssistant:
    """Captures frames, extracts text, and speaks it aloud."""

    def __init__(
        self,
        camera: CameraInput,
        ocr_engine: OcrEngine,
        audio: AudioOutput,
        fallback_message: Optional[str] = "no text detected",
    ) -> None:
        self._camera = camera
        self._ocr_engine = ocr_engine
        self._audio = audio
        self._fallback_message = fallback_message

    def process_frame(self) -> ReadingResult:
        frame = self._camera.get_frame()
        text = self._ocr_engine.extract_text(frame).strip()
        if text:
            self._audio.speak(text)
        elif self._fallback_message:
            self._audio.speak(self._fallback_message)
        return ReadingResult(text=text)
