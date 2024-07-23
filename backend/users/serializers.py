import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from users.models import Subscribtion


User = get_user_model()


class MyUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            'id', 'username', 'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribtion.objects.filter(
                user=request.user, is_subscribed_to=obj).exists()
        return False


class SubscribtionsUserSerialiser(MyUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            'id', 'username', 'is_subscribed',
            'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        from recipes.serializers import FavoriteResipeSerializer

        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            queryset = obj.recipes.all()[:recipes_limit]
        else:
            queryset = obj.recipes.all()

        return FavoriteResipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return len(obj.recipes.all())


class MyUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "password",
            'username',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        user.avatar = validated_data['avatar']
        user.save()
        return user


# class SubscribtionSerializer(serializers.ModelSerializer):
#     is_subscribed_to = MyUserSerializer(required=False)

#     def validate(self, data):
#         request = self.context.get('request')
#         user = request.user
#         is_subscribed_to = self.context['is_subscribed_to']

#         if user == is_subscribed_to:
#             raise serializers.ValidationError(
#                 'Вы не можете подписаться на самого себя.')
#         if Subscribtion.objects.filter(
#                 user=user,
#                 is_subscribed_to=is_subscribed_to).exists():
#             raise serializers.ValidationError(
#                 'Вы уже подписаны на этого пользователя.')
#         return data

#     def create(self, validated_data):
#         request = self.context.get('request')
#         user = request.user
#         is_subscribed_to = self.context['is_subscribed_to']
#         validated_data['user'] = user
#         validated_data['is_subscribed_to'] = is_subscribed_to
#         return super().create(validated_data)

#     class Meta:
#         model = Subscribtion
#         fields = ('user', 'is_subscribed_to',)
#         read_only_fields = ('user', 'is_subscribed_to',)

# class SubscriptionSerializer(serializers.ModelSerializer):
#     is_subscribed_to = MyUserSerializer()

#     class Meta:
#         model = Subscribtion
#         fields = ('is_subscribed_to',)
