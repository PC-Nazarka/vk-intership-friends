from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import CreateReadListViewSet
from apps.users.models import User
from apps.users.permissions import UserPermission
from apps.users.serializers import UserSerializer


class UserViewSet(CreateReadListViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (UserPermission,)

    @action(methods=("GET",), detail=False)
    def me(self, request):
        return Response(
            data=UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )

    @action(methods=('GET',), detail=False)
    def incoming_invites(self, request, *args, **kwargs):
        pass

    @action(methods=('GET',), detail=False)
    def outgoing_invites(self, request, *args, **kwargs):
        pass

    @action(methods=('GET',), detail=False)
    def friends_list(self, request, *args, **kwargs):
        pass

    @action(methods=('GET',), detail=True)
    def get_friend_status(self, request, *args, **kwargs):
        pass

    @action(methods=('GET',), detail=True)
    def delete_friend(self, request, *args, **kwargs):
        pass
