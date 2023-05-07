from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import CreateReadListViewSet
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

    @action(methods=('GET',), detail=False, url_path="incoming-invites")
    def incoming_invites(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=('GET',), detail=False, url_path="outgoing-invites")
    def outgoing_invites(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=('GET',), detail=False, url_path="friends", url_name="friends")
    def friends_list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=('GET',), detail=True, url_path="status", url_name="friend-status")
    def get_friend_status(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.id == user.id:
            return Response(
                data={"message": "Нельзя узнавать статус с самим собой"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        friend_status = FriendStatuses.NOT_FRIENDS
        if request.user.friends.filter(id=user.id).exists():
            friend_status = FriendStatuses.IS_FRIENDS
        elif request.user.incoming.filter(owner=user, target=request.user, is_accept=None).exists():
            friend_status = FriendStatuses.IS_INCOMING
        elif request.user.outgoing.filter(target=user, owner=request.user, is_accept=None).exists():
            friend_status = FriendStatuses.IS_OUTGOING
        return Response(
            data={"status": friend_status},
            status=status.HTTP_200_OK,
        )

    @action(methods=('DELETE',), detail=True, url_path="delete-friend")
    def delete_friend(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.friends.filter(id=user.id).exists():
            request.user.friends.remove(user)
            user.friends.remove(request.user)
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            data={"message": "Пользователь не является вашим другом"},
            status=status.HTTP_400_BAD_REQUEST,
        )
