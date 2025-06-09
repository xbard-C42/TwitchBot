# File: main.py
import asyncio
import logging
import signal
import sys
from pathlib import Path

from openai import AsyncOpenAI
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from config import load_config, ConfigError
from database_manager import DatabaseManager
from tts_manager import TTSManager
from chat_manager import ChatManager
from command_handler import CommandHandler
from littlenavmap_integration import LittleNavmapIntegration
from personality import PersonalityManager
from bot import Bot
from voice_recognition_manager import VoiceConfig, VoiceRecognitionManager

app = FastAPI()
config = VoiceConfig()
voice_mgr = VoiceRecognitionManager(config)

@app.on_event("startup")
async def startup():
    # fire-and-forget the voice loop
    asyncio.create_task(voice_mgr.start_listening())

@app.on_event("shutdown")
async def shutdown():
    await voice_mgr.stop()

@app.get("/voice/status")
def health_check():
    return voice_mgr.get_status()

def setup_logging(config):
    """Setup logging configuration."""
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)

    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Setup file logging
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / 'bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Reduce noise from external libraries
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('motor').setLevel(logging.WARNING)


def setup_sentry(config):
    """Setup Sentry error tracking if configured."""
    if config.sentry_dsn:
        sentry_sdk.init(
            dsn=config.sentry_dsn,
            integrations=[
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
                AsyncioIntegration(auto_enabling=True)
            ],
            traces_sample_rate=0.1,
            environment=config.environment,
            release=f"twitch-ai-overlord-bot@{config.environment}"
        )
        logging.info("Sentry error tracking initialized")


async def create_components(config):
    """Create and initialize all bot components."""
    logger = logging.getLogger('main')

    try:
        # Initialize OpenAI client
        openai_client = AsyncOpenAI(api_key=config.openai.API_KEY)
        logger.info("OpenAI client initialized")

        # Initialize database manager
        db_manager = DatabaseManager(config)
        await db_manager.initialize()
        logger.info("Database manager initialized")

        # Initialize TTS manager
        tts_manager = TTSManager(config)
        logger.info("TTS manager initialized")

        # Initialize LittleNavmap integration
        littlenavmap = LittleNavmapIntegration(config)
        logger.info("LittleNavmap integration initialized")

        # Initialize personality manager
        personality = PersonalityManager()
        personality.load_state()  # Load any saved loyalty scores
        logger.info("Personality manager initialized")

        # Initialize bot
        bot = Bot(
            openai_client=openai_client,
            config=config,
            db_manager=db_manager,
            tts_manager=tts_manager,
            littlenavmap=littlenavmap,
            personality=personality
        )

        # Initialize chat manager (needs bot instance)
        chat_manager = ChatManager(bot, config)
        bot.chat_manager = chat_manager

        # Initialize command handler (needs bot instance)
        command_handler = CommandHandler(bot, config)
        bot.command_handler = command_handler

        logger.info("All components initialized successfully")

        return bot

    except Exception as e:
        logger.error(f"Error creating components: {e}", exc_info=True)
        raise


async def start_bot(bot):
    """Start the bot and all its components."""
    logger = logging.getLogger('main')

    try:
        # Start TTS manager
        await bot.tts_manager.start()
        logger.info("TTS manager started")

        # Start chat manager
        await bot.chat_manager.start()
        logger.info("Chat manager started")

        # Connect to Twitch (this will trigger event_ready which starts LittleNavmap)
        logger.info("Connecting to Twitch...")
        await bot.start()

    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise


async def shutdown_bot(bot):
    """Gracefully shutdown the bot and all components."""
    logger = logging.getLogger('main')
    logger.info("Shutting down bot...")

    try:
        await bot.close()
        logger.info("Bot shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


def signal_handler(bot, loop):
    """Handle shutdown signals."""
    logger = logging.getLogger('main')
    logger.info("Received shutdown signal")

    # Create a task to shutdown gracefully
    loop.create_task(shutdown_bot(bot))


async def main():
    """Main entry point."""
    logger = logging.getLogger('main')

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()

        # Setup logging with config
        setup_logging(config)

        # Setup error tracking
        setup_sentry(config)

        logger.info(f"Starting AI Overlord Bot in {config.environment} environment")

        # Create all components
        bot = await create_components(config)

        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        if sys.platform != 'win32':
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig,
                    lambda: signal_handler(bot, loop)
                )

        # Start the bot
        await start_bot(bot)

    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)