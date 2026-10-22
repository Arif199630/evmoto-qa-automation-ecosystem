"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - COMPREHENSIVE TEST DATASET (4 PILAR QA)
================================================================================
Aplikasi   : EvMoto Driver Dev (com.evmoto.driver.app)
Environment: Dev Golang (https://api-dev.evmoto.internal)
Kredensial : Nomor HP 81299990001 | PIN Bypass 1234
================================================================================
"""
from config.config import Config

DRIVER_ACTIVE_PHONE = Config.DRIVER_ACTIVE_PHONE
DRIVER_ACTIVE_PIN = Config.DRIVER_ACTIVE_PIN

# ==============================================================================
# 1. DATASET REGISTRASI DRIVER BARU (DRV_REGISTER)
# ==============================================================================
DRV_REG_DATA_POSITIVE_TRUE = {
    "TC_DRV_REG_PT_01": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi mitra baru armada ECGO Driver data lengkap tanpa referral",
        "is_ecgo": True,
        "plate_number": "B 1234 EVM",
        "referral_code": "",
        "expected_result": "DATA  YANG DIKIRIM BERHASIL"
    },
    "TC_DRV_REG_PT_02": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi mitra baru non-ECGO dengan kode referral dev (EVMOTODRV)",
        "is_ecgo": False,
        "plate_number": "D 5678 GO",
        "referral_code": "EVMOTODRV",
        "expected_result": "DATA  YANG DIKIRIM BERHASIL"
    },
    "TC_DRV_REG_PT_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi armada non-ECGO plat motor 1 digit (B 1 AA)",
        "is_ecgo": False,
        "plate_number": "B 1 AA",
        "referral_code": "",
        "expected_result": "DATA  YANG DIKIRIM BERHASIL"
    },
    "TC_DRV_REG_PT_04": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi armada ECGO plat motor 4 digit (B 9999 CAD)",
        "is_ecgo": True,
        "plate_number": "B 9999 CAD",
        "referral_code": "",
        "expected_result": "DATA  YANG DIKIRIM BERHASIL"
    },
    "TC_DRV_REG_PT_05": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi armada ECGO wilayah Jawa Barat / Bandung (D 1234 AB)",
        "is_ecgo": True,
        "plate_number": "D 1234 AB",
        "referral_code": "",
        "expected_result": "DATA  YANG DIKIRIM BERHASIL"
    },
    "TC_DRV_REG_PT_06": {
        "tag": "POSITIVE_TRUE",
        "description": "Registrasi armada non-ECGO wilayah Jawa Timur / Surabaya (L 5678 CD)",
        "is_ecgo": False,
        "plate_number": "L 5678 CD",
        "referral_code": "",
        "expected_result": "DATA  YANG DIKIRIM BERHASIL"
    },
    "TC_DRV_REG_PT_07": {
        "tag": "POSITIVE_TRUE",
        "description": "Navigasi kembali dari form pendaftaran driver ke layar login",
        "expected_result": "SUCCESS_NAVIGATE_BACK"
    }
}

DRV_REG_DATA_POSITIVE_FALSE = {
    "TC_DRV_REG_PF_01": {
        "tag": "POSITIVE_FALSE",
        "description": "Registrasi driver menggunakan plat motor yang sudah terdaftar aktif",
        "is_ecgo": True,
        "plate_number": "B 1234 EVM",
        "referral_code": "",
        "expected_error": "Nomor plat sudah terdaftar"
    },
    "TC_DRV_REG_PF_02": {
        "tag": "POSITIVE_FALSE",
        "description": "Registrasi driver menggunakan kode referral kadaluarsa",
        "is_ecgo": True,
        "plate_number": "B 9999 CAD",
        "referral_code": "EXPIRED99",
        "expected_error": "Kode referral tidak valid"
    },
    "TC_DRV_REG_PF_03": {
        "tag": "POSITIVE_FALSE",
        "description": "Pendaftaran submit tanpa mengunggah dokumen KTP dan STNK",
        "is_ecgo": True,
        "plate_number": "B 3333 XYZ",
        "referral_code": "",
        "expected_error": "Harap lengkapi seluruh dokumen persyaratan"
    },
    "TC_DRV_REG_PF_04": {
        "tag": "POSITIVE_FALSE",
        "description": "Pendaftaran dengan nomor plat duplikat milik driver ECGO aktif",
        "is_ecgo": False,
        "plate_number": "B 1234 EVM",
        "referral_code": "",
        "expected_error": "Plat nomor sudah terdaftar pada armada ECGO"
    }
}

DRV_REG_DATA_NEGATIVE_TRUE = {
    "TC_DRV_REG_NT_01": {
        "tag": "NEGATIVE_TRUE",
        "description": "Registrasi driver field nomor plat dikosongkan",
        "is_ecgo": True,
        "plate_number": "",
        "referral_code": "",
        "expected_warning": "Kolom wajib diisi"
    },
    "TC_DRV_REG_NT_02": {
        "tag": "NEGATIVE_TRUE",
        "description": "Registrasi driver format plat nomor tidak valid (hanya angka)",
        "is_ecgo": False,
        "plate_number": "12345",
        "referral_code": "",
        "expected_warning": "Format nomor plat tidak valid"
    },
    "TC_DRV_REG_NT_03": {
        "tag": "NEGATIVE_TRUE",
        "description": "Registrasi driver format plat nomor hanya huruf tanpa angka",
        "is_ecgo": True,
        "plate_number": "B ABC",
        "referral_code": "",
        "expected_warning": "Format nomor plat tidak valid"
    },
    "TC_DRV_REG_NT_04": {
        "tag": "NEGATIVE_TRUE",
        "description": "Registrasi driver plat nomor mengandung karakter simbol terlarang",
        "is_ecgo": False,
        "plate_number": "B 12@4 #$%",
        "referral_code": "",
        "expected_warning": "Format nomor plat tidak valid"
    },
    "TC_DRV_REG_NT_05": {
        "tag": "NEGATIVE_TRUE",
        "description": "Pendaftaran tanpa memilih salah satu radio button ECGO Driver",
        "expected_warning": "Pilih tipe driver terlebih dahulu"
    }
}

DRV_REG_DATA_NEGATIVE_FALSE = {
    "TC_DRV_REG_NF_01": {
        "tag": "NEGATIVE_FALSE",
        "description": "Security test SQL Injection pada kolom plat dan referral driver",
        "is_ecgo": True,
        "plate_number": "' OR '1'='1",
        "referral_code": "' OR '1'='1",
        "expected_behavior": "SAFE_SANITIZED"
    },
    "TC_DRV_REG_NF_02": {
        "tag": "NEGATIVE_FALSE",
        "description": "Security test Cross-Site Scripting (XSS) pada form driver",
        "is_ecgo": False,
        "plate_number": "<script>alert(1)</script>",
        "referral_code": "<img src=x onerror=alert(1)>",
        "expected_behavior": "SAFE_SANITIZED"
    },
    "TC_DRV_REG_NF_03": {
        "tag": "NEGATIVE_FALSE",
        "description": "Boundary Value Analysis panjang nomor plat ekstrem (35 karakter)",
        "is_ecgo": True,
        "plate_number": "B 123456789012345678901234567890 ABC",
        "referral_code": "",
        "expected_behavior": "TRUNCATED_OR_REJECTED"
    },
    "TC_DRV_REG_NF_04": {
        "tag": "NEGATIVE_FALSE",
        "description": "Input whitespace spasi murni pada seluruh kolom formulir registrasi",
        "is_ecgo": True,
        "plate_number": "    ",
        "referral_code": "   ",
        "expected_behavior": "TRIMMED_MANDATORY_ERROR"
    },
    "TC_DRV_REG_NF_05": {
        "tag": "NEGATIVE_FALSE",
        "description": "Rapid click button spamming pada tombol Kirim pendaftaran",
        "is_ecgo": True,
        "plate_number": "B 7777 RAC",
        "referral_code": "",
        "expected_behavior": "ANTI_RACE_SINGLE_SUBMIT"
    }
}

# ==============================================================================
# 2. DATASET LOGIN & AUTENTIKASI DRIVER (DRV_LOGIN)
# ==============================================================================
DRV_LOG_DATA_POSITIVE_TRUE = {
    "TC_DRV_LOG_PT_01": {
        "tag": "POSITIVE_TRUE",
        "description": "Login berhasil menggunakan nomor dev resmi 81299990001 dan OTP bypass 1234",
        "phone": DRIVER_ACTIVE_PHONE,
        "otp": DRIVER_ACTIVE_PIN,
        "expected_result": "SUCCESS_ENTER_HOME"
    },
    "TC_DRV_LOG_PT_02": {
        "tag": "POSITIVE_TRUE",
        "description": "Login berhasil variasi format awalan 0 (082100000000) dan OTP bypass 1234",
        "phone": f"0{DRIVER_ACTIVE_PHONE}",
        "otp": DRIVER_ACTIVE_PIN,
        "expected_result": "SUCCESS_ENTER_HOME"
    },
    "TC_DRV_LOG_PT_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Login berhasil variasi format internasional (+6281299990001) dan OTP 1234",
        "phone": f"+62{DRIVER_ACTIVE_PHONE}",
        "otp": DRIVER_ACTIVE_PIN,
        "expected_result": "SUCCESS_ENTER_HOME"
    },
    "TC_DRV_LOG_PT_04": {
        "tag": "POSITIVE_TRUE",
        "description": "Navigasi Hubungi CS WhatsApp dari layar login",
        "expected_result": "SUCCESS_OPEN_CS"
    },
    "TC_DRV_LOG_PT_05": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi alur Resend OTP (Kirim Ulang Kode) pada layar verifikasi",
        "phone": DRIVER_ACTIVE_PHONE,
        "expected_result": "SUCCESS_RESEND_OTP"
    },
    "TC_DRV_LOG_PT_06": {
        "tag": "POSITIVE_TRUE",
        "description": "Penanganan izin lokasi perangkat Android OS (While using the app)",
        "phone": DRIVER_ACTIVE_PHONE,
        "otp": DRIVER_ACTIVE_PIN,
        "expected_result": "LOCATION_GRANTED_SUCCESS"
    },
    "TC_DRV_LOG_PT_07": {
        "tag": "POSITIVE_TRUE",
        "description": "Penanganan izin notifikasi perangkat Android OS (Allow Notifications)",
        "phone": DRIVER_ACTIVE_PHONE,
        "otp": DRIVER_ACTIVE_PIN,
        "expected_result": "NOTIFICATION_GRANTED_SUCCESS"
    }
}

DRV_LOG_DATA_POSITIVE_FALSE = {
    "TC_DRV_LOG_PF_01": {
        "tag": "POSITIVE_FALSE",
        "description": "Login gagal menggunakan nomor HP driver yang belum terdaftar",
        "phone": "82998877665",
        "expected_popup": "Nomor driver belum terdaftar, silakan daftar terlebih dahulu."
    },
    "TC_DRV_LOG_PF_02": {
        "tag": "POSITIVE_FALSE",
        "description": "Peringatan akun sedang aktif di perangkat lain (Multiple Session)",
        "phone": DRIVER_ACTIVE_PHONE,
        "expected_popup": "Anda sedang Login di perangkat lain"
    },
    "TC_DRV_LOG_PF_03": {
        "tag": "POSITIVE_FALSE",
        "description": "Tombol Join Sekarang tetap nonaktif saat nomor HP < 8 digit (7 digit: 8123456)",
        "phone": "8123456",
        "expected_behavior": "BUTTON_JOIN_DISABLED"
    },
    "TC_DRV_LOG_PF_04": {
        "tag": "POSITIVE_FALSE",
        "description": "Tombol Kirimkan Kode OTP nonaktif selama countdown timer berjalan",
        "phone": DRIVER_ACTIVE_PHONE,
        "expected_behavior": "RESEND_DISABLED_COUNTDOWN"
    },
    "TC_DRV_LOG_PF_05": {
        "tag": "POSITIVE_FALSE",
        "description": "Percobaan input OTP salah berulang kali (Rate Limiting Security)",
        "phone": DRIVER_ACTIVE_PHONE,
        "otp_wrong": "0000",
        "expected_behavior": "RATE_LIMIT_WARNING"
    }
}

DRV_LOG_DATA_NEGATIVE_TRUE = {
    "TC_DRV_LOG_NT_01": {
        "tag": "NEGATIVE_TRUE",
        "description": "Login gagal menggunakan kode OTP salah (9999, bukan 1234)",
        "phone": DRIVER_ACTIVE_PHONE,
        "otp_wrong": "9999",
        "expected_error": "Kode verifikasi salah"
    },
    "TC_DRV_LOG_NT_02": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input kode OTP incomplete (kurang dari 4 digit: 12)",
        "phone": DRIVER_ACTIVE_PHONE,
        "otp_wrong": "12",
        "expected_behavior": "OTP_INCOMPLETE_REJECT"
    },
    "TC_DRV_LOG_NT_03": {
        "tag": "NEGATIVE_TRUE",
        "description": "Field nomor handphone dikosongkan dan menekan Join Sekarang",
        "phone": "",
        "expected_behavior": "BUTTON_DISABLED_EMPTY"
    },
    "TC_DRV_LOG_NT_04": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input nomor handphone terlalu pendek (3 digit: 812)",
        "phone": "812",
        "expected_behavior": "BUTTON_JOIN_DISABLED"
    },
    "TC_DRV_LOG_NT_05": {
        "tag": "NEGATIVE_TRUE",
        "description": "Pembatalan input OTP melalui tombol kembali (Back Button)",
        "phone": DRIVER_ACTIVE_PHONE,
        "expected_result": "RETURN_TO_LOGIN_SCREEN"
    },
    "TC_DRV_LOG_NT_06": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input nomor diawali format tidak valid selain angka 0/8/+62 (misal: 123456789)",
        "phone": "123456789",
        "expected_behavior": "INVALID_PHONE_PREFIX"
    }
}

DRV_LOG_DATA_NEGATIVE_FALSE = {
    "TC_DRV_LOG_NF_01": {
        "tag": "NEGATIVE_FALSE",
        "description": "Uji keamanan SQL Injection pada kolom login nomor telepon",
        "phone": "' OR '1'='1",
        "expected_behavior": "REJECT_INVALID_PHONE_FORMAT"
    },
    "TC_DRV_LOG_NF_02": {
        "tag": "NEGATIVE_FALSE",
        "description": "Uji keamanan SQL Injection tautologi (UNION SELECT)",
        "phone": "81299990001' UNION SELECT NULL--",
        "expected_behavior": "REJECT_INVALID_PHONE_FORMAT"
    },
    "TC_DRV_LOG_NF_03": {
        "tag": "NEGATIVE_FALSE",
        "description": "Uji keamanan XSS script injection pada kolom login telepon",
        "phone": "<script>alert('xss')</script>",
        "expected_behavior": "FILTER_NON_NUMERIC"
    },
    "TC_DRV_LOG_NF_04": {
        "tag": "NEGATIVE_FALSE",
        "description": "Boundary Value Analysis digit nomor telepon ekstrem (25 digit)",
        "phone": "8129999000112345678901234",
        "expected_behavior": "TRUNCATED_TO_MAX_LENGTH"
    },
    "TC_DRV_LOG_NF_05": {
        "tag": "NEGATIVE_FALSE",
        "description": "Filtering karakter huruf alfabet dan simbol pada kolom nomor HP",
        "phone": "821-ABCD-EFGH!@#",
        "expected_behavior": "NUMERIC_ONLY_FILTERED"
    },
    "TC_DRV_LOG_NF_06": {
        "tag": "NEGATIVE_FALSE",
        "description": "Rapid click button spamming pada tombol Join Sekarang",
        "phone": DRIVER_ACTIVE_PHONE,
        "expected_behavior": "NO_CRASH_ANTI_RACE"
    }
}

# ==============================================================================
# 3. DATASET BERANDA & STATUS KERJA (DRV_HOME)
# ==============================================================================
DRV_HOME_DATA_POSITIVE_TRUE = {
    "TC_DRV_HOME_PT_01": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi komponen utama Beranda Driver (Header, Saldo, Metrik Pesanan)",
        "expected_elements": ["Beranda", "Saldo Kamu", "Total Pendapatan", "Pesanan Hari Ini"]
    },
    "TC_DRV_HOME_PT_02": {
        "tag": "POSITIVE_TRUE",
        "description": "Toggle status kerja driver dari Offline menjadi Online",
        "expected_status": "Online"
    },
    "TC_DRV_HOME_PT_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Toggle status kerja driver dari Online kembali ke Offline",
        "expected_status": "Offline"
    },
    "TC_DRV_HOME_PT_04": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi persistensi status kerja Online setelah app restart / resume",
        "expected_status": "Online"
    },
    "TC_DRV_HOME_PT_05": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi kartu Saldo Kamu menampilkan angka nominal mata uang Rp",
        "expected_label": "Saldo Kamu"
    },
    "TC_DRV_HOME_PT_06": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi kartu ringkasan Total Pendapatan aktif",
        "expected_label": "Total Pendapatan"
    },
    "TC_DRV_HOME_PT_07": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi kartu metrik performa Pesanan Hari Ini",
        "expected_label": "Pesanan Hari Ini"
    },
    "TC_DRV_HOME_PT_08": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi kartu metrik performa Pesanan Bulan Ini",
        "expected_label": "Pesanan Bulan Ini"
    },
    "TC_DRV_HOME_PT_09": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi kartu rating pengemudi Rating Saya",
        "expected_label": "Rating Saya"
    },
    "TC_DRV_HOME_PT_10": {
        "tag": "POSITIVE_TRUE",
        "description": "Fitur Muat Ulang (Refresh) Beranda Driver",
        "expected_result": "SUCCESS_REFRESH"
    },
    "TC_DRV_HOME_PT_11": {
        "tag": "POSITIVE_TRUE",
        "description": "Perpindahan Tab Pesanan Reguler dan Pesanan Terjadwal",
        "expected_tabs": ["Pesanan Reguler", "Pesanan Terjadwal"]
    },
    "TC_DRV_HOME_PT_12": {
        "tag": "POSITIVE_TRUE",
        "description": "Navigasi ke Tab Pesanan Berjalan saat driver sedang ada tugas",
        "expected_tab": "Pesanan Berjalan"
    },
    "TC_DRV_HOME_PT_13": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi badge overlay Order Dihalaman Depan Aktif",
        "expected_badge": "Order Dihalaman Depan Aktif"
    },
    "TC_DRV_HOME_PT_14": {
        "tag": "POSITIVE_TRUE",
        "description": "Navigasi tautan Lihat Aktivitas Saya ke riwayat pesanan",
        "expected_target": "Aktivitas Saya"
    },
    "TC_DRV_HOME_PT_15": {
        "tag": "POSITIVE_TRUE",
        "description": "Navigasi antar tab Bottom Navigation Bar (Beranda <-> Aktivitas <-> Menu)",
        "expected_tabs": ["Beranda", "Aktivitas", "Menu"]
    }
}

DRV_HOME_DATA_BUSINESS_LOGIC = {
    "TC_DRV_HOME_BL_01": {
        "tag": "POSITIVE_FALSE",
        "description": "Deteksi driver berada di luar Working Area",
        "expected_warning": "Saat ini anda berada diluar dari Working Area yang tersedia."
    },
    "TC_DRV_HOME_BL_02": {
        "tag": "POSITIVE_FALSE",
        "description": "Auto offline saat berada di luar Working Area",
        "expected_snackbar": "Saat ini anda berada diluar dari Working Area. Status Anda akan offline."
    },
    "TC_DRV_HOME_BL_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi pop-up Area Guarantee Income (GI) dan kriteria operasional",
        "dialog_title": "Area Guarantee Income",
        "expected_terms": ["Online di Jam Operasional", "Tidak Cancel/Reject Order"]
    },
    "TC_DRV_HOME_BL_04": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi aksi tombol Arahkan pada pop-up Area Guarantee Income",
        "expected_button": "Arahkan"
    },
    "TC_DRV_HOME_BL_05": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi aksi tombol Lihat Detail pada modal Guarantee Income",
        "expected_button": "Lihat Detail"
    },
    "TC_DRV_HOME_BL_06": {
        "tag": "POSITIVE_TRUE",
        "description": "Penutupan modal dialog Guarantee Income via tombol Tutup / Dismiss",
        "expected_behavior": "MODAL_DISMISSED"
    },
    "TC_DRV_HOME_BL_07": {
        "tag": "POSITIVE_FALSE",
        "description": "Pemberitahuan Jam Operasional layanan saat driver online di luar jam operasional",
        "expected_title": "Pemberitahuan Jam Operasional",
        "expected_desc": "Saat ini layanan mengikuti jam operasional yang berlaku."
    },
    "TC_DRV_HOME_BL_08": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi notifikasi in-app update Versi Terbaru Telah Tersedia",
        "expected_title": "Versi Terbaru Telah Tersedia"
    },
    "TC_DRV_HOME_BL_09": {
        "tag": "POSITIVE_FALSE",
        "description": "Verifikasi dialog pembaruan wajib (Force Update) Update Sekarang",
        "expected_title": "Update Sekarang"
    },
    "TC_DRV_HOME_BL_10": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi banner tips Semangat & Semoga lain kali lebih beruntung",
        "expected_text": "Semoga lain kali lebih beruntung!"
    }
}

DRV_HOME_DATA_NEGATIVE_FALSE = {
    "TC_DRV_HOME_NF_01": {
        "tag": "NEGATIVE_FALSE",
        "description": "Rapid toggle Online/Offline anti-race condition stress test (5x berturut-turut)",
        "expected_behavior": "NO_DEADLOCK_SMOOTH_SWITCH"
    },
    "TC_DRV_HOME_NF_02": {
        "tag": "NEGATIVE_FALSE",
        "description": "Rapid click pemicu Muat Ulang (Refresh spamming) anti-crash",
        "expected_behavior": "NO_CRASH_DEBOUNCED"
    },
    "TC_DRV_HOME_NF_03": {
        "tag": "NEGATIVE_FALSE",
        "description": "Boundary display nominal saldo bernilai 0 rupiah (Rp 0)",
        "expected_format": "Rp 0"
    },
    "TC_DRV_HOME_NF_04": {
        "tag": "NEGATIVE_FALSE",
        "description": "Boundary display saldo bernilai puluhan juta rupiah (Rp 50.000.000)",
        "expected_format": "Rp 50.000.000"
    },
    "TC_DRV_HOME_NF_05": {
        "tag": "NEGATIVE_FALSE",
        "description": "Stabilitas background location tracking saat aplikasi di-minimize",
        "expected_behavior": "SERVICE_RUNNING_SAFE"
    }
}

# ==============================================================================
# 4. DATASET MENU & PENGATURAN AKUN (DRV_MENU)
# ==============================================================================
DRV_MENU_DATA_POSITIVE_TRUE = {
    "TC_DRV_MENU_PT_01": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi header Menu dan identitas profil driver aktif",
        "expected_title": "Menu"
    },
    "TC_DRV_MENU_PT_02": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses sub-menu Kelola Akun dan deskripsi panduan",
        "expected_title": "Kelola Akun"
    },
    "TC_DRV_MENU_PT_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Toggle izin overlay Izinkan Order di Layar Utama",
        "expected_menu": "Izinkan Order di Layar Utama"
    },
    "TC_DRV_MENU_PT_04": {
        "tag": "POSITIVE_TRUE",
        "description": "Pembersihan cache aplikasi (Clear Cache) dan verifikasi snackbar",
        "expected_snackbar": "Berhasil membersihkan cache"
    },
    "TC_DRV_MENU_PT_05": {
        "tag": "POSITIVE_TRUE",
        "description": "Penggantian bahasa aplikasi ke English dan verifikasi",
        "lang_code": "en",
        "expected_snackbar": "Berhasil mengganti bahasa"
    },
    "TC_DRV_MENU_PT_06": {
        "tag": "POSITIVE_TRUE",
        "description": "Penggantian bahasa aplikasi ke 當代中文 (Chinese) dan verifikasi",
        "lang_code": "cn",
        "expected_snackbar": "Berhasil mengganti bahasa"
    },
    "TC_DRV_MENU_PT_07": {
        "tag": "POSITIVE_TRUE",
        "description": "Pengembalian bahasa aplikasi ke Bahasa Indonesia",
        "lang_code": "id",
        "expected_snackbar": "Berhasil mengganti bahasa"
    },
    "TC_DRV_MENU_PT_08": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses Panduan Cara Penggunaan Aplikasi (Langkah Mudah Menggunakan Aplikasi)",
        "expected_title": "Cara Penggunaan Aplikasi"
    },
    "TC_DRV_MENU_PT_09": {
        "tag": "POSITIVE_TRUE",
        "description": "Membaca panduan Tips untuk Driver (Koneksi stabil & latar belakang)",
        "expected_content": "Tips untuk Driver"
    },
    "TC_DRV_MENU_PT_10": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses menu informasi Tentang Kami (About Us)",
        "expected_menu": "Tentang Kami"
    },
    "TC_DRV_MENU_PT_11": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses menu Pengaturan Jaringan & konektivitas",
        "expected_menu": "Pengaturan Jaringan"
    },
    "TC_DRV_MENU_PT_12": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses menu Pengaturan Lainnya pada aplikasi driver",
        "expected_menu": "Pengaturan Lainnya"
    }
}

DRV_MENU_DATA_ACCOUNT_LIFECYCLE = {
    "TC_DRV_MENU_AL_01": {
        "tag": "POSITIVE_FALSE",
        "description": "Pembatalan konfirmasi Logout akun (Batal Keluar)",
        "expected_dialog": "Yakin Ingin Keluar Dari Akun?"
    },
    "TC_DRV_MENU_AL_02": {
        "tag": "POSITIVE_TRUE",
        "description": "Konfirmasi Logout akun driver hingga kembali ke Layar Login",
        "expected_screen": "Hai, Yuk Join Sekarang"
    },
    "TC_DRV_MENU_AL_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi dialog loading Sedang Memproses Keluar saat logout",
        "expected_loading": "Sedang Memproses Keluar"
    },
    "TC_DRV_MENU_AL_04": {
        "tag": "POSITIVE_FALSE",
        "description": "Pembatalan pengajuan Hapus Akun driver (Batal Hapus)",
        "expected_dialog": "Yakin Ingin Mengajukan Penghapusan Akun?"
    },
    "TC_DRV_MENU_AL_05": {
        "tag": "NEGATIVE_TRUE",
        "description": "Verifikasi klausul kewajiban pada dialog konfirmasi Hapus Akun",
        "expected_terms": "Penghapusan akun driver akan diproses setelah seluruh kewajiban diselesaikan."
    },
    "TC_DRV_MENU_AL_06": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi layar verifikasi OTP penghapusan akun Masukkan Kode OTP",
        "expected_title": "Masukkan Kode OTP"
    }
}

# ==============================================================================
# 5. DATASET EWALLET ECGO & TARIK DANA (DRV_WALLET)
# ==============================================================================
DRV_WALLET_DATA_POSITIVE_TRUE = {
    "TC_DRV_WAL_PT_01": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi tampilan utama modul eWallet: Saldo EVMoto dan Saldo ECGO",
        "expected_cards": ["Saldo EVMoto", "Saldo ECGO"]
    },
    "TC_DRV_WAL_PT_02": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi indikator status hubungan armada ECGO (Terhubung / Belum Terhubung)",
        "expected_labels": ["Terhubung dengan ECGO", "Belum Terhubung"]
    },
    "TC_DRV_WAL_PT_03": {
        "tag": "POSITIVE_TRUE",
        "description": "Membuka modal panduan Hubungkan EVMoto dengan ECGO",
        "expected_title": "Hubungkan EVMoto dengan ECGO"
    },
    "TC_DRV_WAL_PT_04": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi 3 klausul transparansi pemindahan saldo ECGO tanpa biaya tambahan",
        "expected_clauses": [
            "Seluruh saldo tetap menjadi milik Anda",
            "Transaksi tidak memiliki biaya tambahan",
            "Bisa diputus kapan saja"
        ]
    },
    "TC_DRV_WAL_PT_05": {
        "tag": "POSITIVE_TRUE",
        "description": "Alur sukses menghubungkan eWallet hingga modal Berhasil Di Hubungkan",
        "expected_modal": "Berhasil Di Hubungkan"
    },
    "TC_DRV_WAL_PT_06": {
        "tag": "POSITIVE_TRUE",
        "description": "Membuka dialog konfirmasi Putuskan eWallet ECGO",
        "expected_dialog": "Putuskan eWallet"
    },
    "TC_DRV_WAL_PT_07": {
        "tag": "POSITIVE_TRUE",
        "description": "Konfirmasi pemutusan eWallet (Ya, Putuskan) dan verifikasi sukses",
        "expected_snackbar": "Berhasil memutuskan hubungan eWallet ECGO."
    },
    "TC_DRV_WAL_PT_08": {
        "tag": "POSITIVE_TRUE",
        "description": "Membuka menu Pengaturan Otomatis transfer saldo",
        "expected_title": "Pengaturan Otomatis"
    },
    "TC_DRV_WAL_PT_09": {
        "tag": "POSITIVE_TRUE",
        "description": "Mengaktifkan pemicu otomatis Saat Tagihan Jatuh Tempo",
        "trigger": "Saat Tagihan Jatuh Tempo"
    },
    "TC_DRV_WAL_PT_10": {
        "tag": "POSITIVE_TRUE",
        "description": "Mengaktifkan pemicu otomatis Saat Guarantee Income Cair",
        "trigger": "Saat Guarantee Income Cair"
    },
    "TC_DRV_WAL_PT_11": {
        "tag": "POSITIVE_TRUE",
        "description": "Mengaktifkan pemicu otomatis Setiap Orderan Selesai",
        "trigger": "Setiap Orderan Selesai"
    },
    "TC_DRV_WAL_PT_12": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses menu Kirimkan Saldo (Saldo EVMoto -> Saldo ECGO)",
        "expected_title": "Kirimkan Saldo"
    },
    "TC_DRV_WAL_PT_13": {
        "tag": "POSITIVE_TRUE",
        "description": "Kirim saldo nominal valid Rp 50.000 hingga modal Pengiriman Saldo Berhasil",
        "amount": "50000",
        "expected_modal": "Pengiriman Saldo Berhasil"
    },
    "TC_DRV_WAL_PT_14": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses menu Bayar Tagihan dan verifikasi rincian tagihan hari ini",
        "expected_title": "Bayar Tagihan"
    },
    "TC_DRV_WAL_PT_15": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi fitur Pilih Semua Tagihan pada daftar tagihan ECGO",
        "expected_action": "Pilih Semua Tagihan"
    },
    "TC_DRV_WAL_PT_16": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses layar Tarik Dana dan periksa Saldo Aktif Saya",
        "expected_title": "Tarik Dana"
    },
    "TC_DRV_WAL_PT_17": {
        "tag": "POSITIVE_TRUE",
        "description": "Verifikasi informasi minimal penarikan dan kebijakan biaya admin bank",
        "expected_info": ["Minimal penarikan", "Biaya admin mengikuti kebijakan bank"]
    },
    "TC_DRV_WAL_PT_18": {
        "tag": "POSITIVE_TRUE",
        "description": "Pengajuan Tarik Dana nominal valid Rp 100.000 ke rekening tersimpan",
        "amount": "100000",
        "expected_snackbar": "Berhasil pengajuan penarikan dana"
    },
    "TC_DRV_WAL_PT_19": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses sub-menu Nomor Rekening Tersimpan",
        "expected_title": "Nomor Rekening Tersimpan"
    },
    "TC_DRV_WAL_PT_20": {
        "tag": "POSITIVE_TRUE",
        "description": "Penambahan rekening bank BCA baru dan verifikasi snackbar",
        "bank_name": "BCA",
        "account_number": "0123456789",
        "owner_name": "QA DRIVER BCA",
        "expected_snackbar": "Berhasil menambah rekening penarikan"
    },
    "TC_DRV_WAL_PT_21": {
        "tag": "POSITIVE_TRUE",
        "description": "Penambahan rekening bank Mandiri baru",
        "bank_name": "Mandiri",
        "account_number": "1370012345678",
        "owner_name": "QA DRIVER MANDIRI",
        "expected_snackbar": "Berhasil menambah rekening penarikan"
    },
    "TC_DRV_WAL_PT_22": {
        "tag": "POSITIVE_TRUE",
        "description": "Edit ubah nama pemilik rekening pada rekening tersimpan",
        "owner_name_new": "QA DRIVER REVISED",
        "expected_snackbar": "Berhasil mengubah rekening penarikan"
    },
    "TC_DRV_WAL_PT_23": {
        "tag": "POSITIVE_TRUE",
        "description": "Batal hapus rekening (Batal) menjaga rekening tetap tersimpan",
        "expected_behavior": "ACCOUNT_RETAINED"
    },
    "TC_DRV_WAL_PT_24": {
        "tag": "POSITIVE_TRUE",
        "description": "Konfirmasi Hapus rekening tersimpan dan verifikasi snackbar",
        "expected_snackbar": "Berhasil menghapus nomor rekening"
    },
    "TC_DRV_WAL_PT_25": {
        "tag": "POSITIVE_TRUE",
        "description": "Akses layar Riwayat Tarik Dana dan tab Seluruh Riwayat",
        "expected_title": "Riwayat Tarik Dana"
    }
}

DRV_WALLET_DATA_BUSINESS_LOGIC = {
    "TC_DRV_WAL_BL_01": {
        "tag": "POSITIVE_FALSE",
        "description": "Pengajuan Tarik Dana melebihi saldo aktif (Insufficent Balance)",
        "amount": "99999999",
        "expected_error": "Saldo tidak mencukupi"
    },
    "TC_DRV_WAL_BL_02": {
        "tag": "POSITIVE_FALSE",
        "description": "Pengajuan Tarik Dana di bawah batas minimum penarikan (misal: Rp 5.000)",
        "amount": "5000",
        "expected_snackbar": "Minimum penarikan dana"
    },
    "TC_DRV_WAL_BL_03": {
        "tag": "POSITIVE_FALSE",
        "description": "Kirimkan Saldo di bawah ambang batas minimal nominal pengiriman",
        "amount": "1000",
        "expected_error": "Nominal pengiriman saldo di bawah minimum"
    },
    "TC_DRV_WAL_BL_04": {
        "tag": "POSITIVE_FALSE",
        "description": "Penambahan nomor rekening bank yang sudah tersimpan (Duplikat)",
        "account_number": "0123456789",
        "expected_error": "Nomor rekening sudah terdaftar"
    },
    "TC_DRV_WAL_BL_05": {
        "tag": "POSITIVE_FALSE",
        "description": "Tampilan kondisi kosong (Empty State) Belum Ada Nomor Rekening",
        "expected_empty": "Belum Ada Nomor Rekening"
    }
}

DRV_WALLET_DATA_NEGATIVE_TRUE = {
    "TC_DRV_WAL_NT_01": {
        "tag": "NEGATIVE_TRUE",
        "description": "Submit Tarik Dana dengan nominal kosong",
        "amount": "",
        "expected_snackbar": "Harap mengisi nominal penarikan dana"
    },
    "TC_DRV_WAL_NT_02": {
        "tag": "NEGATIVE_TRUE",
        "description": "Tambah rekening baru dengan nomor rekening kosong",
        "account_number": "",
        "owner_name": "QA EMPTY NO",
        "expected_warning": "Nomor rekening wajib diisi"
    },
    "TC_DRV_WAL_NT_03": {
        "tag": "NEGATIVE_TRUE",
        "description": "Tambah rekening baru dengan nama pemilik kosong",
        "account_number": "1234567890",
        "owner_name": "",
        "expected_warning": "Nama pemilik rekening wajib diisi"
    },
    "TC_DRV_WAL_NT_04": {
        "tag": "NEGATIVE_TRUE",
        "description": "Input nomor rekening bank menggunakan karakter huruf atau simbol",
        "account_number": "1234-ABCD-!@#",
        "expected_warning": "Nomor rekening hanya boleh berisi angka"
    }
}

DRV_WALLET_DATA_NEGATIVE_FALSE = {
    "TC_DRV_WAL_NF_01": {
        "tag": "NEGATIVE_FALSE",
        "description": "Security test SQL Injection pada kolom nomor rekening penarikan",
        "account_number": "' OR '1'='1",
        "owner_name": "Hacker ' OR '1'='1",
        "expected_behavior": "SAFE_REJECTED"
    },
    "TC_DRV_WAL_NF_02": {
        "tag": "NEGATIVE_FALSE",
        "description": "Security test XSS script injection pada kolom nama pemilik rekening",
        "account_number": "9876543210",
        "owner_name": "<script>alert('xss')</script>",
        "expected_behavior": "SANITIZED_SAFE"
    },
    "TC_DRV_WAL_NF_03": {
        "tag": "NEGATIVE_FALSE",
        "description": "Rapid double click / button spamming tombol Konfirmasi Penarikan Dana",
        "amount": "50000",
        "expected_behavior": "ATOMIC_TRANSACTION_SINGLE_DEDUCTION"
    }
}

# ==============================================================================
# 6. DATASET AKTIVITAS SAYA & GUARANTEE INCOME (DRV_ACTIVITY)
# ==============================================================================
DRV_ACT_DATA_POSITIVE_TRUE = {
    "TC_DRV_ACT_PT_01": {"tag": "POSITIVE_TRUE", "description": "Akses tab Aktivitas Saya melalui Bottom Navigation Bar"},
    "TC_DRV_ACT_PT_02": {"tag": "POSITIVE_TRUE", "description": "Beralih ke Tab Guarantee Income (GI) dari layar Aktivitas"},
    "TC_DRV_ACT_PT_03": {"tag": "POSITIVE_TRUE", "description": "Verifikasi kartu TOTAL GUARANTEE INCOME pada dashboard GI"},
    "TC_DRV_ACT_PT_04": {"tag": "POSITIVE_TRUE", "description": "Verifikasi rate nominal Guarantee Income/Hour (*Per jam Rp 30.000)"},
    "TC_DRV_ACT_PT_05": {"tag": "POSITIVE_TRUE", "description": "Verifikasi kartu Total Akumulasi Guarantee Income driver"},
    "TC_DRV_ACT_PT_06": {"tag": "POSITIVE_TRUE", "description": "Verifikasi kartu Net Payment of Guarantee yang siap dicairkan"},
    "TC_DRV_ACT_PT_07": {"tag": "POSITIVE_TRUE", "description": "Verifikasi rincian komponen Dipotong dari Guarantee Income"},
    "TC_DRV_ACT_PT_08": {"tag": "POSITIVE_TRUE", "description": "Verifikasi label jam operasional jaminan pendapatan (Periode: 06:00 - 22:00)"},
    "TC_DRV_ACT_PT_09": {"tag": "POSITIVE_TRUE", "description": "Verifikasi timer hitung mundur Sisa waktu jaminan hari ini"},
    "TC_DRV_ACT_PT_10": {"tag": "POSITIVE_TRUE", "description": "Verifikasi timer Sisa waktu kembali ke area saat melintasi batas zona"},
    "TC_DRV_ACT_PT_11": {"tag": "POSITIVE_TRUE", "description": "Verifikasi notice batas waktu kembali dihitung durasi terakhir + 20%"},
    "TC_DRV_ACT_PT_12": {"tag": "POSITIVE_TRUE", "description": "Verifikasi snackbar konfirmasi 'Anda telah memasuki wilayah Gurantee Income'"},
    "TC_DRV_ACT_PT_13": {"tag": "POSITIVE_TRUE", "description": "Verifikasi snackbar peringatan 'Anda telah keluar wilayah Gurantee Income'"},
    "TC_DRV_ACT_PT_14": {"tag": "POSITIVE_TRUE", "description": "Membuka daftar riwayat Guarantee Income Hari Ini"},
    "TC_DRV_ACT_PT_15": {"tag": "POSITIVE_TRUE", "description": "Verifikasi badge status GI 'Sudah Dibayarkan'"},
    "TC_DRV_ACT_PT_16": {"tag": "POSITIVE_TRUE", "description": "Verifikasi badge status GI 'Menunggu Konfirmasi'"},
    "TC_DRV_ACT_PT_17": {"tag": "POSITIVE_TRUE", "description": "Mengetuk tombol Lihat Detail pada kartu riwayat pencairan GI"},
    "TC_DRV_ACT_PT_18": {"tag": "POSITIVE_TRUE", "description": "Beralih ke Tab Riwayat Pendapatan (Revenue Summary)"},
    "TC_DRV_ACT_PT_19": {"tag": "POSITIVE_TRUE", "description": "Verifikasi kartu ringkasan Pendapatan driver dan Yang didapatkan driver"},
    "TC_DRV_ACT_PT_20": {"tag": "POSITIVE_TRUE", "description": "Verifikasi klausul potongan Platform Fee (10% dari total biaya jarak tempuh)"},
    "TC_DRV_ACT_PT_21": {"tag": "POSITIVE_TRUE", "description": "Verifikasi komponen Biaya promo yang disubsidi sistem"},
    "TC_DRV_ACT_PT_22": {"tag": "POSITIVE_TRUE", "description": "Verifikasi pembukuan Perubahan saldo (Saldo sebelum vs Saldo sesudah)"},
    "TC_DRV_ACT_PT_23": {"tag": "POSITIVE_TRUE", "description": "Beralih ke Tab Riwayat Referral Income"},
    "TC_DRV_ACT_PT_24": {"tag": "POSITIVE_TRUE", "description": "Verifikasi ringkasan komisi referral Per Register"},
    "TC_DRV_ACT_PT_25": {"tag": "POSITIVE_TRUE", "description": "Mengetuk tombol Bagikan kode referral ke media sosial / chat"}
}

DRV_ACT_DATA_BUSINESS_LOGIC = {
    "TC_DRV_ACT_BL_01": {"tag": "BUSINESS_LOGIC", "description": "Formula Net Payment: GI Payout = Guarantee Target - Order Income"},
    "TC_DRV_ACT_BL_02": {"tag": "BUSINESS_LOGIC", "description": "Net payment terkunci Rp 0 jika order income mitra melampaui target jaminan"},
    "TC_DRV_ACT_BL_03": {"tag": "BUSINESS_LOGIC", "description": "Penolakan pencairan GI jika jam online kurang dari batas minimum operasional"},
    "TC_DRV_ACT_BL_04": {"tag": "BUSINESS_LOGIC", "description": "Penolakan klaim GI saat status GPS terdeteksi di luar Working Area aktif"},
    "TC_DRV_ACT_BL_05": {"tag": "BUSINESS_LOGIC", "description": "Hangusnya jaminan pendapatan saat batas waktu kembali ke area terlampaui"}
}

DRV_ACT_DATA_NEGATIVE_TRUE = {
    "TC_DRV_ACT_NT_01": {"tag": "NEGATIVE_TRUE", "description": "Empty state 'Anda belum memiliki pendapatan Guarantee Income pada hari ini'"},
    "TC_DRV_ACT_NT_02": {"tag": "NEGATIVE_TRUE", "description": "Empty state 'Belum Ada Riwayat' pada ringkasan pendapatan"},
    "TC_DRV_ACT_NT_03": {"tag": "NEGATIVE_TRUE", "description": "Empty state 'Belum Ada Riwayat Referral' saat belum ada downline"},
    "TC_DRV_ACT_NT_04": {"tag": "NEGATIVE_TRUE", "description": "Filter riwayat dengan input range tanggal masa depan"},
    "TC_DRV_ACT_NT_05": {"tag": "NEGATIVE_TRUE", "description": "Akses detail transaksi yang belum diproses oleh backend"}
}

DRV_ACT_DATA_NEGATIVE_FALSE = {
    "TC_DRV_ACT_NF_01": {"tag": "NEGATIVE_FALSE", "description": "Security test SQL Injection pada kolom pencarian riwayat pendapatan"},
    "TC_DRV_ACT_NF_02": {"tag": "NEGATIVE_FALSE", "description": "Security test XSS script injection pada payload referral sharing"},
    "TC_DRV_ACT_NF_03": {"tag": "NEGATIVE_FALSE", "description": "Rapid multi-tab switching antara GI, Pendapatan, dan Referral"},
    "TC_DRV_ACT_NF_04": {"tag": "NEGATIVE_FALSE", "description": "Penanganan lonjakan sinyal GPS (GPS jitter / mock location)"},
    "TC_DRV_ACT_NF_05": {"tag": "NEGATIVE_FALSE", "description": "Ketahanan aplikasi saat sinyal internet drop ketika memuat revenue"}
}


# ==============================================================================
# 8. DATASET DRIVER SEWA DAN HUBUNGKAN AKUN (CICILAN ECGO DAN ORPHAN MOTOR)
# ==============================================================================
DRV_RENTAL_DATA_FUNCTIONAL = {
    "TC_DRV_RENT_F_01": {
        "tag": "POSITIVE_TRUE",
        "tc_id": "TC_DRV_RENT_F_01",
        "description": "Fresh Driver: Driver baru pertama kali login, verifikasi empty state kendaraan dan toggle Hubungkan Akun OFF",
        "initial_vehicle": None,
        "expected_toggle": "OFF",
        "expected_result": "Saat ini belum tersedia kendaraan"
    },
    "TC_DRV_RENT_F_02": {
        "tag": "POSITIVE_TRUE",
        "tc_id": "TC_DRV_RENT_F_02",
        "description": "Existing Driver tanpa motor: Menautkan motor sewa ECGO perdana dan aktivasi toggle Hubungkan Akun",
        "plate_number": "B 3456 EVM",
        "is_ecgo_rental": True,
        "expected_result": "Berhasil Di Hubungkan"
    },
    "TC_DRV_RENT_F_03": {
        "tag": "POSITIVE_TRUE",
        "tc_id": "TC_DRV_RENT_F_03",
        "description": "Ganti motor beda plat: Motor lama menjadi status Orphan (No Soft-Delete) dan motor baru aktif",
        "old_plate": "B 3456 EVM",
        "new_plate": "B 7890 EC",
        "expected_old_status": "ORPHAN",
        "expected_result": "Berhasil mengubah kendaraan"
    },
    "TC_DRV_RENT_F_04": {
        "tag": "POSITIVE_TRUE",
        "tc_id": "TC_DRV_RENT_F_04",
        "description": "Link akun plat sama: Driver dengan motor aktif menautkan akun cicilan pada unit yang sedang dikendarai",
        "plate_number": "B 7890 EC",
        "expected_result": "Status Akun Terhubung dengan Program Cicilan ECGO"
    },
    "TC_DRV_RENT_F_05": {
        "tag": "POSITIVE_TRUE",
        "tc_id": "TC_DRV_RENT_F_05",
        "description": "Re-assignment motor Orphan: Unit lama yang berstatus Orphan berhasil dialokasikan ke Driver penerima baru",
        "orphan_plate": "B 3456 EVM",
        "new_driver_phone": "081298765432",
        "expected_result": "Unit Orphan berhasil di-reassign ke mitra baru tanpa kehilangan riwayat armada"
    },
    "TC_DRV_RENT_F_06": {
        "tag": "POSITIVE_TRUE",
        "tc_id": "TC_DRV_RENT_F_06",
        "description": "Validasi Toggle One-Way: Setelah status ON, toggle terkunci/disabled dan driver diblokir untuk memutus sepihak",
        "toggle_action": "ATTEMPT_UNLINK",
        "expected_result": "Switch terkunci disabled dan muncul dialog pencegahan pemutusan sepihak"
    }
}

DRV_RENTAL_DATA_INTEGRATION = {
    "TC_DRV_RENT_I_01": {
        "tag": "BUSINESS_LOGIC",
        "tc_id": "TC_DRV_RENT_I_01",
        "description": "Rollback otomatis state toggle jika API sinkronisasi EvMoto-ECGO mengalami timeout atau HTTP 500",
        "api_mock_status": 500,
        "expected_state": "ROLLBACK_TO_OFF",
        "expected_result": "Gagal menghubungkan, saldo dan status dikembalikan ke keadaan semula"
    },
    "TC_DRV_RENT_I_02": {
        "tag": "BUSINESS_LOGIC",
        "tc_id": "TC_DRV_RENT_I_02",
        "description": "Integritas data riwayat perjalanan dan odometer motor Orphan tetap presisi saat dialihkan ke driver lain",
        "orphan_plate": "B 3456 EVM",
        "expected_result": "Riwayat order driver lama tidak tertimpa dan log odometer unit tetap berkesinambungan"
    },
    "TC_DRV_RENT_I_03": {
        "tag": "BUSINESS_LOGIC",
        "tc_id": "TC_DRV_RENT_I_03",
        "description": "Sinkronisasi status toggle Hubungkan Akun secara realtime lintas perangkat (multi-device login)",
        "device_count": 2,
        "expected_result": "Perangkat sekunder langsung menampilkan status ON/Terkunci tanpa perlu relogin"
    }
}

DRV_RENTAL_DATA_SECURITY = {
    "TC_DRV_RENT_S_01": {
        "tag": "NEGATIVE_FALSE",
        "tc_id": "TC_DRV_RENT_S_01",
        "description": "Security test: Pencegahan bypass pemutusan hubungan akun via pemanggilan direct endpoint API backend",
        "endpoint": "/api/v1/driver/vehicle/unlink",
        "method": "POST",
        "expected_status_code": 403,
        "expected_result": "403 Forbidden: One-way binding policy strictly enforced"
    },
    "TC_DRV_RENT_S_02": {
        "tag": "NEGATIVE_FALSE",
        "tc_id": "TC_DRV_RENT_S_02",
        "description": "Anti-fraud: Penolakan penautan unit motor yang sedang aktif terikat pada akun driver lain (duplikat aktif)",
        "duplicate_plate": "B 7890 EC",
        "expected_result": "Kendaraan sedang digunakan oleh driver aktif lain. Hubungi kantor operasional."
    },
    "TC_DRV_RENT_S_03": {
        "tag": "NEGATIVE_FALSE",
        "tc_id": "TC_DRV_RENT_S_03",
        "description": "Security test: Pembatasan akses telemetri, lokasi GPS, dan remote switch bagi driver lama terhadap unit Orphan",
        "action": "ACCESS_ORPHAN_TELEMETRY",
        "expected_result": "Akses ditolak: Mitra tidak memiliki otorisasi terhadap kendaraan yang telah dilepas"
    }
}

DRV_RENTAL_DATA_EXCEPTION_UX = {
    "TC_DRV_RENT_E_01": {
        "tag": "NEGATIVE_TRUE",
        "tc_id": "TC_DRV_RENT_E_01",
        "description": "Penanganan penggantian unit fisik di bengkel/dealer ECGO saat motor mengalami kerusakan teknis berat",
        "flow": "DEALER_UNIT_SWAP",
        "expected_result": "Unit pengganti terhubung secara otomatis ke kontrak sewa aktif driver"
    },
    "TC_DRV_RENT_E_02": {
        "tag": "NEGATIVE_TRUE",
        "tc_id": "TC_DRV_RENT_E_02",
        "description": "Penanganan putus koneksi internet mendadak saat request aktivasi toggle Hubungkan Akun dikirim",
        "network_drop_sec": 4,
        "expected_result": "Sistem menyajikan tombol Coba Lagi tanpa menduplikasi data transaksi di backend"
    },
    "TC_DRV_RENT_E_03": {
        "tag": "NEGATIVE_TRUE",
        "tc_id": "TC_DRV_RENT_E_03",
        "description": "UX validasi masa transisi: Driver tetap dapat mengakses fitur reguler Super Apps meski belum menautkan sewa",
        "is_linked": False,
        "expected_result": "Aplikasi berjalan mulus dengan banner pengingat penautan akun tanpa memblokir aplikasi"
    },
    "TC_DRV_RENT_E_04": {
        "tag": "NEGATIVE_TRUE",
        "tc_id": "TC_DRV_RENT_E_04",
        "description": "Validasi pencocokan NIK/KTP Driver: Penolakan penautan akun jika NIK akun EvMoto berbeda dengan NIK leasing ECGO",
        "nik_evmoto": "3171012345670001",
        "nik_ecgo": "3171019999990009",
        "expected_result": "NIK terdaftar tidak sesuai dengan data perjanjian sewa motor ECGO"
    },
    "TC_DRV_RENT_E_05": {
        "tag": "NEGATIVE_TRUE",
        "tc_id": "TC_DRV_RENT_E_05",
        "description": "Penolakan eksekusi swap baterai stasiun ECGO saat aplikasi driver sedang dalam status on-bid membawa penumpang",
        "trip_status": "ON_TRIP_PASSENGER",
        "expected_result": "Selesaikan perjalanan penumpang terlebih dahulu sebelum melakukan penukaran baterai"
    }
}
