from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.friends.models import Invite


@receiver(post_save, sender=Invite)
def mutual_accept_friend_invite(instance, created, **kwargs) -> None:
    if created:
        if Invite.objects.filter(target=instance.owner, owner=instance.target).exists():
            instance.is_accept = True
            instance.save()
            Invite.objects.filter(target=instance.owner, owner=instance.target).update(is_accept=instance.is_accept)
            instance.owner.friends.add(instance.target)
            instance.target.friends.add(instance.owner)
