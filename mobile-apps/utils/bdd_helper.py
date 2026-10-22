"""
BDD (Behavior-Driven Development) Helper Module
EVMoto User Mobile Automation
Menyediakan helper Given, When, Then, AndStep untuk standarisasi skenario pengujian mobile.
"""
class BDDStep:
    @staticmethod
    def given(step_text: str):
        """Menandai langkah precondition (GIVEN) pada skrip automasi mobile."""
        msg = f"  [GIVEN] {step_text}"
        print(msg)
        return msg

    @staticmethod
    def when(step_text: str):
        """Menandai langkah aksi pengguna (WHEN) pada aplikasi mobile."""
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


given = BDDStep.given
when = BDDStep.when
then = BDDStep.then
and_step = BDDStep.and_step
