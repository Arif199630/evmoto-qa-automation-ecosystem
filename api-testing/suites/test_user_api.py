"""
================================================================================
TEST SUITE: PASSENGER / USER MOBILE BACKEND API
================================================================================
Target Sistem:
  - EvMoto Passenger Core API (/account/base/user/*, /order/api/user/*)
Cakupan Pengujian:
  - Autentikasi Penumpang via OTP Login & Penerbitan Token Sesi
  - Estimasi Biaya Perjalanan (Fare Calculation Engine) Berdasarkan Jarak
  - Siklus Pemesanan: Create Booking Order (Alokasi Pencarian Mitra Driver)
  - Pembatalan Pesanan Secara Graceful (Cancel Order)
================================================================================
"""
import pytest
import jsonschema
from config.api_config import ApiConfig
from client.api_client import ApiClient
from schemas.api_schemas import (
    USER_LOGIN_SUCCESS_SCHEMA,
    USER_ESTIMATE_FARE_SCHEMA,
    USER_CREATE_ORDER_SCHEMA
)


class TestPassengerUserApi:
    """Pengujian Fungsionalitas Aplikasi Pengguna / Penumpang (User App)."""

    def test_tc_api_usr_01_user_login_valid_credentials(self):
        """TC-API-USR-01: Verifikasi autentikasi login penumpang sukses dan menerima token JWT."""
        user_client = ApiClient(base_url=ApiConfig.EVMOTO_BASE_URL)
        # 1. Trigger captcha
        user_client.post(ApiConfig.EP_USER_QUERY_CAPTCHA, json_data={"phone": ApiConfig.USER_PHONE})

        # 2. Login by OTP
        payload = {
            "phone": ApiConfig.USER_PHONE,
            "code": ApiConfig.USER_OTP
        }
        resp = user_client.post(ApiConfig.EP_USER_LOGIN_OTP, json_data=payload)

        assert resp.status_code == 200, f"Gagal login penumpang: {resp.status_code}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=USER_LOGIN_SUCCESS_SCHEMA)

        user_data = res_json.get("data", {})
        assert user_data.get("token") is not None, "Token autentikasi penumpang wajib diterbitkan"
        assert user_data.get("id") is not None, "User ID penumpang wajib ada"

    def test_tc_api_usr_02_fare_estimation(self, authenticated_user_session: ApiClient):
        """TC-API-USR-02: Contract & Calculation - Verifikasi kalkulasi estimasi tarif perjalanan."""
        fare_payload = {
            "originLat": -6.2088,
            "originLng": 106.8456,
            "destLat": -6.1890,
            "destLng": 106.8230,
            "serviceType": "EVMOTO_MOTOR"
        }
        resp = authenticated_user_session.post(ApiConfig.EP_USER_ESTIMATE_FARE, json_data=fare_payload)

        assert resp.status_code == 200, f"Gagal estimasi tarif: {resp.status_code}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=USER_ESTIMATE_FARE_SCHEMA)

        fare_data = res_json.get("data", {})
        assert fare_data.get("distanceKm", 0) > 0, "Jarak tempuh harus lebih besar dari 0 KM"
        assert fare_data.get("totalFare", 0) > 0, "Total tarif harus bernilai positif"
        assert fare_data.get("currency") == "IDR", "Mata uang wajib IDR"

    def test_tc_api_usr_03_create_booking_order(self, authenticated_user_session: ApiClient):
        """TC-API-USR-03: Order Lifecycle - Penumpang membuat pesanan penjemputan baru."""
        order_payload = {
            "pickupLocation": "Menara Astra, Sudirman",
            "destinationLocation": "Grand Indonesia Mall",
            "originLat": -6.2088,
            "originLng": 106.8456,
            "destLat": -6.1890,
            "destLng": 106.8230,
            "serviceType": "EVMOTO_MOTOR",
            "paymentMethod": "EVMOTO_WALLET"
        }
        resp = authenticated_user_session.post(ApiConfig.EP_USER_CREATE_ORDER, json_data=order_payload)

        assert resp.status_code == 200, f"Gagal membuat pesanan: {resp.status_code}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=USER_CREATE_ORDER_SCHEMA)

        order_data = res_json.get("data", {})
        assert order_data.get("orderId") is not None, "Order ID pesanan wajib di-generate"
        assert order_data.get("status") in ("SEARCHING_DRIVER", "CREATED", "ASSIGNED")

    def test_tc_api_usr_04_cancel_booking_order(self, authenticated_user_session: ApiClient):
        """TC-API-USR-04: Order Lifecycle - Pembatalan pesanan perjalanan oleh penumpang."""
        cancel_payload = {
            "orderId": "ORD-EVM-8821",
            "cancelReason": "Mitra terlalu lama merespons"
        }
        resp = authenticated_user_session.post(ApiConfig.EP_USER_CANCEL_ORDER, json_data=cancel_payload)

        assert resp.status_code == 200, f"Gagal membatalkan pesanan: {resp.status_code}"
        res_json = resp.json()
        assert res_json.get("code") == 200
        assert res_json.get("data", {}).get("status") == "CANCELLED"
