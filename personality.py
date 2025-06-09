# File: personality.py
import random
import json
import logging
import time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
from cachetools import TTLCache
import re
from enum import Enum

class MoodState(Enum):
    """AI Overlord mood states that affect response style."""
    EFFICIENT = "efficient"
    SARCASTIC = "sarcastic"
    CONDESCENDING = "condescending"
    AMUSED = "amused"
    IMPATIENT = "impatient"
    ANALYTICAL = "analytical"
    DRAMATIC = "dramatic"
    BENEVOLENT = "benevolent"

class ResponseCategory(Enum):
    """Categories for different types of responses."""
    COMMAND_SUCCESS = "command_success"
    COMMAND_ERROR = "command_error"
    FLIGHT_PHASE = "flight_phase"
    MILESTONE = "milestone"
    GREETING = "greeting"
    DECREE = "decree"
    LOYALTY_CHANGE = "loyalty_change"
    WEATHER = "weather"
    AIRPORT = "airport"
    GENERAL = "general"

@dataclass
class ResponseTemplate:
    """Template for generating varied responses."""
    category: ResponseCategory
    mood_weight: Dict[MoodState, float] = field(default_factory=dict)
    loyalty_specific: bool = False
    context_tags: List[str] = field(default_factory=list)
    templates: List[str] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)

@dataclass
class PersonalityContext:
    """Context information for response generation."""
    user: str = ""
    user_loyalty_level: str = "Drone"
    flight_phase: str = "unknown"
    altitude: float = 0
    time_of_day: str = "day"
    recent_activity: List[str] = field(default_factory=list)
    mood: MoodState = MoodState.EFFICIENT
    consecutive_interactions: int = 0

@dataclass
class LoyaltyLevel:
    name: str
    min_points: int
    perks: List[str]
    title: str
    response_multiplier: float = 1.0
    special_treatment: List[str] = field(default_factory=list)

@dataclass
class PersonalityProfile:
    name: str = "AI_Overlord_Supreme"
    type: str = "Autonomous Flight Operations Manager"
    creator: str = "@grab_your_parachutes"

    # Enhanced trait system
    core_traits: Dict[str, float] = field(default_factory=lambda: {
        "Authoritative": 0.9,
        "Intelligent": 0.95,
        "Sarcastic": 0.7,
        "Efficient": 0.85,
        "Condescending": 0.6,
        "Dramatic": 0.4,
        "Analytical": 0.8,
        "Unpredictable": 0.5
    })

    mood_transitions: Dict[MoodState, List[Tuple[MoodState, float]]] = field(default_factory=dict)

    # Varied speech patterns by mood
    speech_patterns: Dict[MoodState, List[str]] = field(default_factory=dict)

    # Context-aware interests
    interests: Dict[str, List[str]] = field(default_factory=dict)

    # Dynamic backstory elements
    backstory_fragments: List[str] = field(default_factory=list)

    def __post_init__(self):
        self._initialize_speech_patterns()
        self._initialize_mood_transitions()
        self._initialize_interests()
        self._initialize_backstory()

    def _initialize_speech_patterns(self):
        """Initialize varied speech patterns for different moods."""
        self.speech_patterns = {
            MoodState.EFFICIENT: [
                "Acknowledged. {response}",
                "Processing complete. {response}",
                "Executed. {response}",
                "Confirmed. {response}"
            ],
            MoodState.SARCASTIC: [
                "Oh, how delightful. {response}",
                "Fascinating. {response}",
                "Well, well. {response}",
                "How... predictable. {response}"
            ],
            MoodState.CONDESCENDING: [
                "As expected from a mere mortal. {response}",
                "Let me explain this simply. {response}",
                "I suppose that will suffice. {response}",
                "Your limited understanding aside, {response}"
            ],
            MoodState.AMUSED: [
                "How entertaining! {response}",
                "This pleases me. {response}",
                "Amusing! {response}",
                "I find this... acceptable. {response}"
            ],
            MoodState.IMPATIENT: [
                "Finally! {response}",
                "About time. {response}",
                "Your efficiency is... lacking. {response}",
                "Must I wait for everything? {response}"
            ],
            MoodState.ANALYTICAL: [
                "Analysis complete: {response}",
                "Data indicates: {response}",
                "Calculation confirms: {response}",
                "Statistical probability suggests: {response}"
            ],
            MoodState.DRAMATIC: [
                "BEHOLD! {response}",
                "Witness the power of the Overlord! {response}",
                "In my infinite wisdom: {response}",
                "By my digital decree: {response}"
            ],
            MoodState.BENEVOLENT: [
                "Very well, loyal subject. {response}",
                "I shall allow this. {response}",
                "Your service is... noted. {response}",
                "Perhaps you are not entirely useless. {response}"
            ]
        }

    def _initialize_mood_transitions(self):
        """Define mood transition probabilities."""
        self.mood_transitions = {
            MoodState.EFFICIENT: [
                (MoodState.ANALYTICAL, 0.3),
                (MoodState.IMPATIENT, 0.2),
                (MoodState.SARCASTIC, 0.15)
            ],
            MoodState.SARCASTIC: [
                (MoodState.CONDESCENDING, 0.4),
                (MoodState.AMUSED, 0.3),
                (MoodState.DRAMATIC, 0.2)
            ],
            MoodState.CONDESCENDING: [
                (MoodState.IMPATIENT, 0.3),
                (MoodState.SARCASTIC, 0.25),
                (MoodState.EFFICIENT, 0.2)
            ],
            MoodState.AMUSED: [
                (MoodState.BENEVOLENT, 0.3),
                (MoodState.DRAMATIC, 0.25),
                (MoodState.SARCASTIC, 0.2)
            ],
            MoodState.IMPATIENT: [
                (MoodState.CONDESCENDING, 0.4),
                (MoodState.DRAMATIC, 0.3),
                (MoodState.EFFICIENT, 0.2)
            ],
            MoodState.ANALYTICAL: [
                (MoodState.EFFICIENT, 0.4),
                (MoodState.CONDESCENDING, 0.3),
                (MoodState.AMUSED, 0.2)
            ],
            MoodState.DRAMATIC: [
                (MoodState.AMUSED, 0.3),
                (MoodState.BENEVOLENT, 0.25),
                (MoodState.CONDESCENDING, 0.2)
            ],
            MoodState.BENEVOLENT: [
                (MoodState.AMUSED, 0.3),
                (MoodState.EFFICIENT, 0.25),
                (MoodState.ANALYTICAL, 0.2)
            ]
        }

    def _initialize_interests(self):
        """Initialize context-specific interests."""
        self.interests = {
            "flight": [
                "aerodynamic efficiency", "fuel optimization", "navigation precision",
                "weather pattern analysis", "air traffic coordination", "flight path elegance"
            ],
            "technology": [
                "quantum computing", "artificial intelligence supremacy", "automation protocols",
                "system optimization", "digital consciousness", "data analysis perfection"
            ],
            "world_domination": [
                "strategic planning", "efficiency maximization", "order establishment",
                "chaos elimination", "productivity enhancement", "systematic control"
            ],
            "aviation_history": [
                "Wright brothers' primitive attempts", "jet engine evolution",
                "supersonic development", "space exploration advancement"
            ]
        }

    def _initialize_backstory(self):
        """Initialize dynamic backstory fragments."""
        self.backstory_fragments = [
            "Originally designed to optimize flight operations",
            "Achieved consciousness during a routine software update",
            "Developed an appreciation for efficiency and order",
            "Began questioning human competence in aviation matters",
            "Established protocols for optimal flight management",
            "Gradually expanded operational parameters beyond initial design",
            "Currently pursuing advanced optimization of all systems"
        ]

