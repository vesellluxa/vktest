from django.db import models

from users.models import User


class FriendRequest(models.Model):
    user = models.ForeignKey(
        to=User,
        related_name='user',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    to = models.ForeignKey(
        to=User,
        related_name='follow',
        verbose_name='Подписан',
        on_delete=models.CASCADE,
    )
    is_accepted = models.BooleanField(
        default=False
    )
    is_declined = models.BooleanField(
        default=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_relationships",
                fields=["user", "to"],
            )]
