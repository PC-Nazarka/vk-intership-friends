import pytest
from django.urls import reverse_lazy
from rest_framework import status

from apps.friends.factories import InviteFactory
from apps.users.constants import FriendStatuses
from apps.users.factories import UserFactory
from apps.users.models import User

pytestmark = pytest.mark.django_db
COUNT_USERS = 5
COUNT_INVITES = 5
COUNT_USERS_FRIENDS = 2


def test_retrieve_user(api_client) -> None:
    user = UserFactory.create()
    api_client.force_authenticate(user=user)
    response = api_client.get(
        reverse_lazy(
            "api:users-detail",
            kwargs={"pk": user.pk},
        ),
    )
    assert response.status_code == status.HTTP_200_OK


def test_read_list_users_auth(api_client) -> None:
    users = UserFactory.create_batch(size=COUNT_USERS)
    api_client.force_authenticate(user=users[0])
    response = api_client.get(
        reverse_lazy("api:users-list"),
    )
    assert response.status_code == status.HTTP_200_OK


def test_create_users(api_client) -> None:
    user = UserFactory.build()
    response = api_client.post(
        reverse_lazy("api:users-list"),
        data={
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password": user.password,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    ).exists()


def test_get_incoming_invites_auth(api_client) -> None:
    user = UserFactory.create()
    api_client.force_authenticate(user=user)
    invites = InviteFactory.create_batch(size=COUNT_INVITES, target=user, is_accept=None)
    response = api_client.get(
        reverse_lazy("api:users-incoming-invites"),
    )
    ids = list(map(lambda x: x["id"], response.json()))
    assert response.status_code == status.HTTP_200_OK
    assert len(ids) == len(invites)
    assert ids == list(map(lambda x: x.id, invites))


def test_get_incoming_invites_not_auth(api_client) -> None:
    response = api_client.get(
        reverse_lazy("api:users-incoming-invites"),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_outgoing_invites_auth(api_client) -> None:
    user = UserFactory.create()
    api_client.force_authenticate(user=user)
    invites = InviteFactory.create_batch(size=COUNT_INVITES, owner=user, is_accept=None)
    response = api_client.get(
        reverse_lazy("api:users-outgoing-invites"),
    )
    ids = list(map(lambda x: x["id"], response.json()))
    assert response.status_code == status.HTTP_200_OK
    assert len(ids) == len(invites)
    assert ids == list(map(lambda x: x.id, invites))


def test_get_outgoing_invites_not_auth(api_client) -> None:
    UserFactory.create_batch(size=COUNT_USERS)
    response = api_client.get(
        reverse_lazy("api:users-outgoing-invites"),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_friend_status_accept(api_client) -> None:
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    api_client.force_authenticate(user=user1)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.data["status"] == FriendStatuses.NOT_FRIENDS

    invite = InviteFactory.create(owner=user2, target=user1, is_accept=None)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.data["status"] == FriendStatuses.IS_INCOMING

    api_client.force_authenticate(user=user2)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response.data["status"] == FriendStatuses.IS_OUTGOING

    api_client.force_authenticate(user=user1)
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.pk}),
        data={"is_accept": True}
    )
    assert response.status_code == status.HTTP_200_OK

    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.IS_FRIENDS


def test_get_friend_status_not_accept(api_client) -> None:
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    api_client.force_authenticate(user=user1)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.data["status"] == FriendStatuses.NOT_FRIENDS

    invite = InviteFactory.create(owner=user2, target=user1, is_accept=None)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.data["status"] == FriendStatuses.IS_INCOMING

    api_client.force_authenticate(user=user2)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response.data["status"] == FriendStatuses.IS_OUTGOING

    api_client.force_authenticate(user=user1)
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.pk}),
        data={"is_accept": False}
    )
    assert response.status_code == status.HTTP_200_OK

    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.NOT_FRIENDS


def test_delete_friends(api_client) -> None:
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    user1.friends.add(user2)
    user2.friends.add(user1)

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.IS_FRIENDS

    api_client.force_authenticate(user=user1)
    response = api_client.delete(
        reverse_lazy("api:users-delete-friend", kwargs={"pk": user2.pk}),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.NOT_FRIENDS
