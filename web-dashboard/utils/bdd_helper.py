"""
BDD (Behavior-Driven Development) Helper Module
Automation Project EvMoto
Menyediakan helper Given, When, Then, AndStep untuk standarisasi skenario pengujian.
"""
import sys

class BDDStep:
    @staticmethod
    def given(step_text: str):
        """Menandai langkah precondition (GIVEN)."""
        msg = f"  [GIVEN] {step_text}"
        print(msg)
        return msg

    @staticmethod
    def when(step_text: str):
        """Menandai langkah aksi pengguna (WHEN)."""
        msg = f"  [WHEN]  {step_text}"
        print(msg)
        return msg

    @staticmethod
    def then(step_text: str):
        """Menandai langkah verifikasi / ekspektasi hasil (THEN)."""
        msg = f"  [THEN]  {step_text}"
        print(msg)
        return msg

    @staticmethod
    def and_step(step_text: str):
        """Menandai langkah lanjutan (AND)."""
        msg = f"  [AND]   {step_text}"
        print(msg)
        return msg


# Shortcut functions agar pemanggilan di skrip test case sangat elegan dan bersih
given = BDDStep.given
when = BDDStep.when
then = BDDStep.then
and_step = BDDStep.and_step
