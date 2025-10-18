"""Estado de autenticación"""

import reflex as rx

from app.config import ADMIN_PASSWORD_HASH
from app.utils.security import verify_password


class AuthState(rx.State):
    """Estado de autenticación simple (usuario único)"""

    # Estado de autenticación
    is_authenticated: bool = False
    login_error: str = ""
    is_loading: bool = False

    def login(self, password: str) -> rx.event.EventSpec | None:
        """
        Intenta hacer login con la contraseña proporcionada

        Args:
            password: Contraseña ingresada por el usuario

        Returns:
            Redirección al dashboard si es exitoso, None en caso contrario
        """
        self.is_loading = True
        self.login_error = ""

        # Verificar contraseña
        if verify_password(password, ADMIN_PASSWORD_HASH):
            self.is_authenticated = True
            self.login_error = ""
            self.is_loading = False
            return rx.redirect("/dashboard")
        else:
            self.is_authenticated = False
            self.login_error = "Contraseña incorrecta"
            self.is_loading = False
            return None

    def logout(self) -> rx.event.EventSpec:
        """
        Cierra la sesión del usuario

        Returns:
            Redirección a la página de login
        """
        self.is_authenticated = False
        self.login_error = ""
        return rx.redirect("/")

    def check_auth(self) -> rx.event.EventSpec | None:
        """
        Verifica si el usuario está autenticado
        Si no lo está, redirige al login

        Returns:
            Redirección al login si no está autenticado
        """
        if not self.is_authenticated:
            return rx.redirect("/")
        return None
