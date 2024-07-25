from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Subscribtion
from users.serializers import (AvatarSerializer,
                               SubscriptionCreateSerializer,
                               SubscribtionsUserSerialiser)


User = get_user_model()


class UserAvatarAPIView(APIView):

    def put(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
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


class ManageSubscribtionAPIView(APIView):

    def post(self, request, id):
        is_subscribed_to = get_object_or_404(User, id=id)
        data = {
            'user': request.user.id,
            'is_subscribed_to': is_subscribed_to.id
        }
        serializer = SubscriptionCreateSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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


class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscribtionsUserSerialiser
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(subscribers__user=self.request.user)
