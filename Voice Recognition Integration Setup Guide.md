# Voice Recognition Integration Setup Guide

## Overview

This guide will help you integrate the voice recognition system with your existing AI Overlord bot infrastructure. The system provides real-time voice command processing that triggers Streamer.bot actions while maintaining the AI Overlord personality.

## Prerequisites

### Software Requirements
- **Python 3.11+** with your existing bot environment
- **Streamer.bot v0.2.0+** with Speaker.bot plugin
- **OBS Studio** with obs-websocket plugin
- **Audio drivers** that support system audio capture

### Python Dependencies
Add these to your `requirements.txt`:

```text
# Voice Recognition
speechrecognition==3.10.0
pyaudio==0.2.11
webrtcvad==2.0.10
fuzzywuzzy==0.18.0
python-levenshtein==0.21.1

# Audio processing
numpy==1.24.3
```

### Hardware Requirements
- **Microphone** with good noise cancellation (recommended: headset mic)
- **Minimum 4GB RAM** for speech processing
- **Stable internet** for cloud speech recognition APIs

## Installation Steps

### 1. Install Audio Dependencies

**Windows:**
```bash
# Install portaudio for pyaudio
# Download from: http://www.portaudio.com/download.html
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### 2. Set Up Speech Recognition API

Choose one of these options:

#### Option A: Google Speech Recognition (Free, Limited)
```python
# No additional setup required - uses free tier
# Limited to ~50 requests per day
```

#### Option B: Google Cloud Speech-to-Text (Recommended)
```bash
# 1. Create Google Cloud project
# 2. Enable Speech-to-Text API
# 3. Create service account key
# 4. Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

#### Option C: Azure Cognitive Services
```bash
# Add to your .env file
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_region
```

### 3. Configure Streamer.bot

#### Import Actions
1. Open Streamer.bot
2. Go to **Actions** tab
3. Right-click → **Import**
4. Import the JSON file from the `streamerbot_actions` artifact
5. Verify all actions imported successfully

#### Set Up WebSocket
1. In Streamer.bot, go to **Servers/Clients**
2. **WebSocket Server** should be enabled on port 7580
3. Note the URI: `ws://localhost:7580`

#### Configure Global Variables
Set these global variables in Streamer.bot:
- `current_altitude` (number)
- `ground_speed` (number)
- `current_heading` (number)
- `flight_phase` (string)
- `current_lat` (number)
- `current_lon` (number)
- `emergency_active` (boolean)

### 4. Update Your Bot Configuration

Add voice settings to your `.env` file:

```env
# Voice Recognition Settings
VOICE_RECOGNITION_ENABLED=True
VOICE_STT_ENGINE=google  # google, azure, whisper
VOICE_LANGUAGE=en-US
VOICE_CONFIDENCE_THRESHOLD=0.7
VOICE_ACTIVATION_PHRASES=overlord,hey overlord
VOICE_COMMAND_TIMEOUT=5.0

# Streamer.bot Integration
STREAMERBOT_WS_URI=ws://localhost:7580
STREAMERBOT_RECONNECT_ATTEMPTS=5

# Azure Speech (if using)
AZURE_SPEECH_KEY=your_key_here
AZURE_SPEECH_REGION=eastus
```

### 5. Update Your Main Bot File

Modify your `main.py` to include voice recognition:

```python
# Add to your imports
from voice_integration import VoiceIntegration, integrate_voice_with_bot

# In your main bot class __init__ method
async def initialize_voice_recognition(self):
    """Initialize voice recognition if enabled"""
    if self.config.voice.get('VOICE_RECOGNITION_ENABLED', False):
        self.logger.info("Initializing voice recognition...")

        try:
            self.voice_integration = await integrate_voice_with_bot(self)
            self.logger.info("Voice recognition initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize voice recognition: {e}")
            self.voice_integration = None

# In your main() function
async def main():
    bot = AIOverlordBot()

    # Start existing components
    await bot.start()

    # Add voice recognition
    await bot.initialize_voice_recognition()

    # Keep bot running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await bot.stop()
        if bot.voice_integration:
            await bot.voice_integration.stop()
```

### 6. Test the Integration

#### Test Speech Recognition
```python
# Run this test script
python -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Say something!')
    audio = r.listen(source)
    try:
        print('You said: ' + r.recognize_google(audio))
    except:
        print('Could not understand audio')
"
```

#### Test Streamer.bot Connection
1. Start Streamer.bot
2. Run your bot
3. Check logs for "Connected to Streamer.bot"
4. In Streamer.bot, go to **Actions** → Test any imported action

