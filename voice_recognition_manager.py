import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Type
from datetime import datetime, timedelta

import pyaudio
import webrtcvad
import speech_recognition as sr
from fuzzywuzzy import fuzz
from pydantic import BaseSettings, Field
from fastapi import FastAPI
import uvicorn
import websockets

# --- Configuration via Pydantic ---
class VoiceConfig(BaseSettings):
    stt_engine: str = Field("google", description="STT engine to use: google, azure, whisper")
    language: str = Field("en-US", description="Language code for recognition")
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)
    activation_phrases: List[str] = Field(["overlord"], description="Activation keywords")
    cooldown_seconds: float = Field(2.0, ge=0.0)
    streamerbot_ws_uri: str = Field("ws://localhost:7580", description="Streamer.bot WS URI")
    reconnect_attempts: int = Field(5, ge=0)

    class Config:
        env_prefix = "VOICE_"

# --- STT Strategy Pattern ---
class STTEngineBase:
    def __init__(self, language: str):
        self.language = language

    async def transcribe(self, audio_data: sr.AudioData) -> Optional[str]:
        raise NotImplementedError

class GoogleSTTEngine(STTEngineBase):
    def __init__(self, language: str):
        super().__init__(language)
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3

    async def transcribe(self, audio_data: sr.AudioData) -> Optional[str]:
        try:
            text = self.recognizer.recognize_google(audio_data, language=self.language)
            return text.strip()
        except (sr.UnknownValueError, sr.RequestError) as e:
            logging.getLogger("STT").debug(f"Google STT error: {e}")
            return None

# Register additional STT engines here
_STT_REGISTRY: Dict[str, Type[STTEngineBase]] = {
    "google": GoogleSTTEngine,
    # "azure": AzureSTTEngine,
    # "whisper": WhisperSTTEngine,
}

class SpeechToTextEngine:
    def __init__(self, config: VoiceConfig):
        engine_cls = _STT_REGISTRY.get(config.stt_engine)
        if not engine_cls:
            raise ValueError(f"Unsupported STT engine: {config.stt_engine}")
        self.engine = engine_cls(config.language)

    async def transcribe_audio(self, audio_data: sr.AudioData) -> Optional[str]:
        return await self.engine.transcribe(audio_data)

# --- Voice Activity Detection (Raw PyAudio + WebRTC VAD) ---
class VoiceActivationDetector:
    def __init__(self, sample_rate: int = 16000, frame_duration: int = 30):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(2)
        self.buffer: List[bool] = []
        self.triggered = False

    def process_frame(self, frame: bytes) -> (bool, bool):
        is_speech = self.vad.is_speech(frame, self.sample_rate)
        self.buffer.append(is_speech)
        if len(self.buffer) > 10:
            self.buffer.pop(0)
        # Start recording when majority of recent frames are speech
        if not self.triggered and sum(self.buffer) > 0.8 * len(self.buffer):
            self.triggered = True
            return True, True
        # Stop recording when mostly silence
        if self.triggered and sum(self.buffer) < 0.1 * len(self.buffer):
            self.triggered = False
            return False, False
        return is_speech, self.triggered

# --- Intent Classification ---
@dataclass
class VoiceCommand:
    trigger_phrase: str
    action_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.7
    cooldown_seconds: float = 2.0
    aliases: List[str] = field(default_factory=list)

@dataclass
class VoiceIntent:
    command: str
    confidence: float
    parameters: Dict[str, Any]
    raw_text: str
    timestamp: datetime

class IntentClassifier:
    def __init__(self):
        self.commands: Dict[str, VoiceCommand] = {}
        self.parameter_patterns = {'number': r"\b(\d+(?:\.\d+)?)\b",
                                   'altitude': r"\b(\d+(?:,\d{3})*)\b"}

    def register_command(self, cmd: VoiceCommand):
        self.commands[cmd.trigger_phrase] = cmd
        for alias in cmd.aliases:
            self.commands[alias] = cmd

    def classify_intent(self, text: str) -> Optional[VoiceIntent]:
        text_lower = text.lower().strip()
        best_cmd, best_conf = None, 0.0
        # Exact prefix match first
        for trig, cmd in self.commands.items():
            if text_lower.startswith(trig):
                return VoiceIntent(cmd.action_name, 1.0, {}, text, datetime.now())
        # Fuzzy fallback
        for trig, cmd in self.commands.items():
            conf = fuzz.partial_ratio(trig, text_lower) / 100.0
            if conf > cmd.confidence_threshold and conf > best_conf:
                best_cmd, best_conf = cmd, conf
        if best_cmd:
            params = {}
            # Extract parameters only for supported patterns
            for key, pat in self.parameter_patterns.items():
                m = re.search(pat, text)
                if m:
                    val = m.group(1).replace(',', '')
                    params[key] = float(val) if key == 'number' else int(val)
            return VoiceIntent(best_cmd.action_name, best_conf, params, text, datetime.now())
        return None

