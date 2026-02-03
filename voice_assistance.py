"""Voice assistance module for fixed voice commands.

This module provides a speech-to-text workflow that listens for a fixed
set of commands and switches between navigation, object detection, and
reading modes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional


MODES = ("navigation", "object_detection", "reading")


@dataclass(frozen=True)
class CommandConfig:
    """Configuration for recognized command phrases."""

    phrases_by_mode: Dict[str, Iterable[str]] = field(
        default_factory=lambda: {
            "navigation": (
                "navigation mode",
                "switch to navigation",
                "navigation",
            ),
            "object_detection": (
                "object detection mode",
                "switch to object detection",
                "object detection",
                "object mode",
            ),
            "reading": (
                "reading mode",
                "switch to reading",
                "reading",
                "read mode",
            ),
        }
    )

    def __post_init__(self) -> None:
        for mode in self.phrases_by_mode:
            if mode not in MODES:
                raise ValueError(f"Unsupported mode: {mode}")


@dataclass
class ModeSwitchResult:
    """Result of processing a transcript."""

    transcript: str
    matched_command: Optional[str]
    active_mode: str


class Transcriber:
    """Interface for speech-to-text backends."""

    def listen(self, audio_source: object) -> str:
        raise NotImplementedError("Transcriber.listen must be implemented")


class VoiceAssistant:
    """Voice assistant that switches modes based on fixed commands."""

    def __init__(
        self,
        transcriber: Transcriber,
        command_config: Optional[CommandConfig] = None,
        initial_mode: str = "navigation",
    ) -> None:
        if initial_mode not in MODES:
            raise ValueError(f"Unsupported initial mode: {initial_mode}")
        self._transcriber = transcriber
        self._command_config = command_config or CommandConfig()
        self._active_mode = initial_mode

    @property
    def active_mode(self) -> str:
        return self._active_mode

    def listen_and_handle(self, audio_source: object) -> ModeSwitchResult:
        transcript = self._transcriber.listen(audio_source)
        return self.handle_transcript(transcript)

    def handle_transcript(self, transcript: str) -> ModeSwitchResult:
        normalized = " ".join(transcript.lower().split())
        matched_mode = self._match_mode(normalized)
        if matched_mode:
            self._active_mode = matched_mode
        return ModeSwitchResult(
            transcript=transcript,
            matched_command=matched_mode,
            active_mode=self._active_mode,
        )

    def _match_mode(self, transcript: str) -> Optional[str]:
        for mode, phrases in self._command_config.phrases_by_mode.items():
            for phrase in phrases:
                if phrase in transcript:
                    return mode
        return None
