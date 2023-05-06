import pytest
from django.urls import reverse_lazy
from rest_framework import status

from apps.friends.factories import InviteFactory
from apps.friends.models import Invite
from apps.users.constants import FriendStatuses
from apps.users.factories import UserFactory
from apps.users.models import User

pytestmark = pytest.mark.django_db
COUNT_USERS = 5
COUNT_INVITES = 5
COUNT_USERS_FRIENDS = 2


def test_retrieve_user(api_client) -> None:
    """Тест на чтение данных пользователя авторизированным пользователем."""
    temp_user = UserFactory.create()
    user = UserFactory.create()
    api_client.force_authenticate(user=user)
    response = api_client.get(
        reverse_lazy(
            "api:users-detail",
            kwargs={"pk": temp_user.pk},
        ),
    )
    assert response.status_code == status.HTTP_200_OK


def test_read_list_users_auth(api_client) -> None:
    """Тест на чтение данных пользователей авторизированным пользователем."""
    users = UserFactory.create_batch(size=COUNT_USERS)
    api_client.force_authenticate(user=users[0])
    response = api_client.get(
        reverse_lazy("api:users-list"),
    )
    assert response.status_code == status.HTTP_200_OK


def test_create_users(api_client) -> None:
    """Тест на создание пользователя."""
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
    """Тест на чтение входящих заявок авторизированным пользователем."""
    user = UserFactory.create()
    api_client.force_authenticate(user=user)
    invites = InviteFactory.create_batch(size=COUNT_INVITES, target=user)
    response = api_client.get(
        reverse_lazy("api:users-incoming-invites"),
    )
    assert response.status_code == status.HTTP_200_OK
    ids = list(map(lambda x: x["id"], response.json()))
    assert len(ids) == len(invites)
    assert ids == list(map(lambda x: x.id, invites))


def test_get_incoming_invites_not_auth(api_client) -> None:
    """Тест на чтение входящих заявок не авторизированным пользователем."""
    user = UserFactory.create()
    InviteFactory.create_batch(size=COUNT_INVITES, target=user)
    response = api_client.get(
        reverse_lazy("api:users-incoming-invites"),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_outgoing_invites_auth(api_client) -> None:
    """Тест на чтение исходящих заявок авторизированным пользователем."""
    user = UserFactory.create()
    api_client.force_authenticate(user=user)
    invites = InviteFactory.create_batch(size=COUNT_INVITES, owner=user)
    response = api_client.get(
        reverse_lazy("api:users-outgoing-invites"),
    )
    assert response.status_code == status.HTTP_200_OK
    ids = list(map(lambda x: x["id"], response.json()))
    assert len(ids) == len(invites)
    assert ids == list(map(lambda x: x.id, invites))


def test_get_outgoing_invites_not_auth(api_client) -> None:
    """Тест на чтение исходящих заявок не авторизированным пользователем."""
    user = UserFactory.create()
    InviteFactory.create_batch(size=COUNT_INVITES, owner=user)
    response = api_client.get(
        reverse_lazy("api:users-outgoing-invites"),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_friends_list_auth(api_client) -> None:
    """Тест на чтение списка друзей авторизированным пользователем."""
    user = UserFactory.create()
    friends = UserFactory.create_batch(size=COUNT_USERS)
    user.friends.set(friends)
    api_client.force_authenticate(user=user)
    response = api_client.get(
        reverse_lazy("api:users-friends"),
    )
    assert response.status_code == status.HTTP_200_OK
    ids = list(map(lambda x: x["id"], response.json()))
    assert len(ids) == len(friends)
    assert ids == list(map(lambda x: x.id, friends))


def test_get_friends_list_not_auth(api_client) -> None:
    """Тест на чтение списка друзей не авторизированным пользователем."""
    user = UserFactory.create()
    friends = UserFactory.create_batch(size=COUNT_USERS)
    user.friends.set(friends)
    response = api_client.get(
        reverse_lazy("api:users-friends"),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_friend_status_accept(api_client) -> None:
    """Тест на получение статуса пользователя и принятие заявки в друзья."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response2.data["status"] == response1.data["status"] == FriendStatuses.NOT_FRIENDS

    api_client.force_authenticate(user=user1)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={"target": user2.id},
    )
    assert response.status_code == status.HTTP_201_CREATED
    invite = Invite.objects.filter(target=user2, is_accept=None, owner=user1)
    assert invite.exists()

    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.data["status"] == FriendStatuses.IS_OUTGOING

    api_client.force_authenticate(user=user2)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response.data["status"] == FriendStatuses.IS_INCOMING

    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.first().pk}),
        data={"is_accept": True}
    )
    assert response.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.IS_FRIENDS


def test_get_friend_status_not_accept(api_client) -> None:
    """Тест на получение статуса пользователя и отклонение заявки в друзья."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response2.data["status"] == response1.data["status"] == FriendStatuses.NOT_FRIENDS

    api_client.force_authenticate(user=user1)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={"target": user2.id},
    )
    assert response.status_code == status.HTTP_201_CREATED
    invite = Invite.objects.filter(target=user2, is_accept=None, owner=user1)
    assert invite.exists()

    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    assert response.data["status"] == FriendStatuses.IS_OUTGOING

    api_client.force_authenticate(user=user2)
    response = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response.data["status"] == FriendStatuses.IS_INCOMING

    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.first().pk}),
        data={"is_accept": False}
    )
    assert response.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.NOT_FRIENDS


def test_delete_friends(api_client) -> None:
    """Тест на удаление из друзей."""
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


def test_mutual_accept_friend_invite(api_client) -> None:
    """Тест на принятие заявок после отправки взаимных заявок."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    api_client.force_authenticate(user=user1)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user2.id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    api_client.force_authenticate(user=user2)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user1.id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.IS_FRIENDS

    assert Invite.objects.filter(owner=user1, target=user2, is_accept=True).exists()
    assert Invite.objects.filter(owner=user2, target=user1, is_accept=True).exists()


def test_mutual_accept_friend_invite_failed(api_client) -> None:
    """Тест на провальное принятие заявок после отправки взаимных заявок."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    api_client.force_authenticate(user=user1)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user2.id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    api_client.force_authenticate(user=user2)
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": response.data["id"]}),
        data={
            "is_accept": False,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.NOT_FRIENDS

    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user1.id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == "Есть входящая заявка"
    assert response2.data["status"] == "Есть исходящая заявка"


def test_create_invite_to_user_that_already_friend(api_client) -> None:
    """Тест на отправку заявки пользователю, который уже является другом."""
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

    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user1.id,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    message_error = "Нельзя отправить заявку пользователю, который уже является вашим другом"
    assert str(response.data["non_field_errors"][0]) == message_error

    api_client.force_authenticate(user=user1)
    response1 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user2.pk}),
    )
    api_client.force_authenticate(user=user2)
    response2 = api_client.get(
        reverse_lazy("api:users-friend-status", kwargs={"pk": user1.pk}),
    )
    assert response1.data["status"] == response2.data["status"] == FriendStatuses.IS_FRIENDS
