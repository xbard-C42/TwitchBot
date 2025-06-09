# flight_sim_manager.py
class FlightSimManager:
    def __init__(self):
        self.fs2024_connector = FS2024Connector()
        self.xp12_connector = XPlane12Connector()
        self.littlenavmap = LittleNavmapIntegration()

    async def get_unified_flight_data(self):
        # Auto-detect active simulator
        # Unified data format
        # Fallback between sources