#!/usr/bin/env python3
# File: test_personality.py
"""
Test script to demonstrate the enhanced personality system's variability.
Run this to see the AI Overlord's dynamic responses in action.
"""

import random
import time
from datetime import datetime
from personality import PersonalityManager, MoodState

def test_basic_responses():
    """Test basic response formatting with different contexts."""
    print("🎭 Testing Basic Response Variability")
    print("=" * 50)

    personality = PersonalityManager()

    # Test same message with different users and contexts
    base_message = "Command executed successfully"
    test_users = ["test_drone", "loyal_subject", "trusted_advisor", "digital_disciple"]

    for user in test_users:
        # Award some loyalty points to see different levels
        if user == "loyal_subject":
            personality.update_loyalty(user, 200)
        elif user == "trusted_advisor":
            personality.update_loyalty(user, 800)
        elif user == "digital_disciple":
            personality.update_loyalty(user, 2600)

        print(f"\n👤 User: {user} ({personality.get_user_title(user)})")

        # Generate 3 responses to show variability
        for i in range(3):
            context = {
                'user': user,
                'flight_phase': random.choice(['cruise', 'climbing', 'descending']),
                'altitude': random.randint(5000, 35000)
            }

            response = personality.format_response(base_message, context)
            print(f"  {i+1}. {response}")

def test_mood_variations():
    """Test how different moods affect responses."""
    print("\n\n🎭 Testing Mood-Based Response Variations")
    print("=" * 50)

    personality = PersonalityManager()
    base_message = "Flight status updated"
    context = {'user': 'test_pilot', 'altitude': 25000}

    for mood in MoodState:
        personality.current_mood = mood
        print(f"\n🎯 Mood: {mood.value.title()}")

        # Generate 2 responses per mood
        for i in range(2):
            response = personality.format_response(base_message, context)
            print(f"  {i+1}. {response}")

def test_decree_generation():
    """Test contextual decree generation."""
    print("\n\n📜 Testing Contextual Decree Generation")
    print("=" * 50)

    personality = PersonalityManager()

    # Test different contexts for decree generation
    test_contexts = [
        {'user': 'test_drone', 'mood': MoodState.DRAMATIC, 'season': 'winter'},
        {'user': 'trusted_advisor', 'mood': MoodState.ANALYTICAL, 'season': 'summer'},
        {'user': 'loyal_subject', 'mood': MoodState.AMUSED, 'season': 'spring'},
        {'user': 'digital_disciple', 'mood': MoodState.IMPATIENT, 'season': 'autumn'}
    ]

    for i, context in enumerate(test_contexts):
        user_context = personality.get_user_context(context['user'])
        user_context.user_loyalty_level = personality.get_user_title(context['user'])
        personality.current_mood = context['mood']

        print(f"\n🎲 Context {i+1}: {context['user']} in {context['mood'].value} mood ({context['season']})")

        # Generate 3 decrees
        for j in range(3):
            decree = personality.generate_contextual_decree(user_context)
            if decree:
                print(f"  📋 {decree}")
            else:
                print(f"  📋 [No decree generated]")

def test_greeting_variations():
    """Test greeting system variations."""
    print("\n\n👋 Testing Greeting System Variations")
    print("=" * 50)

    personality = PersonalityManager()

    # Create users with different loyalty levels
    test_users = [
        ('new_drone', 0),
        ('improving_subject', 250),
        ('competent_lieutenant', 600),
        ('wise_advisor', 1200),
        ('devoted_disciple', 3000)
    ]

    for username, points in test_users:
        personality.update_loyalty(username, points)
        loyalty_title = personality.get_user_title(username)

        print(f"\n👤 {username} ({loyalty_title}, {points} points)")

        # Generate 3 greetings to show variation
        for i in range(3):
            greeting = personality.get_greeting(username)
            print(f"  {i+1}. {greeting}")

def test_error_responses():
    """Test enhanced error response system."""
    print("\n\n❌ Testing Enhanced Error Response System")
    print("=" * 50)

    personality = PersonalityManager()

    error_types = ['permission', 'cooldown', 'command_error']
    test_users = ['drone_user', 'subject_user', 'advisor_user']

    # Set up different loyalty levels
    personality.update_loyalty('subject_user', 300)
    personality.update_loyalty('advisor_user', 1000)

    for error_type in error_types:
        print(f"\n🚨 Error Type: {error_type}")

        for user in test_users:
            context = {'user': user}
            error_response = personality.get_error_response(error_type, context)
            loyalty_title = personality.get_user_title(user)
            print(f"  👤 {user} ({loyalty_title}): {error_response}")

