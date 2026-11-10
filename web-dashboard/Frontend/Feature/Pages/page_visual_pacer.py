"""
Visual Pacer & Showcase Presenter (Human-like Pacing & On-Screen HUD)
Automation Project EvMoto
Fungsi:
1. Menampilkan HUD (Heads-Up Display) interaktif di bagian atas browser untuk audiens/atasan.
2. Efek Spotlight / Laser Focus pada elemen yang sedang diuji (border glow).
3. Human-like Typing (kecepatan ketik alami karakter demi karakter).
4. Human Pacing (jeda ritmis teratur agar mudah dan nyaman disimak oleh manusia).
"""

import time
import random
from selenium.webdriver.common.by import By


class VisualPacer:
    """Helper untuk menyajikan visualisasi automation testing yang elegan dan nyaman dipandang."""

    @staticmethod
    def inject_hud(driver, title="EvMoto QA Automation Live Showcase", initial_step="Memulai Pengujian..."):
        """Menyisipkan floating status bar (HUD) modern berdesain glassmorphism di layar browser."""
        js_inject = f"""
        (function() {{
            if (document.getElementById('qa-live-hud')) {{
                var existing = document.getElementById('qa-live-hud');
                existing.querySelector('#qa-hud-step').textContent = "{initial_step}";
                return;
            }}

            var style = document.createElement('style');
            style.id = 'qa-hud-style';
            style.innerHTML = `
                @keyframes qaPulse {{
                    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }}
                    70% {{ transform: scale(1.1); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }}
                    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
                }}
                .qa-hud-beacon {{
                    width: 12px;
                    height: 12px;
                    background-color: #22c55e;
                    border-radius: 50%;
                    animation: qaPulse 2s infinite;
                    display: inline-block;
                }}
                .qa-hud-container {{
                    position: fixed;
                    top: 18px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(15, 23, 42, 0.94);
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    border-radius: 50px;
                    padding: 9px 24px;
                    color: #f8fafc;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    font-size: 13.5px;
                    font-weight: 500;
                    box-shadow: 0 12px 35px -5px rgba(0, 0, 0, 0.65), 0 0 15px rgba(56, 189, 248, 0.3);
                    z-index: 99999999;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    pointer-events: none;
                    transition: all 0.3s ease;
                }}
            `;
            document.head.appendChild(style);

            var hud = document.createElement('div');
            hud.id = 'qa-live-hud';
            hud.className = 'qa-hud-container';
            hud.innerHTML = `
                <span class="qa-hud-beacon"></span>
                <span style="color: #38bdf8; font-weight: 700; letter-spacing: 0.5px;">{title}</span>
                <span style="color: #94a3b8;">|</span>
                <span id="qa-hud-step" style="color: #f1f5f9;">{initial_step}</span>
            `;
            document.body.appendChild(hud);
        }})();
        """
        try:
            driver.execute_script(js_inject)
        except Exception:
            pass

    @staticmethod
    def update_hud(driver, step_text, pause_after=0.8):
        """Memperbarui teks langkah di status bar HUD dan memberi jeda wajar untuk dibaca penonton."""
        # Pastikan HUD ada
        VisualPacer.inject_hud(driver, initial_step=step_text)
        safe_text = step_text.replace('"', '\\"').replace("'", "\\'")
        js_update = f"""
        var stepEl = document.getElementById('qa-hud-step');
        if (stepEl) {{
            stepEl.style.opacity = '0';
            setTimeout(function() {{
                stepEl.textContent = "{safe_text}";
                stepEl.style.opacity = '1';
            }}, 150);
        }}
        """
        try:
            driver.execute_script(js_update)
        except Exception:
            pass
        if pause_after > 0:
            time.sleep(pause_after)

    @staticmethod
    def spotlight_element(driver, element, color="#22c55e", scroll=True, pause=0.5):
        """
        Menyorot elemen yang akan diuji dengan border glowing bersinar
        dan menggulir layar secara halus (smooth scroll) ke arah elemen.
        """
        try:
            if scroll:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(0.3)

            driver.execute_script(f"""
                var el = arguments[0];
                el.dataset.qaOriginalBorder = el.style.border || '';
                el.dataset.qaOriginalOutline = el.style.outline || '';
                el.dataset.qaOriginalBoxShadow = el.style.boxShadow || '';
                el.dataset.qaOriginalTransition = el.style.transition || '';
                
                el.style.transition = 'all 0.3s ease';
                el.style.outline = '3px solid {color}';
                el.style.boxShadow = '0 0 18px {color}';
            """, element)
            if pause > 0:
                time.sleep(pause)
        except Exception:
            pass

    @staticmethod
    def remove_spotlight(driver, element):
        """Mengembalikan gaya tampilan elemen ke kondisi semula."""
        try:
            driver.execute_script("""
                var el = arguments[0];
                el.style.outline = el.dataset.qaOriginalOutline || '';
                el.style.boxShadow = el.dataset.qaOriginalBoxShadow || '';
                el.style.transition = el.dataset.qaOriginalTransition || '';
            """, element)
        except Exception:
            pass

    @staticmethod
    def human_type(driver, element, text, clear_first=True, min_delay=0.035, max_delay=0.075):
        """
        Mengetik teks karakter demi karakter dengan variasi jeda acak
        seperti manusia sungguhan yang sedang mengetik di keyboard.
        """
        VisualPacer.spotlight_element(driver, element, color="#38bdf8", pause=0.3)
        if clear_first:
            element.clear()
            time.sleep(0.2)

        for char in text:
            element.send_keys(char)
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)

        time.sleep(0.3)
        VisualPacer.remove_spotlight(driver, element)

    @staticmethod
    def human_click(driver, element, pause_before=0.5, pause_after=0.8, color="#22c55e"):
        """Menyorot tombol, memberi jeda alami, lalu mengeksekusi klik."""
        VisualPacer.spotlight_element(driver, element, color=color, pause=pause_before)
        try:
            driver.execute_script("arguments[0].click();", element)
        except Exception:
            element.click()
        VisualPacer.remove_spotlight(driver, element)
        if pause_after > 0:
            time.sleep(pause_after)

    @staticmethod
    def pace(seconds=1.2):
        """Jeda ritmis santai untuk kenyamanan mata penonton/atasan."""
        time.sleep(seconds)
