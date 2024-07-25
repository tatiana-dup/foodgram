from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators

from common.serializers import Base64ImageField, ShortResipeSerializer
from users.models import Subscribtion
from users.validators import validate_recipes_limit


User = get_user_model()


class MyUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class MyUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

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
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            recipes_limit = validate_recipes_limit(recipes_limit)
            queryset = obj.recipes.all()[:recipes_limit]
        return ShortResipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribtion
        fields = ('user', 'is_subscribed_to')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscribtion.objects.all(),
                fields=('user', 'is_subscribed_to'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]

    def validate(self, data):
        if data['user'] == data['is_subscribed_to']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.')
        return data

    def to_representation(self, instance):
        return SubscribtionsUserSerialiser(instance.is_subscribed_to,
                                           context=self.context).data


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
