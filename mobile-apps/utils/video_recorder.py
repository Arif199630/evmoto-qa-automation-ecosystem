"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - SCREEN VIDEO RECORDER
================================================================================
Merekam layar emulator Android secara otomatis ke format file MP4 resolusi tinggi
selama pengujian automasi berlangsung.
================================================================================
"""
import os
import shutil
import subprocess
import time
from pathlib import Path
from config import config
from utils.logger import get_logger

logger = get_logger("VideoRecorder")

_active_recording_proc = None
_active_remote_path = None
_active_device_udid = None

def start_screen_recording(driver, time_limit: int = 180, video_size: str = "720x1600", bit_rate: int = 4000000, remote_file: str = "live_demo_temp.mp4") -> bool:
    """Memulai perekaman video layar penuh perangkat Android menggunakan ADB native (cepat, tanpa lag Appium)."""
    global _active_recording_proc, _active_remote_path, _active_device_udid
    try:
        device_udid = getattr(config, "DEVICE_UDID", None)
        _active_device_udid = device_udid
        _active_remote_path = f"/sdcard/{remote_file}"

        cmd = ["adb"]
        if device_udid:
            cmd.extend(["-s", device_udid])
        cmd.extend([
            "shell", "screenrecord",
            "--size", video_size,
            "--bit-rate", str(bit_rate),
            "--time-limit", str(time_limit),
            _active_remote_path
        ])

        _active_recording_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info(f"[REC] Perekam video layar native ADB aktif dimulai ({video_size} @ {bit_rate // 1000000}Mbps).")
        return True
    except Exception as e:
        logger.warning(f"[REC WARNING] Fallback Appium perekam video karena: {e}")
        try:
            driver.start_recording_screen(videoSize=video_size, timeLimit=str(time_limit), bitRate=bit_rate)
            return True
        except Exception as e2:
            logger.warning(f"[REC ERROR] Gagal mengaktifkan perekam video: {e2}")
            return False

def stop_and_save_recording(driver, file_name: str = "demo_evmoto_user.mp4") -> str:
    """Menghentikan perekaman ADB dan menyimpan file video MP4 ke folder reports/videos serta direktori artifact."""
    global _active_recording_proc, _active_remote_path, _active_device_udid
    output_path = config.VIDEOS_DIR / file_name

    try:
        if _active_recording_proc or _active_remote_path:
            # 1. Kirim SIGINT (2) ke screenrecord agar MP4 atom ditutup sempurna
            cmd_stop = ["adb"]
            if _active_device_udid:
                cmd_stop.extend(["-s", _active_device_udid])
            cmd_stop.extend(["shell", "pkill", "-2", "screenrecord"])
            subprocess.run(cmd_stop, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            
            time.sleep(1.5)  # Beri waktu OS Android menulis header MP4

            if _active_recording_proc:
                try:
                    _active_recording_proc.terminate()
                except Exception:
                    pass
                _active_recording_proc = None

            # 2. Pull file rekaman dari device
            cmd_pull = ["adb"]
            if _active_device_udid:
                cmd_pull.extend(["-s", _active_device_udid])
            cmd_pull.extend(["pull", _active_remote_path, str(output_path)])
            res = subprocess.run(cmd_pull, capture_output=True, text=True, timeout=30)

            # 3. Hapus file sementara dari device
            cmd_rm = ["adb"]
            if _active_device_udid:
                cmd_rm.extend(["-s", _active_device_udid])
            cmd_rm.extend(["shell", "rm", "-f", _active_remote_path])
            subprocess.run(cmd_rm, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)

            if output_path.exists() and output_path.stat().st_size > 0:
                size_kb = output_path.stat().st_size // 1024
                logger.info(f"[REC SAVED] Video Live Demo tersimpan: {output_path} ({size_kb} KB)")

                # Salin juga ke direktori artifact conversation jika ada
                artifact_dir = Path(r"C:\Users\ASUS\.gemini\antigravity\brain\beb4ebc7-14a5-4fe6-987b-c18630fbbf02")
                if artifact_dir.exists():
                    artifact_dest = artifact_dir / file_name
                    shutil.copy2(output_path, artifact_dest)
                    logger.info(f"[REC ARTIFACT] Video disalin ke artifact: {artifact_dest}")

                return str(output_path)

        # Fallback ke Appium jika native ADB tidak ada
        raw_video = driver.stop_recording_screen()
        if raw_video:
            import base64
            video_bytes = base64.b64decode(raw_video)
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            size_kb = len(video_bytes) // 1024
            logger.info(f"[REC SAVED] Video Live Demo Appium tersimpan: {output_path} ({size_kb} KB)")
            return str(output_path)
    except Exception as e:
        logger.warning(f"[REC ERROR] Gagal menghentikan/menyimpan video: {e}")
    finally:
        _active_recording_proc = None
        _active_remote_path = None
        _active_device_udid = None

    return ""
