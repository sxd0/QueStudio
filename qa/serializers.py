from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db.models import Count, Avg, Max
from .models import Category, Tag, Topic, TopicTag, Post, Comment, TopicVote, PostVote
from .validators import validate_no_banned_words
from django.utils.text import slugify


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class TopicListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    author_name = serializers.CharField(source="author.username", read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    avg_post_rating = serializers.FloatField(read_only=True)
    last_activity = serializers.DateTimeField(read_only=True)
    is_editable = serializers.SerializerMethodField()

    category_slug = serializers.SlugRelatedField(
        source="category", slug_field="slug",
        queryset=Category.objects.all(),
        write_only=True, required=False
    )

    class Meta:
        model = Topic
        fields = (
            "id", "title", "slug",
            "category", "category_slug", "category_name",
            "author", "author_name",
            "rating", "created_at", "updated_at",
            "tags",
            "posts_count", "avg_post_rating", "last_activity", "is_editable",
            "status", "is_active",
        )
        read_only_fields = ("author", "rating", "created_at", "updated_at")
        validators = []
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True},
            "category": {"required": False},
        }

    def get_is_editable(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and (request.user.is_staff or obj.author_id == request.user.id))

    def get_tags(self, obj):
        return [{"id": t.id, "name": t.name, "slug": t.slug} for t in obj.tags.all()]

    def validate(self, attrs):
        title = attrs.get("title") or getattr(self.instance, "title", None)
        if title and not attrs.get("slug") and not getattr(self.instance, "slug", None):
            attrs["slug"] = slugify(title)[:220]

        category = attrs.get("category") or getattr(self.instance, "category", None)
        slug = attrs.get("slug") or getattr(self.instance, "slug", None)

        if category and title:
            qs = Topic.objects.filter(category=category, title__iexact=title)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Тема с таким названием уже существует в этой категории.")

        if category and slug:
            qs = Topic.objects.filter(category=category, slug__iexact=slug)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Слаг уже используется в этой категории.")

        if "title" in attrs:
            validate_no_banned_words(attrs["title"])
        if "body" in attrs:
            validate_no_banned_words(attrs["body"])

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        return super().create(validated_data)


class TopicDetailSerializer(TopicListSerializer):
    body = serializers.CharField()

    class Meta(TopicListSerializer.Meta):
        fields = TopicListSerializer.Meta.fields + ("body",)
        validators = []


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "topic", "author", "author_name", "body", "rating", "is_accepted", "created_at")
        read_only_fields = ("author", "rating", "created_at")

    def validate_body(self, value):
        validate_no_banned_words(value)
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "topic", "post", "author", "author_name", "body", "created_at")
        read_only_fields = ("author", "created_at")

    def validate_body(self, value):
        validate_no_banned_words(value)
        return value

    def validate(self, attrs):
        if not attrs.get("topic") and not attrs.get("post"):
            raise serializers.ValidationError("Нужно указать либо тему, либо пост для комментария.")
        if attrs.get("topic") and attrs.get("post"):
            raise serializers.ValidationError("Комментарий должен быть привязан к теме ИЛИ к посту, не к обоим.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        return super().create(validated_data)
