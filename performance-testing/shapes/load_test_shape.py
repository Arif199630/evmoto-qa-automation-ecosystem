"""
================================================================================
LOCUST SHAPE: STANDARD LOAD TESTING PROFILE
================================================================================
Menguji performa sistem pada kondisi beban kerja operasional normal:
- Ramp-up: 0 -> 30 virtual users dalam 20 detik (spawn rate 2 user/s)
- Steady State: Mempertahankan 30 virtual users selama 30 detik
- Ramp-down / Cooldown: Menurunkan beban kembali ke 0
- Total Durasi: 60 detik
- Target SLA: P95 Latency < 800ms, Failure Rate < 1%
================================================================================
"""
from locust import LoadTestShape


class StandardLoadTestShape(LoadTestShape):
    """Bentuk profil beban bertahap untuk pengujian kapasitas reguler."""

    stages = [
        {"duration": 20, "users": 30, "spawn_rate": 2},   # Ramp-up
        {"duration": 50, "users": 30, "spawn_rate": 2},   # Steady State (Hold)
        {"duration": 60, "users": 0, "spawn_rate": 3},    # Ramp-down / Cooldown
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]

        return None  # Menghentikan load test secara otomatis saat durasi tercapai
