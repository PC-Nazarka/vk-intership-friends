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
        if invite.target.id == request.user.id:
            serializer = InviteAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            invite.is_accept = serializer.data["is_accept"]
            invite.save()
            if invite.is_accept is True:
                invite.target.friends.add(invite.owner)
                invite.owner.friends.add(invite.target)
            return response.Response(
                data={"message": "Статус завки изменен"},
                status=status.HTTP_200_OK,
            )
        return response.Response(
            data={"message": "Нельзя изменть статус чужого приложения"},
            status=status.HTTP_403_FORBIDDEN,
        )
