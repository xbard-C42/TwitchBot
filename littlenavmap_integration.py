# File: littlenavmap_integration.py
# -*- coding: utf-8 -*-
import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import aiohttp
from config import Config

class LittleNavmapIntegration:
    def __init__(self, config: Config):
        self.logger = logging.getLogger('LittleNavmapIntegration')
        self.config = config
        self.base_url = getattr(config, 'LITTLENAVMAP_URL', None) or \
                        getattr(config.littlenavmap, 'BASE_URL', 'http://localhost:8965')
        self.poll_interval = getattr(config, 'LITTLENAVMAP_POLL_INTERVAL', None) or \
                            getattr(config.littlenavmap, 'UPDATE_INTERVAL', 1.0)

        self.session: Optional[aiohttp.ClientSession] = None
        self._poll_task: Optional[asyncio.Task] = None
        self._listeners: List[Callable] = []
        self._last_data: Dict[str, Any] = {}
        self._last_milestones: Dict[str, bool] = {}
        self._last_phase: Optional[str] = None
        self._flight_data_cache: Dict[str, Any] = {}

        # Airport API configuration
        self.airport_api_key = getattr(config, 'AIRPORT_API_KEY', None)

    async def start(self):
        """Start polling LittleNavmap for data."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        if self._poll_task is None:
            self._poll_task = asyncio.create_task(self._poll_loop())
            self.logger.info(f"Started LittleNavmap polling on {self.base_url}")

    async def stop(self):
        """Stop polling and close session."""
        if self._poll_task:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass
            self._poll_task = None

        if self.session:
            await self.session.close()
            self.session = None
        self.logger.info("Stopped LittleNavmap integration")

    async def _poll_loop(self):
        """Continuously poll for data and notify listeners on changes."""
        consecutive_errors = 0
        max_errors = 5

        while True:
            try:
                # Try multiple endpoints for compatibility
                data = await self._fetch_data_with_fallback()

                if data and data != self._last_data:
                    self._last_data = data
                    self._update_flight_data_cache(data)
                    await self._notify_listeners(data)
                    await self._check_milestones_and_phases(data)
                    consecutive_errors = 0
                elif not data:
                    self.logger.debug("No data received from LittleNavmap")

                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                consecutive_errors += 1
                self.logger.error(f"Error polling LittleNavmap: {e}")

                if consecutive_errors >= max_errors:
                    self.logger.error(f"Too many consecutive errors ({max_errors}), backing off")
                    await asyncio.sleep(30)  # Back off for 30 seconds
                    consecutive_errors = 0
                else:
                    await asyncio.sleep(5)

    async def _fetch_data_with_fallback(self) -> Dict[str, Any]:
        """Try multiple endpoints for data with fallback."""
        endpoints = [
            '/api/aircraft',
            '/api/v1/flight',
            '/api/progress',
            '/api/flightplan'
        ]

        for endpoint in endpoints:
            try:
                data = await self._fetch_from_endpoint(endpoint)
                if data:
                    self.logger.debug(f"Successfully fetched data from {endpoint}")
                    return data
            except Exception as e:
                self.logger.debug(f"Failed to fetch from {endpoint}: {e}")
                continue

        return {}

    async def _fetch_from_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Fetch data from a specific endpoint."""
        url = f"{self.base_url}{endpoint}"

        if not self.session:
            raise RuntimeError("Session not initialized")

        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

    def _update_flight_data_cache(self, data: Dict[str, Any]):
        """Update cached flight data with normalized values."""
        try:
            # Convert to standardized units and cache
            self._flight_data_cache = {
                'altitude_ft': self._safe_float(data.get('indicated_altitude', 0)),
                'altitude_agl_ft': self._safe_float(data.get('altitude_above_ground', 0)),
                'ground_altitude_ft': self._safe_float(data.get('ground_altitude', 0)),
                'speed_kt': self._safe_float(data.get('ground_speed', 0)) * 1.943844,  # m/s to knots
                'true_airspeed_kt': self._safe_float(data.get('true_airspeed', 0)) * 1.943844,
                'indicated_airspeed_kt': self._safe_float(data.get('indicated_speed', 0)) * 1.943844,
                'heading_deg': self._safe_float(data.get('heading', 0)),
                'vertical_speed_fpm': self._safe_float(data.get('vertical_speed', 0)) * 196.85,  # m/s to ft/min
                'latitude': self._safe_float(data.get('position', {}).get('lat')),
                'longitude': self._safe_float(data.get('position', {}).get('lon')),
                'wind_speed_kt': self._safe_float(data.get('wind_speed', 0)) * 1.943844,
                'wind_direction_deg': self._safe_float(data.get('wind_direction', 0)),
                'on_ground': data.get('on_ground', False) or self._flight_data_cache.get('altitude_agl_ft', 0) < 5,
                'phase': await self._detect_flight_phase(self._flight_data_cache),
                'next_waypoint': data.get('next_wp_name', ''),
                'distance_to_dest_nm': self._safe_float(data.get('destination_distance', 0)) * 0.539957,  # km to nm
                'fuel_remaining_lbs': self._safe_float(data.get('fuel_remaining', 0)),
                'ete_minutes': self._safe_float(data.get('ete_hours', 0)) * 60,
                'raw_data': data
            }
        except Exception as e:
            self.logger.error(f"Error updating flight data cache: {e}")

    def _safe_float(self, value) -> float:
        """Safely convert value to float."""
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    async def _detect_flight_phase(self, flight_data: Dict[str, Any]) -> str:
        """Enhanced flight phase detection."""
        altitude_agl = flight_data.get('altitude_agl_ft', 0)
        ground_speed = flight_data.get('speed_kt', 0)
        vertical_speed = flight_data.get('vertical_speed_fpm', 0)
        on_ground = flight_data.get('on_ground', False)

        # Use API-provided phase if available
        if 'phase' in self._last_data:
            return self._last_data['phase'].lower()

        # Enhanced logic
        if on_ground and ground_speed < 5:
            return 'parked'
        elif on_ground and ground_speed >= 5:
            return 'taxiing'
        elif altitude_agl < 50 and ground_speed > 40:
            return 'takeoff'
        elif altitude_agl < 1000 and vertical_speed > 300:
            return 'climbing'
        elif altitude_agl > 3000 and abs(vertical_speed) < 200:
            return 'cruise'
        elif vertical_speed < -300:
            return 'descending'
        elif altitude_agl < 300 and vertical_speed < 0:
            return 'approach'
        elif on_ground and ground_speed > 5:
            return 'landing'
        else:
            return 'unknown'

    async def _check_milestones_and_phases(self, data: Dict[str, Any]):
        """Check for milestone announcements and phase changes."""
        try:
            current_phase = self._flight_data_cache.get('phase', 'unknown')

            # Phase change detection
            if current_phase != self._last_phase:
                self.logger.info(f"Flight phase changed: {self._last_phase} → {current_phase}")
                await self._notify_phase_change(self._last_phase, current_phase)
                self._last_phase = current_phase

            # Milestone announcements
            announcements = await self._check_milestones(self._flight_data_cache)
            for announcement in announcements:
                await self._notify_milestone(announcement)

        except Exception as e:
            self.logger.error(f"Error checking milestones and phases: {e}")

    async def _check_milestones(self, flight_data: Dict[str, Any]) -> List[str]:
        """Check for various flight milestones."""
        announcements = []
        altitude_ft = flight_data.get('altitude_ft', 0)

        # Flight level milestones (every 1000 ft above 10,000 ft)
        if altitude_ft >= 10000:
            flight_level = int(altitude_ft / 1000) * 10
            fl_key = f"FL{flight_level}"

            if not self._last_milestones.get(fl_key, False):
                announcements.append(f"Reached flight level {flight_level}")
                self._last_milestones[fl_key] = True

        # Clear lower flight levels when descending
        current_fl = int(altitude_ft / 1000) * 10
        for key in list(self._last_milestones.keys()):
            if key.startswith('FL') and int(key[2:]) > current_fl:
                del self._last_milestones[key]

        # Waypoint milestone
        waypoint = flight_data.get('next_waypoint', '')
        if waypoint and not self._last_milestones.get(f"WP_{waypoint}", False):
            announcements.append(f"Approaching waypoint {waypoint}")
            self._last_milestones[f"WP_{waypoint}"] = True

        return announcements

    async def _notify_listeners(self, data: Dict[str, Any]):
        """Call registered listener callbacks with new data."""
        for listener in self._listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(data)
                else:
                    listener(data)
            except Exception as e:
                self.logger.error(f"Listener error: {e}")

    async def _notify_phase_change(self, old_phase: str, new_phase: str):
        """Notify listeners of phase changes."""
        event = {
            'type': 'phase_change',
            'old_phase': old_phase,
            'new_phase': new_phase,
            'timestamp': datetime.now().isoformat(),
            'flight_data': self._flight_data_cache
        }
        await self._notify_listeners(event)

    async def _notify_milestone(self, milestone: str):
        """Notify listeners of milestone achievements."""
        event = {
            'type': 'milestone',
            'milestone': milestone,
            'timestamp': datetime.now().isoformat(),
            'flight_data': self._flight_data_cache
        }
        await self._notify_listeners(event)

    def add_listener(self, callback: Callable):
        """Register a callback to receive data updates."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable):
        """Unregister a callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    # === COMPATIBILITY METHODS FOR EXISTING BOT ===

    @property
    def last_data(self) -> Dict[str, Any]:
        """Expose the most recent raw flight data."""
        return self._last_data or {}

    async def get_sim_info(self) -> Dict[str, Any]:
        """Legacy compatibility - returns latest sim data."""
        if not self._last_data:
            return {'active': False}

        return {
            'active': True,
            'simconnect_status': 'No Error',
            'indicated_altitude': self._flight_data_cache.get('altitude_ft', 0),
            'altitude_above_ground': self._flight_data_cache.get('altitude_agl_ft', 0),
            'ground_altitude': self._flight_data_cache.get('ground_altitude_ft', 0),
            'ground_speed': self._flight_data_cache.get('speed_kt', 0) / 1.943844,  # Convert back to m/s
            'true_airspeed': self._flight_data_cache.get('true_airspeed_kt', 0) / 1.943844,
            'indicated_speed': self._flight_data_cache.get('indicated_airspeed_kt', 0) / 1.943844,
            'heading': self._flight_data_cache.get('heading_deg', 0),
            'vertical_speed': self._flight_data_cache.get('vertical_speed_fpm', 0) / 196.85,
            'position': {
                'lat': self._flight_data_cache.get('latitude', 0),
                'lon': self._flight_data_cache.get('longitude', 0)
            },
            'wind_speed': self._flight_data_cache.get('wind_speed_kt', 0) / 1.943844,
            'wind_direction': self._flight_data_cache.get('wind_direction_deg', 0),
            'phase': self._flight_data_cache.get('phase', 'unknown'),
            'next_wp_name': self._flight_data_cache.get('next_waypoint', ''),
            'on_ground': self._flight_data_cache.get('on_ground', False)
        }

    async def get_current_flight_data(self) -> Optional[Dict[str, Any]]:
        """Legacy compatibility - returns structured flight data."""
        if not self._flight_data_cache:
            return None

        return {
            'aircraft': {
                'altitude': self._flight_data_cache.get('altitude_ft', 0),
                'speed': self._flight_data_cache.get('speed_kt', 0),
                'heading': self._flight_data_cache.get('heading_deg', 0),
                'vertical_speed': self._flight_data_cache.get('vertical_speed_fpm', 0),
                'latitude': self._flight_data_cache.get('latitude', 0),
                'longitude': self._flight_data_cache.get('longitude', 0),
                'on_ground': self._flight_data_cache.get('on_ground', False)
            },
            'environment': {
                'wind_speed': self._flight_data_cache.get('wind_speed_kt', 0),
                'wind_direction': self._flight_data_cache.get('wind_direction_deg', 0)
            },
            'navigation': {
                'phase': self._flight_data_cache.get('phase', 'unknown'),
                'next_waypoint': self._flight_data_cache.get('next_waypoint', ''),
                'distance_to_destination': self._flight_data_cache.get('distance_to_dest_nm', 0)
            }
        }

    def format_flight_data(self, sim_info: Dict[str, Any]) -> str:
        """Format detailed flight status for !status command."""
        try:
            altitude = round(sim_info.get('indicated_altitude', 0))
            speed_ms = sim_info.get('ground_speed', 0)
            speed_kts = round(speed_ms * 1.943844) if speed_ms else 0
            heading = round(sim_info.get('heading', 0))
            phase = sim_info.get('phase', 'unknown').title()
            altitude_agl = round(sim_info.get('altitude_above_ground', 0))

            base_status = (
                f"Phase: {phase} | "
                f"Altitude: {altitude:,} ft ({altitude_agl:,} AGL) | "
                f"Speed: {speed_kts} kt | "
                f"Heading: {heading}°"
            )

            # Add wind if available
            wind_speed = sim_info.get('wind_speed', 0)
            wind_dir = sim_info.get('wind_direction', 0)
            if wind_speed:
                wind_kts = round(wind_speed * 1.943844)
                base_status += f" | Wind: {round(wind_dir)}° @ {wind_kts} kt"

            # Add next waypoint if available
            waypoint = sim_info.get('next_wp_name', '')
            if waypoint:
                base_status += f" | Next: {waypoint}"

            return base_status

        except Exception as e:
            self.logger.error(f"Error formatting flight data: {e}")
            return "Flight data formatting error"

    def format_brief_status(self, sim_info: Dict[str, Any]) -> str:
        """Format brief status for !brief command."""
        try:
            altitude = round(sim_info.get('indicated_altitude', 0))
            phase = sim_info.get('phase', 'unknown').title()
            speed_ms = sim_info.get('ground_speed', 0)
            speed_kts = round(speed_ms * 1.943844) if speed_ms else 0

            return f"{phase} - {altitude:,} ft at {speed_kts} kt"
        except Exception as e:
            self.logger.error(f"Error formatting brief status: {e}")
            return "Brief status error"

    def format_weather_data(self, sim_info: Dict[str, Any]) -> str:
        """Format weather data for !weather command."""
        try:
            wind_speed = sim_info.get('wind_speed', 0)
            wind_dir = sim_info.get('wind_direction', 0)

            if wind_speed:
                wind_kts = round(wind_speed * 1.943844)
                return f"Wind: {round(wind_dir)}° at {wind_kts} kt"
            else:
                return "Wind: Calm"
        except Exception as e:
            self.logger.error(f"Error formatting weather data: {e}")
            return "Weather data unavailable"

    async def get_airport_info(self, icao: str) -> Dict[str, Any]:
        """Get airport information for !airport command."""
        try:
            # Try LittleNavmap API first
            url = f"{self.base_url}/api/airport/info?ident={icao.upper()}"

            if self.session:
                async with self.session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            return data

            # Fallback to aviationstack if API key available
            if self.airport_api_key:
                return await self._fetch_from_aviationstack(icao)

            return {}

        except Exception as e:
            self.logger.error(f"Error fetching airport info for {icao}: {e}")
            return {}

    async def _fetch_from_aviationstack(self, icao: str) -> Dict[str, Any]:
        """Fetch airport data from aviationstack API."""
        url = f"http://api.aviationstack.com/v1/airports"
        params = {
            'access_key': self.airport_api_key,
            'icao_code': icao.upper()
        }

        try:
            if self.session:
                async with self.session.get(url, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    if 'data' in data and data['data']:
                        return data['data'][0]
            return {}
        except Exception as e:
            self.logger.error(f"Error fetching from aviationstack: {e}")
            return {}

    def format_airport_data(self, info: Dict[str, Any]) -> str:
        """Format airport information for display."""
        try:
            # Handle different API response formats
            name = info.get('airport_name') or info.get('name', 'Unknown Airport')
            icao = info.get('icao_code') or info.get('ident', 'N/A')
            elevation = info.get('elevation_ft') or info.get('elevation', 'N/A')
            city = info.get('city', '')
            country = info.get('country_name') or info.get('country', '')

            base_info = f"{name} ({icao})"
            if city and country:
                base_info += f" | {city}, {country}"
            if elevation != 'N/A':
                base_info += f" | Elevation: {elevation} ft"

            # Add runway information if available
            runways = info.get('runways', [])
            if runways:
                runway_count = len(runways)
                base_info += f" | Runways: {runway_count}"

            return base_info

        except Exception as e:
            self.logger.error(f"Error formatting airport data: {e}")
            return "Airport data formatting error"


# === STANDALONE UTILITY FUNCTIONS ===

async def flight_phase_detector(data: Dict[str, Any]) -> Optional[str]:
    """Standalone flight phase detection function."""
    altitude = data.get('indicated_altitude', 0)
    groundspeed = data.get('ground_speed', 0)
    vertical_speed = data.get('vertical_speed', 0)
    phase = data.get('phase', '').lower()

    # Use API-provided phase if available
    if phase:
        return phase

    # Fallback logic with enhanced thresholds
    if altitude < 5 and groundspeed < 5:
        return 'parked'
    elif groundspeed > 10 and altitude < 50:
        return 'taxiing'
    elif groundspeed > 50 and altitude < 500:
        return 'takeoff'
    elif altitude < 1000 and vertical_speed > 300:
        return 'climbing'
    elif altitude > 3000 and abs(vertical_speed) < 200:
        return 'cruise'
    elif vertical_speed < -300:
        return 'descending'
    elif altitude < 500 and vertical_speed < 0:
        return 'approach'
    else:
        return 'unknown'


async def milestone_announcer(data: Dict[str, Any], last_milestones: Dict[str, bool]) -> List[str]:
    """Generate milestone announcements."""
    announcements = []
    altitude = data.get('indicated_altitude', 0)

    # Flight level announcements (every 1000 ft above 10,000)
    if altitude >= 10000:
        flight_level = int(altitude / 1000) * 10
        key = f"FL{flight_level}"
        if not last_milestones.get(key, False):
            announcements.append(f"Crossed flight level {flight_level}")
            last_milestones[key] = True

    # Waypoint announcements
    waypoint = data.get('next_wp_name')
    if waypoint and not last_milestones.get(f"WP_{waypoint}", False):
        announcements.append(f"Approaching waypoint {waypoint}")
        last_milestones[f"WP_{waypoint}"] = True

    return announcements