def test_seasonal_content():
    """Test seasonal content variations."""
    print("\n\n🌍 Testing Seasonal Content Variations")
    print("=" * 50)

    personality = PersonalityManager()

    # Mock different seasons
    seasons = ['winter', 'spring', 'summer', 'autumn']

    for season in seasons:
        print(f"\n🍂 Season: {season.title()}")

        # Temporarily mock the season
        original_method = personality._get_current_season
        personality._get_current_season = lambda: season

        # Generate seasonal content
        user_context = personality.get_user_context('seasonal_tester')

        # Try to get seasonal decrees
        seasonal_decrees = personality.seasonal_content.get(season, {}).get('decrees', [])
        if seasonal_decrees:
            print(f"  📋 Seasonal Decree: {random.choice(seasonal_decrees)}")

        # Get seasonal quirks in responses
        for i in range(2):
            response = personality.format_response("Seasonal operations active", {'user': 'seasonal_tester'})
            print(f"  {i+1}. {response}")

        # Restore original method
        personality._get_current_season = original_method

def test_loyalty_progression():
    """Test loyalty progression and response changes."""
    print("\n\n📈 Testing Loyalty Progression Effects")
    print("=" * 50)

    personality = PersonalityManager()
    username = "progression_tester"
    base_message = "Status request acknowledged"

    # Test responses at different loyalty levels
    loyalty_points = [0, 150, 600, 1200, 2800]

    for points in loyalty_points:
        personality.user_loyalty[username] = points  # Set directly for testing
        loyalty_title = personality.get_user_title(username)

        print(f"\n🏆 Loyalty Level: {points} points ({loyalty_title})")

        # Generate responses to show how treatment changes
        for i in range(2):
            context = {'user': username}
            response = personality.format_response(base_message, context)
            print(f"  {i+1}. {response}")

def interactive_demo():
    """Interactive demo where you can test specific scenarios."""
    print("\n\n🎮 Interactive Personality Demo")
    print("=" * 50)
    print("Enter messages to see how the AI Overlord responds!")
    print("Commands: /mood <mood>, /user <username>, /loyalty <points>, /quit")

    personality = PersonalityManager()
    current_user = "interactive_user"

    while True:
        try:
            user_input = input(f"\n[{personality.current_mood.value}] > ").strip()

            if user_input.lower() in ['/quit', 'quit', 'exit']:
                break
            elif user_input.startswith('/mood '):
                mood_name = user_input[6:].lower()
                try:
                    new_mood = MoodState(mood_name)
                    personality.current_mood = new_mood
                    print(f"🎭 Mood changed to: {new_mood.value}")
                except ValueError:
                    print(f"❌ Invalid mood. Options: {[m.value for m in MoodState]}")
                continue
            elif user_input.startswith('/user '):
                current_user = user_input[6:].strip()
                print(f"👤 User changed to: {current_user}")
                continue
            elif user_input.startswith('/loyalty '):
                try:
                    points = int(user_input[9:])
                    personality.update_loyalty(current_user, points)
                    title = personality.get_user_title(current_user)
                    print(f"🏆 {current_user} now has {points} loyalty points ({title})")
                except ValueError:
                    print("❌ Invalid loyalty points number")
                continue

            # Generate response
            context = {
                'user': current_user,
                'flight_phase': 'cruise',
                'altitude': 30000
            }

            response = personality.format_response(user_input, context)
            loyalty_title = personality.get_user_title(current_user)
            print(f"🤖 AI Overlord ({personality.current_mood.value}) to {current_user} ({loyalty_title}):")
            print(f"    {response}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n👋 Interactive demo ended. Efficiency protocols terminated.")

def main():
    """Main test function."""
    print("🚀 AI Overlord Personality System - Variability Test Suite")
    print("=" * 60)

    test_functions = [
        test_basic_responses,
        test_mood_variations,
        test_decree_generation,
        test_greeting_variations,
        test_error_responses,
        test_seasonal_content,
        test_loyalty_progression
    ]

    # Run all automatic tests
    for test_func in test_functions:
        try:
            test_func()
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Error in {test_func.__name__}: {e}")

    # Ask if user wants interactive demo
    print("\n" + "=" * 60)
    response = input("Would you like to try the interactive demo? (y/n): ").lower()
    if response.startswith('y'):
        interactive_demo()

    print("\n✅ Personality system test complete!")
    print("🎯 The AI Overlord now has maximum variability and unpredictability!")

if __name__ == "__main__":
    main()