"""
================================================================================
EVMOTO MULTI-DRIVER DISPATCH POOL & WATERFALL CASCADE SIMULATOR
================================================================================
Helper untuk memodelkan dan memvalidasi alur nyata dispatching multi-driver:
1. Ring 1: 5 Driver Standby di radius terdekat (< 5 KM).
2. Ring 2: 2 Driver Standby di radius luar (> 5 KM).
3. Instant Popup Revocation: Saat 1 driver menerima order, popup di driver lain langsung hilang.
4. Exclusion Blacklist: Driver yang menolak/membatalkan di-blacklist dari order tersebut.
5. Re-dispatch Waterfall Cascade: Re-assign ke driver berikutnya di ring yang sama.
6. Distance Band Expansion: Jika seluruh driver ring terdekat habis menolak, sistem
   otomatis melakukan ekspansi radius ke ring berikutnya sesuai konfigurasi Admin Dashboard.
7. Advance Booking Support: Alur identik dengan matriks jarak khusus (0-15 KM).
================================================================================
"""
import time
import threading
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger("MultiDriverPoolSimulator")


class SimulatedDriver:
    """Representasi satu entitas driver & perangkat fisik (device) dalam pool dispatching."""
    def __init__(
        self,
        driver_id: str,
        name: str,
        phone: str,
        distance_km: float,
        ring: str,
        device_model: str = "Android Device",
        is_eligible_gi: bool = True,
        band: str = "Band 1"
    ):
        self.driver_id = driver_id
        self.name = name
        self.phone = phone
        self.distance_km = distance_km
        self.ring = ring  # 'ring1' (< 5km) or 'ring2' (> 5km)
        self.band = band  # 'Band 1' (0-1km), 'Band 2' (1-2km), 'Band 3' (2-5km)
        self.is_eligible_gi = is_eligible_gi
        self.device_model = device_model
        self.is_online = True
        self.is_standby = True
        self.active_order: Optional[Dict[str, Any]] = None
        self.visible_popups: Dict[str, Dict[str, Any]] = {}  # order_id -> offer_dict
        
        # Lapisan Visual UI & Notifikasi Perangkat Mobile:
        self.notification_tray: List[Dict[str, Any]] = []      # Push Notification Bar & Ringtone
        self.screen_ui_state: Dict[str, str] = {}              # order_id -> 'IDLE' | 'MODAL_VISIBLE' | 'CLOSED_PEER' | 'CLOSED_RACE_LOST' | 'NOTIF_ONLY_POPUP_BLOCKED'
        self.race_lost_order_ids: set = set()                  # Catatan order yang pernah kalah swipe simultan
        self.simulate_staging_ui_bug: bool = False             # Saklar simulasi cacat UI staging (Notif masuk tapi popup gagal render)

        # Keuangan & Insentif Guarantee Income (G.I):
        self.gi_incentive_balance: float = 0.0
        self.gi_penalty_history: List[Dict[str, Any]] = []
        self.ewallet_balance: float = 50000.0  # Saldo Dompet Tunai / E-Wallet (murni utuh tidak tersentuh)
        self.total_daily_fare: float = 0.0
        self.popup_timer_expired: Dict[str, bool] = {}
        self.popup_countdown_visible: Dict[str, bool] = {}

    def apply_gi_penalty(self, order_id: str, amount: float = 10000.0, reason: str = "REJECT") -> Dict[str, Any]:
        """Memotong insentif Guarantee Income jika driver Eligible G.I (E-Wallet tetap utuh)."""
        if not self.is_eligible_gi:
            return {"applied": False, "reason": "DRIVER_NOT_ELIGIBLE_GI", "penalty": 0.0}

        self.gi_incentive_balance -= amount
        entry = {
            "order_id": order_id,
            "type": "PENALTY",
            "amount": -amount,
            "reason": reason,
            "timestamp": time.time(),
            "new_balance": self.gi_incentive_balance
        }
        self.gi_penalty_history.append(entry)
        logger.info(
            f"[G.I PENALTY APPLIED] Driver {self.name} ({self.driver_id}) terkena penalti G.I -Rp {int(amount):,} "
            f"karena '{reason}'. Saldo Insentif G.I: Rp {int(self.gi_incentive_balance):,} (E-Wallet Rp {int(self.ewallet_balance):,} AMAN)."
        )
        return {"applied": True, "amount": amount, "balance": self.gi_incentive_balance, "ewallet": self.ewallet_balance}

    def record_completed_trip_fare(self, order_id: str, fare: float) -> Dict[str, Any]:
        """Mencatat perolehan argo pesanan selesai untuk pemulihan (offsetting) pinalti G.I."""
        self.total_daily_fare += fare
        old_balance = self.gi_incentive_balance
        if self.gi_incentive_balance < 0:
            self.gi_incentive_balance = min(0.0, self.gi_incentive_balance + fare)

        entry = {
            "order_id": order_id,
            "type": "TRIP_FARE",
            "amount": fare,
            "total_daily_fare": self.total_daily_fare,
            "recovered_gi_balance": self.gi_incentive_balance,
            "timestamp": time.time()
        }
        self.gi_penalty_history.append(entry)
        logger.info(
            f"[G.I FARE RECOVERY] Driver {self.name} ({self.driver_id}) menyelesaikan order argo Rp {int(fare):,}. "
            f"Total Argo Hari Ini: Rp {int(self.total_daily_fare):,}. Status Insentif G.I: {int(old_balance):,} -> {int(self.gi_incentive_balance):,}."
        )
        return entry

    def trigger_popup_10s_timeout(self, order_id: str) -> Dict[str, Any]:
        """
        Mensimulasikan waktu 10 detik habis pada popup order.
        Jika Eligible G.I: Kena penalti Rp 10.000 dan popup dicabut.
        Jika Non-Eligible: Timer countdown hilang, tetapi popup order tetap stand by di layar.
        """
        if order_id not in self.visible_popups:
            return {"status": "NO_POPUP"}

        self.popup_timer_expired[order_id] = True
        self.popup_countdown_visible[order_id] = False

        if self.is_eligible_gi:
            self.apply_gi_penalty(order_id, amount=10000.0, reason="TIMEOUT_10S")
            self.remove_popup(order_id, reason="TIMEOUT_10S")
            return {
                "status": "REVOKED_WITH_PENALTY",
                "is_eligible_gi": True,
                "penalty": 10000.0,
                "popup_visible": False
            }
        else:
            return {
                "status": "COUNTDOWN_EXPIRED_POPUP_PERSISTS",
                "is_eligible_gi": False,
                "penalty": 0.0,
                "popup_visible": True,
                "countdown_visible": False
            }

    def reset_gi_ledger(self):
        """Mereset saldo insentif G.I dan riwayat penalti."""
        self.gi_incentive_balance = 0.0
        self.gi_penalty_history.clear()
        self.total_daily_fare = 0.0

    def has_popup(self, order_id: str) -> bool:
        """Memeriksa apakah modal popup interaktif sedang aktif tampil di layar."""
        return order_id in self.visible_popups

    def is_modal_popup_visible(self, order_id: str) -> bool:
        """Visual check: apakah popup kartu order tampak di layar dan bisa di-swipe."""
        return order_id in self.visible_popups and self.screen_ui_state.get(order_id) == "MODAL_VISIBLE"

    def is_notification_received(self, order_id: str) -> bool:
        """System check: apakah push notif / suara order masuk diterima perangkat."""
        return any(n.get("order_id") == order_id for n in self.notification_tray)

    def can_driver_swipe(self, order_id: str) -> bool:
        """Apakah pengemudi secara visual memiliki kontrol swipe untuk menerima pesanan."""
        return self.is_modal_popup_visible(order_id) and self.is_online and self.is_standby

    def add_popup(self, offer: Dict[str, Any]):
        """Menerima broadcast pesanan baru ke perangkat driver."""
        order_id = offer["order_id"]

        # 1. Selalu terima notifikasi di system tray (suara & banner push)
        notif_item = {
            "order_id": order_id,
            "title": "Pesanan Masuk!",
            "fare": offer.get("fare"),
            "received_at": time.time()
        }
        self.notification_tray.append(notif_item)

        # 2. Evaluasi apakah UI Pop-up Modal berhasil merender di layar
        if self.simulate_staging_ui_bug and (order_id in self.race_lost_order_ids):
            # REPRODUKSI BUG AKTUAL STAGING:
            # Perangkat hanya menerima Push Notif di status bar / suara,
            # tetapi komponen Dialog UI Pop-up GAGAL me-render ulang di layar!
            self.screen_ui_state[order_id] = "NOTIF_ONLY_POPUP_BLOCKED"
            self.visible_popups.pop(order_id, None)
            logger.warning(
                f"[STAGING UI BUG REPRODUCED] Perangkat {self.name} ({self.driver_id}) menerima Notifikasi untuk {order_id}, "
                f"TETAPI POP-UP KARTU ORDER GAGAL TAMPIL DI LAYAR (Blocked by previous race loss state)!"
            )
        else:
            # PERILAKU NORMAL / PATCHED:
            self.visible_popups[order_id] = offer
            self.screen_ui_state[order_id] = "MODAL_VISIBLE"
            logger.info(f"[UI POPUP RENDERED] Pop-up interaktif {order_id} aktif di layar {self.name} ({self.driver_id}).")

    def record_race_loss(self, order_id: str):
        """Mencatat bahwa perangkat kalah saat swipe simultan."""
        self.race_lost_order_ids.add(order_id)
        self.screen_ui_state[order_id] = "CLOSED_RACE_LOST"
        self.visible_popups.pop(order_id, None)

    def remove_popup(self, order_id: str, reason: str = "REVOKED_PEER"):
        """Menutup popup dari layar."""
        self.visible_popups.pop(order_id, None)
        self.screen_ui_state[order_id] = f"CLOSED_{reason}"

    def clear_all_popups(self):
        self.visible_popups.clear()
        self.notification_tray.clear()
        self.screen_ui_state.clear()
        self.race_lost_order_ids.clear()
        self.popup_timer_expired.clear()
        self.popup_countdown_visible.clear()


