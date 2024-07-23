from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.pagination import CustomPageNumberPagination
from users.models import Subscribtion
from users.serializers import (AvatarSerializer,
                               MyUserSerializer,
                               SubscribtionsUserSerialiser,
                               UserAvatarSerializer)


User = get_user_model()


def validate_recipes_limit(value):
    try:
        value = int(value)
    except ValueError:
        raise ValidationError('Ограничение для количества рецептов '
                              'должно быть целым числом.')
    if value < 0:
        raise ValidationError('Ограничение для количества рецептов '
                              'не может быть меньше нуля.')
    return value


class UserAvatarAPIView(APIView):

    def put(self, request):
        # if 'avatar' not in request.data:
        #     return Response({'avatar': ['Выберите изображение для аватарки.']},
        #                     status=status.HTTP_400_BAD_REQUEST)

        # user = request.user
        # serializer = UserAvatarSerializer(
        #     user, data=request.data, partial=True)
        serializer = AvatarSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribtionAPIView(APIView):

    def post(self, request, id):
        user = request.user
        is_subscribed_to = get_object_or_404(User, id=id)
        if user == is_subscribed_to:
            return Response(
                {'errors': 'Вы не можете подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription, created = Subscribtion.objects.get_or_create(
            user=user, is_subscribed_to=is_subscribed_to)
        if created:
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit:
                recipes_limit = validate_recipes_limit(recipes_limit)
            serializer = SubscribtionsUserSerialiser(
                is_subscribed_to, context={'request': request,
                                           'recipes_limit': recipes_limit})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'errors': 'Вы уже подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = request.user
        is_subscribed_to = get_object_or_404(User, id=id)
        subscribtion = Subscribtion.objects.filter(
            user=user, is_subscribed_to=is_subscribed_to)
        if subscribtion:
            subscribtion.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST)


class UserSubscriptionListView(generics.ListAPIView):
    serializer_class = SubscribtionsUserSerialiser
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        subscriptions = Subscribtion.objects.filter(user=self.request.user)
        return [subscription.is_subscribed_to for
                subscription in subscriptions]

    def list(self, request, *args, **kwargs):
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = validate_recipes_limit(recipes_limit)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'request': request, 'recipes_limit': recipes_limit})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit})
        return Response(serializer.data)