# --- Streamer.bot Action Manager ---
class StreamerBotActionManager:
    def __init__(self, uri: str, reconnects: int):
        self.uri, self.reconnects = uri, reconnects
        self.ws = None
        self.log = logging.getLogger('StreamerBot')

    async def connect(self):
        for attempt in range(self.reconnects + 1):
            try:
                self.ws = await websockets.connect(self.uri)
                self.log.info("Connected to Streamer.bot")
                return
            except Exception as e:
                self.log.error(f"WS connect failed ({attempt}): {e}")
                await asyncio.sleep(2 ** attempt)
        raise ConnectionError("Streamer.bot connect failed")

    async def execute_action(self, name: str, params: Dict[str, Any]):
        if not self.ws:
            await self.connect()
        cmd = {"request": "DoAction", "action": {"name": name}, "args": params}
        await self.ws.send(json.dumps(cmd))
        self.log.info(f"Action sent: {name}")

# --- Main Manager with Task Cancellation & Health API ---
class VoiceRecognitionManager:
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.vad = VoiceActivationDetector()
        self.stt = SpeechToTextEngine(config)
        self.intentifier = IntentClassifier()
        self.sb = StreamerBotActionManager(config.streamerbot_ws_uri,
                                           config.reconnect_attempts)
        self.tasks: List[asyncio.Task] = []
        self.running = False
        self.audio_queue: asyncio.Queue = asyncio.Queue()
        self._register_default_commands()
        # Health-check HTTP
        self.app = FastAPI()
        @self.app.get('/voice/status')
        def status():
            return {'running': self.running, 'tasks': len(self.tasks)}

    def _register_default_commands(self):
        defaults = [
            VoiceCommand('overlord set altitude', 'SetAltitude', aliases=['set altitude']),
            VoiceCommand('overlord flight status', 'ShowFlightStatus')
        ]
        for cmd in defaults:
            self.intentifier.register_command(cmd)

    async def start(self):
        self.running = True
        await self.sb.connect()
        loop = asyncio.get_event_loop()
        self.tasks.append(loop.create_task(self._audio_loop()))
        self.tasks.append(loop.create_task(self._recognition_loop()))
        self.tasks.append(loop.create_task(
            uvicorn.run(self.app, host='0.0.0.0', port=8001, log_level='info')
        ))

    async def _audio_loop(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                         input=True, frames_per_buffer=self.vad.frame_size)
        buffer: List[bytes] = []
        while self.running:
            frame = stream.read(self.vad.frame_size, exception_on_overflow=False)
            is_speech, rec = self.vad.process_frame(frame)
            if rec:
                buffer.append(frame)
            elif buffer:
                data = b''.join(buffer)
                audio = sr.AudioData(data, 16000, 2)
                await self.audio_queue.put(audio)
                buffer.clear()
        stream.stop_stream(); stream.close(); pa.terminate()

    async def _recognition_loop(self):
        while self.running:
            audio = await self.audio_queue.get()
            text = await self.stt.transcribe_audio(audio)
            if text:
                intent = self.intentifier.classify_intent(text)
                if intent:
                    await self._execute(intent)

    async def _execute(self, intent: VoiceIntent):
        await self.sb.execute_action(intent.command, intent.parameters)

    async def stop(self):
        self.running = False
        for t in self.tasks:
            t.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        if self.sb.ws:
            await self.sb.ws.close()

# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config = VoiceConfig()
    vrm = VoiceRecognitionManager(config)
    try:
        asyncio.run(vrm.start())
    except KeyboardInterrupt:
        asyncio.run(vrm.stop())
