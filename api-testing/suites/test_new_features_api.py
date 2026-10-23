"""
================================================================================
TEST SUITE: EVMOTO NEW BACKEND FEATURES (FITUR 2, 3, & 5)
================================================================================
Target Sistem & Versi Aplikasi:
  - User Mobile Apps: v1.2.33 (com.evmoto.user.app)
  - Driver Mobile Apps: v1.9.27 (com.evmoto.driver.app)
  - Fitur 2: Akumulasi Online Driver -> Kupon Free Swap ECGO (Driver v1.9.27)
  - Fitur 3: Paket Kupon Registrasi Pengguna Baru (User v1.2.33)
  - Fitur 5: Subsidi Jam Sibuk Driver Rush Hour (Driver v1.9.27)
Penyusun:
  - Bhagus Arif Prayogo (Senior QA Engineer)
Cakupan Validasi:
  - JSON Schema Contract Verification (4 Pilar QA)
  - Boundary Limit & Rounding Rules
  - Concurrency, Redis Distributed Lock, & Idempotency
  - Financial Isolation (Guarantee Income Protection & Balance Mutations)
================================================================================
"""
import pytest
import jsonschema
from config.api_config import ApiConfig
from client.api_client import ApiClient
from schemas.api_schemas import (
    FREE_SWAP_DAILY_PAYOUT_SCHEMA,
    USER_ONBOARDING_VOUCHER_SCHEMA,
    RUSH_HOUR_SUBSIDY_SCHEMA
)


class TestFitur2OnlineFreeSwapApi:
    """Pengujian Otomatis Fitur 2: Akumulasi Online Driver -> Kupon Free Swap ECGO."""

    def test_tc_api_swap_01_daily_payout_target_met(self, evmoto_client: ApiClient):
        """TC-API-SWAP-01: Verifikasi payout harian kupon swap berhasil saat driver memenuhi target 480 menit."""
        resp = evmoto_client.get(
            ApiConfig.EP_DRIVER_FREE_SWAP_DAILY,
            params={"date": "2026-10-21", "quota": 10}
        )
        assert resp.status_code == 200, f"Status code harus 200, didapat: {resp.status_code}"
        res_json = resp.json()

        # Validasi Schema JSON Kontrak
        jsonschema.validate(instance=res_json, schema=FREE_SWAP_DAILY_PAYOUT_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("allocatedCount", 0) > 0, "Alokasi kupon tidak boleh 0 untuk driver yang memenuhi target"
        assert "evmoto:freeswap:payout:2026-10-21" in data.get("redisLockKey", ""), "Redis lock key harus tercatat"

        # Verifikasi kelayakan driver
        eligible = data.get("eligibleDrivers", [])
        driver_match = next((d for d in eligible if d.get("driverId") == 546), None)
        assert driver_match is not None, "Driver ID 546 wajib masuk daftar eligible"
        assert driver_match.get("couponStatus") == "ISSUED", "Status kupon driver harus ISSUED"
        assert driver_match.get("onlineMinutesWindow") >= 480, "Menit online window harus >= 480 menit"
        assert driver_match.get("ecgoCouponId") is not None, "ID kupon swap ECGO wajib diterbitkan"

    def test_tc_api_swap_02_unlinked_driver_rejected(self, evmoto_client: ApiClient):
        """TC-API-SWAP-02: Verifikasi driver online >= 480 menit tapi belum binding ECGO ditolak dari alokasi kupon."""
        resp = evmoto_client.get(
            ApiConfig.EP_DRIVER_FREE_SWAP_DAILY,
            params={"date": "2026-10-20", "simulate_unlinked": True}
        )
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=FREE_SWAP_DAILY_PAYOUT_SCHEMA)

        data = res_json.get("data", {})
        eligible = data.get("eligibleDrivers", [])
        assert len(eligible) > 0
        unlinked_driver = eligible[0]

        assert unlinked_driver.get("couponStatus") == "REJECTED_UNLINKED", "Driver unlinked harus berstatus REJECTED_UNLINKED"
        assert unlinked_driver.get("ecgoCouponId") is None, "Driver unlinked tidak boleh menerima ID kupon ECGO"
        assert data.get("allocatedCount") == 0, "Alokasi kupon berhasil harus 0"

    def test_tc_api_swap_03_redis_lock_duplicate_defense(self, evmoto_client: ApiClient):
        """TC-API-SWAP-03: Verifikasi pencegahan eksekusi berulang (Double Payout) melalui Redis Distributed Lock."""
        # Eksekusi kedua dengan tanggal yang sama ('2026-10-21') yang sudah diproses di TC-01
        resp = evmoto_client.get(
            ApiConfig.EP_DRIVER_FREE_SWAP_DAILY,
            params={"date": "2026-10-21"}
        )
        assert resp.status_code == 409, f"Panggilan duplikat wajib mengembalikan status 409 Conflict, didapat: {resp.status_code}"
        res_json = resp.json()
        assert res_json.get("code") == 409
        assert "DUPLICATE" in res_json.get("msg", "") or "LOCKED" in res_json.get("msg", "")

    def test_tc_api_swap_04_quota_exhaustion_defense(self, evmoto_client: ApiClient):
        """TC-API-SWAP-04: Verifikasi sisa kuota harian free swap terhitung akurat dan tidak terjadi over-allocation."""
        resp = evmoto_client.get(
            ApiConfig.EP_DRIVER_FREE_SWAP_DAILY,
            params={"date": "2026-10-19", "quota": 5}
        )
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=FREE_SWAP_DAILY_PAYOUT_SCHEMA)

        data = res_json.get("data", {})
        allocated = data.get("allocatedCount", 0)
        remaining = data.get("quotaRemaining", 0)
        assert allocated + remaining == 5, "Total alokasi + sisa kuota wajib sama dengan kuota harian awal (5)"


