from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import exceptions, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Profile, Subscription
from .pagination import CustomPageNumberPagination
from .serializers import AvatarSerializer, SubscriptionSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    @action(
        detail=False,
        methods=["get"],
        serializer_class=SubscriptionSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        authors = user.subscriptions.values_list("author_id", flat=True)
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        serializer_class=SubscriptionSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == "POST":
            if user == author:
                raise exceptions.ValidationError("Нельзя подписаться на себя")

            try:
                Subscription.objects.create(user=user, author=author)
            except Exception as e:
                raise exceptions.ValidationError(str(e))

            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            try:
                subscription = Subscription.objects.get(
                    user=user, author=author
                )
                subscription.delete()
            except Subscription.DoesNotExist:
                raise exceptions.ValidationError("Подписка не существует")
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
