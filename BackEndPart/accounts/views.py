from django.shortcuts import render

import random
import string

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import TelegramLinkCode
from .serializers import RegisterSerializer, ProfileSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def generate_code():
    return "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=6
        )
    )


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            return Response({
                "message": "registered",
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": ProfileSerializer(user.profile).data
            }, status=201)

        return Response(serializer.errors, status=400)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data)


class CreateTelegramLinkCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = generate_code()

        TelegramLinkCode.objects.create(
            user=request.user,
            code=code
        )

        bot_url = f"https://t.me/{settings.BOT_USERNAME}?start={code}"

        return Response({
            "code": code,
            "bot_url": bot_url
        })
