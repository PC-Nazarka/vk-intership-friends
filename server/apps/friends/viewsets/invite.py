from rest_framework import permissions, response, status
from rest_framework.decorators import action

from apps.core.viewsets import CreateReadViewSet
from apps.friends.models import Invite
from apps.friends.serializers import InviteAcceptSerializer, InviteSerializer


class InviteViewSet(CreateReadViewSet):
    serializer_class = InviteSerializer
    queryset = Invite.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=("PATCH",), detail=True)
    def accept(self, request, *args, **kwargs):
        invite = self.get_object()
        if invite.is_accept in (True, False):
            return response.Response(
                data={"message": "На данную заявку уже дали ответ"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if invite.target.id == request.user.id:
            serializer = InviteAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            invite.is_accept = serializer.data["is_accept"]
            invite.save()
            if invite.is_accept is True:
                invite.target.friends.add(invite.owner)
                invite.owner.friends.add(invite.target)
            return response.Response(
                data={"message": "Статус заявки изменен"},
                status=status.HTTP_200_OK,
            )
        if invite.owner.id == request.user.id:
            return response.Response(
                data={"message": "Отправитель заявки не может изменить ее статус"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return response.Response(
            data={"message": "Нельзя изменить статус чужого приложения"},
            status=status.HTTP_403_FORBIDDEN,
        )
