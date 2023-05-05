from django.apps import AppConfig


class FriendsConfig(AppConfig):
    name = 'apps.friends'

    def ready(self) -> None:
        import apps.friends.signals  # noqa F401
