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
    is_accept = serializers.BooleanField(allow_null=True, default=None)

    class Meta:
        model = Invite
        fields = (
            "id",
            "target",
            "is_accept",
        )

    def validate_is_accept(self, is_accept):
        if is_accept is not None:
            raise serializers.ValidationError(
                "Заявка не может с самого начала быть принятой/непринятой",
            )
        return is_accept

    def validate(self, attrs):
        if attrs["target"] == self.context["request"].user:
            raise serializers.ValidationError(
                "Нельзя отправить заявку самому себе",
            )
        if self.context["request"].user.friends.filter(id=attrs["target"].id).exists():
            raise serializers.ValidationError(
                "Нельзя отправить заявку пользователю, который уже является вашим другом",
            )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['target'] = UserSerializer(instance.target).data
        data['owner'] = UserSerializer(instance.owner).data
        return data
