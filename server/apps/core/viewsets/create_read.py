from rest_framework import mixins, viewsets


class CreateReadViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass
