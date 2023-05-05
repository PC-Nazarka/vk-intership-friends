import pytest
from django.urls import reverse_lazy
from rest_framework import status

from apps.users.factories import UserFactory
from apps.users.models import User

pytestmark = pytest.mark.django_db
COUNT_USERS = 5


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


def test_retrieve_user_me(api_client) -> None:
    user = UserFactory.create()
    api_client.force_authenticate(user=user)
    response = api_client.get(
        reverse_lazy(
            "api:users-me",
        ),
    )
    assert response.status_code == status.HTTP_200_OK


def test_read_list_users(api_client) -> None:
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
