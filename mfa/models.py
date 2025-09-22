from django.db import models
from django.conf import settings
from django.utils import timezone

class LoginOTP(models.Model):
    """
    OTP de inicio de sesión (2FA) enviado por correo.
    Guardamos hash del código, no el código en claro.
    """
    user - models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_na 
    )
    code_hash = models.CharField(max_length=64)
    created_at = models.DateTimefield(default=timezone.now)
    expires_at = models.DateTimefield()
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    used = models.BooleanField(default=False)
    # aduitoria del destino:
    sent_to = models.EmailField(blank=True, null=true)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["used"]),
        ]

    def __str__(self):
        return f"OTP(user={self.user_id}, used={self.used}, expira={self.expires_at})"
