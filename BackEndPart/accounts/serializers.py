from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    bio = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"]
        )

        Profile.objects.create(
            user=user,
            name=validated_data["name"],
            bio=validated_data.get("bio", "")
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Profile
        fields = [
            "id",
            "username",
            "name",
            "bio",
            "telegram_id",
            "telegram_username",
            "telegram_connected",
        ]