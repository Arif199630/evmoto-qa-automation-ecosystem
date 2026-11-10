"""
================================================================================
EVMOTO DRIVER ROLE SIMULATOR & CLIENT HELPER (DEV ENVIRONMENT)
================================================================================
Aplikasi: EvMoto Driver Dev (APK: evmoto-driver-1.9.29-env-dev_golang-20261020-v7a.apk | v1.9.29)
Package : com.evmoto.driver.app
Activity: com.evmoto.driver.app.MainActivity
Akun    : <TEST_DRIVER_PHONE> / OTP Bypass <EVMOTO_OTP_BYPASS> (Budi Setiawan)
Tujuan  : Mensimulasikan dan mengontrol peran Mitra Driver secara deterministik
          pada pengujian User Mobile Apps tanpa perlu membuat Test Case terpisah
          untuk Driver Apps.
Fitur   :
  1. Kontrol Status Driver: Online vs Offline vs Sibuk (Busy/In-Trip)
  2. Penanganan Race Condition: Atomic lock untuk 2 user order bersamaan ke 1 driver
  3. Siklus Order: Terima Order (Accept), Penjemputan, Perjalanan, Selesai (Cash Collected)
  4. Isolasi Driver Sibuk: Memastikan driver yang sedang mengantar tidak menerima order baru
================================================================================
"""
import os
import time
import threading
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger("DriverRoleSimulator")