class TestFitur3UserOnboardingVouchersApi:
    """Pengujian Otomatis Fitur 3: Paket Kupon Registrasi Pengguna Baru (Onboarding)."""

    def test_tc_api_usr_vcr_01_registration_voucher_issuance(self, evmoto_client: ApiClient):
        """TC-API-VCR-01: Verifikasi user baru EvMoto (companyId = 1) menerima paket kupon selamat datang lengkap."""
        payload = {
            "userId": 9011,
            "companyId": 1,
            "phone": "081272370011",
            "channel": "MOBILE_REGISTRATION"
        }
        resp = evmoto_client.put(ApiConfig.EP_USER_REGISTER, json_data=payload)
        assert resp.status_code == 200, f"Registrasi harus berhasil: {resp.status_code}"
        res_json = resp.json()

        # Validasi Schema JSON Kontrak
        jsonschema.validate(instance=res_json, schema=USER_ONBOARDING_VOUCHER_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("companyId") == 1
        assert data.get("vouchersIssued") == 3, "User baru wajib menerima 3 kupon selamat datang"
        assert data.get("totalDiscountValue") == 35000.0, "Total nilai kupon onboarding harus Rp 35.000"
        assert len(data.get("vouchers", [])) == 3, "Array vouchers wajib berisi 3 objek kupon"

    def test_tc_api_usr_vcr_02_whatsapp_login_voucher_issuance(self, evmoto_client: ApiClient):
        """TC-API-VCR-02: Verifikasi registrasi first-time via WhatsApp (threeLogin) otomatis memicu kupon onboarding."""
        payload = {
            "userId": 9012,
            "companyId": 1,
            "authType": "WHATSAPP_OAUTH",
            "whatsappToken": "wa_oauth_token_verified_772"
        }
        resp = evmoto_client.post(ApiConfig.EP_USER_THREE_LOGIN, json_data=payload)
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=USER_ONBOARDING_VOUCHER_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("vouchersIssued") == 3, "Pendaftaran via WhatsApp wajib menerima kupon paket selamat datang"

    def test_tc_api_usr_vcr_03_non_evmoto_company_isolation(self, evmoto_client: ApiClient):
        """TC-API-VCR-03: Verifikasi registrasi akun tenant eksternal (companyId != 1) tidak mendapatkan paket voucher EvMoto."""
        payload = {
            "userId": 9013,
            "companyId": 99,  # Tenant eksternal
            "phone": "081299990099"
        }
        resp = evmoto_client.put(ApiConfig.EP_USER_REGISTER, json_data=payload)
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=USER_ONBOARDING_VOUCHER_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("companyId") == 99
        assert data.get("vouchersIssued") == 0, "User non-EvMoto tidak boleh menerima voucher promosi onboarding"
        assert len(data.get("vouchers", [])) == 0

    def test_tc_api_usr_vcr_04_budget_depletion_safeguard(self, evmoto_client: ApiClient):
        """TC-API-VCR-04: Verifikasi perlindungan anggaran (lavePrice): loop berhenti saat budget tidak mencukupi voucher berikutnya."""
        payload = {
            "userId": 9014,
            "companyId": 1,
            "simulate_budget_exhausted": True
        }
        resp = evmoto_client.put(ApiConfig.EP_USER_REGISTER, json_data=payload)
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=USER_ONBOARDING_VOUCHER_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("vouchersIssued") == 1, "Loop harus berhenti ketika sisa anggaran hanya cukup untuk 1 voucher"
        assert data.get("budgetDeducted") == 10000.0, "Pengurangan budget harus sesuai voucher yang berhasil diterbitkan"

    def test_tc_api_usr_vcr_05_inactive_package_protection(self, evmoto_client: ApiClient):
        """TC-API-VCR-05: Verifikasi paket kupon yang dinonaktifkan (enable != 2) tidak menerbitkan kupon ke user baru."""
        payload = {
            "userId": 9015,
            "companyId": 1,
            "simulate_inactive_package": True
        }
        resp = evmoto_client.put(ApiConfig.EP_USER_REGISTER, json_data=payload)
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=USER_ONBOARDING_VOUCHER_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("vouchersIssued") == 0, "Paket nonaktif tidak boleh menerbitkan voucher"

    def test_tc_api_usr_vcr_06_voucher_farming_reregister_defense(self, evmoto_client: ApiClient):
        """TC-API-VCR-06: Verifikasi Celah Voucher Farming - User menghapus akun lalu mendaftar ulang dengan nomor yang sama."""
        target_phone = "081272370001"

        # Tahap 1: Pendaftaran pertama kali (Normal First-Time Registration)
        reg_payload_1 = {
            "userId": 9016,
            "companyId": 1,
            "phone": target_phone,
            "authType": "PHONE_OTP"
        }
        resp_1 = evmoto_client.put(ApiConfig.EP_USER_REGISTER, json_data=reg_payload_1)
        assert resp_1.status_code == 200
        res_json_1 = resp_1.json()
        jsonschema.validate(instance=res_json_1, schema=USER_ONBOARDING_VOUCHER_SCHEMA)
        data_1 = res_json_1.get("data", {})
        assert data_1.get("vouchersIssued") == 3, "Pendaftaran pertama kali wajib berhasil menerima 3 kupon selamat datang"
        assert data_1.get("totalDiscountValue") == 35000.0

        # Tahap 2: Simulasi Penutupan / Penghapusan Akun Pengguna (Account Cancellation via Profil)

        # Tahap 3: Re-Registrasi dengan nomor telepon yang sama persis (Simulasi Potensi Voucher Farming)
        reg_payload_2 = {
            "userId": 9017,  # ID user baru hasil re-registrasi
            "companyId": 1,
            "phone": target_phone,
            "authType": "PHONE_OTP",
            "simulate_reregister_after_delete": True
        }
        resp_2 = evmoto_client.put(ApiConfig.EP_USER_REGISTER, json_data=reg_payload_2)
        assert resp_2.status_code == 200
        res_json_2 = resp_2.json()
        jsonschema.validate(instance=res_json_2, schema=USER_ONBOARDING_VOUCHER_SCHEMA)
        data_2 = res_json_2.get("data", {})

        # Tahap 4: Verifikasi Pertahanan Anti-Farming (Sistem Wajib Memblokir Kupon Ganda)
        assert res_json_2.get("msg") == "ALREADY_CLAIMED_ONBOARDING_REWARD" or data_2.get("vouchersIssued") == 0, (
            "POTENSI CELAH KEAMANAN: User yang mendaftar ulang dengan nomor sama tidak boleh menerima kupon kedua kali"
        )
        assert data_2.get("vouchersIssued") == 0, "Jumlah voucher diterbitkan harus 0 untuk re-registrasi nomor yang sama"
        assert data_2.get("totalDiscountValue") == 0.0, "Total diskon harus Rp 0"
        assert len(data_2.get("vouchers", [])) == 0, "Daftar voucher harus kosong"


class TestFitur5RushHourSubsidyApi:
    """Pengujian Otomatis Fitur 5: Subsidi Jam Sibuk Driver (Rush Hour - Private Car Only)."""

    def test_tc_api_rush_01_morning_rush_tier_1(self, evmoto_client: ApiClient):
        """TC-API-RUSH-01: Order mobil jam sibuk pagi (07:15 WIB) dengan tarif Rp 8.000 memperoleh subsidi Tier 1 (Rp 3.000)."""
        payload = {
            "orderId": "ORD-RUSH-T1-001",
            "driverId": 546,
            "vehicleType": 2,  # Private Car
            "orderMoney": 8000,
            "orderTime": "2026-10-23T07:15:00+07:00"
        }
        resp = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload)
        assert resp.status_code == 200, f"Request subsidi harus berhasil: {resp.status_code}"
        res_json = resp.json()

        # Validasi Schema JSON Kontrak
        jsonschema.validate(instance=res_json, schema=RUSH_HOUR_SUBSIDY_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("orderId") == "ORD-RUSH-T1-001"
        assert data.get("windowMatched") == "MORNING_RUSH"
        assert data.get("tierApplied") == 1, "Tarif <= Rp 10.000 wajib masuk Tier 1"
        assert data.get("subsidyAmount") == 3000, "Besaran subsidi Tier 1 wajib Rp 3.000"
        assert data.get("balanceChangeType") == 23, "Tipe mutasi saldo driver wajib 23 (Rush Hour Subsidy)"
        assert data.get("incomeType") == 1, "Tipe income driver wajib 1 (Bonus)"
        assert data.get("isGuaranteedIncomeExempt") is True, "Wajib diisolasi dari Minimum Guaranteed Income"

    def test_tc_api_rush_02_morning_rush_tier_2(self, evmoto_client: ApiClient):
        """TC-API-RUSH-02: Order mobil jam sibuk pagi (08:30 WIB) dengan tarif Rp 15.000 memperoleh subsidi Tier 2 (Rp 4.000)."""
        payload = {
            "orderId": "ORD-RUSH-T2-002",
            "driverId": 546,
            "vehicleType": 2,
            "orderMoney": 15000,
            "orderTime": "2026-10-23T08:30:00+07:00"
        }
        resp = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload)
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=RUSH_HOUR_SUBSIDY_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("tierApplied") == 2, "Tarif Rp 15.000 wajib masuk Tier 2 (Rp 10.001 - Rp 20.000)"
        assert data.get("subsidyAmount") == 4000, "Besaran subsidi Tier 2 wajib Rp 4.000"

    def test_tc_api_rush_03_evening_rush_tier_3(self, evmoto_client: ApiClient):
        """TC-API-RUSH-03: Order mobil jam sibuk sore (17:45 WIB) dengan tarif Rp 28.000 memperoleh subsidi Tier 3 (Rp 5.000)."""
        payload = {
            "orderId": "ORD-RUSH-T3-003",
            "driverId": 546,
            "vehicleType": 2,
            "orderMoney": 28000,
            "orderTime": "2026-10-23T17:45:00+07:00"
        }
        resp = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload)
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=RUSH_HOUR_SUBSIDY_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("windowMatched") == "EVENING_RUSH"
        assert data.get("tierApplied") == 3, "Tarif > Rp 20.000 wajib masuk Tier 3"
        assert data.get("subsidyAmount") == 5000, "Besaran subsidi Tier 3 wajib Rp 5.000"

    def test_tc_api_rush_04_rounding_boundary_order_money(self, evmoto_client: ApiClient):
        """TC-API-RUSH-04: Boundary Test pembulatan tarif: Rp 10.000,50 dibulatkan ke Rp 10.001 sehingga masuk Tier 2."""
        payload = {
            "orderId": "ORD-RUSH-ROUND-004",
            "driverId": 546,
            "vehicleType": 2,
            "orderMoney": 10000.50,  # Boundary rounding threshold
            "orderTime": "2026-10-23T07:45:00+07:00"
        }
        resp = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload)
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=RUSH_HOUR_SUBSIDY_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("orderMoneyRounded") == 10001, "Rp 10.000,50 wajib dibulatkan ke Rp 10.001"
        assert data.get("tierApplied") == 2, "Rp 10.001 wajib masuk Tier 2 (bukan Tier 1)"
        assert data.get("subsidyAmount") == 4000

    def test_tc_api_rush_05_exact_boundary_cutoff_0845_vs_0846(self, evmoto_client: ApiClient):
        """TC-API-RUSH-05: Boundary Limit Time Cutoff: 08:45:00 WIB (Eligible) vs 08:46:00 WIB (Ineligible)."""
        # Order tepat di batas inklusif jam 08:45:00 WIB
        payload_inclusive = {
            "orderId": "ORD-RUSH-CUTOFF-IN",
            "driverId": 546,
            "vehicleType": 2,
            "orderMoney": 12000,
            "orderTime": "2026-10-23T08:45:00+07:00"
        }
        resp_in = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload_inclusive)
        assert resp_in.status_code == 200
        assert resp_in.json()["data"]["subsidyAmount"] == 4000, "08:45:00 WIB inklusif wajib menerima subsidi"

        # Order 1 menit setelah batas (08:46:00 WIB)
        payload_exclusive = {
            "orderId": "ORD-RUSH-CUTOFF-OUT",
            "driverId": 546,
            "vehicleType": 2,
            "orderMoney": 12000,
            "orderTime": "2026-10-23T08:46:00+07:00"
        }
        resp_out = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload_exclusive)
        assert resp_out.status_code == 200
        data_out = resp_out.json()["data"]
        assert data_out.get("subsidyAmount") == 0, "08:46:00 WIB di luar jam sibuk harus bernilai subsidi Rp 0"
        assert data_out.get("tierApplied") == 0

    def test_tc_api_rush_06_non_car_vehicle_type_exclusion(self, evmoto_client: ApiClient):
        """TC-API-RUSH-06: Verifikasi isolasi armada: Order motor (vehicleType = 1) di jam sibuk menerima subsidi Rp 0."""
        payload = {
            "orderId": "ORD-RUSH-BIKE-006",
            "driverId": 546,
            "vehicleType": 1,  # Motorcycle
            "orderMoney": 15000,
            "orderTime": "2026-10-23T07:30:00+07:00"
        }
        resp = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload)
        assert resp.status_code == 200
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=RUSH_HOUR_SUBSIDY_SCHEMA)

        data = res_json.get("data", {})
        assert data.get("vehicleType") == 1
        assert data.get("subsidyAmount") == 0, "Motor tidak boleh mendapatkan subsidi jam sibuk"
        assert data.get("tierApplied") == 0

    def test_tc_api_rush_07_gi_isolation_integrity(self, evmoto_client: ApiClient):
        """TC-API-RUSH-07: Verifikasi integritas finansial: Subsidi rush hour bertipe Bonus (type: 1) tidak memotong Garansi Pendapatan (GI)."""
        payload = {
            "orderId": "ORD-RUSH-GI-007",
            "driverId": 546,
            "vehicleType": 2,
            "orderMoney": 16000,
            "orderTime": "2026-10-23T18:00:00+07:00"
        }
        resp = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload)
        assert resp.status_code == 200
        data = resp.json()["data"]

        assert data.get("balanceChangeType") == 23, "Tipe mutasi saldo wajib changeType = 23"
        assert data.get("incomeType") == 1, "Tipe income wajib 1 (Bonus)"
        assert data.get("isGuaranteedIncomeExempt") is True, "GI calculation hanya memotong incomeType = 2"

    def test_tc_api_rush_08_idempotency_duplicate_order_defense(self, evmoto_client: ApiClient):
        """TC-API-RUSH-08: Idempotency Test: Percobaan pembayaran subsidi kedua untuk orderId yang sama wajib ditolak (HTTP 409)."""
        # Order 'ORD-RUSH-T1-001' sudah dievaluasi dan dibayar pada TC-01
        payload_duplicate = {
            "orderId": "ORD-RUSH-T1-001",
            "driverId": 546,
            "vehicleType": 2,
            "orderMoney": 8000,
            "orderTime": "2026-10-23T07:15:00+07:00"
        }
        resp = evmoto_client.post(ApiConfig.EP_ORDER_RUSH_HOUR_SUBSIDY, json_data=payload_duplicate)
        assert resp.status_code == 409, f"Panggilan subsidi duplikat wajib mengembalikan HTTP 409 Conflict, didapat: {resp.status_code}"
        res_json = resp.json()
        assert res_json.get("code") == 409
        assert "DUPLICATE" in res_json.get("msg", "")
