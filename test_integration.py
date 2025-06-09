#!/usr/bin/env python3
# File: test_integration.py
"""
Development test script for LittleNavmap integration.
Run this to test the integration without starting the full bot.
"""

import asyncio
import logging
import json
from pathlib import Path

from config import load_config
from littlenavmap_integration import LittleNavmapIntegration


# Test data for simulation
MOCK_FLIGHT_DATA = [
    # Parked
    {
        "indicated_altitude": 0,
        "ground_speed": 0,
        "heading": 270,
        "position": {"lat": 40.6413, "lon": -73.7781},
        "on_ground": True
    },
    # Taxiing
    {
        "indicated_altitude": 0,
        "ground_speed": 15,
        "heading": 270,
        "position": {"lat": 40.6413, "lon": -73.7781},
        "on_ground": True
    },
    # Takeoff
    {
        "indicated_altitude": 25,
        "ground_speed": 80,
        "heading": 270,
        "vertical_speed": 1200,
        "position": {"lat": 40.6413, "lon": -73.7781},
        "on_ground": False
    },
    # Climbing
    {
        "indicated_altitude": 5000,
        "ground_speed": 180,
        "heading": 270,
        "vertical_speed": 1800,
        "position": {"lat": 40.7413, "lon": -73.8781}
    },
    # Flight Level 100
    {
        "indicated_altitude": 10000,
        "ground_speed": 250,
        "heading": 270,
        "vertical_speed": 1000,
        "position": {"lat": 40.8413, "lon": -73.9781}
    },
    # Cruise at FL350
    {
        "indicated_altitude": 35000,
        "ground_speed": 450,
        "heading": 270,
        "vertical_speed": 0,
        "position": {"lat": 41.0413, "lon": -74.2781},
        "next_wp_name": "DIXON"
    },
    # Descending
    {
        "indicated_altitude": 20000,
        "ground_speed": 350,
        "heading": 270,
        "vertical_speed": -1500,
        "position": {"lat": 41.2413, "lon": -74.5781}
    },
    # Approach
    {
        "indicated_altitude": 2000,
        "ground_speed": 150,
        "heading": 270,
        "vertical_speed": -800,
        "position": {"lat": 41.4413, "lon": -74.8781}
    },
    # Landing
    {
        "indicated_altitude": 0,
        "ground_speed": 60,
        "heading": 270,
        "vertical_speed": -200,
        "position": {"lat": 41.5413, "lon": -74.9781},
        "on_ground": True
    }
]


class MockLittleNavmapServer:
    """Mock server to simulate LittleNavmap responses."""

    def __init__(self):
        self.data_index = 0
        self.running = False

    async def start_server(self, host='localhost', port=8965):
        """Start a simple HTTP server that returns mock data."""
        from aiohttp import web, web_runner

        app = web.Application()
        app.router.add_get('/api/aircraft', self.handle_aircraft)
        app.router.add_get('/api/v1/flight', self.handle_aircraft)
        app.router.add_get('/api/progress', self.handle_progress)
        app.router.add_get('/api/airport/info', self.handle_airport)

        runner = web_runner.AppRunner(app)
        await runner.setup()

        site = web_runner.TCPSite(runner, host, port)
        await site.start()

        self.running = True
        print(f"Mock LittleNavmap server started on http://{host}:{port}")
        return runner

    async def handle_aircraft(self, request):
        """Return current aircraft data."""
        if self.data_index < len(MOCK_FLIGHT_DATA):
            data = MOCK_FLIGHT_DATA[self.data_index]
        else:
            data = MOCK_FLIGHT_DATA[-1]  # Stay at final state

        return web.json_response(data)

    async def handle_progress(self, request):
        """Return progress data."""
        return web.json_response({
            "destination_distance": 150.5,
            "ete_hours": 2.5,
            "fuel_remaining": 8500
        })

    async def handle_airport(self, request):
        """Return airport data."""
        ident = request.query.get('ident', 'KJFK')
        return web.json_response({
            "ident": ident,
            "name": f"Test Airport {ident}",
            "elevation_ft": 13,
            "runways": [
                {"ident": "04L", "length_ft": 12000},
                {"ident": "04R", "length_ft": 11000}
            ]
        })

    def advance_data(self):
        """Move to next data point."""
        if self.data_index < len(MOCK_FLIGHT_DATA) - 1:
            self.data_index += 1
            print(f"Advanced to data point {self.data_index}")


async def test_flight_event_listener(event_data):
    """Test listener for flight events."""
    print(f"🎯 Flight Event: {json.dumps(event_data, indent=2)}")


async def test_integration():
    """Test the LittleNavmap integration."""
    print("🚀 Starting LittleNavmap Integration Test")

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Load config
        config = load_config()
        print(f"📋 Loaded config for: {config.littlenavmap.BASE_URL}")

        # Create integration
        integration = LittleNavmapIntegration(config)
        integration.add_listener(test_flight_event_listener)

        print("🔌 Starting integration...")
        await integration.start()

        # Test compatibility methods
        print("\n🧪 Testing compatibility methods...")

        # Wait a moment for initial data
        await asyncio.sleep(2)

        # Test get_sim_info
        sim_info = await integration.get_sim_info()
        print(f"✅ get_sim_info(): {sim_info.get('active', False)}")

        # Test get_current_flight_data
        flight_data = await integration.get_current_flight_data()
        if flight_data:
            print(f"✅ get_current_flight_data(): {flight_data['aircraft']['altitude']} ft")

        # Test formatting methods
        if sim_info.get('active'):
            formatted = integration.format_flight_data(sim_info)
            brief = integration.format_brief_status(sim_info)
            weather = integration.format_weather_data(sim_info)

            print(f"✅ format_flight_data(): {formatted}")
            print(f"✅ format_brief_status(): {brief}")
            print(f"✅ format_weather_data(): {weather}")

        # Test airport lookup
        airport_info = await integration.get_airport_info('KJFK')
        if airport_info:
            airport_formatted = integration.format_airport_data(airport_info)
            print(f"✅ get_airport_info('KJFK'): {airport_formatted}")

        print("\n⏰ Integration running. Press Ctrl+C to stop...")

        # Keep running to observe events
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping test...")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("🧹 Cleaning up...")
        await integration.stop()
        print("✅ Test complete")


async def test_with_mock_server():
    """Test with a mock LittleNavmap server."""
    print("🚀 Starting Mock Server Test")

    # Start mock server
    mock_server = MockLittleNavmapServer()
    runner = await mock_server.start_server()

    try:
        # Create a test config pointing to our mock server
        class MockConfig:
            class LittleNavMapConfig:
                BASE_URL = "http://localhost:8965"
                UPDATE_INTERVAL = 2.0

            littlenavmap = LittleNavMapConfig()
            airport_api_key = None

        config = MockConfig()

        # Test integration with mock data
        integration = LittleNavmapIntegration(config)
        integration.add_listener(test_flight_event_listener)

        await integration.start()

        print("📊 Simulating flight progression...")

        # Simulate flight by advancing through data points
        for i in range(len(MOCK_FLIGHT_DATA)):
            print(f"\n📍 Data Point {i + 1}/{len(MOCK_FLIGHT_DATA)}")
            mock_server.advance_data()
            await asyncio.sleep(3)  # Wait for polling to pick up changes

        print("\n✅ Flight simulation complete")

    finally:
        await integration.stop()
        await runner.cleanup()


async def main():
    """Main test function."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--mock':
        await test_with_mock_server()
    else:
        await test_integration()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()