import pytest
from django.urls import reverse_lazy
from rest_framework import status

from apps.friends.factories import InviteFactory
from apps.friends.models import Invite
from apps.users.factories import UserFactory

pytestmark = pytest.mark.django_db
COUNT_USERS_FRIENDS = 2
COUNT_USERS_FRIENDS_OTHER = 3


def test_create_invite_to_friend_auth(api_client) -> None:
    """Тест на создание заявки в друзья авторизированным пользователем."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    api_client.force_authenticate(user=user2)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user1.id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    filter_result = Invite.objects.filter(
        target=user1,
        is_accept=None,
        owner=user2,
    )
    assert filter_result.exists()
    invite_instance = filter_result.first()
    assert user1.incoming.filter(id=invite_instance.id).exists()
    assert user2.outgoing.filter(id=invite_instance.id).exists()


def test_create_invite_to_friend_not_auth(api_client) -> None:
    """Тест на создание заявки в друзья не авторизированным пользователем."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user1.id,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_invite_to_friend_failed(api_client) -> None:
    """Тест на провальное создание заявки в друзья авторизированным пользователем."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    api_client.force_authenticate(user=user2)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user1.id,
            "is_accept": True,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data["is_accept"][0]) == "Заявка не может с самого начала быть принятой/непринятой"


def test_create_invite_to_friend_same_user(api_client) -> None:
    """Тест на создание заявки в друзья самому себе."""
    user1 = UserFactory.create()
    api_client.force_authenticate(user=user1)
    response = api_client.post(
        reverse_lazy("api:invites-list"),
        data={
            "target": user1.id,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.data["non_field_errors"][0]) == "Нельзя отправить заявку самому себе"


def test_read_invite_to_friend_auth(api_client) -> None:
    """Тест на чтение заявки в друзья авторизированным пользователем."""
    user1, user2, user3 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS_OTHER)
    api_client.force_authenticate(user=user2)
    invite = InviteFactory.create(owner=user1, target=user2)

    api_client.force_authenticate(user=user1)
    response = api_client.get(
        reverse_lazy("api:invites-detail", kwargs={'pk': invite.id}),
    )
    assert response.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=user2)
    response = api_client.get(
        reverse_lazy("api:invites-detail", kwargs={'pk': invite.id}),
    )
    assert response.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=user3)
    response = api_client.get(
        reverse_lazy("api:invites-detail", kwargs={'pk': invite.id}),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_read_invite_to_friend_not_auth(api_client) -> None:
    """Тест на просмотр заявки в друзья не авторизированным пользователем."""
    invite = InviteFactory.create()
    response = api_client.get(
        reverse_lazy("api:invites-detail", kwargs={'pk': invite.id}),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_accept_invite_to_friend_auth(api_client) -> None:
    """Тест на принятие заявки в друзья авторизированным пользователем."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    invite = InviteFactory.create(target=user1, owner=user2)
    api_client.force_authenticate(user=user1)
    is_accept_request = True
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.id}),
        data={
            "is_accept": is_accept_request,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Статус заявки изменен"
    assert Invite.objects.get(id=invite.id).is_accept is is_accept_request
    assert user1.friends.filter(id=user2.id).exists()
    assert user2.friends.filter(id=user1.id).exists()


def test_accept_invite_to_friend_not_auth(api_client) -> None:
    """Тест на принятие заявки в друзья не авторизированным пользователем."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    invite = InviteFactory.create(target=user1, owner=user2)
    is_accept_request = True
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.id}),
        data={
            "is_accept": is_accept_request,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Invite.objects.get(id=invite.id).is_accept is not is_accept_request
    assert Invite.objects.get(id=invite.id).is_accept is None


def test_not_accept_invite_to_friend(api_client) -> None:
    """Тест на отклонение заявки в друзья авторизированным пользователем."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    invite = InviteFactory.create(target=user1, owner=user2)
    api_client.force_authenticate(user=user1)
    is_accept_request = False
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.id}),
        data={
            "is_accept": is_accept_request,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Статус заявки изменен"
    assert Invite.objects.get(id=invite.id).is_accept is is_accept_request
    assert not user1.friends.filter(id=user2.id).exists()
    assert not user2.friends.filter(id=user1.id).exists()


def test_accept_other_invite_to_friend(api_client) -> None:
    """Тест на принятие заявки в друзья третьим авторизированным пользователем."""
    user1, user2, user3 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS_OTHER)
    invite = InviteFactory.create(target=user1, owner=user2)
    api_client.force_authenticate(user=user3)
    is_accept_request = False
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.id}),
        data={
            "is_accept": is_accept_request,
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Invite.objects.get(id=invite.id).is_accept is not is_accept_request
    assert Invite.objects.get(id=invite.id).is_accept is None


def test_accept_invite_to_friend_by_owner(api_client) -> None:
    """Тест на изменение статуса заявки в друзья отправителем заявки."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    invite = InviteFactory.create(target=user1, owner=user2)
    api_client.force_authenticate(user=user2)
    is_accept_request = False
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.id}),
        data={
            "is_accept": is_accept_request,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Отправитель заявки не может изменить ее статус"
    assert Invite.objects.get(id=invite.id).is_accept is not is_accept_request
    assert Invite.objects.get(id=invite.id).is_accept is None


def test_accept_invite_to_friend_auth_and_change_status_after(api_client) -> None:
    """Тест на изменение статуса заявки в друзья, после ответа на эту заявку."""
    user1, user2 = UserFactory.create_batch(size=COUNT_USERS_FRIENDS)
    invite = InviteFactory.create(target=user1, owner=user2)
    api_client.force_authenticate(user=user1)
    is_accept_request = True
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.id}),
        data={
            "is_accept": is_accept_request,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Статус заявки изменен"

    is_accept_request_new = False
    response = api_client.patch(
        reverse_lazy("api:invites-accept", kwargs={"pk": invite.id}),
        data={
            "is_accept": is_accept_request_new,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "На данную заявку уже дали ответ"
