"""
================================================================================
LOCUST SHAPE: SUDDEN SURGE SPIKE TESTING PROFILE
================================================================================
Mensimulasikan lonjakan trafik mendadak (Flash Surge / Rush Hour):
- Phase 1: Baseline 5 virtual users (15 detik)
- Phase 2: Lonjakan instan ke 80 virtual users dalam 5 detik (Spawn Rate 16 user/s)
           dipertahankan selama 20 detik (Peak Burst)
- Phase 3: Penurunan mendadak kembali ke baseline 5 virtual users (15 detik)
           untuk mengevaluasi kemampuan pemulihan sistem (System Self-Healing)
- Total Durasi: 55 detik
================================================================================
"""
from locust import LoadTestShape


class SuddenSpikeTestShape(LoadTestShape):
    """Bentuk profil beban lonjakan mendadak untuk menguji elastisitas sistem."""

    stages = [
        {"duration": 15, "users": 5, "spawn_rate": 1},    # Phase 1: Baseline Normal
        {"duration": 40, "users": 80, "spawn_rate": 16},  # Phase 2: Sudden Traffic Burst
        {"duration": 55, "users": 5, "spawn_rate": 15},   # Phase 3: Immediate Recovery Check
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]

        return None
