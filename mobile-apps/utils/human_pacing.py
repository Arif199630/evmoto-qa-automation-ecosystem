"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - HUMAN PACING HELPER
================================================================================
Menyimulasikan perilaku interaksi manusia asli pada aplikasi EvMoto
(jeda berpikir, deliberasi membaca layar, dan ritme ketukan yang realistis).
================================================================================
"""
import time
import random
from utils.logger import get_logger

logger = get_logger("HumanPacing")

def human_pause(min_sec: float = 3.0, max_sec: float = 3.0, message: str = ""):
    """Menyimulasikan waktu membaca/berpikir pengguna nyata (jeda 3 detik)."""
    delay = round(random.uniform(min_sec, max_sec), 2)
    if message:
        logger.info(f"[Human Pacing] {message} (jeda {delay}s)...")
    else:
        logger.info(f"[Human Pacing] Menatap layar aplikasi (jeda {delay}s)...")
    time.sleep(delay)

def human_click(driver, element, label: str = ""):
    """Menyimulasikan ketukan jari manusia dengan jeda natural sebelum dan sesudah sentuhan."""
    pre_delay = round(random.uniform(0.6, 1.2), 2)
    time.sleep(pre_delay)
    if label:
        logger.info(f"[Touch Action] Menyentuh '{label}'...")
    element.click()
    post_delay = round(random.uniform(1.0, 1.8), 2)
    time.sleep(post_delay)

def human_type(driver, element, text: str, label: str = "", clear_first: bool = True):
    """Menyimulasikan pengetikan teks berkarakter dengan kecepatan manusia dan memastikan elemen fokus aktif di layar."""
    # 1. Sentuh field input terlebih dahulu untuk mengaktifkan fokus, kursor, keyboard, dan visual touch ripple
    if label:
        logger.info(f"[Touch Action] Memilih field '{label}' untuk mulai mengetik...")
    try:
        element.click()
    except Exception:
        pass
    time.sleep(0.4)

    if clear_first:
        try:
            element.clear()
        except Exception:
            pass
        time.sleep(0.3)

    if label:
        logger.info(f"[Input Text] Mengetik teks pada '{label}'...")

    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.06, 0.12))
    time.sleep(random.uniform(0.5, 0.9))
