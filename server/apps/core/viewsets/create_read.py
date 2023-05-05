from rest_framework import mixins, viewsets


class CreateReadViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass
