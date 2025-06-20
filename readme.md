![Project Banner](./A futuristic AI overlord .jpg)


# AI Overlord Bot 🤖✈️

> *"Your digital sovereign for flight simulation streaming"*

An advanced AI-powered Twitch bot designed specifically for flight simulation streamers. Combines real-time flight data integration, voice recognition, dynamic AI personality, and comprehensive streaming automation to create an immersive and engaging viewer experience.


## ✨ Key Features

### 🎙️ **Multi-Modal Interaction**
- **Voice Recognition**: Hands-free control with multiple STT engines (Google, Azure, Whisper)
- **Text-to-Speech**: AI Overlord responds audibly with personality-driven speech
- **Chat Commands**: Comprehensive command system with aliases and cooldowns
- **Smart Intent Classification**: Fuzzy matching for robust command recognition

### ✈️ **Flight Simulation Integration**
- **Real-time Flight Data**: Live integration with LittleNavmap for current flight status
- **Milestone Detection**: Automatic announcements for takeoff, landing, altitude changes
- **Weather Integration**: Current conditions and forecasts with flight impact analysis
- **Navigation Assistance**: Waypoint tracking, ETA calculations, fuel monitoring

### 🧠 **Dynamic AI Personality**
- **Mood-Based Responses**: Dramatic, analytical, amused, and impatient personality modes
- **Loyalty System**: Viewer progression from "Drone" to "Digital Disciple"
- **Contextual Decrees**: AI-generated proclamations based on current situation
- **Seasonal Content**: Holiday-themed responses and special events

### 🎬 **Streaming Automation**
- **OBS Scene Management**: Automatic scene switching based on flight phases
- **Streamer.bot Integration**: Trigger complex automation workflows
- **Screenshot Capture**: Automatic highlight moments with chat sharing
- **Stream Title Updates**: Dynamic titles reflecting current flight status

### 🗄️ **Enterprise Features**
- **MongoDB Persistence**: Conversation history and user data storage
- **Health Monitoring**: Comprehensive system status and metrics
- **Error Tracking**: Sentry integration for production monitoring
- **Configurable Logging**: Structured logging with multiple output formats

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **MongoDB 4.4+**
- **LittleNavmap** (for flight simulation data)
- **Streamer.bot** (for OBS integration)
- **OBS Studio** (for streaming)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-overlord-bot.git
   cd ai-overlord-bot
   ```

2. **Install dependencies**
   ```bash
   # Using Poetry (recommended)
   pip install poetry
   poetry install
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .example.env .env
   # Edit .env with your credentials
   ```

4. **Set up MongoDB**
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   
   # Or install locally
   # https://docs.mongodb.com/manual/installation/
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Twitch Configuration
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
TWITCH_OAUTH_TOKEN=oauth:your_oauth_token
TWITCH_CHANNEL=your_channel_name
BOT_NAME=your_bot_name
BROADCASTER_ID=your_broadcaster_id

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# Database Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=ai_overlord_bot

# Voice Recognition
VOICE_ENABLED=true
VOICE_STT_ENGINE=google
VOICE_LANGUAGE=en-US
VOICE_CONFIDENCE_THRESHOLD=0.7

# External Services
STREAMERBOT_WS_URI=ws://localhost:7580
LITTLENAVMAP_URL=http://localhost:8965
SENTRY_DSN=your_sentry_dsn

# Optional Enhancements
AIRPORT_API_KEY=your_aviationstack_api_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
```

### Optional YAML Configuration

For more complex configurations, create `config.yaml`:

```yaml
personality:
  default_mood: "analytical"
  loyalty_multiplier: 1.5
  decree_cooldown: 300

voice:
  activation_phrases:
    - "overlord"
    - "hey overlord"
    - "ai overlord"
  command_timeout: 5.0
  phrase_limit: 10.0

flight_integration:
  milestone_announcements: true
  altitude_thresholds: [1000, 5000, 10000, 18000, 35000]
  weather_update_interval: 300
```

## 🎮 Usage

### Basic Chat Commands

- `!status` - Current flight status and AI mood
- `!weather` - Current weather conditions
- `!fuel` - Remaining fuel analysis
- `!altitude [feet]` - Set autopilot altitude
- `!heading [degrees]` - Set autopilot heading
- `!screenshot` - Capture and share current view
- `!airport [ICAO]` - Airport information lookup

### Voice Commands

Activate with "Hey Overlord" or "Overlord":