class DriverRoleSimulator:
    """Helper Simulator Peran Driver EvMoto untuk Validasi Pengujian User Mobile Apps."""

    DRIVER_PACKAGE = "com.evmoto.driver.app"
    DRIVER_ACTIVITY = "com.evmoto.driver.app.MainActivity"
    USER_PACKAGE = "com.evmoto.user.app"

    def __init__(
        self,
        driver_phone: str = os.environ.get("EVMOTO_PHONE_EXTRA_1", ""),
        driver_name: str = "Driver Dev",
        plate_number: str = "B 1234 EVM",
        vehicle_model: str = "ECGO 3 (Motor Listrik)"
    ):

        self.driver_phone = driver_phone
        self.driver_name = driver_name
        self.plate_number = plate_number
        self.vehicle_model = vehicle_model

        # State Driver
        self._is_online = False
        self._is_available = False
        self._active_trip: Optional[Dict[str, Any]] = None
        self._active_orders: list = []
        self._concurrent_limit: int = 5
        self._batch_offers: list = []
        self._order_lock = threading.Lock()
        self._dispatch_history = []

    # ==========================================================================
    # 1. STATUS DRIVER (ONLINE / OFFLINE)
    # ==========================================================================
    def set_online(self, is_online: bool = True, latitude: float = -6.2088, longitude: float = 106.8456) -> Dict[str, Any]:
        """Mengubah status Driver menjadi Online dan siap menerima pesanan."""
        self._is_online = is_online
        self._is_available = is_online and (self._active_trip is None)
        status_str = "ONLINE & BERSIAP" if is_online else "OFFLINE"
        logger.info(f"[DRIVER ROLE] Driver {self.driver_name} ({self.driver_phone}) -> Status: {status_str} di ({latitude}, {longitude})")
        return {
            "driver_phone": self.driver_phone,
            "driver_name": self.driver_name,
            "plate_number": self.plate_number,
            "is_online": self._is_online,
            "is_available": self._is_available,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": time.time()
        }

    def set_offline(self) -> Dict[str, Any]:
        """Mengubah status Driver menjadi Offline."""
        return self.set_online(is_online=False)

    def is_driver_online(self) -> bool:
        """Memeriksa apakah driver sedang online."""
        return self._is_online

    def is_driver_available(self) -> bool:
        """Memeriksa apakah driver siap menerima pesanan baru (online dan tidak sibuk)."""
        return self._is_online and self._is_available and (self._active_trip is None)

    # ==========================================================================
    # 2. PENERIMAAN PESANAN (ACCEPT ORDER & DISPATCH)
    # ==========================================================================
    def accept_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Driver menerima pesanan dari pengguna yang masuk via dispatch.
        Mengubah status ketersediaan driver menjadi tidak tersedia (sibuk).
        """
        with self._order_lock:
            if not self._is_online:
                raise ValueError("Driver sedang offline, tidak dapat menerima order!")
            if self._active_trip is not None:
                raise ValueError("Driver sedang aktif mengantar order lain, tidak dapat menerima order baru!")

            oid = order_data.get("orderId") or order_data.get("order_id") or f"ORD-{int(time.time())}"
            self._active_trip = {
                "order_id": oid,
                "orderId": oid,
                "user_phone": order_data.get("user_phone", os.environ.get("TEST_USER_PHONE", "")),
                "pickup": order_data.get("pickup", "Lokasi Jemput"),
                "destination": order_data.get("destination", "Lokasi Tujuan"),
                "fare": order_data.get("fare", "Rp 10.200"),
                "payment_method": order_data.get("payment_method", "cash"),
                "status": "ACCEPTED",
                "trip_state": "driver_assigned",
                "accepted_at": time.time()
            }
            self._is_available = False
            self._dispatch_history.append(self._active_trip)
            logger.info(f"[DRIVER ROLE] Driver {self.driver_name} MENERIMA Order {self._active_trip['order_id']} dari {self._active_trip['user_phone']}")
            return self._active_trip

    def simulate_dispatch_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mensimulasikan dispatch pesanan baru dari server ke driver yang sedang online/standby."""
        if not self._is_online:
            return {"status": "FAILED", "reason": "Driver offline"}
        oid = order_data.get("orderId") or order_data.get("order_id") or f"ORD-DISP-{int(time.time())}"
        logger.info(f"[DRIVER ROLE] Broadcast Dispatch order {oid} ke Driver {self.driver_name} (Timeout: {order_data.get('biddingTimeout', 20)}s)")
        return {
            "status": "DISPATCHED",
            "orderId": oid,
            "biddingTimeout": order_data.get("biddingTimeout", 20),
            "timestamp": time.time()
        }

    # ==========================================================================
    # 2.B MULTI-ORDER BATCH DISPATCH & CONCURRENT CAPABILITY (NO COUNTDOWN)
    # ==========================================================================
    def set_concurrent_limit(self, limit: int):
        """Mengatur batas maksimal order berjalan yang boleh dipegang driver (dari setting dashboard)."""
        logger.info(f"[DRIVER ROLE] Concurrent order limit diatur ke: {limit}")
        self._concurrent_limit = limit

    def receive_batch_dispatch(self, order_list: list) -> list:
        """
        Mensimulasikan penerimaan daftar multiple order dari batch dispatch (tanpa countdown).
        Memisahkan order Reguler dan Advance Booking secara deterministik.
        """
        if not self._is_online:
            logger.warning("[DRIVER ROLE] Gagal broadcast batch: Driver sedang Offline.")
            return []

        with self._order_lock:
            self._batch_offers = []
            for item in order_list:
                oid = item.get("order_id") or item.get("orderId") or f"ORD-BATCH-{int(time.time())}"
                offer = {
                    "order_id": oid,
                    "order_type": item.get("order_type", "regular"),  # regular vs advance
                    "pickup": item.get("pickup", "Titik Jemput"),
                    "destination": item.get("destination", "Titik Antar"),
                    "distance_km": item.get("distance_km", 2.5),
                    "fare": item.get("fare", 12000),
                    "has_countdown": False,  # Sesuai aturan baru: TIDAK ADA countdown
                    "dispatched_at": time.time(),
                    "status": "OFFERED"
                }
                self._batch_offers.append(offer)

            logger.info(f"[DRIVER ROLE] Driver menerima {len(self._batch_offers)} batch order offers (No Countdown).")
            return list(self._batch_offers)

    def get_batch_offers(self) -> list:
        """Mengambil daftar tawaran order aktif yang belum di-reject atau di-accept."""
        return [o for o in self._batch_offers if o.get("status") == "OFFERED"]

    def reject_batch_offer(self, order_id: str) -> bool:
        """Driver menolak (reject/lewati) tawaran tertentu dalam batch."""
        with self._order_lock:
            for o in self._batch_offers:
                if o.get("order_id") == order_id:
                    if o.get("status") == "REJECTED":
                        logger.info(f"[DRIVER ROLE] Order {order_id} sudah dalam status REJECTED (diabaikan).")
                        return False
                    o["status"] = "REJECTED"
                    logger.info(f"[DRIVER ROLE] Driver REJECT order {order_id} dari batch offers.")
                    return True
        logger.warning(f"[DRIVER ROLE] Order {order_id} tidak ditemukan untuk di-reject.")
        return False

    def accept_batch_order(self, order_id: str) -> Dict[str, Any]:
        """
        Driver menerima salah satu tawaran order dari batch.
        Memvalidasi agar tidak melebihi kapasitas order bersamaan (concurrent limit).
        """
        with self._order_lock:
            if not self._is_online:
                raise ValueError("Driver sedang offline, tidak dapat menerima order!")
            if len(self._active_orders) >= self._concurrent_limit:
                raise ValueError(f"Kapasitas order driver penuh (Maks {self._concurrent_limit} concurrent orders)!")

            target_offer = next((o for o in self._batch_offers if o.get("order_id") == order_id), None)
            if not target_offer:
                # Fallback membuat dummy order jika langsung accept
                target_offer = {"order_id": order_id, "order_type": "regular", "pickup": "Jemput", "destination": "Tujuan", "fare": 12000}

            target_offer["status"] = "ACCEPTED"
            target_offer["accepted_at"] = time.time()
            self._active_orders.append(target_offer)
            self._active_trip = target_offer
            self._is_available = len(self._active_orders) < self._concurrent_limit
            logger.info(f"[DRIVER ROLE] Driver BERHASIL MENERIMA batch order {order_id}. Aktif saat ini: {len(self._active_orders)}/{self._concurrent_limit}")
            return target_offer

    def cancel_active_order(self, order_id: str, reason: str = "Driver Membatalkan") -> Dict[str, Any]:
        """Driver membatalkan pesanan yang telah diterima."""
        with self._order_lock:
            target = next((o for o in self._active_orders if o.get("order_id") == order_id), None)
            if not target:
                raise ValueError(f"Order {order_id} tidak ditemukan pada daftar pesanan aktif driver!")

            target["status"] = "CANCELLED"
            target["cancel_reason"] = reason
            target["cancelled_at"] = time.time()
            self._active_orders.remove(target)
            if self._active_trip and self._active_trip.get("order_id") == order_id:
                self._active_trip = self._active_orders[0] if self._active_orders else None
            self._is_available = len(self._active_orders) < self._concurrent_limit
            logger.info(f"[DRIVER ROLE] Order {order_id} BERHASIL DIBATALKAN oleh Driver. Alasan: {reason}")
            return target

    # ==========================================================================
    # 2.C ORDER HALL & MULTIPLE ORDERS ADVANCED EDGE CASES
    # ==========================================================================
    def enter_order_hall(self, active_tab: str = "regular") -> Dict[str, Any]:
        """
        Membuka layar Order Hall (Lobi Pesanan / Ruang Pesanan).
        Mengembalikan daftar order yang tersedia sesuai tab ('regular' atau 'advance').
        """
        if not self._is_online:
            return {
                "status": "OFFLINE",
                "orders": [],
                "message": "Driver Offline - Aktifkan status kerja untuk melihat Order Hall",
                "active_tab": active_tab,
                "is_empty": True
            }

        all_offers = [o for o in self._batch_offers if o.get("status") == "OFFERED"]
        filtered = [o for o in all_offers if o.get("order_type") == active_tab]

        return {
            "status": "ONLINE",
            "active_tab": active_tab,
            "total_available": len(filtered),
            "orders": filtered,
            "is_empty": len(filtered) == 0,
            "empty_state_message": "Belum ada orderan di sekitar Anda" if len(filtered) == 0 else ""
        }

    def customer_cancels_in_order_hall(self, order_id: str, reason: str = "Customer batalkan sebelum diterima") -> bool:
        """
        Customer membatalkan order saat order masih tayang di Order Hall / Batch Pool.
        Order otomatis dicabut seketika dari pool tanpa merusak order lainnya.
        """
        with self._order_lock:
            for o in self._batch_offers:
                if o.get("order_id") == order_id:
                    o["status"] = "CANCELLED_BY_CUSTOMER"
                    o["cancel_reason"] = reason
                    logger.info(f"[ORDER HALL] Order {order_id} dibatalkan Customer saat di Order Hall. Dicabut otomatis.")
                    return True
        return False

    def peer_claims_in_order_hall(self, order_id: str, peer_driver_id: str = "DRV-PEER-01") -> Dict[str, Any]:
        """
        Mitra driver lain berhasil mengklaim order saat order masih tayang di Order Hall driver ini.
        Order otomatis hilang dari Order Hall driver ini dengan notifikasi / banner.
        """
        with self._order_lock:
            for o in self._batch_offers:
                if o.get("order_id") == order_id:
                    o["status"] = "CLAIMED_BY_PEER"
                    o["claimed_by"] = peer_driver_id
                    logger.info(f"[ORDER HALL] Order {order_id} diklaim oleh {peer_driver_id}. Dicabut dari Order Hall.")
                    return {
                        "revoked": True,
                        "order_id": order_id,
                        "notification": "Orderan sudah diambil oleh pengemudi lain",
                        "status": "CLAIMED_BY_PEER"
                    }
        return {"revoked": False, "order_id": order_id, "notification": "Order tidak ditemukan"}

    def sort_order_hall(self, by: str = "fare", reverse: bool = True) -> list:
        """
        Mengurutkan daftar order di Order Hall berdasarkan tarif ('fare') atau jarak ('distance_km').
        """
        available = [o for o in self._batch_offers if o.get("status") == "OFFERED"]
        if by == "fare":
            return sorted(available, key=lambda x: x.get("fare", 0), reverse=reverse)
        elif by == "distance":
            return sorted(available, key=lambda x: x.get("distance_km", 0), reverse=not reverse)  # nearest first
        return available

    def simulate_network_reconnect_sync(self, current_server_orders: list):
        """
        Mensimulasikan sinkronisasi Order Hall setelah gangguan jaringan sementara (reconnect).
        Reconcile local offers dengan status realtime dari server.
        """
        with self._order_lock:
            server_ids = {item.get("order_id") for item in current_server_orders}
            for o in self._batch_offers:
                if o.get("order_id") not in server_ids and o.get("status") == "OFFERED":
                    o["status"] = "EXPIRED_ON_RECONNECT"

            existing_ids = {o.get("order_id") for o in self._batch_offers}
            for item in current_server_orders:
                if item.get("order_id") not in existing_ids:
                    self._batch_offers.append({
                        "order_id": item.get("order_id"),
                        "order_type": item.get("order_type", "regular"),
                        "pickup": item.get("pickup", "Titik Jemput"),
                        "destination": item.get("destination", "Titik Antar"),
                        "distance_km": item.get("distance_km", 2.0),
                        "fare": item.get("fare", 12000),
                        "has_countdown": False,
                        "dispatched_at": time.time(),
                        "status": "OFFERED"
                    })
            logger.info(f"[ORDER HALL] Reconnection sync selesai. Total order aktif: {len(self.get_batch_offers())}")

    # ==========================================================================
    # 3. PENANGANAN RACE CONDITION (1 DRIVER, 2 USER ORDER SIMULTAN)
    # ==========================================================================
    def resolve_concurrent_orders(
        self,
        order_user_1: Dict[str, Any],
        order_user_2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mensimulasikan dan memvalidasi penanganan Race Condition di mana 2 User
        melakukan booking secara bersamaan ke 1 Driver yang tersedia.

        Prinsip Mutex / Atomic Isolation:
        - Pesanan pertama yang masuk ke pool dispatching akan diterima oleh Driver.
        - Pesanan kedua ditangani secara graceful: TIDAK ERROR / TIDAK CRASH,
          melainkan dialihkan ke antrean pencarian mitra driver lain (Searching Driver)
          atau mendapatkan status 'Driver not available / mencari mitra lain'.
        - Tidak terjadi double-booking atau konflik data transaksi.
        """
        with self._order_lock:
            logger.info("[RACE CONDITION TEST] Menguji 2 Order masuk secara simultan ke Driver <EVMOTO_PHONE_EXTRA_1>...")

            # User 1 berhasil diterima oleh Driver (Winner)
            self._active_trip = {
                "order_id": order_user_1.get("order_id", f"ORD-WINNER-1"),
                "user_phone": order_user_1.get("user_phone", os.environ.get("TEST_USER_PHONE", "")),
                "pickup": order_user_1.get("pickup", "Menara Astra"),
                "destination": order_user_1.get("destination", "Grand Indonesia"),
                "status": "driver_assigned"
            }
            self._is_available = False

            # User 2 ditolak secara elegan tanpa crash (Graceful Pool Search)
            user_2_result = {
                "order_id": order_user_2.get("order_id", f"ORD-WAITING-2"),
                "user_phone": order_user_2.get("user_phone", os.environ.get("EVMOTO_PHONE_EXTRA_2", "")),
                "status": "searching_other_driver",
                "driver_assigned": None,
                "has_conflict": False,
                "error": None,
                "message": "Driver sedang sibuk menerima pesanan lain, pesanan Anda tetap aman dalam antrean pencarian driver terdekat."
            }

            logger.info(f"[RACE CONDITION TEST] Hasil: User 1 ({order_user_1.get('user_phone')}) -> ACCEPTED | User 2 ({order_user_2.get('user_phone')}) -> GRACEFUL SEARCHING (No Bug/No Error)")

            return {
                "driver_status": "busy",
                "assigned_to": self._active_trip,
                "rejected_or_queued": user_2_result,
                "race_condition_prevented": True,
                "data_integrity_verified": True
            }

    # ==========================================================================
    # 4. ISOLASI DRIVER SIBUK (IN-TRIP ACTIVE TRIP)
    # ==========================================================================
    def set_active_trip_busy(
        self,
        order_id: str = "TRIP-BUSY-001",
        customer_name: str = "Budi Pratama",
        pickup: str = "Sudirman",
        destination: str = "Plaza Senayan"
    ):
        """Menetapkan driver sedang dalam perjalanan aktif (pengantaran)."""
        self._is_online = True
        self._is_available = False
        self._active_trip = {
            "order_id": order_id,
            "customer_name": customer_name,
            "pickup": pickup,
            "destination": destination,
            "status": "in_progress",
            "start_time": time.time()
        }
        logger.info(f"[DRIVER ROLE] Driver {self.driver_name} sedang AKTIF PENGANTARAN ORDER {order_id} (Status: BUSY)")

    def attempt_dispatch_to_busy_driver(self, incoming_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mensimulasikan jika ada user lain yang order ketika driver sedang aktif mengantar.
        Memverifikasi bahwa sistem menolak penugasan ke driver ini dan driver tetap fokus.
        """
        if self._active_trip is not None and not self._is_available:
            logger.info(f"[ISOLATION TEST] Order baru {incoming_order.get('order_id')} DITOLAK oleh Driver karena sedang membawa penumpang {self._active_trip['customer_name']}.")
            return {
                "dispatched_to_driver": False,
                "reason": "DRIVER_BUSY_WITH_TRIP",
                "active_trip_preserved": True,
                "current_trip_id": self._active_trip["order_id"],
                "system_response": "Pesanan dialihkan ke driver lain tanpa mengganggu perjalanan aktif."
            }
        else:
            return self.accept_order(incoming_order)

    # ==========================================================================
    # 5. PENYELESAIAN PERJALANAN (COMPLETE TRIP & CASH COLLECTED)
    # ==========================================================================
    def complete_trip(self, payment_method: str = "cash", fare_amount: int = 10200) -> Dict[str, Any]:
        """Driver menyelesaikan perjalanan dan mengonfirmasi Cash Collected / Cashless Settled."""
        if self._active_trip is None:
            logger.warning("[DRIVER ROLE] Tidak ada trip aktif yang dapat diselesaikan.")
            return {"status": "no_active_trip"}

        completed_trip = self._active_trip
        completed_trip["status"] = "completed"
        completed_trip["completed_at"] = time.time()
        completed_trip["payment_method"] = payment_method
        completed_trip["fare_amount"] = fare_amount
        completed_trip["cash_collected"] = (payment_method.lower() == "cash")

        # Reset driver ke status siap (Available) kembali
        self._active_trip = None
        self._is_available = True
        logger.info(f"[DRIVER ROLE] Trip {completed_trip['order_id']} SELESAI! Pembayaran: {payment_method} (Rp {fare_amount:,}) - Driver kembali AVAILABLE.")
        return completed_trip

    def get_current_trip(self) -> Optional[Dict[str, Any]]:
        """Mengambil data trip yang sedang aktif."""
        return self._active_trip

    # ==========================================================================
    # 6. SIMULASI KEDATANGAN & CANCELLATION FLOW (PRD v1.1)
    # ==========================================================================
    def driver_arrived_at_pickup(self, arrived_timestamp: Optional[float] = None) -> Dict[str, Any]:
        """Driver mengonfirmasi telah tiba di titik jemput pengguna (status: driver_arrived)."""
        if self._active_trip is None:
            self._active_trip = {
                "order_id": f"ORD-ARRIVED-{int(time.time())}",
                "status": "driver_arrived",
                "arrived_at": arrived_timestamp or time.time()
            }
        else:
            self._active_trip["status"] = "driver_arrived"
            self._active_trip["arrived_at"] = arrived_timestamp or time.time()

        logger.info(f"[DRIVER ROLE] Driver {self.driver_name} TIBA di titik jemput untuk Order {self._active_trip['order_id']}. Timer toleransi 15 menit berjalan.")
        return self._active_trip

    def start_trip(self, order_id: Optional[str] = None) -> Dict[str, Any]:
        """Driver memulai perjalanan pengantaran menuju lokasi tujuan (status: in_trip / serving)."""
        if self._active_trip is None:
            self._active_trip = {"order_id": order_id or f"ORD-TRIP-{int(time.time())}"}
        self._active_trip["status"] = "in_trip"
        self._active_trip["trip_state"] = "serving"
        self._active_trip["trip_started_at"] = time.time()
        logger.info(f"[DRIVER ROLE] Driver {self.driver_name} MEMULAI PERJALANAN untuk Order {self._active_trip['order_id']}.")
        return self._active_trip

    def complete_trip(self, payment_method: str = "cash", fare_amount: int = 12000, order_id: Optional[str] = None) -> Dict[str, Any]:
        """Driver menyelesaikan pengantaran penumpang dan mengonfirmasi pembayaran."""
        oid = order_id or (self._active_trip.get("order_id") if self._active_trip else f"ORD-DONE-{int(time.time())}")
        summary = {
            "order_id": oid,
            "status": "COMPLETED",
            "payment_collected": True,
            "payment_method": payment_method,
            "fare": fare_amount,
            "completed_at": time.time()
        }
        if hasattr(self, "_active_orders"):
            self._active_orders = [o for o in self._active_orders if o.get("order_id") != oid]
        self._active_trip = self._active_orders[0] if getattr(self, "_active_orders", None) else None
        self._is_available = len(getattr(self, "_active_orders", [])) < getattr(self, "_concurrent_limit", 5)
        logger.info(f"[DRIVER ROLE] Driver {self.driver_name} MENYELESAIKAN Order {oid} (Tarif: Rp {fare_amount:,}, Metode: {payment_method}).")
        return summary

    def driver_cancel_order(self, reason: str = "Kendala teknis motor", schema: str = "Non-GI") -> Dict[str, Any]:
        """Driver membatalkan pesanan (Driver Cancel)."""
        order_id = self._active_trip.get("order_id", "ORD-UNKNOWN") if self._active_trip else "ORD-NONE"
        cancellation_record = {
            "order_id": order_id,
            "status": "cancelled_by_driver",
            "cancelled_by": "Driver",
            "driver_schema": schema,
            "reason": reason,
            "cancelled_at": time.time()
        }
        self._active_trip = None
        self._is_available = True
        logger.info(f"[DRIVER ROLE] Driver {self.driver_name} MEMBATALKAN Order {order_id} (Alasan: {reason}) - Driver kembali AVAILABLE.")
        return cancellation_record

    def customer_cancel_order(self, reason: str = "Terlalu lama menunggu") -> Dict[str, Any]:
        """Pengguna membatalkan pesanan (Customer Cancel)."""
        order_id = self._active_trip.get("order_id", "ORD-UNKNOWN") if self._active_trip else "ORD-NONE"
        cancellation_record = {
            "order_id": order_id,
            "status": "cancelled_by_customer",
            "cancelled_by": "Customer",
            "reason": reason,
            "cancelled_at": time.time()
        }
        self._active_trip = None
        self._is_available = True
        logger.info(f"[DRIVER ROLE] Order {order_id} DIBATALKAN oleh PENGGUNA (Alasan: {reason}) - Driver kembali AVAILABLE.")
        return cancellation_record

    def system_auto_cancel_no_show(self, order_id: Optional[str] = None) -> Dict[str, Any]:
        """Sistem membatalkan pesanan secara otomatis setelah 30 menit (Fase D No-Show)."""
        active_id = order_id or (self._active_trip.get("order_id") if self._active_trip else "ORD-AUTO-EXPIRED")
        cancellation_record = {
            "order_id": active_id,
            "status": "auto_cancelled_no_show",
            "cancelled_by": "System",
            "reason": "Customer no-show beyond 30 minutes threshold (1800s)",
            "cancelled_at": time.time()
        }
        self._active_trip = None
        self._is_available = True
        logger.info(f"[DRIVER ROLE] Order {active_id} DIBATALKAN OTOMATIS oleh SISTEM (No-Show >= 30 menit) - Driver kembali AVAILABLE.")
        return cancellation_record

