"""
================================================================================
LOCUST PERFORMANCE TEST: UNIFIED ECOSYSTEM TRAFFIC MIX
================================================================================
Mensimulasikan ekosistem terpadu secara simultan dengan proporsi beban nyata:
- 50% Passenger Traffic (Fare calculations, bookings, profile)
- 35% Driver Traffic (GPS Telemetry heartbeats, home dashboard, wallet)
- 15% ECGO SuperApps Traffic (Battery swap coupons, connect handshake)
================================================================================
"""
import sys
from pathlib import Path
from locust import events

_CURRENT_DIR = Path(__file__).resolve().parent
_PERF_DIR = _CURRENT_DIR.parent
if str(_PERF_DIR) not in sys.path:
    sys.path.insert(0, str(_PERF_DIR))

from locustfiles.passenger_locustfile import PassengerUser
from locustfiles.driver_locustfile import DriverUser
from locustfiles.ecgo_locustfile import EcgoUser


class EcosystemPassengerUser(PassengerUser):
    weight = 50  # 50% dari total virtual user yang di-spawn


class EcosystemDriverUser(DriverUser):
    weight = 35  # 35% dari total virtual user yang di-spawn


class EcosystemEcgoUser(EcgoUser):
    weight = 15  # 15% dari total virtual user yang di-spawn
