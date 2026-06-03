from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied

from .models import Post, Like
from .serializers import PostSerializer, CommentSerializer
from .utils import send_telegram_message


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        return {
            "request": self.request
        }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        post = self.get_object()

        if post.author != self.request.user:
            raise PermissionDenied("Нельзя изменить чужой пост.")

        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Нельзя удалить чужой пост.")

        instance.delete()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )

        if created and post.author != request.user:
            profile = post.author.profile

            if profile.telegram_connected and profile.telegram_id:
                send_telegram_message(
                    profile.telegram_id,
                    f"Ваш пост лайкнул {request.user.profile.name}"
                )

        return Response({"message": "liked"})

    @action(detail=True, methods=["delete", "post"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()

        Like.objects.filter(
            user=request.user,
            post=post
        ).delete()

        return Response({"message": "unliked"})

    @action(detail=True, methods=["get", "post"], permission_classes=[IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        post = self.get_object()

        if request.method == "GET":
            comments = post.comments.all().order_by("-created_at")
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(
                author=request.user,
                post=post
            )

            if post.author != request.user:
                profile = post.author.profile

                if profile.telegram_connected and profile.telegram_id:
                    send_telegram_message(
                        profile.telegram_id,
                        f"{request.user.profile.name} оставил комментарий: {comment.text}"
                    )

            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
