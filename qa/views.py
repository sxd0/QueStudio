from django.db.models import Count, Avg, Max, F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from .models import Category, Tag, Topic, Post, Comment, TopicVote, PostVote
from .serializers import (
    CategorySerializer, TagSerializer,
    TopicListSerializer, TopicDetailSerializer,
    PostSerializer, CommentSerializer,
)
from .permissions import IsAuthorOrAdmin
from .filters import TopicFilter
from rest_framework.views import APIView
from django.db.models import Count


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class TopicViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]
    filterset_class = TopicFilter
    search_fields = ("title", "body", "category__name",
                     "tags__name", "author__username")
    ordering_fields = ("created_at", "updated_at", "rating",
                       "posts_count", "last_activity")
    ordering = ("-created_at",)

    def get_queryset(self):
        qs = (Topic.objects
              .select_related("category", "author")
              .prefetch_related("tags")
              )
        qs = qs.annotate(
            posts_count=Count("posts", distinct=True),
            avg_post_rating=Avg("posts__rating"),
            last_activity=Max("posts__created_at"),
        )
        return qs

    def get_serializer_class(self):
        if self.action in ("list",):
            return TopicListSerializer
        return TopicDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        topic = self.get_object()
        if topic.author_id == request.user.id:
            return Response({"detail": "Нельзя голосовать за свою тему."}, status=400)
        value = int(request.data.get("value", 0))
        if value not in (-1, 1):
            return Response({"detail": "value должен быть -1 или 1."}, status=400)

        vote, created = TopicVote.objects.get_or_create(
            topic=topic, user=request.user, defaults={"value": value})
        if not created:
            if vote.value == value:
                vote.delete()
                topic.rating = F("rating") - value
                topic.save(update_fields=["rating"])
                topic.refresh_from_db(fields=["rating"])
                return Response({"rating": topic.rating, "status": "unvoted"})
            else:
                vote.value = value
                vote.save(update_fields=["value"])
                topic.rating = F("rating") + (2 * value)
                topic.save(update_fields=["rating"])
                topic.refresh_from_db(fields=["rating"])
                return Response({"rating": topic.rating, "status": "switched"})
        else:
            topic.rating = F("rating") + value
            topic.save(update_fields=["rating"])
            topic.refresh_from_db(fields=["rating"])
            return Response({"rating": topic.rating, "status": "voted"})

    @action(detail=False, methods=["get"], url_path="hot", permission_classes=[permissions.AllowAny])
    def hot(self, request):
        qs = (Topic.objects.hot()
              .select_related("category", "author")
              .prefetch_related("tags"))
        page = self.paginate_queryset(qs)
        ser = TopicListSerializer(page or qs, many=True, context={"request": request})
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @action(detail=False, methods=["get"], url_path="new", permission_classes=[permissions.AllowAny])
    def new(self, request):
        qs = (self.get_queryset().order_by("-created_at"))
        page = self.paginate_queryset(qs)
        ser = TopicListSerializer(page or qs, many=True, context={"request": request})
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]
    filterset_fields = ("topic", "author")
    search_fields = ("body", "author__username", "topic__title")
    ordering_fields = ("created_at", "rating")

    def get_queryset(self):
        return (Post.objects
                .select_related("topic", "author")
                .prefetch_related("comments"))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        post = self.get_object()
        if post.author_id == request.user.id:
            return Response({"detail": "Нельзя голосовать за своё сообщение."}, status=400)
        value = int(request.data.get("value", 0))
        if value not in (-1, 1):
            return Response({"detail": "value должен быть -1 или 1."}, status=400)

        vote, created = PostVote.objects.get_or_create(
            post=post, user=request.user, defaults={"value": value})
        if not created:
            if vote.value == value:
                vote.delete()
                post.rating = F("rating") - value
                post.save(update_fields=["rating"])
                post.refresh_from_db(fields=["rating"])
                return Response({"rating": post.rating, "status": "unvoted"})
            else:
                vote.value = value
                vote.save(update_fields=["value"])
                post.rating = F("rating") + (2 * value)
                post.save(update_fields=["rating"])
                post.refresh_from_db(fields=["rating"])
                return Response({"rating": post.rating, "status": "switched"})
        else:
            post.rating = F("rating") + value
            post.save(update_fields=["rating"])
            post.refresh_from_db(fields=["rating"])
            return Response({"rating": post.rating, "status": "voted"})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]
    filterset_fields = ("topic", "post", "author")
    search_fields = ("body", "author__username")
    ordering_fields = ("created_at",)

    def get_queryset(self):
        return (Comment.objects
                .select_related("author", "topic", "post"))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class TagCloudAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        data = (Tag.objects
                .annotate(topics=Count("topics"))
                .values("slug", "name", "topics")
                .order_by("-topics"))
        return Response(list(data))
    
class TagSlugsAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        slugs = Tag.objects.values_list("slug", flat=True).order_by("slug")
        return Response(list(slugs))