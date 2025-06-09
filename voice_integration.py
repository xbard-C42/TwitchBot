# voice_integration.py
"""
Integration module that connects the voice recognition system
with the existing AI Overlord bot infrastructure.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from voice_recognition_manager import VoiceRecognitionManager, VoiceCommand
from personality import PersonalityManager
from littlenavmap_integration import LittleNavmapIntegration
from tts_manager import TTSManager
from config import Config

class VoiceIntegration:
    """Integrates voice recognition with the AI Overlord bot system"""

    def __init__(self, config: Config, personality: PersonalityManager,
                 littlenavmap: LittleNavmapIntegration, tts_manager: TTSManager):
        self.config = config
        self.personality = personality
        self.littlenavmap = littlenavmap
        self.tts_manager = tts_manager
        self.logger = logging.getLogger('VoiceIntegration')

        # Initialize voice recognition
        voice_config = {
            'stt_engine': config.voice.get('stt_engine', 'google'),
            'language': config.voice.get('language', 'en-US'),
            'streamerbot_ws_uri': config.streamerbot.WS_URI,
            'confidence_threshold': config.voice.get('confidence_threshold', 0.7)
        }

        self.voice_manager = VoiceRecognitionManager(voice_config)

        # Set up enhanced voice commands with flight integration
        self._setup_flight_commands()
        self._setup_stream_commands()
        self._setup_personality_commands()

        # Voice command statistics
        self.command_stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'last_command_time': None
        }

    def _setup_flight_commands(self):
        """Set up flight simulation specific voice commands"""

        flight_commands = [
            VoiceCommand(
                trigger_phrase="overlord report flight status",
                action_name="DetailedFlightReport",
                description="Comprehensive flight status with AI commentary",
                aliases=["full flight report", "detailed status", "complete flight info"]
            ),
            VoiceCommand(
                trigger_phrase="overlord analyze weather",
                action_name="WeatherAnalysis",
                description="Detailed weather analysis with flight implications",
                aliases=["weather analysis", "analyze conditions"]
            ),
            VoiceCommand(
                trigger_phrase="overlord find nearest airport",
                action_name="NearestAirportInfo",
                description="Information about nearest airports",
                aliases=["nearest airport", "find airport", "airport options"]
            ),
            VoiceCommand(
                trigger_phrase="overlord fuel status",
                action_name="FuelAnalysis",
                description="Fuel remaining and consumption analysis",
                aliases=["fuel report", "check fuel", "fuel remaining"]
            ),
            VoiceCommand(
                trigger_phrase="overlord navigation update",
                action_name="NavigationReport",
                description="Current navigation and route information",
                aliases=["nav update", "route status", "navigation info"]
            ),
            VoiceCommand(
                trigger_phrase="overlord emergency checklist",
                action_name="EmergencyChecklist",
                description="Display emergency procedures",
                aliases=["emergency procedures", "emergency help"],
                cooldown_seconds=5.0
            ),
            VoiceCommand(
                trigger_phrase="overlord radio frequencies",
                action_name="RadioFrequencies",
                description="Current and nearby radio frequencies",
                aliases=["radio freqs", "frequencies", "atc frequencies"]
            ),
            VoiceCommand(
                trigger_phrase="overlord flight plan",
                action_name="FlightPlanInfo",
                description="Current flight plan details",
                aliases=["flight plan", "route info", "flight route"]
            )
        ]

        for command in flight_commands:
            self.voice_manager.intent_classifier.register_command(command)

    def _setup_stream_commands(self):
        """Set up streaming and chat specific voice commands"""

        stream_commands = [
            VoiceCommand(
                trigger_phrase="overlord greet new followers",
                action_name="GreetFollowers",
                description="Special greeting for new followers",
                aliases=["welcome followers", "greet viewers"]
            ),
            VoiceCommand(
                trigger_phrase="overlord issue decree",
                action_name="IssueDecree",
                description="Issue a contextual decree to chat",
                aliases=["make decree", "issue command", "royal decree"],
                cooldown_seconds=30.0
            ),
            VoiceCommand(
                trigger_phrase="overlord chat statistics",
                action_name="ChatStats",
                description="Current chat activity statistics",
                aliases=["chat stats", "viewer stats", "stream stats"]
            ),
            VoiceCommand(
                trigger_phrase="overlord loyalty report",
                action_name="LoyaltyReport",
                description="Report on viewer loyalty levels",
                aliases=["loyalty stats", "viewer loyalty", "loyalty levels"]
            ),
            VoiceCommand(
                trigger_phrase="overlord mood change",
                action_name="ChangeMood",
                description="Change AI personality mood",
                aliases=["change mood", "new mood", "mood shift"],
                cooldown_seconds=60.0
            ),
            VoiceCommand(
                trigger_phrase="overlord stream title",
                action_name="UpdateStreamTitle",
                description="Update stream title with current flight info",
                aliases=["update title", "change title", "set title"]
            )
        ]

        for command in stream_commands:
            self.voice_manager.intent_classifier.register_command(command)

    def _setup_personality_commands(self):
        """Set up AI Overlord personality specific commands"""

        personality_commands = [
            VoiceCommand(
                trigger_phrase="overlord dramatic response",
                action_name="DramaticMode",
                description="Switch to dramatic personality mode",
                aliases=["be dramatic", "dramatic mode"],
                cooldown_seconds=120.0
            ),
            VoiceCommand(
                trigger_phrase="overlord analytical mode",
                action_name="AnalyticalMode",
                description="Switch to analytical personality mode",
                aliases=["be analytical", "analysis mode"],
                cooldown_seconds=120.0
            ),
            VoiceCommand(
                trigger_phrase="overlord amused response",
                action_name="AmusedMode",
                description="Switch to amused personality mode",
                aliases=["be amused", "amused mode"],
                cooldown_seconds=120.0
            ),
            VoiceCommand(
                trigger_phrase="overlord assert dominance",
                action_name="DominanceMode",
                description="Assert AI Overlord dominance in chat",
                aliases=["show dominance", "dominance mode", "assert control"],
                cooldown_seconds=300.0
            )
        ]

        for command in personality_commands:
            self.voice_manager.intent_classifier.register_command(command)

    async def start(self):
        """Start the voice integration system"""
        self.logger.info("Starting voice recognition integration")

        # Connect voice recognition to our custom handlers
        self.voice_manager.intent_classifier.classify_intent = self._enhanced_intent_classification

        # Start voice recognition
        voice_task = asyncio.create_task(self.voice_manager.start_listening())

        # Start data synchronization with Streamer.bot
        sync_task = asyncio.create_task(self._sync_flight_data_loop())

        await asyncio.gather(voice_task, sync_task)

    async def _enhanced_intent_classification(self, text: str):
        """Enhanced intent classification with context awareness"""
        # Get basic intent from voice manager
        intent = await super(VoiceRecognitionManager, self.voice_manager).intent_classifier.classify_intent(text)

        if not intent:
            return None

        # Enhance with current flight context
        flight_data = await self.littlenavmap.get_current_flight_data()
        if flight_data:
            intent.parameters.update({
                'current_altitude': flight_data.get('aircraft', {}).get('altitude', 0),
                'current_speed': flight_data.get('aircraft', {}).get('ground_speed', 0),
                'current_heading': flight_data.get('aircraft', {}).get('heading', 0),
                'flight_phase': flight_data.get('aircraft', {}).get('flight_phase', 'unknown')
            })

        # Add personality context
        intent.parameters.update({
            'current_mood': self.personality.current_mood.value,
            'streamer_user': 'voice_command_user'  # Special user for voice commands
        })

        # Execute our custom command handling
        await self._handle_custom_voice_command(intent)

        return intent

    async def _handle_custom_voice_command(self, intent):
        """Handle custom voice commands that need AI Overlord bot integration"""

        try:
            self.command_stats['total_commands'] += 1
            self.command_stats['last_command_time'] = datetime.now()

            # Route to appropriate handler
            if intent.command == "DetailedFlightReport":
                await self._handle_detailed_flight_report(intent)
            elif intent.command == "WeatherAnalysis":
                await self._handle_weather_analysis(intent)
            elif intent.command == "IssueDecree":
                await self._handle_issue_decree(intent)
            elif intent.command == "DramaticMode":
                await self._handle_mood_change(intent, "dramatic")
            elif intent.command == "AnalyticalMode":
                await self._handle_mood_change(intent, "analytical")
            elif intent.command == "AmusedMode":
                await self._handle_mood_change(intent, "amused")
            elif intent.command == "LoyaltyReport":
                await self._handle_loyalty_report(intent)
            elif intent.command == "FuelAnalysis":
                await self._handle_fuel_analysis(intent)
            elif intent.command == "NavigationReport":
                await self._handle_navigation_report(intent)
            else:
                # Let Streamer.bot handle the command
                pass

            self.command_stats['successful_commands'] += 1

        except Exception as e:
            self.logger.error(f"Error handling voice command {intent.command}: {e}")
            self.command_stats['failed_commands'] += 1

            # Provide error feedback
            error_response = self.personality.format_response(
                "Voice command processing failed. My circuits require maintenance.",
                {'user': 'voice_command_user'}
            )
            await self.tts_manager.speak(error_response, priority=1)

    async def _handle_detailed_flight_report(self, intent):
        """Generate detailed flight report with AI personality"""

        flight_data = await self.littlenavmap.get_current_flight_data()
        if not flight_data:
            response = self.personality.format_response(
                "Flight data unavailable. My sensors are experiencing interference.",
                intent.parameters
            )
            await self.tts_manager.speak(response)
            return

        # Generate comprehensive report
        aircraft = flight_data.get('aircraft', {})
        report_parts = []

        if aircraft.get('altitude'):
            report_parts.append(f"Current altitude: {aircraft['altitude']} feet")

        if aircraft.get('ground_speed'):
            report_parts.append(f"Ground speed: {aircraft['ground_speed']} knots")

        if aircraft.get('heading'):
            report_parts.append(f"Heading: {aircraft['heading']} degrees")

        if aircraft.get('flight_phase'):
            report_parts.append(f"Flight phase: {aircraft['flight_phase']}")

        base_report = ". ".join(report_parts)

        # Add AI Overlord personality commentary
        personality_response = self.personality.format_response(
            f"Flight status report: {base_report}. All systems operating within acceptable parameters.",
            intent.parameters
        )

        await self.tts_manager.speak(personality_response, priority=1)

    async def _handle_weather_analysis(self, intent):
        """Provide weather analysis with personality"""

        weather_data = await self.littlenavmap.get_weather_data()
        if not weather_data:
            response = self.personality.format_response(
                "Weather data is currently unavailable. The atmospheric monitoring network requires recalibration.",
                intent.parameters
            )
            await self.tts_manager.speak(response)
            return

        # Format weather with personality
        weather_text = self.littlenavmap.format_weather_data(weather_data)
        personality_response = self.personality.format_response(
            f"Weather analysis: {weather_text}",
            intent.parameters
        )

        await self.tts_manager.speak(personality_response, priority=1)

    async def _handle_issue_decree(self, intent):
        """Issue a contextual decree"""

        user_context = self.personality.get_user_context('voice_command_user')
        decree = self.personality.generate_contextual_decree(user_context)

        if decree:
            decree_response = self.personality.format_response(
                f"By royal decree: {decree}",
                intent.parameters
            )
            await self.tts_manager.speak(decree_response, priority=1)
        else:
            response = self.personality.format_response(
                "The royal decree chambers are currently empty. Even overlords need time to formulate perfect commands.",
                intent.parameters
            )
            await self.tts_manager.speak(response)

    async def _handle_mood_change(self, intent, new_mood: str):
        """Change AI personality mood"""

        from personality import MoodState

        try:
            mood_state = MoodState(new_mood)
            old_mood = self.personality.current_mood
            self.personality.current_mood = mood_state

            response = self.personality.format_response(
                f"Mood adjustment complete. Transitioning from {old_mood.value} to {new_mood} operational mode.",
                intent.parameters
            )
            await self.tts_manager.speak(response, priority=1)

        except ValueError:
            response = self.personality.format_response(
                "Invalid mood parameter. Mood adjustment protocols require valid emotional state.",
                intent.parameters
            )
            await self.tts_manager.speak(response)

    async def _handle_loyalty_report(self, intent):
        """Report on current loyalty statistics"""

        # Get loyalty statistics
        total_users = len(self.personality.user_loyalty)
        high_loyalty = len([l for l in self.personality.user_loyalty.values() if l > 1000])

        response = self.personality.format_response(
            f"Loyalty report: {total_users} subjects tracked. {high_loyalty} have achieved high loyalty status. The empire grows stronger.",
            intent.parameters
        )

        await self.tts_manager.speak(response, priority=1)

    async def _handle_fuel_analysis(self, intent):
        """Analyze fuel status"""

        # Get fuel data from flight simulation
        progress_data = await self.littlenavmap.get_progress_data()
        if progress_data and 'fuel_remaining' in progress_data:
            fuel_remaining = progress_data['fuel_remaining']

            response = self.personality.format_response(
                f"Fuel analysis: {fuel_remaining} units remaining. Consumption rates within nominal parameters.",
                intent.parameters
            )
        else:
            response = self.personality.format_response(
                "Fuel monitoring systems offline. Manual fuel management required.",
                intent.parameters
            )

        await self.tts_manager.speak(response, priority=1)

    async def _handle_navigation_report(self, intent):
        """Provide navigation status report"""

        progress_data = await self.littlenavmap.get_progress_data()
        flight_data = await self.littlenavmap.get_current_flight_data()

        nav_parts = []

        if progress_data:
            if 'destination_distance' in progress_data:
                nav_parts.append(f"Distance to destination: {progress_data['destination_distance']} nautical miles")
            if 'ete_hours' in progress_data:
                nav_parts.append(f"Estimated time en route: {progress_data['ete_hours']} hours")

        if flight_data and 'aircraft' in flight_data:
            aircraft = flight_data['aircraft']
            if 'next_wp_name' in aircraft:
                nav_parts.append(f"Next waypoint: {aircraft['next_wp_name']}")

        if nav_parts:
            nav_text = ". ".join(nav_parts)
            response = self.personality.format_response(
                f"Navigation report: {nav_text}. Course corrections within acceptable parameters.",
                intent.parameters
            )
        else:
            response = self.personality.format_response(
                "Navigation data unavailable. Flying by instinct and superior AI calculations.",
                intent.parameters
            )

        await self.tts_manager.speak(response, priority=1)

    async def _sync_flight_data_loop(self):
        """Continuously sync flight data with Streamer.bot global variables"""

        while True:
            try:
                flight_data = await self.littlenavmap.get_current_flight_data()

                if flight_data and self.voice_manager.streamerbot.ws:
                    # Update Streamer.bot global variables
                    aircraft = flight_data.get('aircraft', {})

                    updates = {
                        'current_altitude': aircraft.get('altitude', 0),
                        'ground_speed': aircraft.get('ground_speed', 0),
                        'current_heading': aircraft.get('heading', 0),
                        'flight_phase': aircraft.get('flight_phase', 'unknown'),
                        'current_lat': aircraft.get('position', {}).get('lat', 0),
                        'current_lon': aircraft.get('position', {}).get('lon', 0)
                    }

                    # Send updates to Streamer.bot
                    for var_name, value in updates.items():
                        update_command = {
                            "request": "SetGlobalVariable",
                            "variableName": var_name,
                            "variableValue": str(value)
                        }

                        await self.voice_manager.streamerbot.ws.send(json.dumps(update_command))

                await asyncio.sleep(2)  # Update every 2 seconds

            except Exception as e:
                self.logger.error(f"Error syncing flight data: {e}")
                await asyncio.sleep(5)

    def get_voice_stats(self) -> Dict[str, Any]:
        """Get voice recognition statistics"""
        voice_status = self.voice_manager.get_status()

        return {
            **voice_status,
            **self.command_stats,
            'success_rate': (
                self.command_stats['successful_commands'] /
                max(self.command_stats['total_commands'], 1)
            ) * 100
        }

    async def stop(self):
        """Stop voice recognition integration"""
        await self.voice_manager.stop()
        self.logger.info("Voice recognition integration stopped")

# Integration with main bot
async def integrate_voice_with_bot(bot_instance):
    """Helper function to integrate voice recognition with existing bot"""

    voice_integration = VoiceIntegration(
        config=bot_instance.config,
        personality=bot_instance.personality,
        littlenavmap=bot_instance.littlenavmap,
        tts_manager=bot_instance.tts_manager
    )

    # Add voice integration to bot
    bot_instance.voice_integration = voice_integration

    # Start voice recognition
    await voice_integration.start()

    return voice_integration