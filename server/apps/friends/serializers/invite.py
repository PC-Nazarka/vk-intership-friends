from rest_framework import serializers

from apps.friends.models import Invite
from apps.users.models import User
from apps.users.serializers import UserSerializer


class InviteAcceptSerializer(serializers.Serializer):
    is_accept = serializers.BooleanField()

    def validate_is_accept(self, is_accept):
        if is_accept not in (False, True):
            raise serializers.ValidationError(
                "Заявка заявка должна быть принята",
            )
        return is_accept


class InviteSerializer(serializers.ModelSerializer):
    target = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Invite
        fields = (
            "id",
            "target",
            "is_accept",
            "owner",
        )

    def validate_is_accept(self, is_accept):
        if is_accept is not None:
            raise serializers.ValidationError(
                "Заявка не может с самого начала быть принята",
            )
        return is_accept

    def validate_target(self, target):
        if target == self.owner:
            raise serializers.ValidationError(
                "Нельзя отправить заявку самосу себе",
            )
        return target

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['target'] = UserSerializer(instance.target).data
        data['owner'] = UserSerializer(instance.owner).data
        return data
