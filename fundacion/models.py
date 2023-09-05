import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property


class Fundacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=150)

    def __str__(self):
        return self.user.__str__()

    @cached_property
    def stripe_account(self):
        """Más caché?"""
        return stripe.Account.retrieve(
            api_key=settings.STRIPE_SECRET,
            account=self.stripe_id,
        )

    @property
    def is_stripe_account_verified(self):
        account = self.stripe_account
        disabled_reason = (
            bool(account.disabled_reason) if "disabled_reason" in account else False
        )
        return account.details_submitted and not disabled_reason