class MultiDriverDispatchPoolSimulator:
    """Orkestrator Dispatch Pool untuk Pengujian Skenario Waterfall & Re-dispatch."""

    def __init__(self):
        self._lock = threading.Lock()
        self.drivers: Dict[str, SimulatedDriver] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.dispatch_audit_trail: List[Dict[str, Any]] = []

        # Inisialisasi 7 Driver sesuai topologi pengujian:
        # 5 Driver di Ring 1 (< 5 KM)
        self._register_driver("DRV-01", "Driver Ring1-Alpha", "82200000001", 1.2, "ring1")
        self._register_driver("DRV-02", "Driver Ring1-Bravo", "82200000002", 1.8, "ring1")
        self._register_driver("DRV-03", "Driver Ring1-Charlie", "82200000003", 2.5, "ring1")
        self._register_driver("DRV-04", "Driver Ring1-Delta", "82200000004", 3.2, "ring1")
        self._register_driver("DRV-05", "Driver Ring1-Echo", "82200000005", 4.1, "ring1")

        # 2 Driver di Ring 2 (> 5 KM)
        self._register_driver("DRV-06", "Driver Ring2-Foxtrot", "82200000006", 6.5, "ring2")
        self._register_driver("DRV-07", "Driver Ring2-Golf", "82200000007", 8.2, "ring2")

    def _register_driver(self, d_id: str, name: str, phone: str, distance_km: float, ring: str):
        self.drivers[d_id] = SimulatedDriver(d_id, name, phone, distance_km, ring)

    def reset_pool(self):
        """Mereset seluruh pool pengemudi dan pesanan ke status default standby."""
        with self._lock:
            for d in self.drivers.values():
                d.is_online = True
                d.is_standby = True
                d.active_order = None
                d.clear_all_popups()
            self.orders.clear()
            self.dispatch_audit_trail.clear()
            logger.info("[MULTI-DRIVER POOL] Pool berhasil direset ke kondisi baseline.")

    # ==========================================================================
    # 1. PEMBUATAN ORDER OLEH CUSTOMER
    # ==========================================================================
    def create_order(
        self,
        order_id: str,
        order_type: str = "regular",
        distance_km: float = 2.5,
        fare: int = 15000,
        pickup: str = "Menara Sudirman",
        destination: str = "Grand Indonesia"
    ) -> Dict[str, Any]:
        """User membuat pesanan baru (Reguler atau Advance Booking)."""
        with self._lock:
            order = {
                "order_id": order_id,
                "order_type": order_type,  # 'regular' or 'advance'
                "distance_km": distance_km,
                "fare": fare,
                "pickup": pickup,
                "destination": destination,
                "status": "DISPATCHING",
                "current_band": "ring1",
                "assigned_driver": None,
                "rejected_driver_ids": set(),
                "broadcast_history": [],
                "created_at": time.time(),
                "updated_at": time.time()
            }
            self.orders[order_id] = order
            logger.info(f"[POOL ORDER CREATED] Order {order_id} ({order_type.upper()}) dibuat. Menunggu broadcast.")
            return order

    # ==========================================================================
    # 2. BROADCAST BATCH KE DRIVER
    # ==========================================================================
    def broadcast_batch_to_band(self, order_id: str, target_band: str = "ring1") -> List[str]:
        """
        Menyiarkan popup pesanan serentak ke seluruh driver yang memenuhi syarat pada band tertentu.
        Mengecualikan driver yang sudah menolak (exclusion blacklist).
        """
        with self._lock:
            order = self.orders.get(order_id)
            if not order:
                raise ValueError(f"Order {order_id} tidak ditemukan!")

            order["current_band"] = target_band
            eligible_drivers = [
                d for d in self.drivers.values()
                if d.ring == target_band
                and d.is_online
                and d.is_standby
                and d.driver_id not in order["rejected_driver_ids"]
            ]

            target_driver_ids = []
            offer_payload = {
                "order_id": order_id,
                "order_type": order["order_type"],
                "pickup": order["pickup"],
                "destination": order["destination"],
                "distance_km": order["distance_km"],
                "fare": order["fare"],
                "band": target_band,
                "dispatched_at": time.time()
            }

            for d in eligible_drivers:
                d.add_popup(offer_payload)
                target_driver_ids.append(d.driver_id)

            order["broadcast_history"].append({
                "band": target_band,
                "timestamp": time.time(),
                "recipient_driver_ids": target_driver_ids
            })

            logger.info(
                f"[POOL BROADCAST] Order {order_id} disiarkan ke Band [{target_band.upper()}]: "
                f"{len(target_driver_ids)} Driver ({', '.join(target_driver_ids) if target_driver_ids else 'KOSONG'})"
            )
            return target_driver_ids

    # ==========================================================================
    # 3. DRIVER AKSI: TERIMA ORDER (SWIPE ACCEPT & INSTANT REVOCATION)
    # ==========================================================================
    def driver_accept_order(self, driver_id: str, order_id: str) -> Dict[str, Any]:
        """
        Driver melakukan Swipe/Terima pesanan.
        Efek Kritis: Popup order pada seluruh driver sekitarnya (peers) LANGSUNG HILANG!
        """
        with self._lock:
            order = self.orders.get(order_id)
            driver = self.drivers.get(driver_id)

            if not order or not driver:
                raise ValueError("Order atau Driver tidak valid!")

            if order["status"] == "ACCEPTED":
                driver.record_race_loss(order_id)
                raise ValueError(f"Race condition: Order {order_id} sudah diambil oleh {order['assigned_driver']}!")

            if not driver.has_popup(order_id):
                driver.record_race_loss(order_id)
                raise ValueError(f"Driver {driver_id} tidak memiliki penawaran untuk order {order_id}!")

            # 1. Update State Order
            order["status"] = "ACCEPTED"
            order["assigned_driver"] = driver_id
            order["accepted_at"] = time.time()
            order["updated_at"] = time.time()

            # 2. Update Driver
            driver.active_order = order
            driver.is_standby = False
            driver.remove_popup(order_id, reason="ACCEPTED_BY_SELF")

            # 3. INSTANT REVOCATION: Hapus popup order dari SELURUH driver rekanan seketika!
            revoked_count = 0
            for peer in self.drivers.values():
                if peer.driver_id != driver_id and peer.has_popup(order_id):
                    peer.remove_popup(order_id, reason="PEER_CLAIMED")
                    revoked_count += 1

            logger.info(
                f"[INSTANT REVOCATION] Order {order_id} BERHASIL DIAMBIL oleh {driver.name} ({driver_id}). "
                f"Popup seketika DICABUT dari {revoked_count} rekan pengemudi lainnya!"
            )
            return {
                "order_id": order_id,
                "status": "ACCEPTED",
                "assigned_driver": driver_id,
                "revoked_peers_count": revoked_count
            }

    # ==========================================================================
    # 4. DRIVER AKSI: TOLAK ORDER (REJECT & WATERFALL RE-DISPATCH)
    # ==========================================================================
    def driver_reject_order(self, driver_id: str, order_id: str) -> Dict[str, Any]:
        """
        Driver menekan tombol 'Tolak' (Reject/Lewati).
        Efek Kritis:
          1. Driver tersebut di-blacklist dari order tersebut (tidak akan muncul lagi).
          2. Order TIDAK BOLEH MATI / CANCELLED!
          3. Order otomatis di-reassign ke sisa driver di ring yang sama, atau ekspansi band.
        """
        with self._lock:
            order = self.orders.get(order_id)
            driver = self.drivers.get(driver_id)

            if not order or not driver:
                raise ValueError("Order atau Driver tidak valid!")

            # 1. Cabut popup dari driver yang menolak
            driver.remove_popup(order_id)

            # 2. Masukkan ke Blacklist Exclusion List
            order["rejected_driver_ids"].add(driver_id)
            logger.info(f"[DRIVER REJECT] Driver {driver.name} ({driver_id}) MENOLAK Order {order_id}. Blacklist aktif.")

            # 3. Jalankan Re-dispatch Waterfall Cascade
            return self._execute_waterfall_cascade_unlocked(order_id)

    # ==========================================================================
    # 5. DRIVER AKSI: CANCEL SETELAH TERIMA (POST-ACCEPTANCE CANCEL RECOVERY)
    # ==========================================================================
    def driver_cancel_accepted_order(self, driver_id: str, order_id: str, reason: str = "Kendala Kendaraan") -> Dict[str, Any]:
        """
        Driver membatalkan pesanan yang sebelumnya telah diterima.
        Efek Kritis:
          1. Order TIDAK BOLEH CANCELLED secara global ke customer!
          2. Status order kembali ke RE_DISPATCHING.
          3. Driver pemohon dibatalkan dan dimasukkan ke Blacklist.
          4. Order dilempar kembali ke pool untuk dijemput driver lain!
        """
        with self._lock:
            order = self.orders.get(order_id)
            driver = self.drivers.get(driver_id)

            if not order or not driver:
                raise ValueError("Order atau Driver tidak valid!")

            if order["assigned_driver"] != driver_id:
                raise ValueError(f"Driver {driver_id} bukan pemegang order aktif {order_id}!")

            # 1. Pulihkan driver ke standby
            driver.active_order = None
            driver.is_standby = True

            # 2. Kembalikan order ke pool (BUKAN CANCELLED)
            order["status"] = "RE_DISPATCHING"
            order["assigned_driver"] = None
            order["rejected_driver_ids"].add(driver_id)
            order["last_driver_cancel_reason"] = reason

            logger.info(
                f"[POST-ACCEPT CANCEL RECOVERY] Driver {driver.name} ({driver_id}) BATALKAN order {order_id} "
                f"karena '{reason}'. Order dipulihkan ke status RE_DISPATCHING (Bebas dari Pembatalan Global)!"
            )

            # 3. Jalankan Re-dispatch Waterfall Cascade
            return self._execute_waterfall_cascade_unlocked(order_id)

    # ==========================================================================
    # 6. LOGIKA INTI: WATERFALL CASCADE & DISTANCE BAND EXPANSION
    # ==========================================================================
    def _execute_waterfall_cascade_unlocked(self, order_id: str) -> Dict[str, Any]:
        """Logika internal untuk mengevaluasi re-dispatch atau ekspansi band."""
        order = self.orders[order_id]
        current_band = order["current_band"]

        # Cari sisa driver yang berhak di band saat ini
        remaining_candidates_same_band = [
            d for d in self.drivers.values()
            if d.ring == current_band
            and d.is_online
            and d.is_standby
            and d.driver_id not in order["rejected_driver_ids"]
        ]

        if remaining_candidates_same_band:
            # Skenario 5: Masih ada driver lain di ring yang sama
            # Pastikan popup order aktif di mereka
            dispatched_ids = []
            offer_payload = {
                "order_id": order_id,
                "order_type": order["order_type"],
                "pickup": order["pickup"],
                "destination": order["destination"],
                "distance_km": order["distance_km"],
                "fare": order["fare"],
                "band": current_band,
                "dispatched_at": time.time()
            }
            for d in remaining_candidates_same_band:
                if not d.has_popup(order_id):
                    d.add_popup(offer_payload)
                dispatched_ids.append(d.driver_id)

            order["status"] = "RE_DISPATCHING"
            logger.info(
                f"[CASCADE: SAME BAND] Order {order_id} tetap aktif di Band [{current_band.upper()}]. "
                f"Tersedia untuk {len(dispatched_ids)} driver lain: {', '.join(dispatched_ids)}"
            )
            return {
                "order_id": order_id,
                "status": "RE_DISPATCHING",
                "action": "SAME_BAND_REASSIGN",
                "current_band": current_band,
                "eligible_drivers": dispatched_ids,
                "band_expanded": False
            }

        # Skenario 6: Hak seluruh driver di ring saat ini sudah habis (semua reject / cancel)
        # Jika saat ini di Ring 1, kita EKSPANSI ke Ring 2 (> 5 KM)!
        if current_band == "ring1":
            logger.info(
                f"[CASCADE: BAND EXPANSION TRIGGERED] Seluruh 5 driver di Ring 1 telah menolak Order {order_id}. "
                f"Sistem mengaktifkan Distance Band Expansion ke Ring 2 (> 5 KM)!"
            )
            order["current_band"] = "ring2"
            ring2_candidates = [
                d for d in self.drivers.values()
                if d.ring == "ring2"
                and d.is_online
                and d.is_standby
                and d.driver_id not in order["rejected_driver_ids"]
            ]

            dispatched_ids = []
            offer_payload = {
                "order_id": order_id,
                "order_type": order["order_type"],
                "pickup": order["pickup"],
                "destination": order["destination"],
                "distance_km": order["distance_km"],
                "fare": order["fare"],
                "band": "ring2",
                "dispatched_at": time.time()
            }
            for d in ring2_candidates:
                d.add_popup(offer_payload)
                dispatched_ids.append(d.driver_id)

            order["status"] = "BAND_EXPANDED"
            logger.info(
                f"[BAND EXPANSION SUCCESS] Order {order_id} berhasil disiarkan ke Ring 2: "
                f"{len(dispatched_ids)} Driver ({', '.join(dispatched_ids)})"
            )
            return {
                "order_id": order_id,
                "status": "BAND_EXPANDED",
                "action": "EXPAND_TO_RING_2",
                "current_band": "ring2",
                "eligible_drivers": dispatched_ids,
                "band_expanded": True
            }

        # Jika di Ring 2 juga sudah habis menolak
        order["status"] = "NO_DRIVER_FOUND"
        logger.warning(f"[CASCADE EXHAUSTED] Seluruh driver di Ring 1 dan Ring 2 telah menolak order {order_id}!")
        return {
            "order_id": order_id,
            "status": "NO_DRIVER_FOUND",
            "action": "EXHAUSTED",
            "current_band": "exhausted",
            "eligible_drivers": [],
            "band_expanded": False
        }

    # ==========================================================================
    # HELPER INSPEKSI UNTUK ASSERTION PENGUJIAN
    # ==========================================================================
    def get_driver_visible_orders(self, driver_id: str) -> List[str]:
        """Mengambil list order_id yang sedang tampak di layar popup driver."""
        with self._lock:
            driver = self.drivers.get(driver_id)
            return list(driver.visible_popups.keys()) if driver else []

    def is_order_visible_on_driver(self, driver_id: str, order_id: str) -> bool:
        """Memeriksa apakah order tertentu tampak di layar driver."""
        with self._lock:
            driver = self.drivers.get(driver_id)
            return driver.has_popup(order_id) if driver else False

    def get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Mengambil data utuh order terkini."""
        with self._lock:
            return self.orders.get(order_id)


# ==============================================================================
# THREE-BAND GUARANTEE INCOME (G.I) DISPATCH SIMULATOR
# ==============================================================================
class ThreeBandGIDispatchPoolSimulator:
    """
    Simulator Dispatch Pool 3-Band & Guarantee Income (G.I) Aturan Baru:
    Topologi:
      - Band 1 (0-1 km) : 2 Driver (1 Eligible G.I, 1 Non-Eligible)
      - Band 2 (1-2 km) : 3 Driver (3 Eligible G.I)
      - Band 3 (2-5 km) : 3 Driver (2 Eligible G.I, 1 Non-Eligible)
    Total: 8 Driver.

    Urutan Waterfall Cascade (5 Tahap):
      Tahap 1: Band 1 - Eligible G.I (DRV-B1-GI-01)
      Tahap 2: Band 1 - Non-Eligible (DRV-B1-NON-01)
      Tahap 3: Band 2 - Eligible G.I (DRV-B2-GI-01, DRV-B2-GI-02, DRV-B2-GI-03) Broadcast Simultan
      Tahap 4: Band 3 - Eligible G.I (DRV-B3-GI-01, DRV-B3-GI-02) Broadcast Simultan
      Tahap 5: Band 3 - Non-Eligible (DRV-B3-NON-01)

    Aturan Bisnis:
      1. Prioritas Band Terdekat: Band 1 -> Band 2 -> Band 3.
      2. Prioritas Kategori: Driver Eligible G.I didahulukan dalam setiap Band.
      3. Penalti Rp 10.000: Hanya untuk Driver Eligible G.I saat Reject, Cancel, atau Timeout (> 10s).
      4. Bebas Penalti: Driver G.I yang kalah cepat saat broadcast TIDAK terkena penalti (Rp 0).
      5. Sumber Penalti: Murni memotong Akumulasi Insentif G.I hari itu (E-Wallet/Dompet Tunai AMAN).
      6. Offsetting Recovery: Argo pesanan yang diselesaikan memulihkan saldo insentif minus hingga Rp 0.
      7. Non-Eligible 10s Popup: Timer countdown habis, popup TETAP MUNCUL sampai diambil atau di-reject.
    """

    CASCADE_STAGES = [
        {"stage": 1, "band": "Band 1", "category": "ELIGIBLE_GI", "driver_ids": ["DRV-B1-GI-01"]},
        {"stage": 2, "band": "Band 1", "category": "NON_ELIGIBLE", "driver_ids": ["DRV-B1-NON-01"]},
        {"stage": 3, "band": "Band 2", "category": "ELIGIBLE_GI", "driver_ids": ["DRV-B2-GI-01", "DRV-B2-GI-02", "DRV-B2-GI-03"]},
        {"stage": 4, "band": "Band 3", "category": "ELIGIBLE_GI", "driver_ids": ["DRV-B3-GI-01", "DRV-B3-GI-02"]},
        {"stage": 5, "band": "Band 3", "category": "NON_ELIGIBLE", "driver_ids": ["DRV-B3-NON-01"]},
    ]

    def __init__(self):
        self._lock = threading.Lock()
        self.drivers: Dict[str, SimulatedDriver] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self._init_topology()

    def _init_topology(self):
        # 1. BAND 1 (0 - 1 KM): 2 Driver (1 G.I, 1 Non-G.I)
        self.drivers["DRV-B1-GI-01"] = SimulatedDriver(
            driver_id="DRV-B1-GI-01", name="Driver B1-GI-01", phone="82210000001",
            distance_km=0.6, ring="ring1", is_eligible_gi=True, band="Band 1"
        )
        self.drivers["DRV-B1-NON-01"] = SimulatedDriver(
            driver_id="DRV-B1-NON-01", name="Driver B1-NonGI-01", phone="82210000002",
            distance_km=0.8, ring="ring1", is_eligible_gi=False, band="Band 1"
        )

        # 2. BAND 2 (1 - 2 KM): 3 Driver (3 Eligible G.I)
        self.drivers["DRV-B2-GI-01"] = SimulatedDriver(
            driver_id="DRV-B2-GI-01", name="Driver B2-GI-01", phone="82220000001",
            distance_km=1.2, ring="ring1", is_eligible_gi=True, band="Band 2"
        )
        self.drivers["DRV-B2-GI-02"] = SimulatedDriver(
            driver_id="DRV-B2-GI-02", name="Driver B2-GI-02", phone="82220000002",
            distance_km=1.5, ring="ring1", is_eligible_gi=True, band="Band 2"
        )
        self.drivers["DRV-B2-GI-03"] = SimulatedDriver(
            driver_id="DRV-B2-GI-03", name="Driver B2-GI-03", phone="82220000003",
            distance_km=1.8, ring="ring1", is_eligible_gi=True, band="Band 2"
        )

        # 3. BAND 3 (2 - 5 KM): 3 Driver (2 Eligible G.I, 1 Non-Eligible)
        self.drivers["DRV-B3-GI-01"] = SimulatedDriver(
            driver_id="DRV-B3-GI-01", name="Driver B3-GI-01", phone="82230000001",
            distance_km=2.6, ring="ring1", is_eligible_gi=True, band="Band 3"
        )
        self.drivers["DRV-B3-GI-02"] = SimulatedDriver(
            driver_id="DRV-B3-GI-02", name="Driver B3-GI-02", phone="82230000002",
            distance_km=3.4, ring="ring1", is_eligible_gi=True, band="Band 3"
        )
        self.drivers["DRV-B3-NON-01"] = SimulatedDriver(
            driver_id="DRV-B3-NON-01", name="Driver B3-NonGI-01", phone="82230000003",
            distance_km=4.2, ring="ring1", is_eligible_gi=False, band="Band 3"
        )

    def reset_pool(self, reset_ledgers: bool = False):
        """Mereset state pengemudi dan order ke kondisi awal."""
        with self._lock:
            for d in self.drivers.values():
                d.is_online = True
                d.is_standby = True
                d.active_order = None
                d.clear_all_popups()
                if reset_ledgers:
                    d.reset_gi_ledger()
            self.orders.clear()
            logger.info("[THREE-BAND POOL] Pool 8 driver berhasil direset.")

    def create_order(
        self,
        order_id: str,
        order_type: str = "regular",
        distance_km: float = 2.5,
        fare: int = 15000,
        pickup: str = "Grand Indonesia",
        destination: str = "SCBD Sudirman"
    ) -> Dict[str, Any]:
        """Membuat pesanan baru dan otomatis menyiarkan ke Tahap 1 (Band 1 - Eligible G.I)."""
        with self._lock:
            order = {
                "order_id": order_id,
                "order_type": order_type,
                "distance_km": distance_km,
                "fare": fare,
                "pickup": pickup,
                "destination": destination,
                "status": "DISPATCHING",
                "current_stage_idx": 0,
                "assigned_driver": None,
                "rejected_driver_ids": set(),
                "created_at": time.time(),
                "updated_at": time.time()
            }
            self.orders[order_id] = order
            logger.info(f"[3-BAND ORDER] Order {order_id} dibuat. Mulai broadcast Tahap 1...")
            self._broadcast_stage_unlocked(order_id, stage_idx=0)
            return order

    def _broadcast_stage_unlocked(self, order_id: str, stage_idx: int) -> List[str]:
        """Internal broadcast ke seluruh driver pada stage tertentu."""
        order = self.orders[order_id]
        if stage_idx >= len(self.CASCADE_STAGES):
            order["status"] = "EXHAUSTED_NO_DRIVER"
            logger.warning(f"[3-BAND CASCADE EXHAUSTED] Seluruh 5 tahap pada 3 Band telah habis. Order {order_id} tidak terpenuhi.")
            return []

        stage_info = self.CASCADE_STAGES[stage_idx]
        order["current_stage_idx"] = stage_idx
        order["current_band"] = stage_info["band"]
        order["current_category"] = stage_info["category"]

        recipients = []
        offer_payload = {
            "order_id": order_id,
            "order_type": order["order_type"],
            "pickup": order["pickup"],
            "destination": order["destination"],
            "distance_km": order["distance_km"],
            "fare": order["fare"],
            "band": stage_info["band"],
            "category": stage_info["category"],
            "dispatched_at": time.time()
        }

        for d_id in stage_info["driver_ids"]:
            driver = self.drivers[d_id]
            if driver.is_online and driver.is_standby and d_id not in order["rejected_driver_ids"]:
                driver.add_popup(offer_payload)
                driver.popup_countdown_visible[order_id] = True
                driver.popup_timer_expired[order_id] = False
                recipients.append(d_id)

        logger.info(
            f"[3-BAND BROADCAST] Tahap {stage_info['stage']} ({stage_info['band']} - {stage_info['category']}): "
            f"Disiarkan simultan ke {len(recipients)} Driver ({', '.join(recipients)})"
        )
        return recipients

    def driver_accept_order(self, driver_id: str, order_id: str) -> Dict[str, Any]:
        """
        Driver menerima pesanan (First Swipe Wins).
        Popup seketika dicabut dari rekan driver lainnya.
        Rekan driver yang kalah cepat TIDAK DIKENAKAN PENALTI G.I!
        """
        with self._lock:
            order = self.orders.get(order_id)
            driver = self.drivers.get(driver_id)
            if not order or not driver:
                raise ValueError("Order atau Driver tidak valid!")

            if order["status"] == "ACCEPTED":
                driver.record_race_loss(order_id)
                raise ValueError(f"Race condition: Order {order_id} sudah diambil oleh {order['assigned_driver']}!")

            if not driver.has_popup(order_id):
                driver.record_race_loss(order_id)
                raise ValueError(f"Driver {driver_id} tidak memiliki popup order {order_id}!")

            # 1. Update State Order & Driver
            order["status"] = "ACCEPTED"
            order["assigned_driver"] = driver_id
            order["accepted_at"] = time.time()

            driver.active_order = order
            driver.is_standby = False
            driver.remove_popup(order_id, reason="ACCEPTED_BY_SELF")

            # 2. INSTANT REVOCATION DARI PEERS (Bebas Penalti)
            revoked_peers = []
            for peer in self.drivers.values():
                if peer.driver_id != driver_id and peer.has_popup(order_id):
                    peer.remove_popup(order_id, reason="PEER_CLAIMED")
                    revoked_peers.append(peer.driver_id)
                    # Pastikan peer TIDAK dikenakan penalti G.I karena order keburu diambil
                    logger.info(f"[PEER REVOKED FREE] Popup dicabut dari {peer.name} ({peer.driver_id}) TANPA PENALTI G.I.")

            return {
                "order_id": order_id,
                "status": "ACCEPTED",
                "assigned_driver": driver_id,
                "revoked_peers": revoked_peers
            }

    def driver_reject_order(self, driver_id: str, order_id: str) -> Dict[str, Any]:
        """
        Driver menolak pesanan (Reject).
        Jika Eligible G.I -> Kena pinalti Rp 10.000 pada akumulasi insentif G.I (E-Wallet aman).
        Jika seluruh driver pada stage aktif telah menolak -> Cascade ke stage berikutnya!
        """
        with self._lock:
            order = self.orders.get(order_id)
            driver = self.drivers.get(driver_id)
            if not order or not driver:
                raise ValueError("Order atau Driver tidak valid!")

            # 1. Hapus popup & masukkan ke Blacklist
            driver.remove_popup(order_id, reason="REJECTED_BY_DRIVER")
            order["rejected_driver_ids"].add(driver_id)

            # 2. Pinalti G.I jika eligible
            penalty_info = driver.apply_gi_penalty(order_id, amount=10000.0, reason="REJECT_ORDER")

            # 3. Evaluasi apakah stage aktif masih memiliki driver tersisa
            stage_idx = order["current_stage_idx"]
            stage_info = self.CASCADE_STAGES[stage_idx]
            remaining_in_stage = [
                d_id for d_id in stage_info["driver_ids"]
                if self.drivers[d_id].has_popup(order_id)
            ]

            advanced = False
            next_recipients = []
            if not remaining_in_stage:
                # Seluruh driver di stage aktif telah menolak -> CASCADE KE TAHAP BERIKUTNYA!
                next_stage_idx = stage_idx + 1
                advanced = True
                next_recipients = self._broadcast_stage_unlocked(order_id, stage_idx=next_stage_idx)

            return {
                "order_id": order_id,
                "driver_id": driver_id,
                "status": "REJECTED",
                "penalty_applied": penalty_info.get("applied", False),
                "penalty_amount": penalty_info.get("amount", 0.0),
                "gi_incentive_balance": driver.gi_incentive_balance,
                "ewallet_balance": driver.ewallet_balance,
                "stage_advanced": advanced,
                "next_recipients": next_recipients
            }

    def driver_timeout_order(self, driver_id: str, order_id: str) -> Dict[str, Any]:
        """
        Waktu 10 detik habis pada popup driver.
        Jika Eligible G.I -> Kena pinalti Rp 10.000, popup dicabut, dan cascade dievaluasi.
        Jika Non-Eligible -> Countdown habis, tetapi popup TETAP MUNCUL di layar.
        """
        with self._lock:
            order = self.orders.get(order_id)
            driver = self.drivers.get(driver_id)
            if not order or not driver:
                raise ValueError("Order atau Driver tidak valid!")

            timeout_result = driver.trigger_popup_10s_timeout(order_id)

            advanced = False
            next_recipients = []
            if driver.is_eligible_gi:
                # Masukkan ke blacklist karena timeout dihitung penolakan pasif
                order["rejected_driver_ids"].add(driver_id)
                stage_idx = order["current_stage_idx"]
                stage_info = self.CASCADE_STAGES[stage_idx]
                remaining_in_stage = [
                    d_id for d_id in stage_info["driver_ids"]
                    if self.drivers[d_id].has_popup(order_id)
                ]
                if not remaining_in_stage:
                    next_stage_idx = stage_idx + 1
                    advanced = True
                    next_recipients = self._broadcast_stage_unlocked(order_id, stage_idx=next_stage_idx)

            return {
                "order_id": order_id,
                "driver_id": driver_id,
                "timeout_result": timeout_result,
                "stage_advanced": advanced,
                "next_recipients": next_recipients
            }

    def driver_cancel_accepted_order(self, driver_id: str, order_id: str, reason: str = "Kendala Kendaraan") -> Dict[str, Any]:
        """
        Driver membatalkan pesanan setelah sebelumnya diterima (Accept -> Cancel).
        Efek:
          1. Driver G.I tetap kena pinalti Rp 10.000.
          2. Order TIDAK MATI / TIDAK CANCELLED GLOBAL.
          3. Order dikembalikan ke status RE_DISPATCHING dan melompat ke tahap berikutnya.
        """
        with self._lock:
            order = self.orders.get(order_id)
            driver = self.drivers.get(driver_id)
            if not order or not driver:
                raise ValueError("Order atau Driver tidak valid!")

            if order["assigned_driver"] != driver_id:
                raise ValueError(f"Driver {driver_id} bukan pemegang order aktif {order_id}!")

            # 1. Pinalti G.I
            penalty_info = driver.apply_gi_penalty(order_id, amount=10000.0, reason=f"CANCEL_ACCEPTED_ORDER: {reason}")

            # 2. Pulihkan status driver & blacklist dari order ini
            driver.active_order = None
            driver.is_standby = True
            order["rejected_driver_ids"].add(driver_id)
            order["assigned_driver"] = None
            order["status"] = "RE_DISPATCHING"

            # 3. Lanjutkan re-dispatch cascade ke tahap berikutnya
            next_stage_idx = order["current_stage_idx"] + 1
            next_recipients = self._broadcast_stage_unlocked(order_id, stage_idx=next_stage_idx)

            return {
                "order_id": order_id,
                "driver_id": driver_id,
                "status": "RE_DISPATCHING",
                "penalty_applied": penalty_info.get("applied", False),
                "penalty_amount": penalty_info.get("amount", 0.0),
                "gi_incentive_balance": driver.gi_incentive_balance,
                "ewallet_balance": driver.ewallet_balance,
                "next_recipients": next_recipients
            }

    def complete_trip_with_gi_recovery(self, driver_id: str, order_id: str, fare: float) -> Dict[str, Any]:
        """Driver menyelesaikan pesanan dan argo digunakan untuk pemulihan insentif G.I minus."""
        with self._lock:
            driver = self.drivers.get(driver_id)
            if not driver:
                raise ValueError("Driver tidak ditemukan!")

            recovery_entry = driver.record_completed_trip_fare(order_id, fare)
            return {
                "driver_id": driver_id,
                "order_id": order_id,
                "fare": fare,
                "new_gi_balance": driver.gi_incentive_balance,
                "total_daily_fare": driver.total_daily_fare,
                "ewallet_balance": driver.ewallet_balance
            }

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self.orders.get(order_id)


