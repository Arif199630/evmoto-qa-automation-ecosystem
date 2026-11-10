"""
User Data Provider Module
Automation Project EvMoto
Memuat kredensial dan data multiple user secara terpusat dari users.json
dan mendukung environment variable overrides tanpa hardcode.
"""
import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_JSON_PATH = os.path.join(CURRENT_DIR, "users.json")


class UserDataProvider:
    """Class penyedia data kredensial multiple user untuk test automation."""

    _users = None

    @classmethod
    def load_users(cls):
        """Membaca data users dari file users.json."""
        if cls._users is None:
            if os.path.exists(USERS_JSON_PATH):
                with open(USERS_JSON_PATH, "r", encoding="utf-8-sig") as f:
                    cls._users = json.load(f)
            else:
                cls._users = {}

            # Override default super_admin via Config / environment variable sesuai env aktif (dev/prod)
            try:
                from config import Config
                env_user = Config.VALID_USER
                env_pass = Config.VALID_PASS
            except Exception:
                env_user = os.getenv("VALID_USER")
                env_pass = os.getenv("VALID_PASS")

            if "super_admin" in cls._users:
                if env_user:
                    cls._users["super_admin"]["username"] = env_user
                if env_pass:
                    cls._users["super_admin"]["password"] = env_pass
        return cls._users

    @classmethod
    def get_user(cls, key_or_role: str) -> dict:
        """Mengambil data user berdasarkan key (cth: 'super_admin', 'branch_manager', 'invalid_user')."""
        users = cls.load_users()
        if key_or_role in users:
            return users[key_or_role]
        for user_key, data in users.items():
            if data.get("role", "").lower() == key_or_role.lower():
                return data
        raise KeyError(f"User dengan identitas '{key_or_role}' tidak ditemukan di users.json")

    @classmethod
    def get_credentials(cls, key_or_role: str = "super_admin") -> tuple:
        """Mengembalikan pasangan tuple (username, password) untuk user tertentu."""
        user = cls.get_user(key_or_role)
        return user["username"], user["password"]

    @classmethod
    def get_super_admin(cls) -> dict:
        return cls.get_user("super_admin")

    @classmethod
    def get_invalid_user(cls) -> dict:
        return cls.get_user("invalid_user")

    @classmethod
    def get_wrong_password_user(cls) -> dict:
        return cls.get_user("wrong_password_user")

    @classmethod
    def get_sqli_payload(cls, variant: str = "classic") -> dict:
        return cls.get_user(f"sqli_{variant}_user")

    @classmethod
    def get_xss_payload(cls) -> dict:
        return cls.get_user("xss_payload_user")

    @classmethod
    def list_all_roles(cls) -> list:
        """Mendapatkan daftar semua peran/role yang tersedia."""
        return [data.get("role") for data in cls.load_users().values()]
