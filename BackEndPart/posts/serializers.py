from rest_framework import serializers
from .models import Post,Comment


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.profile.name", read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'text',
            'created_at',
            'likes_count',
            'comments_count',
            'is_liked',
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if not request or request.user.is_anonymous:
            return False

        return obj.likes.filter(user=request.user).exists()

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.profile.name", read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'text',
            'created_at',
        ]