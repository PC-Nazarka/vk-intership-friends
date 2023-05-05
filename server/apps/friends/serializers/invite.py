from rest_framework import serializers

from apps.friends.models import Invite


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = (
            "id",
            "target",
            "is_accept",
            "owner",
        )