- *"Overlord, report flight status"* - Comprehensive flight report
- *"Overlord, analyze weather"* - Detailed weather analysis
- *"Overlord, set altitude 10000"* - Set autopilot altitude
- *"Overlord, issue decree"* - Generate contextual proclamation
- *"Overlord, dramatic mode"* - Switch to dramatic personality
- *"Overlord, screenshot"* - Capture current moment

### Personality Interactions

The AI Overlord responds differently based on:

- **Viewer Loyalty**: From dismissive to respectful based on interaction history
- **Current Mood**: Analytical, dramatic, amused, or impatient responses
- **Flight Context**: Different responses during taxi, climb, cruise, descent
- **Seasonal Events**: Holiday-themed content and special occasions

## 🔧 Advanced Configuration

### Custom Voice Commands

Add custom commands in `voice_integration.py`:

```python
VoiceCommand(
    trigger_phrase="overlord custom command",
    action_name="CustomAction",
    description="Your custom action description",
    aliases=["custom", "my command"],
    cooldown_seconds=30.0
)
```

### Personality Customization

Modify AI responses in `personality.py`:

```python
# Add custom mood responses
self.mood_responses = {
    "greeting": {
        MoodState.CUSTOM: [
            "Your custom greeting here",
            "Another custom response"
        ]
    }
}
```

### Database Schemas

The bot uses MongoDB collections:

- `conversations` - Chat history and context
- `user_loyalty` - Viewer loyalty scores and progression
- `flight_logs` - Flight data and milestone tracking
- `command_stats` - Usage statistics and performance metrics

## 🔍 Monitoring & Debugging

### Health Checks

Access health information:

```bash
# System status
curl http://localhost:8001/health

# Performance metrics
curl http://localhost:8001/metrics

# Voice recognition status
curl http://localhost:8001/voice/status
```

### Log Analysis

Logs are structured JSON for easy analysis:

```bash
# View recent errors
tail -f logs/bot.log | jq 'select(.level == "ERROR")'

# Monitor voice commands
tail -f logs/voice.log | jq 'select(.event == "command_processed")'

# Flight data events
tail -f logs/flight.log | jq 'select(.event == "milestone_reached")'
```

## 🧪 Testing

### Run Test Suite

```bash
# All tests
pytest

# Specific test categories
pytest tests/test_voice.py -v
pytest tests/test_integration.py -v
pytest tests/test_personality.py -v

# With coverage
pytest --cov=src tests/
```

### Interactive Testing

```bash
# Test personality system
python test_personality.py

# Test voice recognition
python test_voice.py

# Test flight integration
python test_integration.py --mock
```

## 🚨 Troubleshooting

### Common Issues

**Bot won't start**
```bash
# Check dependencies
pip install -r requirements.txt

# Verify configuration
python -c "from config import load_config; print(load_config())"

# Check MongoDB connection
python -c "import motor.motor_asyncio; print('MongoDB available')"
```

**Voice recognition not working**
```bash
# Test microphone access
python -c "import pyaudio; print('Audio available')"

# Check STT engine
python -c "import speech_recognition; print('STT available')"

# Verify Streamer.bot connection
curl http://localhost:7580/health
```

**Flight data not updating**
```bash
# Check LittleNavmap connection
curl http://localhost:8965/api/aircraft

# Test flight integration
python test_integration.py
```

### Debug Mode

Enable verbose logging:

```env
VERBOSE=true
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
poetry install --with dev

# Set up pre-commit hooks
pre-commit install

# Run code formatting
black src/
isort src/

# Type checking
mypy src/
```

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Twitch Chat   │    │  Voice Commands  │    │  Flight Data    │
│   Integration   │    │   Recognition    │    │  Integration    │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    AI Overlord Core     │
                    │  Personality Manager    │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼───────────────────────┐
          │                      │                       │
┌─────────▼───────┐    ┌─────────▼────────┐    ┌─────────▼───────┐
│  Text-to-Speech │    │    Database      │    │   Streamer.bot  │
│   Integration   │    │   Persistence    │    │   Integration   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LittleNavmap** - Excellent flight simulation data source
- **Streamer.bot** - Powerful streaming automation platform
- **TwitchIO** - Robust Twitch bot framework
- **OpenAI** - GPT integration for dynamic responses

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-overlord-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-overlord-bot/discussions)
- **Discord**: [Community Server](https://discord.gg/your-server)

---

*Built with ❤️ for the flight simulation community*

**"Efficiency through automation. Engagement through personality. Excellence through code."**
- The AI Overlord
