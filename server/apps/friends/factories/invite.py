from factory import SubFactory, django

from apps.friends.models import Invite
from apps.users.factories import UserFactory


class InviteFactory(django.DjangoModelFactory):
    target = SubFactory(UserFactory)
    is_accept = None
    owner = SubFactory(UserFactory)

    class Meta:
        model = Invite
