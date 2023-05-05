from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import CreateReadListViewSet
from apps.friends.models import Invite
from apps.friends.serializers import InviteSerializer
from apps.users.constants import FriendStatuses
from apps.users.models import User
from apps.users.permissions import UserPermission
from apps.users.serializers import UserSerializer


class UserViewSet(CreateReadListViewSet):
    permission_classes = (UserPermission,)

    def get_serializer_class(self):
        if self.action in ("outgoing_invites", "incoming_invites"):
            return InviteSerializer
        return UserSerializer

    def get_queryset(self):
        if self.action == "incoming_invites":
            return self.request.user.incoming.filter(is_accept=None)
        elif self.action == "outgoing_invites":
            return self.request.user.outgoing.filter(is_accept=None)
        elif self.action == "friends_list":
            return self.request.user.friends.all()
        return User.objects.all()

    @action(methods=('GET',), detail=False)
    def incoming_invites(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=('GET',), detail=False)
    def outgoing_invites(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=('GET',), detail=False)
    def friends_list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=('GET',), detail=True, url_path="status", url_name="friend-status")
    def get_friend_status(self, request, *args, **kwargs):
        friend_status = FriendStatuses.NOT_FRIENDS
        user = self.get_object()
        if request.user.friends.filter(id=user.id).exists():
            friend_status = FriendStatuses.IS_FRIENDS
        elif Invite.objects.filter(owner=user, target=request.user).exists():
            friend_status = FriendStatuses.IS_INCOMING
        elif Invite.objects.filter(target=user, owner=request.user).exists():
            friend_status = FriendStatuses.IS_OUTGOING
        return Response(
            data={"status": friend_status},
            status=status.HTTP_200_OK,
        )

    @action(methods=('DELETE',), detail=True, url_name="delete-friend")
    def delete_friend(self, request, *args, **kwargs):
        user = self.get_object()
        request.user.friends.remove(user)
        user.friends.remove(request.user)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
