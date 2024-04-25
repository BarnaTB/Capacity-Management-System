from django.contrib.auth.tokens import PasswordResetTokenGenerator

from accounts.models import User


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: User, timestamp: int) -> str:
        return f"{timestamp}{user.role}"