#### Test Voice Commands
1. Ensure your microphone is working
2. Start the bot with voice recognition enabled
3. Say: **"Overlord flight status"**
4. Check if:
   - TTS responds with flight information
   - Streamer.bot action executes
   - OBS overlays update (if configured)

## Voice Command Reference

### Flight Commands
- **"Overlord report flight status"** → Detailed status with AI commentary
- **"Overlord analyze weather"** → Weather analysis with personality
- **"Overlord find nearest airport"** → Airport information
- **"Overlord fuel status"** → Fuel analysis
- **"Overlord navigation update"** → Route and navigation info
- **"Overlord emergency checklist"** → Emergency procedures
- **"Overlord radio frequencies"** → ATC frequency information

### Stream Commands
- **"Overlord greet new followers"** → Welcome new followers
- **"Overlord issue decree"** → Generate contextual decree
- **"Overlord chat statistics"** → Chat activity stats
- **"Overlord loyalty report"** → Viewer loyalty information
- **"Overlord mood change"** → Switch personality mood

### System Commands
- **"Overlord set altitude [number]"** → Set autopilot altitude
- **"Overlord set heading [number]"** → Set autopilot heading
- **"Overlord take screenshot"** → Capture and save screenshot
- **"Overlord change scene"** → Cycle through OBS scenes
- **"Overlord emergency"** → Trigger emergency alerts

## Troubleshooting

### Common Issues

#### "No module named 'pyaudio'"
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

#### "Microphone not detected"
```python
# List available microphones
import speech_recognition as sr
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"Microphone {index}: {name}")
```

#### Voice commands not recognized
1. **Check microphone levels** in system audio settings
2. **Reduce background noise** - use headset microphone
3. **Speak clearly** and pause between words
4. **Check confidence threshold** in config (try lowering to 0.5)
5. **Test different speech engines** (Google vs Azure)

#### Streamer.bot connection failed
1. **Verify Streamer.bot is running** and WebSocket server enabled
2. **Check port 7580** is not blocked by firewall
3. **Confirm WebSocket URI** in configuration
4. **Review Streamer.bot logs** for connection errors

#### Actions not executing
1. **Verify actions imported** correctly in Streamer.bot
2. **Check global variables** are properly set
3. **Test actions manually** in Streamer.bot interface
4. **Review action code** for syntax errors

### Performance Optimization

#### Reduce Latency
```python
# In voice config
VOICE_CONFIDENCE_THRESHOLD=0.6  # Lower = faster recognition
VOICE_COMMAND_TIMEOUT=3.0       # Shorter timeout
```

#### Improve Accuracy
```python
# Use better speech engine
VOICE_STT_ENGINE=azure  # More accurate than Google free tier

# Adjust microphone settings
recognizer.energy_threshold = 4000  # Higher for noisy environments
recognizer.pause_threshold = 0.8    # Longer pause detection
```

#### System Resources
- **Close unnecessary applications** during streaming
- **Use wired headset** instead of Bluetooth
- **Dedicated microphone** separate from webcam audio

## Advanced Configuration

### Custom Voice Commands

Add custom commands by extending the voice integration:

```python
# In voice_integration.py, add to _setup_flight_commands()
VoiceCommand(
    trigger_phrase="overlord custom action",
    action_name="MyCustomAction",
    description="Your custom action description",
    aliases=["alternative phrase", "another way to say it"],
    cooldown_seconds=5.0
)
```

### Multiple Language Support

```python
# Configure for different languages
VOICE_LANGUAGE=de-DE  # German
VOICE_LANGUAGE=fr-FR  # French
VOICE_LANGUAGE=es-ES  # Spanish
```

### Noise Filtering

```python
# Advanced audio processing
import noisereduce as nr

# Add noise reduction to speech processing
def preprocess_audio(audio_data):
    # Apply noise reduction
    reduced_noise = nr.reduce_noise(y=audio_data, sr=16000)
    return reduced_noise
```

## Next Steps

Once voice recognition is working:

1. **Configure OBS overlays** to show voice command feedback
2. **Set up StreamElements integration** for enhanced alerts
3. **Add Discord notifications** for important voice commands
4. **Create custom Streamer.bot actions** for your specific needs
5. **Test with different flight simulation phases**
6. **Fine-tune personality responses** for voice interactions

## Support

If you encounter issues:

1. **Check the logs** for detailed error messages
2. **Test each component individually** (speech → intent → action)
3. **Verify all dependencies** are installed correctly
4. **Review Streamer.bot action logs** for execution errors
5. **Test with simple commands first** before complex scenarios

The voice recognition system is designed to integrate seamlessly with your existing AI Overlord bot while providing powerful real-time interaction capabilities during streaming.