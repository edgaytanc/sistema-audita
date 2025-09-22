import secrets
import hashlib
import hmac
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from .model. import LoginOTP

# Parámetors ajustables
OTP_TTL_MINUTES = 10            # minutos de vigencia del código
OTP_LENGTH = 6                  # longitud del codigo
RESEND_COOLDOWN_SECONDS = 60    # espera mínima para reenviar
MAX_PER_HOUR_PER_USER = 5       # límite por hora por usuario (anti-spam)

def _hash(code: srt) -> str:
    """ Hashea el código con SHA-256 (hex)"""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()

def _throttle_can_generate(user_id: int) ->bool:
    """
    Control básico por cache: máximo N OTP hora por usuario.
    Cambia el backend de cache en settings si quieres usar Redis en prod.
    """

    key = f"otp_count_u{user_id}"
    count = cache.get(key, 0)
    if count >= MAX_PER_HOUR_PER_USER:
        return False
    cache.set(key, count +1, timeout=60 * 60)   # Ventana de 1 hora
    return True

def generate_otp(user):
    """
    Genera OTP de 6 dígitos y persiste su hash con TTL.
    Devuelve (code_en_claro, instancia_otp) o (None, None) si throttling lo bloquea.
    """
    