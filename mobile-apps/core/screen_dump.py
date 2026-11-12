"""
Pengganti ringan driver.page_source untuk layar aplikasi EvMoto.

Di emulator CI, page_source pada layar yang memuat Google Maps (Beranda, alur pesan, Aktivitas) selalu habis waktu
240 detik, sedangkan pencarian elemen biasa (XPath / UiSelector / accessibility id) hanya 0,0-0,2 detik
(pengukuran CI run 43155338579, 12 Nov 2026). Fungsi ini mengumpulkan elemen berlabel lewat pencarian biasa lalu
menulisnya sebagai XML datar dengan atribut yang sama seperti page source (class, text, content-desc, hint,
clickable, enabled, bounds), sehingga bukti kegagalan tetap tersimpan dan locator bisa dicek offline.
"""
import time
from xml.sax.saxutils import quoteattr

ATTRS = ("text", "content-desc", "hint", "clickable", "enabled", "checked", "selected", "bounds", "resource-id")
QUERY = "//*[@content-desc!='' or @text!='' or @hint!='' or contains(@class, 'EditText') or contains(@class, 'Button')]"


def dump(driver, max_elements: int = 250, budget_seconds: float = 40.0) -> str:
    t0 = time.time()
    nodes = []
    for el in driver.find_elements("xpath", QUERY)[:max_elements]:
        if time.time() - t0 > budget_seconds:
            nodes.append('<truncated reason="budget"/>')
            break
        try:
            attrs = {"class": el.get_attribute("class") or "node"}
            for a in ATTRS:
                v = el.get_attribute(a)
                if v not in (None, "", "null"):
                    attrs[a] = v
        except Exception:
            continue
        tag = attrs["class"].replace("$", "_") or "node"
        nodes.append(f"<{tag} " + " ".join(f"{k}={quoteattr(str(v))}" for k, v in attrs.items()) + "/>")
    return "<?xml version='1.0' encoding='UTF-8'?>\n<hierarchy dump='ringan'>\n" + "\n".join(nodes) + "\n</hierarchy>\n"
