"""
System Management Page Object
Website:
 - /mgr  : Platform Administrator
 - /role : Role Management
 - /menu : Menu Management
 - /dept : Divisional Management
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class SystemManagementPage(BasePage):
    """Page Object untuk Modul System Management dan 4 sub-halamannya."""

    # Locators Platform Administrator (/mgr)
    LOCATOR_MGR_SEARCH_INPUT     = (By.ID, "user-name")
    LOCATOR_MGR_SEARCH_BTN       = (By.CSS_SELECTOR, "main form button[type='submit']")
    LOCATOR_MGR_TABLE            = (By.TAG_NAME, "table")
    LOCATOR_MGR_ROWS             = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_MGR_RADIO            = (By.CSS_SELECTOR, "[data-manager-user]")
    LOCATOR_MGR_EDIT_BTN         = (By.CSS_SELECTOR, "[data-manager-edit]")
    LOCATOR_MGR_SELECTION_ERROR  = (By.CSS_SELECTOR, "[data-manager-selection-error]")

    # Locators Role Management (/role)
    LOCATOR_ROLE_SEARCH_INPUT    = (By.CSS_SELECTOR, "input[name='roleName']")
    LOCATOR_ROLE_EDIT_BTN        = (By.CSS_SELECTOR, "[data-role-edit]")
    LOCATOR_ROLE_RADIO           = (By.CSS_SELECTOR, "[data-role-choice]")
    LOCATOR_ROLE_SELECTION_ERROR = (By.CSS_SELECTOR, "[data-role-selection-error]")

    # Locators Menu Management (/menu)
    LOCATOR_MENU_SEARCH_INPUT    = (By.CSS_SELECTOR, "input[name='menuName']")
    LOCATOR_MENU_EDIT_BTN        = (By.CSS_SELECTOR, "[data-menu-edit]")
    LOCATOR_MENU_RADIO           = (By.CSS_SELECTOR, "[data-menu-choice]")
    LOCATOR_MENU_SELECTION_ERROR = (By.CSS_SELECTOR, "[data-menu-selection-error]")

    # Locators Divisional Management (/dept)
    LOCATOR_DEPT_SEARCH_INPUT    = (By.CSS_SELECTOR, "input[name='condition']")
    LOCATOR_DEPT_EDIT_BTN        = (By.CSS_SELECTOR, "[data-department-edit]")
    LOCATOR_DEPT_RADIO           = (By.CSS_SELECTOR, "[data-department-choice]")
    LOCATOR_DEPT_SELECTION_ERROR = (By.CSS_SELECTOR, "[data-department-selection-error]")

    # --- 1. Platform Administrator (/mgr) ---
    def navigate_mgr(self):
        """Buka halaman Platform Administrator."""
        self.open(Config.MGR_URL)

    def get_mgr_heading_text(self):
        """Ambil heading h1 pada /mgr."""
        return self.get_text((By.TAG_NAME, "h1"))

    def is_mgr_table_displayed(self, timeout=5):
        """Periksa apakah tabel admin tampil."""
        return self.is_displayed(self.LOCATOR_MGR_TABLE, timeout=timeout)

    def is_mgr_edit_btn_displayed(self):
        """Periksa apakah tombol Edit/Update tampil."""
        return self.is_displayed(self.LOCATOR_MGR_EDIT_BTN)

    def get_mgr_rows_count(self):
        """Ambil jumlah baris data admin."""
        return len(self.find_all(self.LOCATOR_MGR_ROWS))

    def search_admin(self, keyword):
        """Cari admin berdasarkan keyword."""
        self.type_text(self.LOCATOR_MGR_SEARCH_INPUT, keyword)
        form = self.find((By.CSS_SELECTOR, "form[action='/mgr']"))
        form.submit()

    def click_mgr_edit_btn(self):
        """Klik tombol Edit/Update admin."""
        self.click(self.LOCATOR_MGR_EDIT_BTN)

    def is_mgr_selection_error_displayed(self):
        """Periksa apakah banner error seleksi admin tampil."""
        return self.is_displayed(self.LOCATOR_MGR_SELECTION_ERROR)

    # --- 2. Role Management (/role) ---
    def navigate_role(self):
        """Buka halaman Role Management."""
        self.open(Config.ROLE_URL)

    def get_role_heading_text(self):
        """Ambil heading h1 pada /role."""
        return self.get_text((By.TAG_NAME, "h1"))

    def is_role_table_displayed(self):
        """Periksa apakah tabel role tampil."""
        return self.is_displayed((By.TAG_NAME, "table"))

    def search_role(self, role_name):
        """Cari role berdasarkan nama role."""
        self.type_text(self.LOCATOR_ROLE_SEARCH_INPUT, role_name)
        form = self.find((By.CSS_SELECTOR, "form[action='/role']"))
        form.submit()

    def click_role_edit_btn(self):
        """Klik tombol Edit/Update role."""
        self.click(self.LOCATOR_ROLE_EDIT_BTN)

    def is_role_selection_error_displayed(self):
        """Periksa apakah banner error seleksi role tampil."""
        return self.is_displayed(self.LOCATOR_ROLE_SELECTION_ERROR)

    # --- 3. Menu Management (/menu) ---
    def navigate_menu(self):
        """Buka halaman Menu Management."""
        self.open(Config.MENU_URL)

    def is_menu_table_displayed(self):
        """Periksa apakah tabel menu tampil."""
        return self.is_displayed((By.TAG_NAME, "table"))

    def search_menu(self, menu_name):
        """Cari menu berdasarkan nama menu."""
        self.type_text(self.LOCATOR_MENU_SEARCH_INPUT, menu_name)
        form = self.find((By.CSS_SELECTOR, "form[action='/menu']"))
        form.submit()

    def click_menu_edit_btn(self):
        """Klik tombol Edit/Update menu."""
        self.click(self.LOCATOR_MENU_EDIT_BTN)

    def is_menu_selection_error_displayed(self):
        """Periksa apakah banner error seleksi menu tampil."""
        return self.is_displayed(self.LOCATOR_MENU_SELECTION_ERROR)

    # --- 4. Divisional Management (/dept) ---
    def navigate_dept(self):
        """Buka halaman Divisional Management."""
        self.open(Config.DEPT_URL)

    def is_dept_table_displayed(self, timeout=5):
        """Periksa apakah tabel departemen tampil."""
        return self.is_displayed((By.TAG_NAME, "table"), timeout=timeout)

    def click_dept_edit_btn(self):
        """Klik tombol Edit/Update departemen."""
        self.click(self.LOCATOR_DEPT_EDIT_BTN)

    def is_dept_selection_error_displayed(self):
        """Periksa apakah banner error seleksi departemen tampil."""
        return self.is_displayed(self.LOCATOR_DEPT_SELECTION_ERROR)