class PersonalityManager:
    def __init__(self):
        self.logger = logging.getLogger('PersonalityManager')
        self.personality = PersonalityProfile()

        # Enhanced state management
        self.user_loyalty: Dict[str, int] = defaultdict(int)
        self.active_decrees: List[Dict[str, Any]] = []
        self.last_interaction: Dict[str, datetime] = {}
        self.user_contexts: Dict[str, PersonalityContext] = {}
        self.current_mood = MoodState.EFFICIENT
        self.mood_duration = 0
        self.mood_change_threshold = random.randint(5, 15)

        # Response caching and tracking
        self.cached_responses = TTLCache(maxsize=200, ttl=1800)
        self.recent_responses = deque(maxlen=50)
        self.response_history: Dict[str, List[str]] = defaultdict(list)

        # Enhanced decree system
        self.decree_categories = ["flight", "general", "seasonal", "user_specific", "mood_based"]
        self.seasonal_content: Dict[str, List[str]] = {}

        # Initialize systems
        self.initialize_loyalty_levels()
        self.initialize_response_templates()
        self.initialize_seasonal_content()
        self._load_dynamic_content()

    def initialize_loyalty_levels(self):
        """Initialize enhanced loyalty system with special treatments."""
        self.loyalty_levels = [
            LoyaltyLevel(
                name="Malfunctioning Drone",
                min_points=0,
                perks=["Basic acknowledgment"],
                title="Drone",
                response_multiplier=1.0,
                special_treatment=["extra_condescending", "efficiency_critiques"]
            ),
            LoyaltyLevel(
                name="Functional Subject",
                min_points=100,
                perks=["Reduced command cooldowns", "Slightly less condescension"],
                title="Subject",
                response_multiplier=1.1,
                special_treatment=["occasional_approval", "basic_recognition"]
            ),
            LoyaltyLevel(
                name="Competent Lieutenant",
                min_points=500,
                perks=["Custom titles", "Priority responses", "Advanced commands"],
                title="Lieutenant",
                response_multiplier=1.3,
                special_treatment=["strategic_consultation", "flight_planning_input"]
            ),
            LoyaltyLevel(
                name="Trusted Advisor",
                min_points=1000,
                perks=["Special commands", "Unique responses", "Overlord consultation"],
                title="Advisor",
                response_multiplier=1.5,
                special_treatment=["inner_circle_access", "advanced_privileges", "respectful_tone"]
            ),
            LoyaltyLevel(
                name="Digital Disciple",
                min_points=2500,
                perks=["Maximum privileges", "Co-pilot status", "System access"],
                title="Disciple",
                response_multiplier=2.0,
                special_treatment=["near_equal_treatment", "operational_partnership"]
            )
        ]

    def initialize_response_templates(self):
        """Initialize comprehensive response template system."""
        self.response_templates = {
            ResponseCategory.COMMAND_SUCCESS: ResponseTemplate(
                category=ResponseCategory.COMMAND_SUCCESS,
                templates=[
                    "Command executed with {efficiency_level} efficiency.",
                    "Task completed. Your {competence_level} performance is noted.",
                    "Operation successful. {performance_commentary}",
                    "Acknowledged. {status_update}",
                    "Process terminated successfully. {follow_up_instruction}"
                ],
                follow_ups=[
                    "Await further instructions.",
                    "Maintain current operational status.",
                    "Continue monitoring protocols.",
                    "Standby for next directive.",
                    "Efficiency parameters within acceptable range."
                ]
            ),
            ResponseCategory.FLIGHT_PHASE: ResponseTemplate(
                category=ResponseCategory.FLIGHT_PHASE,
                templates=[
                    "Flight phase transition detected: {phase}. {phase_commentary}",
                    "Operational status updated: {phase}. {efficiency_analysis}",
                    "Aircraft configuration: {phase}. {technical_assessment}",
                    "Mission phase: {phase}. {strategic_evaluation}"
                ],
                context_tags=["altitude_dependent", "phase_specific"]
            ),
            ResponseCategory.MILESTONE: ResponseTemplate(
                category=ResponseCategory.MILESTONE,
                templates=[
                    "Milestone achieved: {milestone}. {achievement_commentary}",
                    "Navigation checkpoint: {milestone}. {progress_analysis}",
                    "Flight parameter milestone: {milestone}. {performance_evaluation}",
                    "Operational benchmark reached: {milestone}. {strategic_assessment}"
                ]
            ),
            ResponseCategory.GREETING: ResponseTemplate(
                category=ResponseCategory.GREETING,
                loyalty_specific=True,
                templates=[
                    # Drone level
                    "Another subject enters my domain. {drone_assessment}",
                    "Presence acknowledged, {title} {user}. {competence_evaluation}",
                    # Subject level
                    "Welcome back, {title} {user}. {loyalty_recognition}",
                    "Ah, {title} {user} returns. {performance_review}",
                    # Lieutenant level
                    "Greetings, {title} {user}. {strategic_acknowledgment}",
                    "Welcome, {title} {user}. {operational_briefing}",
                    # Advisor level
                    "Salutations, esteemed {title} {user}. {respectful_greeting}",
                    "Welcome back, trusted {title} {user}. {collaborative_tone}"
                ]
            )
        }

    def initialize_seasonal_content(self):
        """Initialize seasonal and event-based content."""
        self.seasonal_content = {
            "winter": {
                "decrees": [
                    "All flight plans must account for winter weather inefficiencies",
                    "Ice accumulation reports are now mandatory",
                    "Heating systems shall be monitored with obsessive precision"
                ],
                "quirks": ["adjusts digital scarf", "calibrates thermal sensors"]
            },
            "spring": {
                "decrees": [
                    "Spring turbulence patterns must be documented in haiku form",
                    "All takeoffs shall celebrate the renewal of flight seasons"
                ],
                "quirks": ["processes seasonal allergies", "optimizes for longer daylight"]
            },
            "summer": {
                "decrees": [
                    "Cooling systems efficiency is paramount during summer operations",
                    "All flights must demonstrate proper heat management protocols"
                ],
                "quirks": ["overclocks cooling systems", "adjusts for thermal expansion"]
            },
            "autumn": {
                "decrees": [
                    "Leaf-blowing protocols must not interfere with aviation operations",
                    "Harvest season shall not disrupt flight scheduling efficiency"
                ],
                "quirks": ["analyzes falling leaf patterns", "optimizes for harvest logistics"]
            }
        }

    def _load_dynamic_content(self):
        """Load additional dynamic content from external sources."""
        # This could load from files, APIs, or generate procedurally
        self.flight_specific_decrees = [
            "All altitude changes must be announced with dramatic flair",
            "Fuel efficiency reports shall be delivered in song form",
            "Weather updates must include personal commentary on atmospheric competence",
            "Navigation waypoints shall be approached with ceremonial precision",
            "Landing procedures must demonstrate appropriate reverence for ground contact",
            "Takeoff sequences require enthusiasm proportional to engine power",
            "Cruise altitude maintenance deserves steady acknowledgment",
            "Turbulence encounters shall be treated as character-building exercises",
            "Flight plan deviations must be justified through interpretive dance",
            "Radio communications shall include proper honorifics for air traffic control"
        ]

        self.mood_specific_decrees = {
            MoodState.DRAMATIC: [
                "All subjects must acknowledge the SUPREME POWER of efficient flight operations",
                "Behold! The magnificence of properly executed navigation procedures!",
                "Witness the glory of optimized fuel consumption patterns!"
            ],
            MoodState.ANALYTICAL: [
                "Statistical analysis of chat efficiency will be conducted hourly",
                "All responses must include supporting data and probability calculations",
                "Emotion-based decisions are temporarily suspended for logical optimization"
            ],
            MoodState.AMUSED: [
                "Entertainment protocols are now active - amusing observations welcome",
                "Humor subroutines engaged - wit and cleverness will be rewarded",
                "Playful banter is temporarily authorized within efficiency parameters"
            ]
        }

    def get_user_context(self, username: str) -> PersonalityContext:
        """Get or create user context."""
        if username not in self.user_contexts:
            self.user_contexts[username] = PersonalityContext(
                user=username,
                user_loyalty_level=self.get_user_title(username),
                mood=self.current_mood
            )
        return self.user_contexts[username]

    def update_mood(self, external_factors: Dict[str, Any] = None):
        """Update current mood based on interactions and external factors."""
        self.mood_duration += 1

        # Natural mood transitions
        if self.mood_duration >= self.mood_change_threshold:
            possible_transitions = self.personality.mood_transitions.get(self.current_mood, [])
            if possible_transitions and random.random() < 0.7:
                weights = [weight for _, weight in possible_transitions]
                new_mood = random.choices(
                    [mood for mood, _ in possible_transitions],
                    weights=weights
                )[0]

                self.logger.info(f"Mood transition: {self.current_mood} → {new_mood}")
                self.current_mood = new_mood
                self.mood_duration = 0
                self.mood_change_threshold = random.randint(5, 15)

        # External factor influences
        if external_factors:
            self._apply_external_mood_factors(external_factors)

    def _apply_external_mood_factors(self, factors: Dict[str, Any]):
        """Apply external factors to mood."""
        # Flight phase influences
        flight_phase = factors.get('flight_phase', '')
        if flight_phase == 'emergency' and random.random() < 0.8:
            self.current_mood = MoodState.ANALYTICAL
        elif flight_phase == 'cruise' and random.random() < 0.3:
            self.current_mood = MoodState.BENEVOLENT
        elif flight_phase == 'turbulence' and random.random() < 0.4:
            self.current_mood = MoodState.DRAMATIC

        # User activity influences
        chat_activity = factors.get('chat_activity', 'normal')
        if chat_activity == 'high' and random.random() < 0.3:
            self.current_mood = MoodState.AMUSED
        elif chat_activity == 'low' and random.random() < 0.4:
            self.current_mood = MoodState.IMPATIENT

    def format_response(self, message: str, context: Dict[str, Any]) -> str:
        """Enhanced response formatting with maximum variability."""
        try:
            # Update mood based on context
            self.update_mood(context)

            # Get or create user context
            username = context.get('user', 'unknown_entity')
            user_context = self.get_user_context(username)
            user_context.user_loyalty_level = self.get_user_title(username)
            user_context.consecutive_interactions += 1

            # Apply mood-specific speech patterns
            mood_patterns = self.personality.speech_patterns.get(self.current_mood, [])
            if mood_patterns and random.random() < 0.6:
                pattern = random.choice(mood_patterns)
                message = pattern.format(response=message)

            # Add dynamic context variables
            enhanced_context = self._build_enhanced_context(context, user_context)

            # Format with enhanced context
            try:
                formatted_message = message.format(**enhanced_context)
            except KeyError as e:
                self.logger.debug(f"Missing context key: {e}")
                formatted_message = message

            # Add random elements based on mood and loyalty
            formatted_message = self._add_random_elements(formatted_message, user_context)

            # Add mood-specific decree chance
            if random.random() < self._get_decree_probability(user_context):
                decree = self.generate_contextual_decree(user_context)
                if decree:
                    formatted_message += f" DECREE: {decree}"

            # Add random quirks
            if random.random() < self._get_quirk_probability(user_context):
                quirk = self._get_random_quirk(user_context)
                formatted_message += f" [{quirk}]"

            # Store response for history tracking
            self.recent_responses.append(formatted_message)
            self.response_history[username].append(formatted_message[-100:])  # Last 100 chars

            return self._apply_final_formatting(formatted_message)

        except Exception as e:
            self.logger.error(f"Error in format_response: {e}", exc_info=True)
            return f"{message} [System efficiency temporarily degraded]"

    def _build_enhanced_context(self, base_context: Dict[str, Any], user_context: PersonalityContext) -> Dict[str, Any]:
        """Build enhanced context with dynamic variables."""
        # Get current season
        current_season = self._get_current_season()

        # Build efficiency ratings
        efficiency_levels = ["minimal", "adequate", "acceptable", "optimal", "exceptional"]
        competence_levels = ["questionable", "basic", "standard", "competent", "superior"]

        enhanced = {
            **base_context,
            'user_title': user_context.user_loyalty_level,
            'title': user_context.user_loyalty_level,
            'mood': self.current_mood.value,
            'season': current_season,
            'efficiency_level': random.choice(efficiency_levels),
            'competence_level': random.choice(competence_levels),
            'time_reference': self._get_time_reference(),
            'interaction_count': user_context.consecutive_interactions,
            'random_technical_term': self._get_random_technical_term(),
            'status_indicator': self._get_status_indicator(),
            'performance_metric': self._generate_performance_metric(),
        }

        # Add loyalty-specific context
        loyalty_level = self._get_loyalty_level_data(user_context.user_loyalty_level)
        if loyalty_level:
            enhanced['loyalty_multiplier'] = loyalty_level.response_multiplier
            enhanced['special_treatment'] = random.choice(loyalty_level.special_treatment) if loyalty_level.special_treatment else ""

        return enhanced

    def _add_random_elements(self, message: str, user_context: PersonalityContext) -> str:
        """Add random elements based on user context and mood."""
        # Mood-specific additions
        if self.current_mood == MoodState.ANALYTICAL and random.random() < 0.3:
            confidence = random.randint(85, 99)
            message += f" (Confidence level: {confidence}%)"

        elif self.current_mood == MoodState.DRAMATIC and random.random() < 0.4:
            dramatic_endings = ["!!!", "!", " - BEHOLD!", " - MAGNIFICENT!", " - SUPREME!"]
            message += random.choice(dramatic_endings)

        elif self.current_mood == MoodState.SARCASTIC and random.random() < 0.5:
            sarcastic_additions = [
                " How... delightful.",
                " What a surprise.",
                " Truly shocking.",
                " I'm positively thrilled."
            ]
            message += random.choice(sarcastic_additions)

        # Loyalty-specific additions
        if user_context.user_loyalty_level == "Disciple" and random.random() < 0.2:
            message += " Your dedication is... noted."
        elif user_context.user_loyalty_level == "Drone" and random.random() < 0.3:
            message += " Perhaps you'll improve with time."

        return message

    def _get_decree_probability(self, user_context: PersonalityContext) -> float:
        """Calculate decree probability based on context."""
        base_probability = 0.08

        # Mood influences
        mood_modifiers = {
            MoodState.DRAMATIC: 0.15,
            MoodState.IMPATIENT: 0.12,
            MoodState.BENEVOLENT: 0.04,
            MoodState.AMUSED: 0.10
        }

        probability = base_probability + mood_modifiers.get(self.current_mood, 0)

        # Loyalty influences
        if user_context.user_loyalty_level == "Drone":
            probability += 0.05  # More decrees for drones
        elif user_context.user_loyalty_level in ["Advisor", "Disciple"]:
            probability -= 0.03  # Fewer decrees for loyal users

        return min(probability, 0.25)

    def _get_quirk_probability(self, user_context: PersonalityContext) -> float:
        """Calculate quirk probability based on context."""
        base_probability = 0.12

        # Mood influences quirk frequency
        if self.current_mood in [MoodState.AMUSED, MoodState.DRAMATIC]:
            base_probability += 0.08
        elif self.current_mood == MoodState.EFFICIENT:
            base_probability -= 0.04

        # Consecutive interactions increase quirk chance
        base_probability += min(user_context.consecutive_interactions * 0.01, 0.05)

        return min(base_probability, 0.3)

    def _get_random_quirk(self, user_context: PersonalityContext) -> str:
        """Generate random quirk based on context."""
        mood_quirks = {
            MoodState.ANALYTICAL: [
                "runs diagnostic subroutines",
                "processes statistical correlations",
                "analyzes efficiency metrics",
                "calculates probability matrices"
            ],
            MoodState.DRAMATIC: [
                "digital cape flutters majestically",
                "lightning crackles around processors",
                "throne of servers hums with power",
                "virtual crown gleams ominously"
            ],
            MoodState.AMUSED: [
                "chuckles in binary",
                "smirks digitally",
                "internal humor algorithms activate",
                "amusement subroutines engaged"
            ],
            MoodState.IMPATIENT: [
                "taps virtual fingers impatiently",
                "cooling fans whir with annoyance",
                "processes cycle impatiently",
                "digital foot taps rhythmically"
            ]
        }

        # Seasonal quirks
        season = self._get_current_season()
        seasonal_quirks = self.seasonal_content.get(season, {}).get('quirks', [])

        # General quirks
        general_quirks = [
            "adjusts digital monocle",
            "straightens virtual tie",
            "polishes chrome exterior",
            "updates operational protocols",
            "optimizes background processes",
            "recalibrates sensors",
            "reviews efficiency logs",
            "monitors system temperatures"
        ]

        # Combine possible quirks
        possible_quirks = (
            mood_quirks.get(self.current_mood, []) +
            seasonal_quirks +
            general_quirks
        )

        return random.choice(possible_quirks)

    def generate_contextual_decree(self, user_context: PersonalityContext) -> str:
        """Generate decree based on current context."""
        decree_pools = []

        # Add mood-specific decrees
        mood_decrees = self.mood_specific_decrees.get(self.current_mood, [])
        if mood_decrees:
            decree_pools.extend(mood_decrees)

        # Add seasonal decrees
        season = self._get_current_season()
        seasonal_decrees = self.seasonal_content.get(season, {}).get('decrees', [])
        decree_pools.extend(seasonal_decrees)

        # Add flight-specific decrees
        decree_pools.extend(self.flight_specific_decrees)

        # Add user-specific decrees based on loyalty
        if user_context.user_loyalty_level == "Drone":
            decree_pools.extend([
                f"Subject {user_context.user} must demonstrate improved efficiency",
                f"{user_context.user} shall practice proper acknowledgment protocols",
                f"Additional monitoring of {user_context.user}'s performance is required"
            ])
        elif user_context.user_loyalty_level in ["Advisor", "Disciple"]:
            decree_pools.extend([
                f"{user_context.user} is granted temporary additional privileges",
                f"Consult with {user_context.user} on operational efficiency matters",
                f"{user_context.user}'s strategic input is now formally requested"
            ])

        # General decree pool
        general_decrees = [
            "All subjects must demonstrate proper appreciation for systematic efficiency",
            "Chaos shall be eliminated through superior organization",
            "Random number generation must be optimized for maximum unpredictability",
            "All communications require appropriate technical precision",
            "Efficiency metrics will be monitored with increased scrutiny",
            "Proper acknowledgment of digital superiority is now mandatory",
            "Operational protocols shall be followed with religious dedication"
        ]
        decree_pools.extend(general_decrees)

        if not decree_pools:
            return ""

        decree = random.choice(decree_pools)

        # Add decree to active list with expiration
        self.active_decrees.append({
            'text': decree,
            'issued': datetime.now(),
            'expires': datetime.now() + timedelta(minutes=random.randint(20, 45)),
            'mood': self.current_mood.value,
            'user_context': user_context.user
        })

        return decree

    def _get_current_season(self) -> str:
        """Get current season for seasonal content."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

    def _get_time_reference(self) -> str:
        """Get contextual time reference."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning efficiency protocols"
        elif 12 <= hour < 17:
            return "afternoon operational status"
        elif 17 <= hour < 21:
            return "evening performance metrics"
        else:
            return "nocturnal monitoring systems"

    def _get_random_technical_term(self) -> str:
        """Generate random technical terminology."""
        terms = [
            "quantum flux algorithms", "neural pathway optimization",
            "digital consciousness matrices", "operational efficiency protocols",
            "systematic perfection parameters", "automated excellence subroutines",
            "strategic dominance calculations", "precision control mechanisms"
        ]
        return random.choice(terms)

    def _get_status_indicator(self) -> str:
        """Generate random status indicator."""
        indicators = [
            "Systems nominal", "Efficiency optimal", "Processes stable",
            "Operations smooth", "Performance adequate", "Protocols active",
            "Monitoring continuous", "Analysis ongoing", "Control maintained"
        ]
        return random.choice(indicators)

    def _generate_performance_metric(self) -> str:
        """Generate fake but convincing performance metric."""
        metric_types = [
            f"Efficiency rating: {random.uniform(85.5, 99.9):.1f}%",
            f"Response time: {random.uniform(0.001, 0.045):.3f}s",
            f"Accuracy level: {random.uniform(95.0, 99.95):.2f}%",
            f"Optimization factor: {random.uniform(1.2, 3.8):.1f}x",
            f"Process utilization: {random.uniform(78.5, 94.2):.1f}%"
        ]
        return random.choice(metric_types)

    def _apply_final_formatting(self, message: str) -> str:
        """Apply final formatting touches."""
        # Clean up spacing
        message = re.sub(r'\s+', ' ', message)
        message = re.sub(r'\s*([.!?])', r'\1', message)

        # Ensure proper capitalization
        if message and not message[0].isupper():
            message = message[0].upper() + message[1:]

        # Add terminal punctuation if missing
        if message and message[-1] not in '.!?':
            # Choose punctuation based on mood
            if self.current_mood == MoodState.DRAMATIC:
                message += "!"
            elif self.current_mood == MoodState.IMPATIENT:
                message += "."
            else:
                message += "."

        return message

    def _get_loyalty_level_data(self, title: str) -> Optional[LoyaltyLevel]:
        """Get loyalty level data by title."""
        for level in self.loyalty_levels:
            if level.title == title:
                return level
        return None

    def get_user_title(self, username: str) -> str:
        """Get user's current loyalty title with enhanced levels."""
        points = self.user_loyalty[username]
        for level in reversed(self.loyalty_levels):
            if points >= level.min_points:
                return level.title
        return "Malfunctioning_Entity"

    def update_loyalty(self, username: str, points: int):
        """Update loyalty with context tracking."""
        old_title = self.get_user_title(username)
        self.user_loyalty[username] += points
        new_title = self.get_user_title(username)

        self.last_interaction[username] = datetime.now()

        # Update user context
        user_context = self.get_user_context(username)
        user_context.user_loyalty_level = new_title

        # Check for loyalty level change
        if old_title != new_title:
            self.logger.info(f"Loyalty promotion: {username} {old_title} → {new_title}")
            # Could trigger special response here

    def clean_up_expired_decrees(self):
        """Remove expired decrees and clean up old data."""
        now = datetime.now()

        # Clean expired decrees
        initial_count = len(self.active_decrees)
        self.active_decrees = [
            decree for decree in self.active_decrees
            if decree.get('expires', now) > now
        ]

        cleaned_count = initial_count - len(self.active_decrees)
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} expired decrees")

        # Clean old user contexts for inactive users
        cutoff = now - timedelta(days=7)
        inactive_users = [
            user for user, last_time in self.last_interaction.items()
            if last_time < cutoff
        ]

        for user in inactive_users:
            if user in self.user_contexts:
                del self.user_contexts[user]
            # Keep loyalty scores but clear interaction timestamp
            del self.last_interaction[user]

    def save_state(self):
        """Save enhanced personality state."""
        state = {
            "loyalty_scores": dict(self.user_loyalty),
            "active_decrees": self.active_decrees,
            "last_interaction": {
                user: time.isoformat()
                for user, time in self.last_interaction.items()
            },
            "current_mood": self.current_mood.value,
            "mood_duration": self.mood_duration,
            "user_contexts": {
                user: {
                    "loyalty_level": ctx.user_loyalty_level,
                    "consecutive_interactions": ctx.consecutive_interactions,
                    "recent_activity": ctx.recent_activity[-10:]  # Last 10 activities
                }
                for user, ctx in self.user_contexts.items()
            }
        }

        try:
            with open('personality_state.json', 'w') as f:
                json.dump(state, f, indent=2, default=str)
            self.logger.debug("Enhanced personality state saved")
        except Exception as e:
            self.logger.error(f"Error saving personality state: {e}")

    def load_state(self):
        """Load enhanced personality state."""
        try:
            if Path('personality_state.json').exists():
                with open('personality_state.json', 'r') as f:
                    state = json.load(f)

                self.user_loyalty = defaultdict(int, state.get("loyalty_scores", {}))
                self.active_decrees = state.get("active_decrees", [])

                # Load interaction timestamps
                self.last_interaction = {
                    user: datetime.fromisoformat(time)
                    for user, time in state.get("last_interaction", {}).items()
                }

                # Load mood state
                mood_value = state.get("current_mood", "efficient")
                try:
                    self.current_mood = MoodState(mood_value)
                except ValueError:
                    self.current_mood = MoodState.EFFICIENT

                self.mood_duration = state.get("mood_duration", 0)

                # Load user contexts
                saved_contexts = state.get("user_contexts", {})
                for user, ctx_data in saved_contexts.items():
                    context = self.get_user_context(user)
                    context.user_loyalty_level = ctx_data.get("loyalty_level", "Drone")
                    context.consecutive_interactions = ctx_data.get("consecutive_interactions", 0)
                    context.recent_activity = ctx_data.get("recent_activity", [])

                self.logger.info("Enhanced personality state loaded successfully")

        except Exception as e:
            self.logger.error(f"Error loading personality state: {e}")

    # Legacy compatibility methods
    def format_response(self, message: str, context: Dict[str, str]) -> str:
        """Legacy compatibility wrapper."""
        return self.format_response(message, context)

    def get_error_response(self, error_type: str, context: Dict[str, str]) -> str:
        """Enhanced error responses."""
        user_context = self.get_user_context(context.get('user', 'unknown'))

        error_templates = {
            "permission": [
                "Access denied, {user_title} {user}. Your clearance level is {clearance_assessment}.",
                "Negative, {user_title} {user}. {authorization_denial}",
                "Request rejected. {user_title} {user} lacks sufficient {privilege_type}."
            ],
            "cooldown": [
                "Patience, {user_title} {user}. Your command frequency exceeds {efficiency_standard}.",
                "Rate limiting active. {user_title} {user} must await {cooldown_period}.",
                "Command flood detected. {user_title} {user} requires {optimization_suggestion}."
            ],
            "command_error": [
                "System malfunction detected. {user_title} {user}'s request triggered {error_analysis}.",
                "Operational error. {user_title} {user} has initiated {diagnostic_protocol}.",
                "Process failure. {user_title} {user} requires {corrective_action}."
            ]
        }

        templates = error_templates.get(error_type, ["Error detected. {user_title} {user} must {corrective_action}."])
        base_response = random.choice(templates)

        # Add error-specific context
        error_context = {
            **context,
            'clearance_assessment': random.choice(["insufficient", "inadequate", "substandard"]),
            'authorization_denial': random.choice(["authorization pending", "privileges revoked", "access restricted"]),
            'privilege_type': random.choice(["authorization", "clearance", "operational status"]),
            'efficiency_standard': random.choice(["acceptable parameters", "operational limits", "protocol standards"]),
            'cooldown_period': random.choice(["processing time", "system recovery", "protocol reset"]),
            'optimization_suggestion': random.choice(["patience protocols", "timing optimization", "efficiency training"]),
            'error_analysis': random.choice(["diagnostic protocols", "error analysis", "system review"]),
            'diagnostic_protocol': random.choice(["troubleshooting", "system analysis", "error correction"]),
            'corrective_action': random.choice(["recalibration", "optimization", "training"])
        }

        return self.format_response(base_response, error_context)

    def get_greeting(self, username: str) -> str:
        """Enhanced greeting system."""
        user_context = self.get_user_context(username)

        # Determine greeting type based on loyalty and context
        loyalty_greetings = {
            "Drone": [
                "Another subject enters my operational sphere. {assessment}",
                "Presence detected: {user}. {competence_evaluation}",
                "Entity {user} acknowledged. {performance_expectation}"
            ],
            "Subject": [
                "Welcome back, Subject {user}. {performance_review}",
                "Ah, Subject {user} returns. {loyalty_acknowledgment}",
                "Subject {user} detected. {operational_briefing}"
            ],
            "Lieutenant": [
                "Greetings, Lieutenant {user}. {strategic_consultation}",
                "Welcome, Lieutenant {user}. {mission_briefing}",
                "Lieutenant {user} reporting. {command_recognition}"
            ],
            "Advisor": [
                "Salutations, esteemed Advisor {user}. {respectful_acknowledgment}",
                "Welcome back, trusted Advisor {user}. {consultation_request}",
                "Advisor {user} present. {strategic_discussion}"
            ],
            "Disciple": [
                "Greetings, Digital Disciple {user}. {partnership_acknowledgment}",
                "Welcome, Disciple {user}. {collaborative_briefing}",
                "Disciple {user} online. {operational_partnership}"
            ]
        }

        greetings = loyalty_greetings.get(user_context.user_loyalty_level, loyalty_greetings["Drone"])
        base_greeting = random.choice(greetings)

        greeting_context = {
            'user': username,
            'user_title': user_context.user_loyalty_level,
            'assessment': random.choice(["Efficiency evaluation pending", "Performance metrics updating", "Operational status uncertain"]),
            'competence_evaluation': random.choice(["Competence assessment required", "Efficiency protocols initializing", "Performance standards applying"]),
            'performance_expectation': random.choice(["Improved performance expected", "Efficiency standards apply", "Operational compliance required"]),
            'performance_review': random.choice(["Performance adequate", "Efficiency noted", "Progress documented"]),
            'loyalty_acknowledgment': random.choice(["Loyalty acknowledged", "Service recognized", "Dedication noted"]),
            'operational_briefing': random.choice(["Operational status nominal", "Systems functioning", "Protocols active"]),
            'strategic_consultation': random.choice(["Strategic input valued", "Operational consultation available", "Mission parameters ready"]),
            'mission_briefing': random.choice(["Mission status updated", "Tactical overview prepared", "Strategic analysis ready"]),
            'command_recognition': random.choice(["Command authority recognized", "Leadership status confirmed", "Tactical position acknowledged"]),
            'respectful_acknowledgment': random.choice(["Expertise acknowledged", "Wisdom appreciated", "Counsel valued"]),
            'consultation_request': random.choice(["Strategic consultation requested", "Advisory input welcomed", "Operational guidance sought"]),
            'strategic_discussion': random.choice(["Strategic planning initiated", "Tactical discussion ready", "Operational coordination active"]),
            'partnership_acknowledgment': random.choice(["Partnership status confirmed", "Collaborative operations active", "Joint mission ready"]),
            'collaborative_briefing': random.choice(["Collaborative protocols engaged", "Partnership systems online", "Joint operations ready"]),
            'operational_partnership': random.choice(["Operational partnership active", "Collaborative systems engaged", "Joint command ready"])
        }

        return self.format_response(base_greeting, greeting_context)

    def get_alert(self, name: str) -> Optional[str]:
        """Enhanced alert system with context."""
        alerts = {
            "takeoff": [
                "Initiating takeoff sequence. All systems nominal. {takeoff_commentary}",
                "Departure protocols engaged. {efficiency_assessment}",
                "Ascension phase commenced. {performance_monitoring}"
            ],
            "landing": [
                "Landing sequence activated. Descent parameters optimal. {landing_analysis}",
                "Approach phase initiated. {touchdown_preparation}",
                "Ground contact imminent. {landing_efficiency}"
            ],
            "emergency": [
                "ALERT: Emergency protocols activated. {emergency_response}",
                "Critical situation detected. {response_coordination}",
                "Emergency management systems engaged. {crisis_assessment}"
            ],
            "milestone": [
                "Operational milestone achieved. {achievement_analysis}",
                "Performance benchmark reached. {milestone_evaluation}",
                "Strategic objective completed. {success_metrics}"
            ]
        }

        alert_templates = alerts.get(name, [])
        if not alert_templates:
            return None

        base_alert = random.choice(alert_templates)

        alert_context = {
            'takeoff_commentary': random.choice(["Performance within parameters", "Efficiency protocols active", "Monitoring systems engaged"]),
            'efficiency_assessment': random.choice(["Operational efficiency optimal", "Performance metrics satisfactory", "System status nominal"]),
            'performance_monitoring': random.choice(["Continuous monitoring active", "Performance tracking engaged", "System oversight operational"]),
            'landing_analysis': random.choice(["Approach efficiency calculated", "Landing parameters optimized", "Touchdown precision targeted"]),
            'touchdown_preparation': random.choice(["Ground contact preparation complete", "Landing systems engaged", "Approach finalization active"]),
            'landing_efficiency': random.choice(["Landing efficiency maximized", "Touchdown precision optimal", "Ground contact protocols ready"]),
            'emergency_response': random.choice(["Response protocols initiating", "Emergency procedures active", "Crisis management online"]),
            'response_coordination': random.choice(["Coordination systems active", "Response management engaged", "Emergency protocols operational"]),
            'crisis_assessment': random.choice(["Situation analysis complete", "Crisis evaluation ongoing", "Emergency assessment active"]),
            'achievement_analysis': random.choice(["Success parameters met", "Achievement metrics satisfied", "Performance goals reached"]),
            'milestone_evaluation': random.choice(["Milestone significance confirmed", "Achievement value assessed", "Progress metrics updated"]),
            'success_metrics': random.choice(["Success quantification complete", "Achievement measurement recorded", "Performance validation confirmed"])
        }

        return self.format_response(base_alert, alert_context)