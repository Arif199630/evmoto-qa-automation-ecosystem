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
    def __init__(self, driver_id: str, name: str, phone: str, distance_km: float, ring: str, device_model: str = "Android Device"):
        self.driver_id = driver_id
        self.name = name
        self.phone = phone
        self.distance_km = distance_km
        self.ring = ring  # 'ring1' (< 5km) or 'ring2' (> 5km)
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

