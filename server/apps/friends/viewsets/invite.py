from rest_framework import permissions
from rest_framework.decorators import action

from apps.core.viewsets import CreateReadViewSet
from apps.friends.models import Invite
from apps.friends.serializers import InviteSerializer


class InviteViewSet(CreateReadViewSet):
    serializer_class = InviteSerializer
    queryset = Invite.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=("POST",), detail=True)
    def accept(self, request, *args, **kwargs):
        pass
