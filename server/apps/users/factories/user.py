from factory import Faker, django

from apps.users.models import User

PASSWORD = "root123"


class UserFactory(django.DjangoModelFactory):
    username = Faker("user_name")
    email = Faker("email")
    password = PASSWORD

    class Meta:
        model = User
        django_get_or_create = ["username"]
