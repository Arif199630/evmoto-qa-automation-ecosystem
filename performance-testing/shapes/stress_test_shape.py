"""
================================================================================
LOCUST SHAPE: STEP-UP STRESS TESTING PROFILE
================================================================================
Menguji batas saturasi (breaking point) dan kurva degradasi sistem backend:
- Stage 1: 20 virtual users (20 detik) - Beban Awal
- Stage 2: 50 virtual users (20 detik) - Beban Sedang
- Stage 3: 80 virtual users (20 detik) - Beban Berat
- Stage 4: 120 virtual users (25 detik) - Beban Puncak (Maksimal)
- Total Durasi: 85 detik
================================================================================
"""
from locust import LoadTestShape


class StepUpStressTestShape(LoadTestShape):
    """Bentuk profil beban bertingkat untuk mencari batas kapasitas server."""

    stages = [
        {"duration": 20, "users": 20, "spawn_rate": 2},    # Stage 1: Initial
        {"duration": 40, "users": 50, "spawn_rate": 3},    # Stage 2: Moderate
        {"duration": 60, "users": 80, "spawn_rate": 4},    # Stage 3: Heavy
        {"duration": 85, "users": 120, "spawn_rate": 5},   # Stage 4: Extreme / Stress Peak
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]

        return None
