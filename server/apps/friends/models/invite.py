from django.db import models


class Invite(models.Model):
    target = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="incoming",
        verbose_name="Входящие заявки",
    )
    is_accept = models.BooleanField(
        default=None,
        blank=True,
        null=True,
        verbose_name="Принята ли заявка",
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="outgoing",
        verbose_name="Исходящие заявки",
    )

    class Meta:
        verbose_name = "Заявка в друзья"
        verbose_name_plural = "Заявки в друзья"

    def __str__(self) -> str:
        return f"{self.target.id}, {self.is_accept} {self.owner.id}"
